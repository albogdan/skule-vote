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
    pass


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
