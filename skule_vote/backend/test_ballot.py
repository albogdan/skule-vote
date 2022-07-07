from django.test import TestCase

from backend.ballot import calculate_results

from backend.admin import generate_results
from backend.models import (
    Ballot,
    Candidate,
    Election,
    ElectionSession,
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
    #   sid: string (voterID, useless here)
    #   ranking: number[] (index of choice in choices array)
    # }

    # "choices" is an array of "choice" (i.e. list of all candidates/options)
    # choice: {
    #   name: string
    #   statement: string (useless here)
    # }

    # numSeats: Number of seats available in election

    # "totalVotes" is the total votes cast (manually verify with quota after)
    # each object in "rounds" is 1 round and displays the voteCount for remaining candidates
    # Returns: {
    #   winners: [] (array of names)
    #   rounds: [{choice1: voteCount, ...}] (index in array = round number)
    #   quota: Number
    #   totalVotes: Number (total number of ballots cast)
    #   spoiledBallots: Number (total number of spoiled ballots)
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

        candidates = Candidate.objects.filter(election=election).exclude(
            name="Reopen Nominations"
        )
        ron = Candidate.objects.get(election=election, name="Reopen Nominations")
        return [ron] + list(candidates)

    def _create_results(self, ballots, choices, election, error=False):
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

        if error:
            # Change the ranking to be invalid
            ballots_formatted[0]["ranking"][0] = len(choices) + 1

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

        choices = self._create_candidates(referendum)
        ron, candidate = choices[0], choices[1]

        NUM_VOTERS = 4
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate],
                [candidate],
                [ron],
            ],
            referendum,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, referendum)
        self.assertEqual(results["winners"], [candidate.name])
        self.assertEqual(results["rounds"][0][candidate.name], 2)
        self.assertEqual(results["rounds"][0][ron.name], 1)
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

        choices = self._create_candidates(referendum)
        ron, candidate = choices[0], choices[1]

        NUM_VOTERS = 4
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [ron],
                [candidate],
                [ron],
            ],
            referendum,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, referendum)
        self.assertEqual(results["winners"], [ron.name])
        self.assertEqual(results["rounds"][0][candidate.name], 1)
        self.assertEqual(results["rounds"][0][ron.name], 2)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 1: YES/NO election with a tie
    def test_one_candidate_tie(self):
        self._create_referendum(self.election_session)
        referendum = Election.objects.filter(category="referenda")[0]

        choices = self._create_candidates(referendum)
        ron, candidate = choices[0], choices[1]

        NUM_VOTERS = 5
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate],
                [ron],
                [ron],
                [candidate],
            ],
            referendum,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, referendum)
        self.assertEqual(results["winners"], ["NO (TIE)"])
        self.assertEqual(results["rounds"][0][candidate.name], 2)
        self.assertEqual(results["rounds"][0][ron.name], 2)
        self.assertEqual(results["quota"], 3)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 1: YES/NO election with one ballot having an error
    def test_one_candidate_ballot_errored(self):
        self._create_referendum(self.election_session)
        referendum = Election.objects.filter(category="referenda")[0]

        choices = self._create_candidates(referendum)
        ron, candidate = choices[0], choices[1]

        NUM_VOTERS = 4
        NUM_SPOILED = 1
        NUM_ERRORED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate],
                [ron],
                [ron],
            ],
            referendum,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, referendum, error=True)
        self.assertEqual(results["winners"], [ron.name])
        self.assertEqual(results["rounds"][0][candidate.name], 1 - NUM_ERRORED)
        self.assertEqual(results["rounds"][0][ron.name], 2)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 1)
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

            one_candidate_ballots.append(
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

            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        ballots = ron_only_ballots + all_candidate_ballots + one_candidate_ballots
        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 7)
        self.assertEqual(results["rounds"][0][candidate2.name], 1)
        self.assertEqual(results["rounds"][0][ron.name], 4)
        self.assertEqual(len(results["rounds"]), 1)
        self.assertEqual(results["quota"], 7)
        self.assertEqual(results["spoiledBallots"], NUM_SPOILED)
        self.assertEqual(results["totalVotes"], NUM_VOTERS - NUM_SPOILED)

    # CASE 2: 1 seat election with winner determined in first round + one ballot that has an error
    def test_one_seat_winner_one_round_errored(self):
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
        NUM_ERRORED = 1
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

            one_candidate_ballots.append(
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

            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        ballots = ron_only_ballots + all_candidate_ballots + one_candidate_ballots

        for ballot in ballots:
            Ballot.objects.create(**ballot)
        ballot_dict = BallotSerializer(Ballot.objects.all())

        # Ballot dict gives us Candidate objects, we need indicies from the choices list.
        ballots_formatted = ballot_dict.map_candidates_in_ballots_to_choices(
            ballots=ballot_dict.data, choices=choices
        )

        # Change the ranking to be invalid
        ballots_formatted[11]["ranking"][0] = 5

        # The choice array is a queryset, we need a dictionary
        choices_dict = CandidateSerializer(choices, many=True).data
        for i in range(len(choices_dict)):
            choices_dict[i] = dict(choices_dict[i])

        results = calculate_results(
            ballots=ballots_formatted,
            choices=choices_dict,
            numSeats=officer.seats_available,
        )

        self.assertEqual(results["winners"], [candidate1.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 7)
        self.assertEqual(results["rounds"][0][candidate2.name], 1 - NUM_ERRORED)
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
        """
        This case tests a boundary condition. The winning candidate gets the exactly the same number of votes as
        the correct quota, which should be calculated based on the number of non-spoiled ballots. If spoiled ballots
        are included, the quota will be wrong and the election will incorrectly not have a winner.
        """
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

    # CASE 2: 1 seat election with winner determined in first round w/ disqualification
    def test_one_seat_two_candidates_winner_with_and_without_dq(self):
        self._create_officer(self.election_session)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )
        # DQ candidate 1
        candidate1.disqualified_status = True
        candidate1.save()

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

            one_candidate_ballots.append(
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

            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        ballots = ron_only_ballots + all_candidate_ballots + one_candidate_ballots
        for ballot in ballots:
            b = Ballot.objects.create(**ballot)
            b.save()

        results = generate_results(
            ElectionSession.objects.filter(
                election_session_name=self.election_session.election_session_name
            )
        )
        election_results = results[
            f"{self.election_session.election_session_name} ElectionSession"
        ][officer.election_name]
        # Assert results without DQ - candidate 1 wins
        self.assertEqual(
            election_results["results_without_dq"]["winners"], [candidate1.name]
        )
        self.assertEqual(
            election_results["results_without_dq"]["rounds"][0][candidate1.name], 7
        )
        self.assertEqual(
            election_results["results_without_dq"]["rounds"][0][candidate2.name], 1
        )
        self.assertEqual(
            election_results["results_without_dq"]["rounds"][0][ron.name], 4
        )
        self.assertEqual(len(election_results["results_without_dq"]["rounds"]), 1)
        self.assertEqual(election_results["results_without_dq"]["quota"], 7)
        self.assertEqual(
            election_results["results_without_dq"]["spoiledBallots"], NUM_SPOILED
        )
        self.assertEqual(
            election_results["results_without_dq"]["totalVotes"],
            NUM_VOTERS - NUM_SPOILED,
        )

        # Assert results with DQ - RON wins
        self.assertEqual(election_results["results_with_dq"]["winners"], [ron.name])
        self.assertEqual(election_results["results_with_dq"]["rounds"][0][ron.name], 7)
        self.assertEqual(
            election_results["results_with_dq"]["rounds"][0][candidate2.name], 5
        )
        self.assertEqual(len(election_results["results_with_dq"]["rounds"]), 1)
        self.assertEqual(election_results["results_with_dq"]["quota"], 7)
        self.assertEqual(
            election_results["results_with_dq"]["spoiledBallots"], NUM_SPOILED
        )
        self.assertEqual(
            election_results["results_with_dq"]["totalVotes"], NUM_VOTERS - NUM_SPOILED
        )

    # CASE 2: 1 seat election with winner determined in first round  w/ disqualification
    def test_one_seat_three_candidates_winner_with_and_without_dq(self):
        self._create_officer(self.election_session)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 3)
        ron, candidate1, candidate2, candidate3 = (
            choices[0],
            choices[1],
            choices[2],
            choices[3],
        )
        # DQ candidate 1
        candidate1.disqualified_status = True
        candidate1.save()

        NUM_VOTERS = 16
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
                    "candidate": candidate3,
                    "rank": 2,
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

            one_candidate_ballots.append(
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

            one_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": ron,
                    "rank": 1,
                    "election": officer,
                }
            )

        for v in voters[12:16]:
            all_candidate_ballots.append(
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
                    "candidate": candidate2,
                    "rank": 1,
                    "election": officer,
                }
            )
            all_candidate_ballots.append(
                {
                    "voter": v,
                    "candidate": candidate1,
                    "rank": 2,
                    "election": officer,
                }
            )

        ballots = ron_only_ballots + all_candidate_ballots + one_candidate_ballots
        for ballot in ballots:
            b = Ballot.objects.create(**ballot)
            b.save()

        results = generate_results(
            ElectionSession.objects.filter(
                election_session_name=self.election_session.election_session_name
            )
        )
        election_results = results[
            f"{self.election_session.election_session_name} ElectionSession"
        ][officer.election_name]
        # Assert results without DQ - candidate 1 wins
        self.assertEqual(
            election_results["results_without_dq"]["winners"], [candidate1.name]
        )
        self.assertEqual(
            election_results["results_without_dq"]["rounds"][2][candidate1.name], 11
        )
        self.assertEqual(
            election_results["results_without_dq"]["rounds"][2][candidate2.name], 0
        )
        self.assertEqual(
            election_results["results_without_dq"]["rounds"][2][candidate3.name], 0
        )
        self.assertEqual(
            election_results["results_without_dq"]["rounds"][2][ron.name], 5
        )
        self.assertEqual(len(election_results["results_without_dq"]["rounds"]), 3)
        self.assertEqual(election_results["results_without_dq"]["quota"], 9)
        self.assertEqual(
            election_results["results_without_dq"]["spoiledBallots"], NUM_SPOILED
        )
        self.assertEqual(
            election_results["results_without_dq"]["totalVotes"],
            NUM_VOTERS - NUM_SPOILED,
        )

        # Assert results with DQ - candidate 2 wins
        self.assertEqual(
            election_results["results_with_dq"]["winners"], [candidate2.name]
        )
        self.assertEqual(election_results["results_with_dq"]["rounds"][1][ron.name], 7)
        self.assertEqual(
            election_results["results_with_dq"]["rounds"][1][candidate2.name], 9
        )
        self.assertEqual(
            election_results["results_with_dq"]["rounds"][1][candidate3.name], 0
        )
        self.assertEqual(len(election_results["results_with_dq"]["rounds"]), 2)
        self.assertEqual(election_results["results_with_dq"]["quota"], 9)
        self.assertEqual(
            election_results["results_with_dq"]["spoiledBallots"], NUM_SPOILED
        )
        self.assertEqual(
            election_results["results_with_dq"]["totalVotes"], NUM_VOTERS - NUM_SPOILED
        )

    # CASE 3: Multi-seat election with 3 candidates and 2 seats, no one wins
    def test_two_seats_three_candidates_no_winner(self):
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

    # CASE 3: Multi-seat election with 5 candidates and 2 seats
    def test_two_seats_five_candidates(self):
        """
        The distribution of votes in each round is IDENTICAL to the test below
        (test_two_seats_five_candidates_var_2). However, the results of the final
        4th round are different. The reason is due to backwardsEliminationProcess.
        To determine which candidate to eliminate, backwardsEliminationProcess
        looks at the rankings per ballot prior to the current round.

        In this test, some ballots have length 1 while all other ballots have length 2.
        In the other test, all ballots have length 2. Thus, the ballots of len(1) produce
        different results in backwardsEliminationProcess than a ballot of len(>1) even
        though the votes each candidate gets per round is the same.

        Ultimately, the final results are the same, which is what matters. These 2 tests
        show the weird behavior of backwardsEliminationProcess that took me some time to debug.
        """
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
        self.assertEqual(results["rounds"][3][candidate1.name], 0)
        self.assertEqual(results["rounds"][3][candidate2.name], 0)
        self.assertEqual(results["rounds"][3][candidate3.name], 2)
        self.assertEqual(results["rounds"][3][candidate4.name], 0)
        self.assertEqual(results["rounds"][3][ron.name], 1)
        self.assertEqual(len(results["rounds"]), 4)
        self.assertEqual(results["quota"], 3)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 5 candidates and 2 seats
    def test_two_seats_five_candidates_var_2(self):
        """
        Please read the docstring of test_two_seats_three_candidates_0_winners_3_rounds
        to understand why this test exists and how it relates to
        test_two_seats_three_candidates_0_winners_3_rounds
        """
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
        self.assertEqual(results["rounds"][3][candidate1.name], 0)
        self.assertEqual(results["rounds"][3][candidate2.name], 2)
        self.assertEqual(results["rounds"][3][candidate3.name], 0)
        self.assertEqual(results["rounds"][3][candidate4.name], 0)
        self.assertEqual(results["rounds"][3][ron.name], 1)
        self.assertEqual(len(results["rounds"]), 4)
        self.assertEqual(results["quota"], 3)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 5 candidates and 2 seats, has ties in elimination and winners
    # for backwardsEliminationProcess to solve
    def test_two_seats_five_candidates_backwards_elim_process_1(self):
        """
        This test was written to increase testing coverage of backwardsEliminationProcess
        as it has both a tie in candidates to eliminate as well as a tie in who to choose
        a winner from.
        """
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
                [candidate1, candidate2, candidate3, candidate4],
                [candidate1, candidate3, candidate3, candidate4],
                [candidate2, candidate1, candidate3, candidate4],
                [candidate2, candidate1, candidate3, candidate4],
                [candidate3, candidate1, candidate2, candidate4],
                [candidate3, candidate2, candidate1, candidate4],
                [candidate4, candidate3, ron, candidate1],
                [candidate4, ron, candidate1, candidate2],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate2.name, candidate3.name]),
        self.assertEqual(results["rounds"][0][candidate1.name], 2)
        self.assertEqual(results["rounds"][0][candidate2.name], 2)
        self.assertEqual(results["rounds"][0][candidate3.name], 2)
        self.assertEqual(results["rounds"][0][candidate4.name], 2)
        self.assertEqual(results["rounds"][0][ron.name], 0)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 3)
        self.assertEqual(results["rounds"][1][candidate3.name], 3)
        self.assertEqual(results["rounds"][1][candidate4.name], 2)
        self.assertEqual(results["rounds"][1][ron.name], 0)
        self.assertEqual(results["rounds"][2][candidate1.name], 0)
        self.assertEqual(results["rounds"][2][candidate2.name], 0)
        self.assertEqual(results["rounds"][2][candidate3.name], 3)
        self.assertEqual(results["rounds"][2][candidate4.name], 2)
        self.assertEqual(results["rounds"][2][ron.name], 0)
        self.assertEqual(len(results["rounds"]), 3)
        self.assertEqual(results["quota"], 3)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 4 candidates and 2 seats, has ties in elimination
    # for backwardsEliminationProcess to solve in the second round
    def test_two_seats_four_candidates_backwards_elim_process_2(self):
        """
        This test was written to increase testing coverage of backwardsEliminationProcess
        as it has a tie for elimination in the second round.
        """
        self._create_officer(self.election_session, 2)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 3)
        ron, candidate1, candidate2, candidate3 = (
            choices[0],
            choices[1],
            choices[2],
            choices[3],
        )

        NUM_VOTERS = 15
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate3, ron],
                [candidate1, candidate3, ron],
                [candidate1, candidate3, ron],
                [candidate1, candidate3, ron],
                [candidate1, candidate3, ron],
                [candidate1, candidate3, ron],
                [candidate2, ron],
                [candidate2, ron],
                [candidate2, ron],
                [candidate2, ron],
                [candidate3, ron],
                [candidate3, ron],
                [candidate3, ron],
                [ron],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name, ron.name]),
        self.assertEqual(results["rounds"][0][candidate1.name], 6)
        self.assertEqual(results["rounds"][0][candidate2.name], 4)
        self.assertEqual(results["rounds"][0][candidate3.name], 3)
        self.assertEqual(results["rounds"][0][ron.name], 1)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 4)
        self.assertEqual(results["rounds"][1][candidate3.name], 4)
        self.assertEqual(results["rounds"][1][ron.name], 1)
        self.assertEqual(results["rounds"][2][candidate1.name], 0)
        self.assertEqual(results["rounds"][2][candidate2.name], 4)
        self.assertEqual(results["rounds"][2][candidate3.name], 0)
        self.assertEqual(results["rounds"][2][ron.name], 5)
        self.assertEqual(len(results["rounds"]), 3)
        self.assertEqual(results["quota"], 5)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)

    # CASE 3: Multi-seat election with 5 candidates and 2 seats, has ties in a winner
    # for backwardsEliminationProcess to solve in the third round
    def test_two_seats_five_candidates_backwards_elim_process_3(self):
        """
        This test was written to increase testing coverage of backwardsEliminationProcess
        as it has a tie between winners in the third round.
        """
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

        NUM_VOTERS = 19
        NUM_SPOILED = 1
        ballots, voters = self._create_ballots(
            [
                [candidate3, ron],
                [candidate3, ron],
                [candidate3, ron],
                [candidate3, ron],
                [candidate3, ron],
                [candidate3, ron],
                [candidate1, candidate3],
                [candidate1, candidate3],
                [candidate1, candidate2],
                [candidate1, candidate2],
                [candidate2],
                [candidate2],
                [candidate2, ron],
                [candidate2, ron],
                [candidate2, ron],
                [candidate4, candidate1],
                [candidate4, candidate1],
                [candidate4, candidate2],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate3.name, candidate2.name]),
        self.assertEqual(results["rounds"][0][candidate1.name], 4)
        self.assertEqual(results["rounds"][0][candidate2.name], 5)
        self.assertEqual(results["rounds"][0][candidate3.name], 6)
        self.assertEqual(results["rounds"][0][candidate4.name], 3)
        self.assertEqual(results["rounds"][0][ron.name], 0)
        self.assertEqual(results["rounds"][1][candidate1.name], 6)
        self.assertEqual(results["rounds"][1][candidate2.name], 6)
        self.assertEqual(results["rounds"][1][candidate3.name], 6)
        self.assertEqual(results["rounds"][1][candidate4.name], 0)
        self.assertEqual(results["rounds"][1][ron.name], 0)
        self.assertEqual(results["rounds"][2][candidate1.name], 0)
        self.assertEqual(results["rounds"][2][candidate2.name], 8)
        self.assertEqual(results["rounds"][2][candidate3.name], 8)
        self.assertEqual(results["rounds"][2][candidate4.name], 0)
        self.assertEqual(results["rounds"][2][ron.name], 0)
        self.assertEqual(results["rounds"][3][candidate1.name], 0)
        self.assertEqual(results["rounds"][3][candidate2.name], 8)
        self.assertEqual(results["rounds"][3][candidate3.name], 0)
        self.assertEqual(results["rounds"][3][candidate4.name], 0)
        self.assertEqual(results["rounds"][3][ron.name], 0.75)
        self.assertEqual(len(results["rounds"]), 4)
        self.assertEqual(results["quota"], 7)
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
        results = self._create_results(ballots, choices, officer, error=True)
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
        """Ron wins second round, therefore third round does not occur"""
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

    # CASE 3: Multi-seat election with 3 candidates and 3 seats, 2 candidates win (not ron)
    def test_three_seats_three_candidates_two_winners_no_ron(self):
        """Ron does not pass the quota to win the third round"""
        self._create_officer(self.election_session, 3)
        officer = Election.objects.filter(category="officer")[0]

        choices = self._create_candidates(officer, 2)
        ron, candidate1, candidate2 = (
            choices[0],
            choices[1],
            choices[2],
        )

        NUM_VOTERS = 5
        NUM_SPOILED = 0
        ballots, voters = self._create_ballots(
            [
                [candidate1, candidate2, ron],
                [candidate1, candidate2, ron],
                [candidate1, candidate2, ron],
                [candidate2, candidate1],
                [candidate2, candidate1],
            ],
            officer,
            NUM_VOTERS,
            NUM_SPOILED,
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], [candidate1.name, candidate2.name])
        self.assertEqual(results["rounds"][0][candidate1.name], 3)
        self.assertEqual(results["rounds"][0][candidate2.name], 2)
        self.assertEqual(results["rounds"][0][ron.name], 0)
        self.assertEqual(results["rounds"][1][candidate1.name], 0)
        self.assertEqual(results["rounds"][1][candidate2.name], 3)
        self.assertEqual(results["rounds"][1][ron.name], 0)
        self.assertEqual(results["rounds"][2][candidate1.name], 0)
        self.assertEqual(results["rounds"][2][candidate2.name], 0)
        self.assertEqual(results["rounds"][2][ron.name], 1 / 3)
        self.assertEqual(len(results["rounds"]), 3)
        self.assertEqual(results["quota"], 2)
        self.assertEqual(results["spoiledBallots"], 0)
        self.assertEqual(results["totalVotes"], len(voters) - NUM_SPOILED)
