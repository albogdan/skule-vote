from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from backend.models import ElectionSession, Election, Candidate, Eligibility
from skule_vote.tests import SetupMixin


class ElectionSessionAdminTestCase(SetupMixin, TestCase):
    """
    Tests the changelist view for ElectionSessions, which shows the standard fields for
    ElectionSessions and a few custom fields.
    """

    def setUp(self):
        super().setUp()
        self._set_election_session_data()
        self._login_admin()

    def _create_election_session(self, data=None):
        """
        Creates and saves an ElectionSession. By default it is one that has already
        started, and contains no Elections, Candidates, or Eligibilities.
        """
        if data is None:
            data = self.data

        election_session = ElectionSession.objects.create(**data)
        election_session.save()

        return election_session

    def test_election_session_name_start_and_end_time_can_be_changed_before_session_start(
        self,
    ):
        # Get an ElectionSession that has not started
        self._set_election_session_data(start_time_offset_days=1)
        election_session = self._create_election_session()

        list_view = reverse(
            "admin:backend_electionsession_change",
            kwargs={"object_id": election_session.id},
        )

        new_start = self._now() + timedelta(days=5)
        new_end = self._now() + timedelta(days=10)
        new_data = {
            "election_session_name": "ElectionSession2021Part2",
            "start_time_0": new_start.date(),
            "start_time_1": new_start.time(),
            "end_time_0": new_end.date(),
            "end_time_1": new_end.time(),
        }

        response = self.client.post(list_view, data=new_data)

        self.assertRedirects(
            response, reverse("admin:backend_electionsession_changelist")
        )

        election_session.refresh_from_db()
        self.assertEqual(
            election_session.election_session_name, new_data["election_session_name"]
        )
        self.assertEqual(election_session.start_time, new_start)
        self.assertEqual(election_session.end_time, new_end)

    def test_end_time_can_be_changed_after_session_start(
        self,
    ):
        # Get an ElectionSession that has started
        election_session = self._create_election_session()

        list_view = reverse(
            "admin:backend_electionsession_change",
            kwargs={"object_id": election_session.id},
        )

        new_end = self._now() + timedelta(days=10)
        new_data = {
            "election_session_name": self.data["election_session_name"],
            "start_time_0": self.data["start_time"].date(),
            "start_time_1": self.data["start_time"].time(),
            "end_time_0": new_end.date(),
            "end_time_1": new_end.time(),
        }

        response = self.client.post(list_view, data=new_data)

        self.assertRedirects(
            response, reverse("admin:backend_electionsession_changelist")
        )

        election_session.refresh_from_db()

        self.assertEqual(
            election_session.election_session_name, self.data["election_session_name"]
        )
        self.assertEqual(
            election_session.start_time.astimezone(settings.TZ_INFO),
            self.data["start_time"],
        )
        self.assertEqual(
            election_session.end_time.astimezone(settings.TZ_INFO), new_end
        )

    def test_start_time_and_name_cannot_be_changed_after_session_start(
        self,
    ):
        # Get an ElectionSession that has started
        election_session = self._create_election_session()

        list_view = reverse(
            "admin:backend_electionsession_change",
            kwargs={"object_id": election_session.id},
        )

        # Try changing the start_time
        new_start = self._now() + timedelta(days=1)
        new_data = {
            "election_session_name": self.data["election_session_name"],
            "start_time_0": new_start.date(),
            "start_time_1": new_start.time(),
            "end_time_0": self.data["end_time"].date(),
            "end_time_1": self.data["end_time"].time(),
        }

        response = self.client.post(list_view, data=new_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try changing the ElectionSessionName
        new_data = {
            "election_session_name": "NewElectionSessionName2021",
            "start_time_0": self.data["start_time"].date(),
            "start_time_1": self.data["start_time"].time(),
            "end_time_0": self.data["end_time"].date(),
            "end_time_1": self.data["end_time"].time(),
        }

        response = self.client.post(list_view, data=new_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election_session.refresh_from_db()

        self.assertEqual(
            election_session.election_session_name, self.data["election_session_name"]
        )
        self.assertEqual(
            election_session.start_time.astimezone(settings.TZ_INFO),
            self.data["start_time"],
        )
        self.assertEqual(
            election_session.end_time.astimezone(settings.TZ_INFO),
            self.data["end_time"],
        )

    def test_csv_uploads_can_be_changed_before_session_start(
        self,
    ):
        # Get an ElectionSession that has not started
        self._set_election_session_data(start_time_offset_days=1)
        election_session = self._create_election_session()

        list_view = reverse(
            "admin:backend_electionsession_change",
            kwargs={"object_id": election_session.id},
        )

        files = self._build_csv_files()

        new_data = {
            "election_session_name": self.data["election_session_name"],
            "start_time_0": self.data["start_time"].date(),
            "start_time_1": self.data["start_time"].time(),
            "end_time_0": self.data["end_time"].date(),
            "end_time_1": self.data["end_time"].time(),
            "upload_elections": files["upload_elections"],
            "upload_candidates": files["upload_candidates"],
            "upload_eligibilities": files["upload_eligibilities"],
        }

        response = self.client.post(list_view, data=new_data)

        self.assertRedirects(
            response, reverse("admin:backend_electionsession_changelist")
        )

        election_session.refresh_from_db()
        self.assertEqual(
            election_session.election_session_name, new_data["election_session_name"]
        )
        self.assertEqual(ElectionSession.objects.count(), 1)
        self.assertEqual(
            Election.objects.count(), len(self.body_definitions["elections"])
        )
        self.assertEqual(
            Candidate.objects.count(), len(self.body_definitions["candidates"])
        )
        self.assertEqual(
            Eligibility.objects.count(), len(self.body_definitions["eligibilities"])
        )

    def test_csv_uploads_cannot_be_changed_after_session_start(
        self,
    ):
        # Get an ElectionSession that has started
        self._set_election_session_data(start_time_offset_days=-1)
        election_session = self._create_election_session()

        list_view = reverse(
            "admin:backend_electionsession_change",
            kwargs={"object_id": election_session.id},
        )

        files = self._build_csv_files()

        new_data = {
            "election_session_name": self.data["election_session_name"],
            "start_time_0": self.data["start_time"].date(),
            "start_time_1": self.data["start_time"].time(),
            "end_time_0": self.data["end_time"].date(),
            "end_time_1": self.data["end_time"].time(),
            "upload_elections": files["upload_elections"],
            "upload_candidates": files["upload_candidates"],
            "upload_eligibilities": files["upload_eligibilities"],
        }

        response = self.client.post(list_view, data=new_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        election_session.refresh_from_db()

        self.assertEqual(ElectionSession.objects.count(), 1)
        self.assertEqual(Election.objects.count(), 0)
        self.assertEqual(Candidate.objects.count(), 0)
        self.assertEqual(Eligibility.objects.count(), 0)

    def test_uploading_new_csvs_removes_the_old_objects(self):
        # Create an ElectionSession that has not started
        self._set_election_session_data(start_time_offset_days=1)
        form = self._build_form(files=self._build_csv_files())
        self.assertTrue(form.is_valid())
        election_session = form.save()

        list_view = reverse(
            "admin:backend_electionsession_change",
            kwargs={"object_id": election_session.id},
        )

        modified_body_definitions = {
            "elections": [
                [
                    "2nd Year EngSci Officer",
                    "2",
                    "Officer",
                ],
            ],
            "candidates": [
                [
                    "Bobby Draper",
                    "2nd Year EngSci Officer",
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                ],
            ],
            "eligibilities": [
                [
                    "2nd Year EngSci Officer",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "1",
                    "0",
                    "0",
                    "0",
                    "0",
                    "0",
                    "1",
                    "0",
                    "0",
                    "0",
                    "Full and Part Time",
                ],
            ],
        }
        modified_csv_files = self._build_csv_files(body=modified_body_definitions)

        new_data = {
            "election_session_name": self.data["election_session_name"],
            "start_time_0": self.data["start_time"].date(),
            "start_time_1": self.data["start_time"].time(),
            "end_time_0": self.data["end_time"].date(),
            "end_time_1": self.data["end_time"].time(),
            "upload_elections": modified_csv_files["upload_elections"],
            "upload_candidates": modified_csv_files["upload_candidates"],
            "upload_eligibilities": modified_csv_files["upload_eligibilities"],
        }

        response = self.client.post(list_view, data=new_data)
        self.assertRedirects(
            response, reverse("admin:backend_electionsession_changelist")
        )

        election_session.refresh_from_db()

        self.assertEqual(ElectionSession.objects.count(), 1)
        self.assertEqual(ElectionSession.objects.all()[0], election_session)
        self.assertEqual(Election.objects.count(), 1)
        self.assertEqual(Candidate.objects.count(), 1)
        self.assertEqual(Eligibility.objects.count(), 1)
