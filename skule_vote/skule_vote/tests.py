from datetime import datetime

from django.conf import settings

from backend.models import (
    DISCIPLINE_CHOICES,
    STUDY_YEAR_CHOICES,
    Election,
    ElectionSession,
    Eligibility,
)


class SetupElectionsMixin:
    def setUp(self):
        self.curr_session = ElectionSession(
            election_session_name="Summer 2021 Elections",
            start_time=datetime.now().replace(tzinfo=settings.TZ_INFO),
            end_time=datetime(year=2022, month=12, day=23).replace(
                tzinfo=settings.TZ_INFO
            ),
        )
        self.curr_session.save()

        self._create_referendum()
        self._create_class_reps()
        self._create_officer()
        self._create_parttime_chair()
        self._create_discipline_club_chair()

    def _create_class_reps(self):
        # Create class reps for all years, disciplines, and PEY
        for discipline_code, discipline_name in DISCIPLINE_CHOICES:
            if discipline_code == "ENG":
                election = Election(
                    election_name=f"{discipline_name} Class Rep",
                    election_session=self.curr_session,
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
                    election_session=self.curr_session,
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
                election_session=self.curr_session,
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

    def _create_parttime_chair(self):
        election = Election(
            election_name="Part-Time Chair",
            election_session=self.curr_session,
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

    def _create_discipline_club_chair(self):

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
                    election_session=self.curr_session,
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
                election_session=self.curr_session,
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

    def _create_referendum(self):
        election = Election(
            election_name="Random Club Levy",
            election_session=self.curr_session,
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

    def _create_officer(self):
        election = Election(
            election_name="President",
            election_session=self.curr_session,
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
