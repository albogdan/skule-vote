import random
import string

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from skule_vote.tests import SetupElectionsMixin
from backend.models import (
    DISCIPLINE_CHOICES,
    STUDY_YEAR_CHOICES,
    Voter,
)

DISCIPLINES_POST_DICT = {
    discipline_code: f"AE{discipline_code}BLAH"
    for discipline_code, discipline_name in DISCIPLINE_CHOICES
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


class GetCookieTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.elections_view = reverse("api:backend:election-list")
        self.cookie_view = reverse("api:backend:bypass-cookie")

    def test_get_cookie(self):
        voter_dict = urlencode_cookie_request(year=1, pey=False, discipline="ENG")

        # When sending requests with client.post, django moves url query params to request.GET in the view :(
        # That's why we need to send them as a dictionary in the data field so we can read them in POST
        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.cookies["student_number_hash"].value.split(":")[0],
            voter_dict["pid"],
        )

        voter = Voter.objects.get(student_number_hash=voter_dict["pid"])
        self.assertEqual(voter.student_status, "full_time")
        self.assertEqual(voter.study_year, 1)
        self.assertEqual(voter.pey, False)
        self.assertEqual(voter.discipline, "ENG")
        self.assertEqual(voter.engineering_student, True)

    def test_nonregistered_student(self):
        voter_dict = urlencode_cookie_request(registered=False)

        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Make sure the view didn't create a voter entry
        with self.assertRaises(Voter.DoesNotExist):
            Voter.objects.get(student_number_hash=voter_dict["pid"])

    def test_nonengineering_student(self):
        voter_dict = urlencode_cookie_request(engineering=False)

        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Make sure the view didn't create a voter entry
        with self.assertRaises(Voter.DoesNotExist):
            Voter.objects.get(student_number_hash=voter_dict["pid"])

    def test_nonundergrad_student(self):
        voter_dict = urlencode_cookie_request(undergrad=False)

        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Make sure the view didn't create a voter entry
        with self.assertRaises(Voter.DoesNotExist):
            Voter.objects.get(student_number_hash=voter_dict["pid"])

    def test_nonstudent(self):
        voter_dict = urlencode_cookie_request(student=False)

        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Make sure the view didn't create a voter entry
        with self.assertRaises(Voter.DoesNotExist):
            Voter.objects.get(student_number_hash=voter_dict["pid"])

    def test_update_voter(self):
        voter_dict = urlencode_cookie_request(year=1, pey=False, discipline="ENG")
        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.cookies["student_number_hash"].value.split(":")[0],
            voter_dict["pid"],
        )

        # Change year and discipline of the voter
        voter_dict["postcd"] = "AEELEBLAH"
        voter_dict["yofstudy"] = "3"
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.cookies["student_number_hash"].value.split(":")[0],
            voter_dict["pid"],
        )

        voter = Voter.objects.get(student_number_hash=voter_dict["pid"])
        self.assertEqual(Voter.objects.count(), 1)
        self.assertEqual(voter.student_status, "full_time")
        self.assertEqual(voter.study_year, 3)
        self.assertEqual(voter.pey, False)
        self.assertEqual(voter.discipline, "ELE")
        self.assertEqual(voter.engineering_student, True)


class GetElectionsTestCase(SetupElectionsMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.elections_view = reverse("api:backend:election-list")
        self.cookie_view = reverse("api:backend:bypass-cookie")

    def test_no_cookie(self):
        response = self.client.get(self.elections_view)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        # All class reps are in the db, but each student is eligible to vote for exactly one!
        for discipline_code, discipline_name in DISCIPLINE_CHOICES:
            if discipline_code == "ENG":
                voter_dict = urlencode_cookie_request(year=1, discipline="ENG")
                response = self.client.post(self.cookie_view, voter_dict, follow=True)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                response = self.client.get(self.elections_view)
                class_reps = [
                    elec
                    for elec in response.json()
                    if elec["category"] == "class_representative"
                ]
                self.assertEqual(len(class_reps), 1)
                self.assertTrue(discipline_name in class_reps[0]["election_name"])
                continue

            for year, year_name in STUDY_YEAR_CHOICES:
                voter_dict = urlencode_cookie_request(
                    year=year, discipline=discipline_code
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
                    discipline_name in class_reps[0]["election_name"],
                    (class_reps, year, year_name, discipline_code, discipline_name),
                )
                self.assertTrue(
                    year_name in class_reps[0]["election_name"],
                    (class_reps, year, year_name, discipline_code, discipline_name),
                )

            voter_dict = urlencode_cookie_request(
                year=year, pey=True, discipline=discipline_code
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
            self.assertTrue(discipline_name in class_reps[0]["election_name"])
            self.assertTrue("PEY" in class_reps[0]["election_name"])

    def test_parttime_chair(self):
        # Part time students of any discipline and year are eligible
        for attendance_code, expected in [("PT", True), ("FT", False)]:
            for discipline_code, discipline_name in DISCIPLINE_CHOICES:
                if discipline_code == "ENG":
                    voter_dict = urlencode_cookie_request(
                        year=1, discipline="ENG", attendance=attendance_code
                    )
                    response = self.client.post(
                        self.cookie_view, voter_dict, follow=True
                    )
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    response = self.client.get(self.elections_view)
                    pt_chair = [
                        elec for elec in response.json() if elec["category"] == "other"
                    ]

                    if expected:
                        self.assertEqual(len(pt_chair), 1)
                        self.assertEqual(
                            pt_chair[0]["election_name"], "Part-Time Chair"
                        )
                    else:
                        self.assertEqual(len(pt_chair), 0)
                    continue

                for year, year_name in STUDY_YEAR_CHOICES:
                    voter_dict = urlencode_cookie_request(
                        year=year,
                        discipline=discipline_code,
                        attendance=attendance_code,
                    )
                    response = self.client.post(
                        self.cookie_view, voter_dict, follow=True
                    )
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    response = self.client.get(self.elections_view)
                    pt_chair = [
                        elec for elec in response.json() if elec["category"] == "other"
                    ]

                    if expected:
                        self.assertEqual(len(pt_chair), 1)
                        self.assertEqual(
                            pt_chair[0]["election_name"], "Part-Time Chair"
                        )
                    else:
                        self.assertEqual(len(pt_chair), 0)

    def test_officer(self):
        # All students are eligible
        for attendance_code in ["PT", "FT"]:
            for discipline_code, discipline_name in DISCIPLINE_CHOICES:
                if discipline_code == "ENG":
                    voter_dict = urlencode_cookie_request(
                        year=1, discipline="ENG", attendance=attendance_code
                    )
                    response = self.client.post(
                        self.cookie_view, voter_dict, follow=True
                    )
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    response = self.client.get(self.elections_view)
                    pres = [
                        elec
                        for elec in response.json()
                        if elec["category"] == "officer"
                    ]
                    self.assertEqual(len(pres), 1)
                    continue

                for year, year_name in STUDY_YEAR_CHOICES:
                    voter_dict = urlencode_cookie_request(
                        year=year,
                        discipline=discipline_code,
                        attendance=attendance_code,
                    )
                    response = self.client.post(
                        self.cookie_view, voter_dict, follow=True
                    )
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    response = self.client.get(self.elections_view)
                    pres = [
                        elec
                        for elec in response.json()
                        if elec["category"] == "officer"
                    ]
                    self.assertEqual(len(pres), 1)

    def test_referendum(self):
        # All students are eligible
        for attendance_code in ["PT", "FT"]:
            for discipline_code, discipline_name in DISCIPLINE_CHOICES:
                if discipline_code == "ENG":
                    voter_dict = urlencode_cookie_request(
                        year=1, discipline="ENG", attendance=attendance_code
                    )
                    response = self.client.post(
                        self.cookie_view, voter_dict, follow=True
                    )
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    response = self.client.get(self.elections_view)
                    referendum = [
                        elec
                        for elec in response.json()
                        if elec["category"] == "referenda"
                    ]
                    self.assertEqual(len(referendum), 1)
                    continue

                for year, year_name in STUDY_YEAR_CHOICES:
                    voter_dict = urlencode_cookie_request(
                        year=year,
                        discipline=discipline_code,
                        attendance=attendance_code,
                    )
                    response = self.client.post(
                        self.cookie_view, voter_dict, follow=True
                    )
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    response = self.client.get(self.elections_view)
                    referendum = [
                        elec
                        for elec in response.json()
                        if elec["category"] == "referenda"
                    ]
                    self.assertEqual(len(referendum), 1)

    def test_discipline_club_chair(self):
        for attendance_code in ["PT", "FT"]:
            for discipline_code, discipline_name in DISCIPLINE_CHOICES:
                if discipline_code == "ENG":
                    continue

                for year, year_name in STUDY_YEAR_CHOICES:
                    voter_dict = urlencode_cookie_request(
                        year=year,
                        discipline=discipline_code,
                        attendance=attendance_code,
                    )
                    response = self.client.post(
                        self.cookie_view, voter_dict, follow=True
                    )
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    response = self.client.get(self.elections_view)
                    expected_election_name = (
                        "ECE Club Chair"
                        if discipline_code in ["CPE", "ELE"]
                        else f"{discipline_name} Club Chair"
                    )
                    chair = [
                        elec
                        for elec in response.json()
                        if elec["category"] == "discipline_club"
                    ]
                    self.assertEqual(len(chair), 1)
                    self.assertEqual(chair[0]["election_name"], expected_election_name)
