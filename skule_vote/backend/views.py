import hashlib

import django.core.signing
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from rest_framework import exceptions, generics

from backend.models import (
    Ballot,
    Candidate,
    Election,
    ElectionSession,
    Eligibility,
    Voter,
)
from backend.serializers import ElectionSerializer


class IneligibleVoterError(Exception):
    pass


class IncorrectHashError(Exception):
    pass


class CookieView(View):
    def get(self, request, *args, **kwargs):
        if not settings.CONNECT_TO_UOFT:
            return render(request, "cookieform.html")

        try:
            student_number_hash = self._create_verified_voter(request.GET)
        except (IneligibleVoterError, IncorrectHashError):
            return HttpResponse(status=401)

        res = redirect(reverse_lazy("api:backend:election-list"))
        res.set_signed_cookie("student_number_hash", student_number_hash)
        return res

    def post(self, request, *args, **kwargs):
        if not settings.CONNECT_TO_UOFT:
            try:
                student_number_hash = self._create_verified_voter(
                    request.POST, verify_hash=False
                )
            except IneligibleVoterError:
                return HttpResponse(status=401)

            res = redirect(reverse_lazy("api:backend:election-list"))
            res.set_signed_cookie("student_number_hash", student_number_hash)
            return res

        return HttpResponse(status=405)

    @staticmethod
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
        student = query_dict.get("isstudent")
        registered = query_dict.get("isregistered")
        undergrad = query_dict.get("isundergrad")
        primaryorg = query_dict.get("primaryorg")
        yofstudy = query_dict.get("yofstudy")
        campus = query_dict.get("campus")
        postcd = query_dict.get("postcd")
        attendance = query_dict.get("attendance")
        assocorg = query_dict.get("assocorg")
        pid = query_dict.get("pid")

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

            if check_hash != query_dict.get("hash"):
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
            voter.study_year = (
                3 if yofstudy is None or yofstudy == "" else int(yofstudy)
            )
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


class ElectionListView(generics.ListAPIView):
    serializer_class = ElectionSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        try:
            student_number_hash = self.request.get_signed_cookie("student_number_hash")
        except (django.core.signing.BadSignature, KeyError):
            raise exceptions.NotAuthenticated

        voter = Voter.objects.get(student_number_hash=student_number_hash)

        q = Election.objects.all()

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
