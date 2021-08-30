from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from skule_vote.tests import SetupMixin
from backend.models import (
    Ballot,
    DISCIPLINE_CHOICES,
    STUDY_YEAR_CHOICES,
    Election,
    ElectionSession,
    Eligibility,
    Message,
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
            name="TestElectionSession", start_time_offset_days=6
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
            end_time_offset_days=-3,
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


class VoterEligibleViewTestCase(SetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.cookie_view = reverse("api:backend:bypass-cookie")
        self.voter_eligible_view = reverse("api:backend:voter-eligible")

    def test_no_cookie_returns_not_eligible(self):
        # Query the API endpoint we're testing
        response = self.client.get(self.voter_eligible_view)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"), {"voter_eligible": False}
        )

    def test_yes_cookie_returns_eligible(self):
        # Create a cookie (POST for the same reason as in CookieViewTestCase:test_get_cookie)
        voter_dict = self._urlencode_cookie_request(year=1, pey=False, discipline="ENG")
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Query the API endpoint we're testing
        response = self.client.get(self.voter_eligible_view)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertJSONEqual(
            str(response.content, encoding="utf8"), {"voter_eligible": True}
        )


class BallotSubmitViewTestCase(SetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.ballot_submit_view = reverse("api:backend:ballot-submit")
        self.cookie_view = reverse("api:backend:bypass-cookie")

        # Empty and started election session
        self.election_session = self._create_election_session(
            self._set_election_session_data()
        )

    def test_no_cookie_permission_denied(self):
        response = self.client.get(self.ballot_submit_view)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_cookie_permission_denied(self):
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

        response = self.client.get(self.ballot_submit_view)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_election_id(self):
        voter_dict = self._urlencode_cookie_request()
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Invalid election Id
        payload = {"electionId": 999999, "ranking": {}}
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Not including election Id
        payload = {"ranking": {}}
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_candidate(self):
        voter_dict = self._urlencode_cookie_request()
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = self._create_officer(self.election_session)
        payload = {"electionId": election.id, "ranking": {"1": 9999999}}
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ineligible_election_discipline(self):
        voter_dict = self._urlencode_cookie_request(discipline="CHE", year=1)
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = Election(
            election_name="Engineering Science 1st Year Rep",
            seats_available=1,
            category="class_representative",
            election_session=self.election_session,
        )
        election.save()
        eligibility = Eligibility(
            election=election,
            esc_eligible=True,
            year_1_eligible=True,
            status_eligible="full_and_part_time",
        )
        eligibility.save()

        candidate_list = self.add_candidates(election)
        payload = {
            "electionId": election.id,
            "ranking": {"1": candidate_list[0].id, "2": candidate_list[1].id},
        }
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ballot = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballot), 0)

    def test_ineligible_election_year(self):
        voter_dict = self._urlencode_cookie_request(discipline="ESC", year=2)
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = Election(
            election_name="Engineering Science 1st Year Rep",
            seats_available=1,
            category="class_representative",
            election_session=self.election_session,
        )
        election.save()
        eligibility = Eligibility(
            election=election,
            esc_eligible=True,
            year_1_eligible=True,
            status_eligible="full_and_part_time",
        )
        eligibility.save()

        candidate_list = self.add_candidates(election)
        payload = {
            "electionId": election.id,
            "ranking": {"1": candidate_list[0].id, "2": candidate_list[1].id},
        }
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ballot = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballot), 0)

    def test_ineligible_election_pey(self):
        voter_dict = self._urlencode_cookie_request(discipline="ESC", pey=True)
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = Election(
            election_name="Engineering Science 1st Year Rep",
            seats_available=1,
            category="class_representative",
            election_session=self.election_session,
        )
        election.save()
        eligibility = Eligibility(
            election=election,
            esc_eligible=True,
            year_1_eligible=True,
            status_eligible="full_and_part_time",
        )
        eligibility.save()

        candidate_list = self.add_candidates(election)
        payload = {
            "electionId": election.id,
            "ranking": {"1": candidate_list[0].id, "2": candidate_list[1].id},
        }
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ballot = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballot), 0)

        voter_dict = self._urlencode_cookie_request(discipline="ESC", year=1)
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = Election(
            election_name="Engineering Science PEY Rep",
            seats_available=1,
            category="class_representative",
            election_session=self.election_session,
        )
        election.save()
        eligibility = Eligibility(
            election=election,
            esc_eligible=True,
            pey_eligible=True,
            status_eligible="full_and_part_time",
        )
        eligibility.save()

        candidate_list = self.add_candidates(election)
        payload = {
            "electionId": election.id,
            "ranking": {"1": candidate_list[0].id, "2": candidate_list[1].id},
        }
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ballot = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballot), 0)

    def test_ineligible_election_status(self):
        voter_dict = self._urlencode_cookie_request(discipline="ESC", attendance="FT")
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = self._create_parttime_chair(self.election_session)
        candidates = self.add_candidates(election)

        payload = {
            "electionId": election.id,
            "ranking": {"1": candidates[0].id, "2": candidates[1].id},
        }
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ballot = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballot), 0)

    def test_successful_vote_officer(self):
        voter_dict = self._urlencode_cookie_request()
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = self._create_officer(self.election_session)
        candidates = self.add_candidates(election)
        payload = {
            "electionId": election.id,
            "ranking": {"1": candidates[0].id, "2": candidates[1].id},
        }
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ballots = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballots), 2)
        for ballot in ballots:
            self.assertEqual(
                ballot.voter, Voter.objects.get(student_number_hash=voter_dict["pid"])
            )
            self.assertEqual(ballot.candidate.id, payload["ranking"][str(ballot.rank)])

    def test_successful_vote_class_rep(self):
        voter_dict = self._urlencode_cookie_request(discipline="ESC", year=1)
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = Election(
            election_name="Engineering Science 1st Year Rep",
            seats_available=1,
            category="class_representative",
            election_session=self.election_session,
        )
        election.save()
        eligibility = Eligibility(
            election=election,
            esc_eligible=True,
            year_1_eligible=True,
            status_eligible="full_and_part_time",
        )
        eligibility.save()

        candidates = self.add_candidates(election, num=3)
        payload = {
            "electionId": election.id,
            "ranking": {
                "1": candidates[0].id,
                "2": candidates[1].id,
                "3": candidates[2].id,
            },
        }
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ballots = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballots), 3)
        for ballot in ballots:
            self.assertEqual(
                ballot.voter, Voter.objects.get(student_number_hash=voter_dict["pid"])
            )
            self.assertEqual(ballot.candidate.id, payload["ranking"][str(ballot.rank)])

    def test_successful_vote_class_rep_pey(self):
        voter_dict = self._urlencode_cookie_request(discipline="CIV", pey=True)
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = Election(
            election_name="Engineering Science PEY Rep",
            seats_available=1,
            category="class_representative",
            election_session=self.election_session,
        )
        election.save()
        eligibility = Eligibility(
            election=election,
            civ_eligible=True,
            pey_eligible=True,
            status_eligible="full_and_part_time",
        )
        eligibility.save()

        candidates = self.add_candidates(election, num=4)
        payload = {
            "electionId": election.id,
            "ranking": {"1": candidates[0].id},
        }
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ballots = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballots), 1)
        for ballot in ballots:
            self.assertEqual(
                ballot.voter, Voter.objects.get(student_number_hash=voter_dict["pid"])
            )
            self.assertEqual(ballot.candidate.id, payload["ranking"][str(ballot.rank)])

    def test_successful_vote_referendum(self):
        voter_dict = self._urlencode_cookie_request(
            discipline="CIV", attendance="PT", year=4
        )
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = self._create_referendum(self.election_session)

        candidates = self.add_candidates(election, num=1)
        payload = {
            "electionId": election.id,
            "ranking": {"1": candidates[0].id},
        }
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ballots = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballots), 1)
        for ballot in ballots:
            self.assertEqual(
                ballot.voter, Voter.objects.get(student_number_hash=voter_dict["pid"])
            )
            self.assertEqual(ballot.candidate.id, payload["ranking"][str(ballot.rank)])

    def test_prevent_double_vote(self):
        voter_dict = self._urlencode_cookie_request()
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = self._create_officer(self.election_session)
        candidates = self.add_candidates(election)

        # First attempt should go through
        payload = {"electionId": election.id, "ranking": {}}
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # This should fail
        payload = {"electionId": election.id, "ranking": {"1": candidates[0].id}}
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Make sure the ballots in the db are correct
        ballot = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballot), 1)
        self.assertEqual(
            ballot[0].voter, Voter.objects.get(student_number_hash=voter_dict["pid"])
        )
        self.assertEqual(ballot[0].candidate, None)
        self.assertEqual(ballot[0].rank, None)

    def test_successful_spoiled_ballot(self):
        voter_dict = self._urlencode_cookie_request()
        response = self.client.post(self.cookie_view, voter_dict, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election = self._create_officer(self.election_session)
        self.add_candidates(election)
        payload = {"electionId": election.id, "ranking": {}}
        response = self.client.post(self.ballot_submit_view, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ballot = Ballot.objects.filter(election=election)
        self.assertEqual(len(ballot), 1)
        self.assertEqual(
            ballot[0].voter, Voter.objects.get(student_number_hash=voter_dict["pid"])
        )
        self.assertEqual(ballot[0].candidate, None)
        self.assertEqual(ballot[0].rank, None)


class MessageViewTestCase(SetupMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.cookie_view = reverse("api:backend:bypass-cookie")
        self.message_view = reverse("api:backend:messages")

    def test_inactive_election_session_no_messages_returned(self):
        self._set_election_session_data(
            name="TestElectionSession",
            start_time_offset_days=-4,
            end_time_offset_days=-3,
        )
        past_election_session = self._create_election_session()

        past_message = Message(
            message="PastMessageElectiondf ;test ",
            active=True,
            election_session=past_election_session,
        )
        past_message.save()

        response = self.client.get(self.message_view)

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_active_election_session_returns_only_active_messages(self):
        self._set_election_session_data(
            name="TestElectionSession",
            start_time_offset_days=-4,
            end_time_offset_days=5,
        )
        live_election_session = self._create_election_session()

        active_1 = Message(
            message="Current session test message active 1 asdfgfa",
            active=True,
            election_session=live_election_session,
        )
        active_1.save()
        active_2 = Message(
            message="Current session active test message 2 asdgfa ",
            active=True,
            election_session=live_election_session,
        )
        active_2.save()
        inactive_1 = Message(
            message="Current session inactive message asdgfa ",
            active=False,
            election_session=live_election_session,
        )
        inactive_1.save()

        response = self.client.get(self.message_view)

        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertContains(response, active_1.message)
        self.assertContains(response, active_2.message)
        self.assertNotContains(response, inactive_1.message)

    def test_past_and_active_and_future_election_session_only_returns_active_messages(
        self,
    ):
        self._set_election_session_data(
            name="TestLiveElectionSession",
            start_time_offset_days=-1,
            end_time_offset_days=5,
        )
        live_election_session = self._create_election_session()

        live_message = Message(
            message="This is a message for the live election session",
            active=True,
            election_session=live_election_session,
        )
        live_message.save()

        self._set_election_session_data(
            name="TestPastElectionSession",
            start_time_offset_days=-5,
            end_time_offset_days=-3,
        )
        past_election_session = self._create_election_session()

        past_message = Message(
            message="This is a message for the past election session",
            active=True,
            election_session=past_election_session,
        )
        past_message.save()

        self._set_election_session_data(
            name="TestFutureElectionSession",
            start_time_offset_days=5,
            end_time_offset_days=8,
        )
        future_election_session = self._create_election_session()

        future_message = Message(
            message="This is a message for the future election session",
            active=True,
            election_session=future_election_session,
        )
        future_message.save()

        response = self.client.get(self.message_view)

        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(ElectionSession.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertContains(response, live_message.message)
        self.assertNotContains(response, past_message.message)
        self.assertNotContains(response, future_message.message)
