import hashlib

from django.conf import settings
import django.core.signing
from django.http import HttpResponse
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


# http://127.0.0.1:8000/api/backend/cookie/?isstudent=True&isregistered=True&isundergrad=True&primaryorg=APSE&yofstudy=1&campus=blah&postcd=AEENG&attendance=FT&assocorg=null&pid=asdflkjwerwwf
def CookieView(request):

    # Read query string
    student = request.GET.get("isstudent")
    registered = request.GET.get("isregistered")
    undergrad = request.GET.get("isundergrad")
    primaryorg = request.GET.get("primaryorg")
    yofstudy = request.GET.get("yofstudy")
    campus = request.GET.get("campus")
    postcd = request.GET.get("postcd")
    attendance = request.GET.get("attendance")
    assocorg = request.GET.get("assocorg")
    pid = request.GET.get("pid")

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
        voter.study_year = int(yofstudy)
        voter.engineering_student = primaryorg == "APSE"
        voter.discipline = postcd[2:5]  # corresponds to DISCIPLINE_CHOICES

        # No need to check for unregistered. We would have returned 401 by now
        voter.student_status = "full_time" if attendance == "FT" else "part_time"

        voter.save()

    except Voter.DoesNotExist:  # new voter -> add to DB
        voter = Voter(
            student_number_hash=pid,
            pey=(assocorg == "AEPEY"),
            study_year=int(yofstudy),
            engineering_student=(primaryorg == "APSE"),
            discipline=postcd[2:5],
            student_status="full_time" if attendance == "FT" else "part_time",
        )
        voter.save()

    res = HttpResponse(status=200)
    res.set_signed_cookie("student_number_hash", pid)
    return res


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
