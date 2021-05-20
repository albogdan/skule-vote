import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from skule_vote.tests import SetupElectionsMixin
from backend.models import DISCIPLINE_CHOICES, STUDY_YEAR_CHOICES, Election, Eligibility

DISCIPLINES_POST_DICT = {
    discipline_tuple[0]: f"AE{discipline_tuple[0]}BLAH"
    for discipline_tuple in DISCIPLINE_CHOICES
}


def urlencode_cookie_request(
    student=True,
    undergrad=True,
    registered=True,
    engineering=True,
    discipline="ESC",
    year=1,
    pey=False,
    attendance="FT",
):
    # student number hash
    chars = string.ascii_letters + string.digits
    pid = "".join(random.choice(chars) for i in range(16))

    if pey:
        assocorg = "AEPEY"
        yofstudy = ""
    else:
        assocorg = "null"
        yofstudy = str(year)

    attendance = attendance
    postcd = DISCIPLINES_POST_DICT[discipline]

    primaryorg = "APSE" if engineering else "null"
    isstudent = str(student)
    isundergrad = str(undergrad)
    isregistered = str(registered)
    campus = "UTSG"

    # return f"?pid={pid}&assocorg={assocorg}&yofstudy={yofstudy}&attendance={attendance}&postcd={postcd}&primaryorg={primaryorg}&isstudent={isstudent}&isundergrad={isundergrad}&isregistered={isregistered}&campus={campus}"

    return {
        "pid": pid,
        "assocorg": assocorg,
        "yofstudy": yofstudy,
        "attendance": attendance,
        "postcd": postcd,
        "primaryorg": primaryorg,
        "isstudent": isstudent,
        "isundergrad": isundergrad,
        "isregistered": isregistered,
        "campus": campus,
    }


class GetElectionsTestCase(SetupElectionsMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.elections_view = reverse("api:backend:election-list")
        self.cookie_view = reverse("api:backend:cookie")

    def test_no_cookie(self):
        response = self.client.get(self.elections_view)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_cookie(self):
        voter_dict = urlencode_cookie_request()

        # When sending requests with client.post, django moves url query params to request.GET in the view :(
        # That's why we need to send them as a dictionary in the data field so we can read them in POST
        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.cookies["student_number_hash"].value.split(":")[0],
            voter_dict["pid"],
        )

    def test_modify_cookie(self):
        # Make sure the election endpoint notices that we change the student number hash
        voter_dict = urlencode_cookie_request()

        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.cookies["student_number_hash"].value.split(":")[0],
            voter_dict["pid"],
        )

        hash_signature = "".join(
            self.client.cookies["student_number_hash"].value.split(":")[1:]
        )
        self.client.cookies["student_number_hash"].set(
            "student_number_hash",
            "im hacking the hash:" + hash_signature,
            "im hacking the hash:" + hash_signature,
        )

        response = self.client.get(self.elections_view)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_class_reps(self):
        for discipline_tuple in DISCIPLINE_CHOICES:
            if discipline_tuple[0] == "ENG":
                voter_dict = urlencode_cookie_request(year=1, discipline="ENG")
                response = self.client.post(self.cookie_view, voter_dict, follow=True)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                response = self.client.get(self.elections_view)
                print(response.json())
                class_reps = [
                    elec
                    for elec in response.json()
                    if elec["category"] == "class_representative"
                ]
                self.assertEqual(len(class_reps), 1)
                self.assertTrue(discipline_tuple[1] in class_reps[0]["election_name"])
                continue

            for year_tuple in STUDY_YEAR_CHOICES:
                voter_dict = urlencode_cookie_request(
                    year=year_tuple[0], discipline=discipline_tuple[0]
                )
                response = self.client.post(self.cookie_view, voter_dict, follow=True)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                response = self.client.get(self.elections_view)
                class_reps = [
                    elec
                    for elec in response.json()
                    if elec["category"] == "class_representative"
                ]

                self.assertEqual(len(class_reps), 1)
                self.assertTrue(
                    discipline_tuple[1] in class_reps[0]["election_name"],
                    (class_reps, year_tuple, discipline_tuple),
                )
                self.assertTrue(
                    year_tuple[1] in class_reps[0]["election_name"],
                    (class_reps, year_tuple, discipline_tuple),
                )

            voter_dict = urlencode_cookie_request(
                year=year_tuple[0], pey=True, discipline=discipline_tuple[0]
            )
            response = self.client.post(self.cookie_view, voter_dict, follow=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.get(self.elections_view)
            class_reps = [
                elec
                for elec in response.json()
                if elec["category"] == "class_representative"
            ]

            self.assertEqual(len(class_reps), 1)
            self.assertTrue(
                discipline_tuple[1] in class_reps[0]["election_name"],
                (class_reps, "pey", discipline_tuple),
            )
            self.assertTrue(
                "PEY" in class_reps[0]["election_name"],
                (class_reps, "pey", discipline_tuple),
            )
