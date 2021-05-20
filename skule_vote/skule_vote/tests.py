from datetime import datetime

from django.conf import settings

from backend.models import (
    ElectionSession,
    Election,
    Eligibility,
    DISCIPLINE_CHOICES,
    STUDY_YEAR_CHOICES,
)


class SetupElectionsMixin:
    def setUp(self):
        curr_session = ElectionSession(
            election_session_name="Summer 2021 Elections",
            start_time=datetime.now().replace(tzinfo=settings.TZ_INFO),
            end_time=datetime(year=2022, month=12, day=23),
        )
        curr_session.save()

        for discipline_tuple in DISCIPLINE_CHOICES:
            if discipline_tuple[0] == "ENG":
                election = Election(
                    election_name=f"{discipline_tuple[1]} Class Rep",
                    election_session=curr_session,
                    seats_available=1,
                    category="class_representative",
                )
                election.save()

                kwargs = {
                    "year_1_eligible": True,
                    f"{discipline_tuple[0].lower()}_eligible": True,
                }
                elgibility = Eligibility(
                    election=election, status_eligible="full_and_part_time", **kwargs
                )
                elgibility.save()
                continue

            for year_tuple in STUDY_YEAR_CHOICES:
                election = Election(
                    election_name=f"{year_tuple[1]} {discipline_tuple[1]} Class Rep",
                    election_session=curr_session,
                    seats_available=1,
                    category="class_representative",
                )
                election.save()

                kwargs = {
                    f"year_{year_tuple[0]}_eligible": True,
                    f"{discipline_tuple[0].lower()}_eligible": True,
                }
                elgibility = Eligibility(
                    election=election, status_eligible="full_and_part_time", ** kwargs
                )
                elgibility.save()

            election = Election(
                election_name=f"PEY {discipline_tuple[1]} Class Rep",
                election_session=curr_session,
                seats_available=1,
                category="class_representative",
            )
            election.save()

            kwargs = {
                f"pey_eligible": True,
                f"{discipline_tuple[0].lower()}_eligible": True,
            }
            elgibility = Eligibility(
                election=election, status_eligible="full_and_part_time", **kwargs
            )
            elgibility.save()
