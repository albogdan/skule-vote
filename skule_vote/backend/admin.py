from django.conf import settings
from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin

from backend.forms import ElectionSessionAdminForm
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
        ("Name of Election Session.", {"fields": ("election_session_name",)}),
        (
            "Set the timeline of your Election Session.",
            {"fields": ("start_time", "end_time")},
        ),
        (
            "(Optional) Election, Candidate, and Eligibility CSV Uploads. ",
            {
                "fields": (
                    "upload_elections",
                    "upload_candidates",
                    "upload_eligibilities",
                ),
                "description": "Upload CSVs defining Elections, Candidates, and Eligibilities. "
                "If none are uploaded then only the ElectionSession will be created. "
                "Note that all three must be uploaded at the same time. Re-uploading will delete"
                " all previous Elections, Candidates, and Eligibilities for that ElectionSession "
                "and insert a new one with the new data.",
            },
        ),
    )

    search_fields = ["election_session_name"]

    form = ElectionSessionAdminForm

    change_list_template = "election-session/change_list.html"


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
        ("Name of Election.", {"fields": ("election_name",)}),
        (
            "Choose the Election Session this falls under.",
            {"fields": ("election_session",)},
        ),
        ("Define Election parameters.", {"fields": ("seats_available", "category")}),
    )

    search_fields = ["election_name"]


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "election",
        "get_election_session",
        "created_at",
        "updated_at",
    )
    list_filter = ("election", "election__election_session")

    fieldsets = (
        ("Name of Candidate or Referendum.", {"fields": ("name",)}),
        ("Choose an Election.", {"fields": ("election",)}),
        ("Enter Candidate or Referendum statement.", {"fields": ("statement",)}),
        (
            "(Optional) Display Candidate's disqualification ruling on the ballot. Ignore for Referenda.",
            {
                "fields": (
                    "disqualified_status",
                    "disqualified_link",
                    "disqualified_message",
                )
            },
        ),
        (
            "(Optional) Display Candidate's rule violation on the ballot. Ignore for Referenda.",
            {
                "fields": (
                    "rule_violation_link",
                    "rule_violation_message",
                )
            },
        ),
    )
    search_fields = ["name"]

    def get_election_session(self, obj):
        return obj.election.election_session

    get_election_session.short_description = "Election Session"
    get_election_session.admin_order_field = "election"

    def get_queryset(self, request):
        if settings.DEBUG:
            return Candidate.objects.all()
        else:
            return Candidate.objects.all().exclude(name="Reopen Nominations")

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return super().has_delete_permission(request, obj)
        elif obj is not None and obj.name == "Reopen Nominations":
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    pass


class BallotResource(resources.ModelResource):
    class Meta:
        model = Ballot

        fields = (
            "voter__student_number_hash",
            "candidate__name",
            "rank",
            "election__election_name",
            "election__election_session__election_session_name",
        )
        export_order = (
            "voter__student_number_hash",
            "candidate__name",
            "rank",
            "election__election_name",
            "election__election_session__election_session_name",
        )

    def get_export_headers(self):
        export_headers = [
            "student_number_hash",
            "candidate_name",
            "rank",
            "election_name",
            "election_session_name",
        ]
        return export_headers


@admin.register(Ballot)
class BallotAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = BallotResource


@admin.register(Eligibility)
class EligibilityAdmin(admin.ModelAdmin):
    list_display = (
        "election",
        "get_election_id",
        "get_election_session",
        "created_at",
        "updated_at",
    )
    list_filter = ("election__election_session",)

    def get_election_id(self, obj):
        return obj.election.id

    get_election_id.short_description = "Election ID"

    def get_election_session(self, obj):
        return obj.election.election_session

    get_election_session.short_description = "Election Session"
    get_election_session.admin_order_field = "election"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("election_session", "get_short_message", "active", "hideable")
    list_filter = ("election_session", "active")
    search_fields = ["message"]

    fieldsets = (
        (
            "Enter your message to be displayed on the webpage.",
            {"fields": ("message",)},
        ),
        (
            "Select which Election Session this message applies to.",
            {"fields": ("election_session",)},
        ),
        (
            "Define whether the message is active (visible) and whether it is hideable by the user.",
            {"fields": ("active", "hideable")},
        ),
    )

    def get_short_message(self, obj):
        return f"{obj.message[:64]}..."

    get_short_message.short_description = "Message"
