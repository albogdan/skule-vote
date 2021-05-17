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
    list_display = (
        "election_session_name",
        "id",
        "start_time",
        "end_time",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Name your Election Session.", {"fields": ("election_session_name",)}),
        (
            "Define when the Election is happening.",
            {"fields": ("start_time", "end_time")},
        ),
    )

    search_fields = ["election_session_name"]


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        "election_name",
        "id",
        "election_session",
        "category",
        "created_at",
        "updated_at",
    )
    list_filter = ("election_session", "category")

    fieldsets = (
        ("Name your Election.", {"fields": ("election_name",)}),
        ("Choose an Election Session.", {"fields": ("election_session",)}),
        ("Define Election parameters.", {"fields": ("seats_available", "category")}),
    )

    search_fields = ["election_name"]


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
    list_filter = ("election", "election__election_session")

    fieldsets = (
        ("Name your Candidate.", {"fields": ("candidate_name",)}),
        ("Choose an Election.", {"fields": ("election",)}),
        ("Enter Candidate's writing.", {"fields": ("blurb", "preamble")}),
        (
            "(Optional) Enter information about the Candidate being disqualified.",
            {
                "fields": (
                    "disqualified_status",
                    "disqualified_link",
                    "disqualified_blurb",
                )
            },
        ),
        (
            "(Optional) Enter information about the Candidate violating a rule.",
            {"fields": ("rule_violation_message", "rule_violation_link")},
        ),
    )
    search_fields = ["candidate_name"]

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
    list_display = (
        "election",
        "get_election_session",
        "created_at",
        "updated_at",
    )
    list_filter = ("election__election_session",)

    def get_election_session(self, obj):
        return obj.election.election_session

    get_election_session.short_description = "Election Session"
    get_election_session.admin_order_field = "election"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("election_session", "get_short_message", "active", "hideable")
    list_filter = ("election_session", "active")
    search_fields = ["message"]

    def get_short_message(self, obj):
        return f"{obj.message[:64]}..."

    get_short_message.short_description = "Message"
