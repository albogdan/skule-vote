from datetime import datetime
import hashlib

import django.core.signing
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from rest_framework import exceptions, generics

from backend.models import (
    Election,
    ElectionSession,
    Voter,
)
from backend.serializers import ElectionSerializer, ElectionSessionSerializer


class IneligibleVoterError(Exception):
    pass


class IncorrectHashError(Exception):
    pass


class IncompleteVoterInfoError(Exception):
    pass


def _now():
    return datetime.now().astimezone(settings.TZ_INFO)


def _create_verified_voter(query_dict, verify_hash=True):
    """
    This method decodes the voter information query string in the format returned by UofT. It then determines if the
    voter is eligible to vote in EngSoc elections.

    If they are, it updates their existing voter entry with the latest information. If there is no existing entry,
    a new one will be created. It then returns the student number hash which can be used as a UUID for this voter.

    If the voter is not eligible to vote in EngSoc elections, or if verify_hash==True and the query string hash is
    tampered with, it will raise an exception.
    """
    # Read query string
    try:
        student = query_dict["isstudent"]
        registered = query_dict["isregistered"]
        undergrad = query_dict["isundergrad"]
        primaryorg = query_dict["primaryorg"]
        yofstudy = query_dict["yofstudy"]
        campus = query_dict["campus"]
        postcd = query_dict["postcd"]
        attendance = query_dict["attendance"]
        assocorg = query_dict["assocorg"]
        pid = query_dict["pid"]
    except KeyError:
        raise IncompleteVoterInfoError

    # Verify data integrity
    if verify_hash:
        check_string = (
            student
            + registered
            + undergrad
            + primaryorg
            + yofstudy
            + campus
            + postcd
            + attendance
            + assocorg
            + pid
            + settings.UOFT_SECRET_KEY
        )
        h = hashlib.md5()
        h.update(check_string)
        check_hash = h.hexdigest()

        try:
            uoft_hash = query_dict.get("hash")
        except KeyError:
            raise IncompleteVoterInfoError

        if check_hash != uoft_hash:
            raise IncorrectHashError()

    # Verify basic eligibility for EngSoc elections
    eligible = (
        student == "True"
        and registered == "True"
        and primaryorg == "APSE"
        and undergrad == "True"
    )
    if not eligible:
        raise IneligibleVoterError()

    try:
        # previous voter -> update the info in DB
        voter = Voter.objects.get(student_number_hash=pid)
        voter.pey = assocorg == "AEPEY"  # either AEPEY or null
        voter.study_year = 3 if yofstudy is None or yofstudy == "" else int(yofstudy)
        voter.engineering_student = primaryorg == "APSE"

        # The university will send us the POSt code
        # This substring determines the engineering discipline and corresponds to DISCIPLINE_CHOICES
        voter.discipline = postcd[2:5]

        # No need to check for unregistered. We would have returned 401 by now
        voter.student_status = "full_time" if attendance == "FT" else "part_time"

        voter.save()

    except Voter.DoesNotExist:  # new voter -> add to DB
        voter = Voter(
            student_number_hash=pid,
            pey=(assocorg == "AEPEY"),
            study_year=(3 if yofstudy is None or yofstudy == "" else int(yofstudy)),
            engineering_student=(primaryorg == "APSE"),
            discipline=postcd[2:5],
            student_status="full_time" if attendance == "FT" else "part_time",
        )
        voter.save()

    return pid


class CookieView(View):
    """
    This view will receive the payload from the UofT endpoint, verifies data integrity, creates or updates the
    appropriate voter entry, and sets a signed cookie with the student number hash. This cookie is used to retrieve
    the list of eligible elections, as well as to vote.
    """

    def get(self, request, *args, **kwargs):
        try:
            student_number_hash = _create_verified_voter(request.GET)
        except (IneligibleVoterError, IncorrectHashError):
            return HttpResponse(status=401)
        except IncompleteVoterInfoError:
            return HttpResponse(status=400)

        # TODO: redirect to frontend
        res = HttpResponseRedirect(reverse_lazy("api:backend:election-list"))
        res.set_signed_cookie("student_number_hash", student_number_hash)
        return res


class BypassUofTCookieView(View):
    """
    This view is exclusively for use in testing. It renders a form that lets the developer input their desired
    eligibility criteria, then creates a querystring similar to the one sent by UofT. This view then creates a voter
    with those properties and return a signed cookie.

    Since this view allows the developer to create an unlimited number of  arbitrary voters, it is only added as a
    path when setting.CONNECT_TO_UOFT is set to 0. In prod, setting.CONNECT_TO_UOFT should always be set to 1.
    """

    def get(self, request, *args, **kwargs):
        return render(request, "cookieform.html")

    def post(self, request, *args, **kwargs):
        try:
            student_number_hash = _create_verified_voter(
                request.POST, verify_hash=False
            )
        except IneligibleVoterError:
            return HttpResponse(status=401)
        except IncompleteVoterInfoError:
            return HttpResponse(status=400)

        # TODO: Redirect to frontend
        res = HttpResponseRedirect(reverse_lazy("api:backend:election-list"))
        res.set_signed_cookie("student_number_hash", student_number_hash)
        return res


class ElectionListView(generics.ListAPIView):
    """
    Returns all election that a specific voter is eligible to vote for. Also ensures that the voter has a valid signed
    cookie.
    """

    serializer_class = ElectionSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        try:
            student_number_hash = self.request.get_signed_cookie("student_number_hash")
        except (django.core.signing.BadSignature, KeyError):
            raise exceptions.NotAuthenticated

        voter = Voter.objects.get(student_number_hash=student_number_hash)

        now = _now()
        election_session = ElectionSession.objects.filter(
            Q(start_time__lt=now) & Q(end_time__gt=now)
        )
        if not election_session.exists():
            return election_session

        # Return only Elections in an active ElectionSession
        q = Election.objects.filter(Q(election_session=election_session[0]))

        # A voter isn't eligible to vote in an election where they have already voted
        q = q.exclude(ballots__voter=voter)

        # Filter based on student fulltime/parttime status
        q = q.filter(
            Q(eligibilities__status_eligible=voter.student_status)
            | Q(eligibilities__status_eligible="full_and_part_time")
        )

        # For pey students we don't check year and vice versa
        if voter.pey:
            q = q.filter(eligibilities__pey_eligible=True)
        else:
            kwargs = {f"eligibilities__year_{voter.study_year}_eligible": True}
            q = q.filter(**kwargs)

        # Finally filter based on discipline
        kwargs = {f"eligibilities__{voter.discipline.lower()}_eligible": True}
        q = q.filter(**kwargs)

        return q


class ElectionSessionListView(generics.ListAPIView):
    """
    Returns the currently happening ElectionSessions. If there are none live, then returns the
    upcoming ElectionSession.
    """

    serializer_class = ElectionSessionSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        now = _now()

        # This is guaranteed to return <=1 ElectionSessions due to the constraints implemented
        # in the ElectionSession save() method.
        election_session = ElectionSession.objects.filter(
            Q(start_time__lt=now) & Q(end_time__gt=now)
        )

        if not election_session.exists():
            election_session = ElectionSession.objects.filter(
                Q(start_time__gt=now)
            ).order_by("start_time")[:1]

        return election_session
