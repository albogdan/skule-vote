from rest_framework import serializers
from backend.models import Election, Candidate


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = (
            "id",
            "candidate_name",
            "blurb",
            "preamble",
            "disqualified_status",
            "disqualified_link",
            "disqualified_blurb",
            "rule_violation_message",
            "rule_violation_link",
        )


class ElectionSerializer(serializers.ModelSerializer):
    # This will query all candidates for a given election and nest their serialized representation in the
    # "candidates" field as a list
    candidates = CandidateSerializer(many=True, read_only=True)

    class Meta:
        model = Election
        fields = (
            "id",
            "election_name",
            "category",
            "seats_available",
            "candidates",
        )
