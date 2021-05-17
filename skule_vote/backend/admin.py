from django.contrib import admin

from backend.models import (
    ElectionSession,
    Election,
    Candidate,
    Voter,
    Ballot,
    Eligibility,
    Message,
)


@admin.register(ElectionSession)
class ElectionSessionAdmin(admin.ModelAdmin):
    pass


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    pass


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "candidate_name",
        "id",
        "election",
        "get_election_session",
        "created_at",
        "updated_at",
    )
    list_filter = ("election",)

    def get_election_session(self, obj):
        return obj.election.election_session

    get_election_session.short_description = "Election Session"
    get_election_session.admin_order_field = "election"


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    pass


@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    pass


@admin.register(Eligibility)
class EligibilityAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
