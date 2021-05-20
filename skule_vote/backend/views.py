import hashlib

from django.conf import settings
import django.core.signing
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics, exceptions

from backend.models import (
    Election,
    ElectionSession,
    Eligibility,
    Candidate,
    Voter,
    Ballot,
)
from backend.serializers import ElectionSerializer


def get_eligible_election_query(voter):
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


def CookieView(request):

    if request.method == "POST":
        # Read query string
        student = request.POST.get("isstudent")
        registered = request.POST.get("isregistered")
        undergrad = request.POST.get("isundergrad")
        primaryorg = request.POST.get("primaryorg")
        yofstudy = request.POST.get("yofstudy")
        campus = request.POST.get("campus")
        postcd = request.POST.get("postcd")
        attendance = request.POST.get("attendance")
        assocorg = request.POST.get("assocorg")
        pid = request.POST.get("pid")

        # Verify data integrity
        # check_string = (
        #     student
        #     + registered
        #     + undergrad
        #     + primaryorg
        #     + yofstudy
        #     + campus
        #     + postcd
        #     + attendance
        #     + assocorg
        #     + pid
        #     + settings.UOFT_SECRET_KEY
        # )
        # h = hashlib.md5()
        # h.update(check_string)
        # check_hash = h.hexdigest()
        #
        # if check_hash != request.GET.get("hash"):
        #     return HttpResponse(status=401)

        # Verify basic eligibility for EngSoc elections
        eligible = (
            student == "True"
            and registered == "True"
            and primaryorg == "APSE"
            and undergrad == "True"
        )
        if not eligible:
            return HttpResponse(status=401)

        try:
            # previous voter -> update the info in DB
            voter = Voter.objects.get(student_number_hash=pid)
            voter.pey = assocorg == "AEPEY"  # either AEPEY or null
            voter.study_year = 3 if yofstudy is None else int(yofstudy)
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
                study_year=(3 if yofstudy is None else int(yofstudy)),
                engineering_student=(primaryorg == "APSE"),
                discipline=postcd[2:5],
                student_status="full_time" if attendance == "FT" else "part_time",
            )
            voter.save()

        res = HttpResponseRedirect("/api/elections")
        res.set_signed_cookie("student_number_hash", pid)
        return res
    elif request.method == "GET":
        return render(request, "cookieform.html")


class ElectionListView(generics.ListAPIView):
    serializer_class = ElectionSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        try:
            student_number_hash = self.request.get_signed_cookie("student_number_hash")
            print(student_number_hash)
        except (django.core.signing.BadSignature, KeyError):
            raise exceptions.NotAuthenticated

        voter = Voter.objects.get(student_number_hash=student_number_hash)

        return get_eligible_election_query(voter)
