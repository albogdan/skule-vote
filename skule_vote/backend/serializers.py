from django.db import transaction

from backend.models import Ballot, Candidate, Election, ElectionSession, Message, Voter
from rest_framework import serializers

# General Ballot serializer used for views and recording ballots
class BallotSerializer(serializers.Serializer):
    electionId = serializers.IntegerField(min_value=0)
    # rank -> candidate_id
    ranking = serializers.DictField(child=serializers.IntegerField(), allow_empty=True)

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


# Specialized Ballot serializer used for converting to the format that
# the calculate_results function in ballot.py expects
class BallotResultsCalculationSerializer(serializers.BaseSerializer):
    # Note: queryset must be a list
    def to_representation(self, queryset):
        ballots_formatted = []
        ballots_intermediate = {}
        """
        ballots_intermediate = {
            "voter": {"rank_1": "candidate_1", "rank_2": "candidate_2"}
        }
        """

        # Get all the voters and create a ballot dict with voters as keys
        for ballot in queryset:
            if ballot.voter not in ballots_intermediate.keys():
                ballots_intermediate[ballot.voter] = {}
            ballots_intermediate[ballot.voter][ballot.rank] = ballot.candidate

        for voter in ballots_intermediate.keys():
            voter_ballots = {"voter_id": voter.student_number_hash, "ranking": []}
            for rank in sorted(
                ballots_intermediate[voter].keys()
            ):  # Want ranks in order
                if rank is not None:
                    voter_ballots["ranking"].append(ballots_intermediate[voter][rank])
            ballots_formatted.append(voter_ballots)
        return ballots_formatted

    @staticmethod
    def map_candidates_in_ballots_to_choices(ballots, choices):
        new_ballots = ballots.copy()
        for ballot in new_ballots:
            for i in range(len(ballot["ranking"])):
                ballot["ranking"][i] = list(choices).index(ballot["ranking"][i])
        return new_ballots


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


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("message",)
