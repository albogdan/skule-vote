from django.test import TestCase

from backend.ballot import calculate_results

# from backend.ballot_new import calculate_results # Uncomment to test with the new file

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

    def _create_candidates(self, election, num_candidates=1):
        candidate1 = Candidate(
            name="Alex Bogdan", statement="Insert statement here.", election=election
        )
        candidate1.save()
        if num_candidates > 1:
            candidate2 = Candidate(
                name="Lisa Li", statement="Insert statement here.", election=election
            )
            candidate2.save()
        if num_candidates > 2:
            candidate3 = Candidate(
                name="Armin Ale", statement="Insert statement here.", election=election
            )
            candidate3.save()
        if num_candidates > 3:
            candidate4 = Candidate(
                name="Quin Sykora",
                statement="Insert statement here.",
                election=election,
            )
            candidate4.save()

        return Candidate.objects.filter(election=election)

    def _create_results(self, ballots, choices, election):
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

        # Return calculated results
        return calculate_results(
            ballots=ballots_formatted,
            choices=choices_dict,
            numSeats=election.seats_available,
        )

    def _create_ballots(self, raw_ballots, election, num_voters, num_spoiled=0):
        self._generate_voters(count=num_voters)
        voters = Voter.objects.all()
        ballots = []

        for i, ballot in enumerate(raw_ballots):
            for rank, choice in enumerate(ballot):
                ballots.append(
                    {
                        "voter": voters[i],
                        "candidate": choice,
                        "rank": rank,
                        "election": election,
                    }
                )

        for j in range(num_spoiled):
            ballots.append(
                {
                    "voter": voters[i + 1 + j],
                    "candidate": None,
                    "rank": None,
                    "election": election,
                }
            )

        return ballots, voters

    # CASE 1: YES/NO election with candidate winning
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

    # CASE 1: YES/NO election with ron winning
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

    # CASE 1: YES/NO election with a tie
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

    # CASE 1: YES/NO election with some ballots being errors
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

    # CASE 2: 1 seat election with winner determined in first round
    def test_one_seat_winner_one_round(self):
        self._create_officer(self.election_session)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_VOTERS = 12
        NUM_SPOILED = 0
        self._generate_voters(count=NUM_VOTERS)
        voters = Voter.objects.all()

        ron_only_ballots = []
        for v in voters[:4]:
            ron_only_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 0,
                    "election": officer,
                }
            )

        all_candidate_ballots = []
        for v in voters[4:8]:
            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate1,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate2,
                    "rank": 1,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 2,
                    "election": officer,
                }
            )

        one_candidate_ballots = []
        for v in voters[8:11]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate1,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        for v in voters[11:12]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate2,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        ballots = all_candidate_ballots + one_candidate_ballots + ron_only_ballots
        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 7)
        self.assertEqual(results["rounds"][0][candidate2.name], 1)
        self.assertEqual(results["rounds"][0][ron.name], 4)
        self.assertEqual(len(results["rounds"]), 1)
        self.assertEqual(results["quota"], 7)
        self.assertEqual(results["spoiledBallots"], NUM_SPOILED)
        self.assertEqual(results["totalVotes"], NUM_VOTERS - NUM_SPOILED)

    # CASE 2: 1 seat election with winner determined after two rounds
    def test_one_seat_winner_two_rounds(self):
        self._create_officer(self.election_session)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 3)
        ron, candidate1, candidate2, candidate3 = (
            choices[0],
            choices[1],
            choices[2],
            choices[3],
        )

        NUM_VOTERS = 12
        NUM_SPOILED = 0
        self._generate_voters(count=NUM_VOTERS)
        voters = Voter.objects.all()

        ron_only_ballots = []
        for v in voters[:1]:
            ron_only_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 0,
                    "election": officer,
                }
            )

        all_candidate_ballots = []
        for v in voters[1:2]:
            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate1,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate2,
                    "rank": 1,
                    "election": officer,
                }
            )
            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate3,
                    "rank": 2,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 3,
                    "election": officer,
                }
            )

        one_candidate_ballots = []
        for v in voters[2:3]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate1,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        for v in voters[3:9]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate2,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )
        for v in voters[9:12]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate3,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        ballots = all_candidate_ballots + one_candidate_ballots + ron_only_ballots
        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate2.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 2)
        self.assertEqual(results["rounds"][0][candidate2.name], 6)
        self.assertEqual(results["rounds"][0][candidate3.name], 3)
        self.assertEqual(results["rounds"][0][ron.name], 1)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 7)
        self.assertEqual(results["rounds"][1][candidate3.name], 3)
        self.assertEqual(results["rounds"][1][ron.name], 2)
        self.assertEqual(len(results["rounds"]), 2)
        self.assertEqual(results["quota"], 7)
        self.assertEqual(results["spoiledBallots"], NUM_SPOILED)
        self.assertEqual(results["totalVotes"], NUM_VOTERS - NUM_SPOILED)

    # CASE 2: 1 seat election with winner determined after two rounds with some spoiled ballots
    def test_one_seat_winner_two_rounds_spoiled_ballots(self):
        # This case tests a boundary condition. The winning candidate gets the exactly the same number of votes as
        # the correct quota, which should be calculated based on the number of non-spoiled ballots. If spoiled ballots
        # are included, the quota will be wrong and the election will incorrectly not have a winner.
        self._create_officer(self.election_session)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 3)
        ron, candidate1, candidate2, candidate3 = (
            choices[0],
            choices[1],
            choices[2],
            choices[3],
        )

        NUM_VOTERS = 14
        NUM_SPOILED = 2
        self._generate_voters(count=NUM_VOTERS)
        voters = Voter.objects.all()

        ron_only_ballots = []
        for v in voters[:1]:
            ron_only_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 0,
                    "election": officer,
                }
            )

        all_candidate_ballots = []
        for v in voters[1:2]:
            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate1,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate2,
                    "rank": 1,
                    "election": officer,
                }
            )
            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate3,
                    "rank": 2,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 3,
                    "election": officer,
                }
            )

        one_candidate_ballots = []
        for v in voters[2:3]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate1,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        for v in voters[3:9]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate2,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )
        for v in voters[9:12]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate3,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        spoiled_ballots = []
        for v in voters[12:14]:
            spoiled_ballots.append(
                {
                    "voter": v,
                    "candidate": None,
                    "rank": None,
                    "election": officer,
                }
            )

        ballots = (
            all_candidate_ballots
            + one_candidate_ballots
            + ron_only_ballots
            + spoiled_ballots
        )
        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate2.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 2)
        self.assertEqual(results["rounds"][0][candidate2.name], 6)
        self.assertEqual(results["rounds"][0][candidate3.name], 3)
        self.assertEqual(results["rounds"][0][ron.name], 1)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 7)
        self.assertEqual(results["rounds"][1][candidate3.name], 3)
        self.assertEqual(results["rounds"][1][ron.name], 2)
        self.assertEqual(len(results["rounds"]), 2)
        self.assertEqual(results["quota"], 7)
        self.assertEqual(results["spoiledBallots"], NUM_SPOILED)
        self.assertEqual(results["totalVotes"], NUM_VOTERS - NUM_SPOILED)

    # CASE 2: 1 seat election with no winners because nothing meets quota
    def test_one_seat_no_winner(self):
        self._create_officer(self.election_session)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 3)
        ron, candidate1, candidate2, candidate3 = (
            choices[0],
            choices[1],
            choices[2],
            choices[3],
        )

        NUM_VOTERS = 12
        NUM_SPOILED = 0
        self._generate_voters(count=NUM_VOTERS)
        voters = Voter.objects.all()

        ron_only_ballots = []
        for v in voters[:2]:
            ron_only_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 0,
                    "election": officer,
                }
            )

        all_candidate_ballots = []
        for v in voters[2:3]:
            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate1,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate2,
                    "rank": 1,
                    "election": officer,
                }
            )
            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate3,
                    "rank": 2,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 3,
                    "election": officer,
                }
            )

        one_candidate_ballots = []
        for v in voters[3:4]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate1,
                    "rank": 0,
                    "election": officer,
                }
            )

            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        for v in voters[4:8]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate2,
                    "rank": 0,
                    "election": officer,
                }
            )

        for v in voters[8:12]:
            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate3,
                    "rank": 0,
                    "election": officer,
                }
            )

        ballots = all_candidate_ballots + one_candidate_ballots + ron_only_ballots
        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [])
        self.assertEqual(results["rounds"][0][candidate1.name], 2)
        self.assertEqual(results["rounds"][0][candidate2.name], 4)
        self.assertEqual(results["rounds"][0][candidate3.name], 4)
        self.assertEqual(results["rounds"][0][ron.name], 2)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 5)
        self.assertEqual(results["rounds"][1][candidate3.name], 4)
        self.assertEqual(results["rounds"][1][ron.name], 3)
        self.assertEqual(results["rounds"][2][candidate1.name], 0)
        self.assertEqual(results["rounds"][2][candidate2.name], 5)
        self.assertEqual(results["rounds"][2][candidate3.name], 0)
        self.assertEqual(results["rounds"][2][ron.name], 3)
        self.assertEqual(len(results["rounds"]), 3)
        self.assertEqual(results["quota"], 7)
        self.assertEqual(results["spoiledBallots"], NUM_SPOILED)
        self.assertEqual(results["totalVotes"], NUM_VOTERS - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, no one wins
    def test_two_seats_three_candidates_0_winners(self):
        """No one meets the quota to win, thus there are no winners"""
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_VOTERS = 4
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1],
                [candidate2],
                [ron],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [])
        self.assertEqual(results["rounds"][0][candidate1.name], 1)
        self.assertEqual(results["rounds"][0][candidate2.name], 1)
        self.assertEqual(results["rounds"][0][ron.name], 1)
        self.assertEqual(len(results["rounds"]), 1)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, WEIRD BEHAVIOUR
    def test_two_seats_three_candidates_0_winners_BROKEN1(self):
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 4)
        ron, candidate1, candidate2, candidate3, candidate4 = (
            choices[0],
            choices[1],
            choices[2],
            choices[3],
            choices[4],
        )

        NUM_VOTERS = 9
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate2],
                [candidate1, candidate2],
                [candidate2, candidate1],
                [candidate2, candidate1],
                [candidate3],
                [candidate3],
                [candidate4, candidate1],
                [ron],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        print("\nresults 1", results, "\n")
        self.assertEqual(results["winners"], [candidate1.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 2)
        self.assertEqual(results["rounds"][0][candidate2.name], 2)
        self.assertEqual(results["rounds"][0][candidate3.name], 2)
        self.assertEqual(results["rounds"][0][candidate4.name], 1)
        self.assertEqual(results["rounds"][0][ron.name], 1)
        self.assertEqual(results["rounds"][1][candidate1.name], 3)
        self.assertEqual(results["rounds"][1][candidate2.name], 2)
        self.assertEqual(results["rounds"][1][candidate3.name], 2)
        self.assertEqual(results["rounds"][1][candidate4.name], 0)
        self.assertEqual(results["rounds"][1][ron.name], 1)
        self.assertEqual(results["rounds"][2][candidate1.name], 0)
        self.assertEqual(results["rounds"][2][candidate2.name], 2)
        self.assertEqual(results["rounds"][2][candidate3.name], 2)
        self.assertEqual(results["rounds"][2][candidate4.name], 0)
        self.assertEqual(results["rounds"][2][ron.name], 1)
        # TODO: why tf in round 4, Lisa is eliminated even tho she has the exact same votes every round as Armin
        self.assertEqual(len(results["rounds"]), 4)
        self.assertEqual(results["quota"], 3)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, WEIRD BEHAVIOUR
    def test_two_seats_three_candidates_0_winners_BROKEN2(self):
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 4)
        ron, candidate1, candidate2, candidate3, candidate4 = (
            choices[0],
            choices[1],
            choices[2],
            choices[3],
            choices[4],
        )

        NUM_VOTERS = 9
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate3],
                [candidate1, candidate3],
                [candidate2, candidate3],
                [candidate2, candidate3],
                [candidate3, candidate1],
                [candidate3, candidate1],
                [candidate4, candidate1],
                [ron],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        print("\nresults 2", results, "\n")
        self.assertEqual(results["winners"], [candidate1.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 2)
        self.assertEqual(results["rounds"][0][candidate2.name], 2)
        self.assertEqual(results["rounds"][0][candidate3.name], 2)
        self.assertEqual(results["rounds"][0][candidate4.name], 1)
        self.assertEqual(results["rounds"][0][ron.name], 1)
        self.assertEqual(results["rounds"][1][candidate1.name], 3)
        self.assertEqual(results["rounds"][1][candidate2.name], 2)
        self.assertEqual(results["rounds"][1][candidate3.name], 2)
        self.assertEqual(results["rounds"][1][candidate4.name], 0)
        self.assertEqual(results["rounds"][1][ron.name], 1)
        self.assertEqual(results["rounds"][2][candidate1.name], 0)
        self.assertEqual(results["rounds"][2][candidate2.name], 2)
        self.assertEqual(results["rounds"][2][candidate3.name], 2)
        self.assertEqual(results["rounds"][2][candidate4.name], 0)
        self.assertEqual(results["rounds"][2][ron.name], 1)
        # TODO: why tf in round 4, Lisa is eliminated even tho she has the exact same votes every round as Armin
        self.assertEqual(len(results["rounds"]), 3)
        self.assertEqual(results["quota"], 3)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, 1 candidate wins
    def test_two_seats_three_candidates_one_winner(self):
        """The second place person does not meet the quota to win, thus there is only one winner"""
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_VOTERS = 5
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate2, ron],
                [ron],
                [candidate1],
                [candidate1, ron],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 3)
        self.assertEqual(results["rounds"][0][candidate2.name], 0)
        self.assertEqual(results["rounds"][0][ron.name], 1)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 1 / 3)
        self.assertEqual(results["rounds"][1][ron.name], 4 / 3)
        self.assertEqual(len(results["rounds"]), 2)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, ron wins first
    def test_two_seats_three_candidates_one_winner_ron(self):
        """RON wins first round, thus no further rounds are calculated"""
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_VOTERS = 5
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [ron, candidate1, candidate2],
                [ron, candidate1],
                [ron, candidate1],
                [ron, candidate1],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [ron.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 0)
        self.assertEqual(results["rounds"][0][candidate2.name], 0)
        self.assertEqual(results["rounds"][0][ron.name], 4)
        self.assertEqual(len(results["rounds"]), 1)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, a ballot has an errors
    def test_two_seats_three_candidates_ballot_errored(self):
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_ERRORED = 1
        NUM_VOTERS = 5
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate2, ron],
                [candidate1, ron],
                [candidate1, ron],
                [candidate1, ron],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

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
        ballots_formatted[0]["ranking"][0] = 5

        # Calculate the results and assert
        results = calculate_results(
            ballots=ballots_formatted,
            choices=choices_dict,
            numSeats=officer.seats_available,
        )
        self.assertEqual(results["winners"], [candidate1.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 4 - NUM_ERRORED)
        self.assertEqual(results["rounds"][0][candidate2.name], 0)
        self.assertEqual(results["rounds"][0][ron.name], 0)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 0)
        self.assertEqual(results["rounds"][1][ron.name], 1)
        self.assertEqual(len(results["rounds"]), 2)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, 2 candidates win
    def test_two_seats_three_candidates_two_winners(self):
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_VOTERS = 5
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate2, ron],
                [candidate1, candidate2],
                [candidate1, candidate2],
                [candidate1, candidate2],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name, candidate2.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 4)
        self.assertEqual(results["rounds"][0][candidate2.name], 0)
        self.assertEqual(results["rounds"][0][ron.name], 0)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 2)
        self.assertEqual(results["rounds"][1][ron.name], 0)
        self.assertEqual(len(results["rounds"]), 2)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, 1 candidate and ron win
    def test_two_seats_three_candidates_two_winners_ron(self):
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_VOTERS = 5
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, ron, candidate2],
                [candidate1, ron],
                [candidate1, ron],
                [candidate1, ron],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name, ron.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 4)
        self.assertEqual(results["rounds"][0][candidate2.name], 0)
        self.assertEqual(results["rounds"][0][ron.name], 0)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 0)
        self.assertEqual(results["rounds"][1][ron.name], 2)
        self.assertEqual(len(results["rounds"]), 2)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, 2 candidates win by a tie
    def test_two_seats_three_candidates_two_winners_tie(self):
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_VOTERS = 5
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate2, ron],
                [candidate1, candidate2],
                [candidate2, candidate1],
                [candidate2, candidate1],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name, candidate2.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 2)
        self.assertEqual(results["rounds"][0][candidate2.name], 2)
        self.assertEqual(results["rounds"][0][ron.name], 0)
        self.assertEqual(len(results["rounds"]), 1)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, 1 candidate and ron win by a tie
    def test_two_seats_three_candidates_two_winners_tie_ron(self):
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_VOTERS = 5
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, ron, candidate2],
                [candidate1, ron],
                [ron, candidate1],
                [ron, candidate1],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [ron.name, candidate1.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 2)
        self.assertEqual(results["rounds"][0][candidate2.name], 0)
        self.assertEqual(results["rounds"][0][ron.name], 2)
        self.assertEqual(len(results["rounds"]), 1)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 4 candidates and 3 seats, 2 candidates win
    def test_three_seats_four_candidates_two_winners(self):
        """No one passed the quota to win third place"""
        self._create_officer(self.election_session, 3)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 3)
        ron, candidate1, candidate2, candidate3 = (
            choices[0],
            choices[1],
            choices[2],
            choices[3],
        )

        NUM_VOTERS = 6
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate3],
                [candidate1, candidate2, candidate3],
                [candidate1, candidate2, candidate3],
                [candidate1, candidate2, candidate3],
                [candidate2, candidate3],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name, candidate2.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 4)
        self.assertEqual(results["rounds"][0][candidate2.name], 1)
        self.assertEqual(results["rounds"][0][candidate3.name], 0)
        self.assertEqual(results["rounds"][0][ron.name], 0)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 2.5)
        self.assertEqual(results["rounds"][1][candidate3.name], 0.5)
        self.assertEqual(results["rounds"][1][ron.name], 0)
        self.assertEqual(results["rounds"][2][candidate1.name], 0)
        self.assertEqual(results["rounds"][2][candidate2.name], 0)
        self.assertEqual(results["rounds"][2][candidate3.name], 1)
        self.assertEqual(results["rounds"][2][ron.name], 0)
        self.assertEqual(len(results["rounds"]), 3)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 4 candidates and 3 seats, 1 candidate and ron win
    def test_three_seats_four_candidates_two_winners_ron(self):
        """Ron wins second round, therefore third round does not occue"""
        self._create_officer(self.election_session, 3)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 3)
        ron, candidate1, candidate2, candidate3 = (
            choices[0],
            choices[1],
            choices[2],
            choices[3],
        )

        NUM_VOTERS = 6
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate2, candidate3],
                [candidate1, ron, candidate3],
                [candidate1, ron, candidate3],
                [candidate1, ron, candidate3],
                [ron, candidate3],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name, ron.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 4)
        self.assertEqual(results["rounds"][0][candidate2.name], 0)
        self.assertEqual(results["rounds"][0][candidate3.name], 0)
        self.assertEqual(results["rounds"][0][ron.name], 1)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 0.5)
        self.assertEqual(results["rounds"][1][candidate3.name], 0)
        self.assertEqual(results["rounds"][1][ron.name], 2.5)
        self.assertEqual(len(results["rounds"]), 2)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)
