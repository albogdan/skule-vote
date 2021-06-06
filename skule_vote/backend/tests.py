from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from skule_vote.tests import SetupMixin
from backend.models import (
    DISCIPLINE_CHOICES,
    STUDY_YEAR_CHOICES,
    ElectionSession,
    Voter,
)


class CookieViewTestCase(SetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.elections_view = reverse("api:backend:election-list")
        self.cookie_view = reverse("api:backend:bypass-cookie")

    def test_get_cookie(self):
        voter_dict = self._urlencode_cookie_request(year=1, pey=False, discipline="ENG")

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
        voter_dict = self._urlencode_cookie_request(registered=False)

        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Make sure the view didn't create a voter entry
        with self.assertRaises(Voter.DoesNotExist):
            Voter.objects.get(student_number_hash=voter_dict["pid"])

    def test_nonengineering_student(self):
        voter_dict = self._urlencode_cookie_request(engineering=False)

        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Make sure the view didn't create a voter entry
        with self.assertRaises(Voter.DoesNotExist):
            Voter.objects.get(student_number_hash=voter_dict["pid"])

    def test_nonundergrad_student(self):
        voter_dict = self._urlencode_cookie_request(undergrad=False)

        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Make sure the view didn't create a voter entry
        with self.assertRaises(Voter.DoesNotExist):
            Voter.objects.get(student_number_hash=voter_dict["pid"])

    def test_nonstudent(self):
        voter_dict = self._urlencode_cookie_request(student=False)

        response = self.client.post(self.cookie_view, voter_dict, follow=True)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Make sure the view didn't create a voter entry
        with self.assertRaises(Voter.DoesNotExist):
            Voter.objects.get(student_number_hash=voter_dict["pid"])

    def test_update_voter(self):
        voter_dict = self._urlencode_cookie_request(year=1, pey=False, discipline="ENG")
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


class ElectionsViewTestCase(SetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.elections_view = reverse("api:backend:election-list")
        self.cookie_view = reverse("api:backend:bypass-cookie")

    def test_no_cookie(self):
        response = self.client.get(self.elections_view)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_modify_cookie(self):
        # Make sure the election endpoint notices that we change the student number hash
        voter_dict = self._urlencode_cookie_request()

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
        election_session = self._create_election_session(
            self._set_election_session_data()
        )
        self.setUpElections(election_session)

        # All class reps are in the db, but each student is eligible to vote for exactly one!
        for discipline_code, discipline_name in DISCIPLINE_CHOICES:
            if discipline_code == "ENG":
                voter_dict = self._urlencode_cookie_request(year=1, discipline="ENG")
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
                voter_dict = self._urlencode_cookie_request(
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

            voter_dict = self._urlencode_cookie_request(
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
        election_session = self._create_election_session(
            self._set_election_session_data()
        )
        self.setUpElections(election_session)

        # Part time students of any discipline and year are eligible
        for attendance_code, expected in [("PT", True), ("FT", False)]:
            for discipline_code, discipline_name in DISCIPLINE_CHOICES:
                if discipline_code == "ENG":
                    voter_dict = self._urlencode_cookie_request(
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
                    voter_dict = self._urlencode_cookie_request(
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
        election_session = self._create_election_session(
            self._set_election_session_data()
        )
        self.setUpElections(election_session)

        # All students are eligible
        for attendance_code in ["PT", "FT"]:
            for discipline_code, discipline_name in DISCIPLINE_CHOICES:
                if discipline_code == "ENG":
                    voter_dict = self._urlencode_cookie_request(
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
                    voter_dict = self._urlencode_cookie_request(
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
        election_session = self._create_election_session(
            self._set_election_session_data()
        )
        self.setUpElections(election_session)

        # All students are eligible
        for attendance_code in ["PT", "FT"]:
            for discipline_code, discipline_name in DISCIPLINE_CHOICES:
                if discipline_code == "ENG":
                    voter_dict = self._urlencode_cookie_request(
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
                    voter_dict = self._urlencode_cookie_request(
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
        election_session = self._create_election_session(
            self._set_election_session_data()
        )
        self.setUpElections(election_session)

        for attendance_code in ["PT", "FT"]:
            for discipline_code, discipline_name in DISCIPLINE_CHOICES:
                if discipline_code == "ENG":
                    continue

                for year, year_name in STUDY_YEAR_CHOICES:
                    voter_dict = self._urlencode_cookie_request(
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

    def test_live_and_future_election_session_returns_only_live_elections(self):
        live_election_session = self._create_election_session(
            self._set_election_session_data()
        )
        self._create_referendum(live_election_session)

        future_election_session = self._create_election_session(
            self._set_election_session_data(
                name="SpringElectionSession2022",
                start_time_offset_days=8,
                end_time_offset_days=16,
            )
        )
        self._create_officer(future_election_session)

        voter_dict = self._urlencode_cookie_request(
            year=1, discipline="ENG", attendance="FT"
        )
        self.client.post(self.cookie_view, voter_dict, follow=True)

        response = self.client.get(self.elections_view)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        referendum = live_election_session.elections.all()[0]
        officer = future_election_session.elections.all()[0]
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["election_name"], referendum.election_name)
        self.assertNotEqual(response.json()[0]["election_name"], officer.election_name)

    def test_live_and_past_election_session_returns_only_live_elections(self):
        live_election_session = self._create_election_session(
            self._set_election_session_data()
        )
        self._create_referendum(live_election_session)

        past_election_session = self._create_election_session(
            self._set_election_session_data(
                name="SpringElectionSession2022",
                start_time_offset_days=-6,
                end_time_offset_days=-4,
            )
        )
        self._create_officer(past_election_session)

        voter_dict = self._urlencode_cookie_request(
            year=1, discipline="ENG", attendance="FT"
        )
        self.client.post(self.cookie_view, voter_dict, follow=True)

        response = self.client.get(self.elections_view)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        referendum = live_election_session.elections.all()[0]
        officer = past_election_session.elections.all()[0]
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["election_name"], referendum.election_name)
        self.assertNotEqual(response.json()[0]["election_name"], officer.election_name)

    def test_future_election_session_returns_empty_list(self):
        future_election_session = self._create_election_session(
            self._set_election_session_data(
                start_time_offset_days=8,
                end_time_offset_days=16,
            )
        )
        self._create_officer(future_election_session)

        voter_dict = self._urlencode_cookie_request(
            year=1, discipline="ENG", attendance="FT"
        )
        self.client.post(self.cookie_view, voter_dict, follow=True)

        response = self.client.get(self.elections_view)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()), 0)
        self.assertEqual(response.json(), [])

    def test_past_election_session_returns_empty_list(self):
        past_election_session = self._create_election_session(
            self._set_election_session_data(
                start_time_offset_days=-8,
                end_time_offset_days=-4,
            )
        )
        self._create_officer(past_election_session)

        voter_dict = self._urlencode_cookie_request(
            year=1, discipline="ENG", attendance="FT"
        )
        self.client.post(self.cookie_view, voter_dict, follow=True)

        response = self.client.get(self.elections_view)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()), 0)
        self.assertEqual(response.json(), [])


class ElectionSessionViewTestCase(SetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.election_session_view = reverse("api:backend:election-session-list")

    def test_live_election_session_returns_future_election_does_not_success(self):
        future_session = self._set_election_session_data(
            name="TestElectionSession", start_time_offset_days=1
        )
        self._create_election_session()
        current_session = self._set_election_session_data()
        self._create_election_session()

        response = self.client.get(self.election_session_view)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ElectionSession.objects.count(), 2)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["election_session_name"],
            current_session["election_session_name"],
        )
        self.assertEqual(
            response.json()[0]["start_time"], current_session["start_time"].isoformat()
        )
        self.assertEqual(
            response.json()[0]["end_time"], current_session["end_time"].isoformat()
        )

    def test_live_election_session_returns_past_election_session_does_not_success(self):
        past = self._set_election_session_data(
            name="TestElectionSession",
            start_time_offset_days=-4,
            end_time_offset_days=-2,
        )
        self._create_election_session()
        current_session = self._set_election_session_data()
        self._create_election_session()

        response = self.client.get(self.election_session_view)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ElectionSession.objects.count(), 2)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["election_session_name"],
            current_session["election_session_name"],
        )
        self.assertEqual(
            response.json()[0]["start_time"], current_session["start_time"].isoformat()
        )
        self.assertEqual(
            response.json()[0]["end_time"], current_session["end_time"].isoformat()
        )

    def test_no_live_election_session_returns_future_election_session_success(self):
        future_session = self._set_election_session_data(start_time_offset_days=1)
        self._create_election_session()
        response = self.client.get(self.election_session_view)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ElectionSession.objects.count(), 1)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["election_session_name"],
            future_session["election_session_name"],
        )
        self.assertEqual(
            response.json()[0]["start_time"], future_session["start_time"].isoformat()
        )
        self.assertEqual(
            response.json()[0]["end_time"], future_session["end_time"].isoformat()
        )

    def test_no_live_or_future_elections_returns_empty_list(self):
        past_session = self._set_election_session_data(
            start_time_offset_days=-4, end_time_offset_days=-2
        )
        self._create_election_session()

        response = self.client.get(self.election_session_view)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ElectionSession.objects.count(), 1)
        self.assertEqual(len(response.json()), 0)
        self.assertEqual(response.json(), [])

    def test_multiple_future_election_sessions_returns_closest_one(self):
        last_session = self._set_election_session_data(
            start_time_offset_days=10, end_time_offset_days=12
        )
        self._create_election_session()
        middle_session = self._set_election_session_data(
            start_time_offset_days=6, end_time_offset_days=8
        )
        self._create_election_session()
        first_session = self._set_election_session_data(
            start_time_offset_days=2, end_time_offset_days=4
        )
        self._create_election_session()

        response = self.client.get(self.election_session_view)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ElectionSession.objects.count(), 3)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["election_session_name"],
            first_session["election_session_name"],
        )
        self.assertEqual(
            response.json()[0]["start_time"], first_session["start_time"].isoformat()
        )
        self.assertEqual(
            response.json()[0]["end_time"], first_session["end_time"].isoformat()
        )
