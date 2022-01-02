from django.test import TestCase

from backend.ballot import calculate_results
# from backend.ballot_new import results as calculate_results # Uncomment to test with the new file

from backend.models import (
    Ballot,
    Election,
    Candidate,
    Voter,
)
from backend.serializers import (
    BallotResultsCalculationSerializer as BallotSerializer,
    CandidateSerializer,
)

from skule_vote.tests import SetupMixin


class BallotTestCase(SetupMixin, TestCase):
    # RON = {"Name": "Reopen nominations", "statement": None}

    # Parameters:

    # "ballots" is every single ballot cast in that election (i.e. array of "ballot")
    # "ranking" is an array as well, in order (index corresponds to "choice" array)
    # ballot: {
    # sid: string (voterID, useless here)
    # ranking: number[] (index of choice in choices array)
    # }

    # "choices" is an array of "choice" (i.e. list of all candidates/options)
    # choice: {
    # name: string
    # statement: string (useless here)
    # }

    # numSeats: Number of seats available in election

    # "totalVotes" is the total votes cast (manually verify with quota after)
    # each object in "rounds" is 1 round and displays the voteCount for remaining candidates
    # Returns: {
    # winners: [] (array of names)
    # rounds: [{choice1: voteCount, ...}] (index in array = round number)
    # quota: Number
    # totalVotes: Number (total number of ballots cast)
    # spoiledBallots: Number (total number of spoiled ballots)
    # }
    # */
    def setUp(self):
        super().setUp()
        self._set_election_session_data()

        self.election_session = self._create_election_session()

    # YES/NO election (simplest case) i.e. a referendum or one person running
    def test_one_candidate_no_tie(self):
        self._create_referendum(self.election_session)
        referendum = Election.objects.filter(category="referenda")[0]

        # Add a Candidate
        candidate = Candidate(
            name="Lisa Li", statement="Insert statement here.", election=referendum
        )
        candidate.save()

        choices = Candidate.objects.filter(election=referendum)
        ron, candidate = choices[0], choices[1]

        NUM_VOTERS = 4
        NUM_SPOILED = 1
        self._generate_voters(count=NUM_VOTERS)
        voters = Voter.objects.all()
        ballots = [
            {  # First vote (2 candidates ranked)
                "voter": voters[0],
                "candidate": candidate,
                "rank": 0,
                "election": referendum,
            },
            {  # Second vote (1 candidate ranked)
                "voter": voters[1],
                "candidate": candidate,
                "rank": 0,
                "election": referendum,
            },
            {  # Third vote (1 candidate ranked)
                "voter": voters[2],
                "candidate": ron,
                "rank": 0,
                "election": referendum,
            },
            {  # Spoiled ballot
                "voter": voters[3],
                "candidate": None,
                "rank": None,
                "election": referendum,
            },
        ]

        # Create and serialize the ballots
        for ballot in ballots:
            Ballot.objects.create(**ballot)
        ballot_dict = BallotSerializer(Ballot.objects.all())

        # Ballot dict gives us Candidate objects, we need indicies from the choices list.
        ballots_formatted = ballot_dict.map_candidates_in_ballots_to_choices(
            ballots=ballot_dict.data, choices=choices
        )

        # The choice array is a queryset, we need a dictionary
        choices_dict = CandidateSerializer(choices, many=True).data
        for i in range(len(choices_dict)):
            choices_dict[i] = dict(choices_dict[i])

        # Calculate the results and assert
        results = calculate_results(
            ballots=ballots_formatted,
            choices=choices_dict,
            numSeats=referendum.seats_available,
        )
        self.assertEqual(results["winners"], ["Lisa Li"])
        self.assertEqual(results["rounds"][0]["Lisa Li"], 2)
        self.assertEqual(results["rounds"][0]["Reopen Nominations"], 1)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)

        # Total votes is len(voters) - NUM_SPOILED because
        # 1. We consider rankings of multiple candidates for the *same* position
        #   as a single vote (i.e., voters[0] ranking two candidates is 1 vote.
        # 2. We don't consider spoiled ballots as votes
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    def test_one_candidate_no_tie_ron_wins(self):
        self._create_referendum(self.election_session)
        referendum = Election.objects.filter(category="referenda")[0]

        # Add a Candidate
        candidate = Candidate(
            name="Lisa Li", statement="Insert statement here.", election=referendum
        )
        candidate.save()

        choices = Candidate.objects.filter(election=referendum)
        ron, candidate = choices[0], choices[1]

        NUM_VOTERS = 4
        NUM_SPOILED = 1
        self._generate_voters(count=NUM_VOTERS)
        voters = Voter.objects.all()
        ballots = [
            {  # First vote (2 candidates ranked)
                "voter": voters[0],
                "candidate": ron,
                "rank": 0,
                "election": referendum,
            },
            {  # Second vote (1 candidate ranked)
                "voter": voters[1],
                "candidate": candidate,
                "rank": 0,
                "election": referendum,
            },
            {  # Third vote (1 candidate ranked)
                "voter": voters[2],
                "candidate": ron,
                "rank": 0,
                "election": referendum,
            },
            {  # Spoiled ballot
                "voter": voters[3],
                "candidate": None,
                "rank": None,
                "election": referendum,
            },
        ]

        # Create and serialize the ballots
        for ballot in ballots:
            Ballot.objects.create(**ballot)
        ballot_dict = BallotSerializer(Ballot.objects.all())

        # Ballot dict gives us Candidate objects, we need indicies from the choices list.
        ballots_formatted = ballot_dict.map_candidates_in_ballots_to_choices(
            ballots=ballot_dict.data, choices=choices
        )

        # The choice array is a queryset, we need a dictionary
        choices_dict = CandidateSerializer(choices, many=True).data
        for i in range(len(choices_dict)):
            choices_dict[i] = dict(choices_dict[i])

        # Calculate the results and assert
        results = calculate_results(
            ballots=ballots_formatted,
            choices=choices_dict,
            numSeats=referendum.seats_available,
        )
        self.assertEqual(results["winners"], ["Reopen Nominations"])
        self.assertEqual(results["rounds"][0]["Lisa Li"], 1)
        self.assertEqual(results["rounds"][0]["Reopen Nominations"], 2)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)

        # Total votes is len(voters) - NUM_SPOILED because
        # 1. We consider rankings of multiple candidates for the *same* position
        #   as a single vote (i.e., voters[0] ranking two candidates is 1 vote.
        # 2. We don't consider spoiled ballots as votes
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)


    # YES/NO election with a tie
    def test_one_candidate_tie(self):
        self._create_referendum(self.election_session)
        referendum = Election.objects.filter(category="referenda")[0]

        # Add a Candidate
        candidate = Candidate(
            name="Lisa Li", statement="Insert statement here.", election=referendum
        )
        candidate.save()

        choices = Candidate.objects.filter(election=referendum)
        ron, candidate = choices[0], choices[1]

        NUM_VOTERS = 5
        NUM_SPOILED = 1
        self._generate_voters(count=NUM_VOTERS)
        voters = Voter.objects.all()
        ballots = [
            {  # First vote (1 candidate ranked)
                "voter": voters[0],
                "candidate": candidate,
                "rank": 0,
                "election": referendum,
            },
            {  # Second vote (1 candidate ranked)
                "voter": voters[1],
                "candidate": ron,
                "rank": 0,
                "election": referendum,
            },
            {  # Third vote (1 candidate ranked)
                "voter": voters[2],
                "candidate": ron,
                "rank": 0,
                "election": referendum,
            },
            {  # Fourth vote (1 candidate ranked)
                "voter": voters[3],
                "candidate": candidate,
                "rank": 0,
                "election": referendum,
            },
            {  # Spoiled ballot
                "voter": voters[4],
                "candidate": None,
                "rank": None,
                "election": referendum,
            },
        ]

        # Create and serialize the ballots
        for ballot in ballots:
            Ballot.objects.create(**ballot)
        ballot_dict = BallotSerializer(Ballot.objects.all())

        # Ballot dict gives us Candidate objects, we need indicies from the choices list.
        ballots_formatted = ballot_dict.map_candidates_in_ballots_to_choices(
            ballots=ballot_dict.data, choices=choices
        )

        # The choice array is a queryset, we need a dictionary
        choices_dict = CandidateSerializer(choices, many=True).data
        for i in range(len(choices_dict)):
            choices_dict[i] = dict(choices_dict[i])

        # Calculate the results and assert
        results = calculate_results(
            ballots=ballots_formatted,
            choices=choices_dict,
            numSeats=referendum.seats_available,
        )
        self.assertEqual(results["winners"], ["NO (TIE)"])
        self.assertEqual(results["rounds"][0]["Lisa Li"], 2)
        self.assertEqual(results["rounds"][0]["Reopen Nominations"], 2)
        self.assertEqual(results["quota"], 3)
        self.assertEqual(results["spoiledBallots"], 1)

        # Total votes is len(voters) - NUM_SPOILED because
        # 1. We consider rankings of multiple candidates for the *same* position
        #   as a single vote (i.e., voters[0] ranking two candidates is 1 vote.
        # 2. We don't consider spoiled ballots as votes
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # YES/NO election with some ballots being errors
    def test_one_candidate_ballot_errored(self):
        self._create_referendum(self.election_session)
        referendum = Election.objects.filter(category="referenda")[0]

        # Add a Candidate
        candidate = Candidate(
            name="Lisa Li", statement="Insert statement here.", election=referendum
        )
        candidate.save()

        choices = Candidate.objects.filter(election=referendum)
        ron, candidate = choices[0], choices[1]

        NUM_VOTERS = 4
        NUM_SPOILED = 1
        NUM_ERRORED = 1
        self._generate_voters(count=NUM_VOTERS)
        voters = Voter.objects.all()
        ballots = [
            {  # First vote (1 candidate ranked)
                "voter": voters[0],
                "candidate": candidate,
                "rank": 0,
                "election": referendum,
            },
            {  # Second vote (1 candidate ranked)
                "voter": voters[1],
                "candidate": ron,
                "rank": 0,
                "election": referendum,
            },
            {  # Third vote (1 candidate ranked)
                "voter": voters[2],
                "candidate": ron,
                "rank": 0,
                "election": referendum,
            },
            {  # Spoiled ballot
                "voter": voters[3],
                "candidate": None,
                "rank": None,
                "election": referendum,
            },
        ]

        # Create and serialize the ballots
        for ballot in ballots:
            Ballot.objects.create(**ballot)
        ballot_dict = BallotSerializer(Ballot.objects.all())

        # Ballot dict gives us Candidate objects, we need indicies from the choices list.
        ballots_formatted = ballot_dict.map_candidates_in_ballots_to_choices(
            ballots=ballot_dict.data, choices=choices
        )

        # The choice array is a queryset, we need a dictionary
        choices_dict = CandidateSerializer(choices, many=True).data
        for i in range(len(choices_dict)):
            choices_dict[i] = dict(choices_dict[i])

        # Change the ranking to be invalid
        ballots_formatted[0]["ranking"][0] = 2

        # Calculate the results and assert
        results = calculate_results(
            ballots=ballots_formatted,
            choices=choices_dict,
            numSeats=referendum.seats_available,
        )
        self.assertEqual(results["winners"], ["Reopen Nominations"])
        self.assertEqual(results["rounds"][0]["Lisa Li"], 1 - NUM_ERRORED)
        self.assertEqual(results["rounds"][0]["Reopen Nominations"], 2)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)

        # Total votes is len(voters) - NUM_SPOILED because
        # 1. We consider rankings of multiple candidates for the *same* position
        #   as a single vote (i.e., voters[0] ranking two candidates is 1 vote.
        # 2. We don't consider spoiled ballots as votes
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)
