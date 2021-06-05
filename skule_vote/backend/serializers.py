from backend.models import Candidate, Election, ElectionSession
from rest_framework import serializers


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = (
            "id",
            "name",
            "statement",
            "disqualified_status",
            "disqualified_link",
            "disqualified_message",
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


class ElectionSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectionSession
        fields = (
            "election_session_name",
            "start_time",
            "end_time",
        )
