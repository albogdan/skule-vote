import csv
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import random
import string

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model

from backend.forms import ElectionSessionAdminForm

from backend.models import (
    DISCIPLINE_CHOICES,
    STUDY_YEAR_CHOICES,
    Election,
    ElectionSession,
    Eligibility,
)

User = get_user_model()

DISCIPLINES_POST_DICT = {
    discipline_code: f"AE{discipline_code}BLAH"
    for discipline_code, discipline_name in DISCIPLINE_CHOICES
}


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
                    "Class Representative",
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

    def setUpElections(self, election_session):
        self._create_referendum(election_session)
        self._create_class_reps(election_session)
        self._create_officer(election_session)
        self._create_parttime_chair(election_session)
        self._create_discipline_club_chair(election_session)

    def _create_class_reps(self, election_session):
        # Create class reps for all years, disciplines, and PEY
        for discipline_code, discipline_name in DISCIPLINE_CHOICES:
            if discipline_code == "ENG":
                election = Election(
                    election_name=f"{discipline_name} Class Rep",
                    election_session=election_session,
                    seats_available=1,
                    category="class_representative",
                )
                election.save()

                kwargs = {
                    "year_1_eligible": True,
                    f"{discipline_code.lower()}_eligible": True,
                }
                elgibility = Eligibility(
                    election=election, status_eligible="full_and_part_time", **kwargs
                )
                elgibility.save()
                continue

            for year, year_name in STUDY_YEAR_CHOICES:
                election = Election(
                    election_name=f"{year_name} {discipline_name} Class Rep",
                    election_session=election_session,
                    seats_available=1,
                    category="class_representative",
                )
                election.save()

                kwargs = {
                    f"year_{year}_eligible": True,
                    f"{discipline_code.lower()}_eligible": True,
                }
                elgibility = Eligibility(
                    election=election, status_eligible="full_and_part_time", **kwargs
                )
                elgibility.save()

            election = Election(
                election_name=f"PEY {discipline_name} Class Rep",
                election_session=election_session,
                seats_available=1,
                category="class_representative",
            )
            election.save()

            kwargs = {
                f"pey_eligible": True,
                f"{discipline_code.lower()}_eligible": True,
            }
            elgibility = Eligibility(
                election=election, status_eligible="full_and_part_time", **kwargs
            )
            elgibility.save()

    def _create_parttime_chair(self, election_session):
        election = Election(
            election_name="Part-Time Chair",
            election_session=election_session,
            seats_available=1,
            category="other",
        )
        election.save()

        kwargs = {
            f"year_{year}_eligible": True for year, year_name in STUDY_YEAR_CHOICES
        } | {
            f"{discipline_code.lower()}_eligible": True
            for discipline_code, discipline_name in DISCIPLINE_CHOICES
        }
        elgibility = Eligibility(
            election=election, status_eligible="part_time", **kwargs
        )
        elgibility.save()

    def _create_discipline_club_chair(self, election_session):

        for discipline_code, discipline_name in DISCIPLINE_CHOICES:
            # The goal is to test multiple years of the same discipline being eligible, so no point in testing track one
            if discipline_code == "ENG":
                continue

            # Computer Engineering and Electrical Engineering share a club
            if discipline_code == "CPE":
                continue

            if discipline_code == "ELE":
                election = Election(
                    election_name="ECE Club Chair",
                    election_session=election_session,
                    seats_available=1,
                    category="discipline_club",
                )
                election.save()

                kwargs = {
                    f"year_{year}_eligible": True
                    for year, year_name in STUDY_YEAR_CHOICES
                } | {"ele_eligible": True, "cpe_eligible": True}

                elgibility = Eligibility(
                    election=election, status_eligible="full_and_part_time", **kwargs
                )
                elgibility.save()
                continue

            # Other disciplines
            election = Election(
                election_name=f"{discipline_name} Club Chair",
                election_session=election_session,
                seats_available=1,
                category="discipline_club",
            )
            election.save()

            kwargs = {
                f"year_{year}_eligible": True for year, year_name in STUDY_YEAR_CHOICES
            } | {f"{discipline_code.lower()}_eligible": True}

            elgibility = Eligibility(
                election=election, status_eligible="full_and_part_time", **kwargs
            )
            elgibility.save()

    def _create_referendum(self, election_session):
        election = Election(
            election_name="Random Club Levy",
            election_session=election_session,
            seats_available=1,
            category="referenda",
        )
        election.save()

        # Everyone eligible
        kwargs = {
            f"year_{year}_eligible": True for year, year_name in STUDY_YEAR_CHOICES
        } | {
            f"{discipline_code.lower()}_eligible": True
            for discipline_code, discipline_name in DISCIPLINE_CHOICES
        }
        elgibility = Eligibility(
            election=election, status_eligible="full_and_part_time", **kwargs
        )
        elgibility.save()

    def _create_officer(self, election_session):
        election = Election(
            election_name="President",
            election_session=election_session,
            seats_available=1,
            category="officer",
        )
        election.save()

        # Everyone eligible
        kwargs = {
            f"year_{year}_eligible": True for year, year_name in STUDY_YEAR_CHOICES
        } | {
            f"{discipline_code.lower()}_eligible": True
            for discipline_code, discipline_name in DISCIPLINE_CHOICES
        }
        elgibility = Eligibility(
            election=election, status_eligible="full_and_part_time", **kwargs
        )
        elgibility.save()

    def _login_admin(self):
        self.client.login(username=self.user.username, password=self.password)

    def _set_election_session_data(
        self,
        name="ElectionSession2021",
        start_time_offset_days=-2,
        end_time_offset_days=5,
    ):
        """
        Sets default bare-bones data for ElectionSession with start and end time offsets
        passed in as parameters.
        """

        self.data = {
            "election_session_name": name,
            "start_time": self._now() + timedelta(days=start_time_offset_days),
            "end_time": self._now() + timedelta(days=end_time_offset_days),
        }
        return self.data

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

    def _build_election_session_form(self, data=None, files=None):
        """
        Builds an ElectionSessionAdminForm with the given data and files.
        """

        if data is None:
            data = self.data

        return ElectionSessionAdminForm(data=data, files=files)

    def _build_admin_csv_files(self, header=None, body=None):
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
            file_name = f"{model_file} {''.join(random.choice(string.ascii_letters) for i in range(10))} (1).csv"

            file_dict[f"upload_{model_file}"] = InMemoryUploadedFile(
                file=csv_bytes_io,
                field_name=f"upload_{model_file}",
                name=file_name,
                content_type="text/csv",
                size=len(csv_bytes_io.getvalue()),
                charset=None,
            )

        return file_dict

    @staticmethod
    def _now():
        return datetime.now().replace(microsecond=0).astimezone(settings.TZ_INFO)

    @staticmethod
    def _urlencode_cookie_request(
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
