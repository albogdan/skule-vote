from backend.models import Ballot, Candidate, Election, ElectionSession
from rest_framework import serializers


class BallotSerializer(serializers.BaseSerializer):
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
