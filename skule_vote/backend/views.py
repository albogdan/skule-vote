import hashlib

from django.conf import settings
import django.core.signing
from backend.models import (
    Election,
    ElectionSession,
    Eligibility,
    Candidate,
    Voter,
    Ballot,
)

from django.http import HttpResponse

from rest_framework import generics, exceptions
from backend.serializers import ElectionSerializer

def CookieView(request):

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

    check_string = student + registered + undergrad + primaryorg + yofstudy + campus + postcd + attendance + assocorg + pid + settings.UOFT_SECRET_KEY
    h = hashlib.md5()
    h.update(check_string)
    check_hash = h.hexdigest()

    if check_hash != request.GET.get("hash"):
        return HttpResponse(status=401)

    res = HttpResponse(status=200)
    res.set_signed_cookie("discipline", discipline)
    res.set_signed_cookie("year", year)
    res.set_signed_cookie("status", status)
    res.set_signed_cookie("pey", pey)
    return res


class ElectionListView(generics.ListAPIView):
    serializer_class = ElectionSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        try:
            discipline = self.request.get_signed_cookie("discipline")
            year = self.request.get_signed_cookie("year")
            status = self.request.get_signed_cookie("status")
            pey = self.request.get_signed_cookie("pey")
        except (django.core.signing.BadSignature, KeyError):
            raise exceptions.NotAuthenticated
        print(pey==True)
        discipline = "trackone"
        year = "first-year"
        status = "fulltime"
        pey = False

        return self.get_eligible_election_query(discipline, year, status, pey)


    @staticmethod
    def get_eligible_election_query(discipline, year, status, pey):
        print(Election.objects.filter(
            eligibilities__eng_eligible=(discipline == TRACKONE),
            eligibilities__che_eligible=(discipline == CHEMICAL),
            eligibilities__civ_eligible=(discipline == CIVIL),
            eligibilities__ele_eligible=(discipline == ELECTRICAL),
            eligibilities__cpe_eligible=(discipline == COMPUTER),
            eligibilities__esc_eligible=(discipline == ENGSCI),
            eligibilities__ind_eligible=(discipline == INDY),
            eligibilities__lme_eligible=(discipline == MINERAL),
            eligibilities__mec_eligible=(discipline == MECHANICAL),
            eligibilities__mms_eligible=(discipline == MSE),
            eligibilities__first_year_eligible=(year == 1),
            eligibilities__second_year_eligible=(year == 2),
            eligibilities__third_year_eligible=(year == 3),
            eligibilities__fourth_year_eligible=(year == 4),
            eligibilities__pey_eligible=(pey == True),
        ))
        return Election.objects.all()
