import csv
from datetime import datetime, timedelta
from io import BytesIO, StringIO

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model

from backend.forms import ElectionSessionAdminForm

User = get_user_model()


class SetupMixin:
    """
    Mixin for things that are reusable for multiple test classes.
    """

    def setUp(self):
        self.password = "foobar123"
        self.user = User.objects.create_user(
            username="foo@bar.com",
            password=self.password,
            first_name="Test",
            last_name="Bar",
            email="foo@bar.com",
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.header_definitions = {
            "elections": ["election_name", "seats_available", "category"],
            "candidates": ["name", "election_name", "statement"],
            "eligibilities": [
                "election_name",
                "eng_eligible",
                "che_eligible",
                "civ_eligible",
                "ele_eligible",
                "cpe_eligible",
                "esc_eligible",
                "ind_eligible",
                "lme_eligible",
                "mec_eligible",
                "mms_eligible",
                "year_1_eligible",
                "year_2_eligible",
                "year_3_eligible",
                "year_4_eligible",
                "pey_eligible",
                "status_eligible",
            ],
        }
        self.body_definitions = {
            "elections": [
                [
                    "1st Year Civil Engineering Representative",
                    "1",
                    "Class Representatives",
                ],
                ["4th Year Chair", "1", "Officer"],
            ],
            "candidates": [
                [
                    "Bobby Draper",
                    "1st Year Civil Engineering Representative",
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                ],
                [
                    "James Holden",
                    "4th Year Chair",
                    "Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
                ],
            ],
            "eligibilities": [
                [
                    "1st Year Civil Engineering Representative",
                    "0",
                    "0",
                    "1",
                    "0",
                    "0",
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
                    "Full and Part Time",
                ],
                [
                    "4th Year Chair",
                    "0",
                    "1",
                    "1",
                    "1",
                    "1",
                    "1",
                    "1",
                    "1",
                    "1",
                    "1",
                    "0",
                    "0",
                    "0",
                    "1",
                    "1",
                    "Full and Part Time",
                ],
            ],
        }

    def _login_admin(self):
        self.client.login(username=self.user.username, password=self.password)

    def _set_election_session_data(
        self, start_time_offset_days=-2, end_time_offset_days=5
    ):
        """
        Sets default bare-bones data for ElectionSession with start and end time offsets
        passed in as parameters.
        """

        self.data = {
            "election_session_name": "ElectionSession2021",
            "start_time": self._now() + timedelta(days=start_time_offset_days),
            "end_time": self._now() + timedelta(days=end_time_offset_days),
        }

    def _build_form(self, data=None, files=None):
        """
        Builds an ElectionSessionAdminForm with the given data and files.
        """

        if data is None:
            data = self.data

        return ElectionSessionAdminForm(data=data, files=files)

    def _build_csv_files(self, header=None, body=None):
        """
        Builds the CSV files for an ElectionSessionAdminForm.
        """

        if header is None:
            header = self.header_definitions
        if body is None:
            body = self.body_definitions

        file_dict = {}
        files_to_create = ["elections", "candidates", "eligibilities"]
        for model_file in files_to_create:
            writer_file = StringIO()
            writer = csv.writer(writer_file)
            writer.writerow(header[model_file])
            writer.writerows(body[model_file])
            csv_bytes_io = BytesIO(writer_file.getvalue().encode("utf-8"))

            file_dict[f"upload_{model_file}"] = InMemoryUploadedFile(
                file=csv_bytes_io,
                field_name=f"upload_{model_file}",
                name=f"{model_file}.csv",
                content_type="text/csv",
                size=len(csv_bytes_io.getvalue()),
                charset=None,
            )

        return file_dict

    @staticmethod
    def _now():
        return datetime.now().replace(microsecond=0).astimezone(settings.TZ_INFO)
