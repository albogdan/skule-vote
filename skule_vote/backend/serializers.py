from django.db import transaction

from backend.models import Ballot, Candidate, Election, ElectionSession, Voter
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


class BallotSerializer(serializers.Serializer):
    electionId = serializers.CharField(max_length=200, allow_blank=False)
    # rank -> candidate_id
    ranking = serializers.DictField(allow_empty=True)

    def validate(self, data):
        """
        Ensure candidates belong to the election.
        """

        candidate_ids = [
            c.id for c in Candidate.objects.filter(election=data["electionId"])
        ]
        for _, candidate in data["ranking"].items():
            if candidate not in candidate_ids:
                raise serializers.ValidationError(
                    f"No candidate with id: {candidate} exists in election: {data['electionId']}"
                )

        return data

    def save(self):
        election = Election.objects.get(id=self.validated_data["electionId"])
        candidates_dict = {c.id: c for c in Candidate.objects.filter(election=election)}
        voter = Voter.objects.get(
            student_number_hash=self.context["student_number_hash"]
        )

        with transaction.atomic(durable=True):
            if self.validated_data["ranking"]:
                for rank in self.validated_data["ranking"]:
                    ballot = Ballot(
                        voter=voter,
                        candidate=candidates_dict[self.validated_data["ranking"][rank]],
                        election=election,
                        rank=int(rank),
                    )
                    ballot.save()
            else:
                # Spoiled ballot
                ballot = Ballot(
                    voter=voter,
                    election=election,
                )
                ballot.save()
