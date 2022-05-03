from django.test import TestCase
import json

from backend.ballot import calculate_results

# from backend.ballot_new import calculate_results  # Uncomment to test with the new file

from backend.admin import generate_results
from backend.models import (
    Ballot,
    Candidate,
    Election,
    Voter,
)
from backend.serializers import (
    BallotResultsCalculationSerializer as BallotSerializer,
    CandidateSerializer,
)

from skule_vote.tests import SetupMixin


class BallotRealDataTestCase(SetupMixin, TestCase):
    def setUp(self):
        super().setUp()
        self._set_election_session_data()

        self.election_session = self._create_election_session()

    def _create_candidates(self, names, election):
        for name in names:
            candidate = Candidate(
                name=name, statement="Insert statement here.", election=election
            )
            candidate.save()
        candidates = Candidate.objects.filter(election=election).exclude(
            name="Reopen Nominations"
        )
        candidates = list(candidates)
        ron = Candidate.objects.get(election=election, name="Reopen Nominations")

        # Make sure they appear in the same order as names
        candidates_in_order = []
        for name in names:
            for c in candidates:
                if c.name == name:
                    candidates_in_order.append(c)
                    continue
        return candidates_in_order + [ron]

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

    def _create_ballots(self, raw_ballots, election, choices_in_order, num_voters=0):
        num_spoiled = 0
        clean_ballots = []
        for b in raw_ballots:
            ranking = []
            for rank in b["M"]["ranking"]["L"]:
                ranking.append(choices_in_order[int(rank["N"])])

            if len(ranking) == 0:
                num_spoiled += 1
            else:
                clean_ballots.append(ranking)

        self._generate_voters(count=len(raw_ballots))
        voters = Voter.objects.all()
        ballots = []

        for i, ballot in enumerate(clean_ballots):
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

    def test_valedictoria_2022(self):
        # Real data and results from the 2022 Valedictoria election
        self._create_officer(self.election_session, 1)
        officer = Election.objects.filter(category="officer")[0]

        with open("./backend/test_data/2022_Valedictoria.txt", "r") as f:
            lines = f.read()
            election = json.loads(lines)

        names = [c["M"]["name"]["S"] for c in election["choices"]["L"]]
        names.pop()  # Remove Ron from list

        choices = self._create_candidates(names, officer)

        ballots, voters = self._create_ballots(
            election["Ballots"]["L"], officer, choices
        )

        results = self._create_results(ballots, choices, officer)
        self.assertEqual(results["winners"], ["Joshua Pius"])

        self.assertEqual(results["rounds"][0]["Matthew Van Oirschot"], 29)
        self.assertEqual(results["rounds"][0]["Brohath Amrithraj"], 45)
        self.assertEqual(results["rounds"][0]["Susan Sun"], 34)
        self.assertEqual(results["rounds"][0]["Joshua Pius"], 74)
        self.assertEqual(results["rounds"][0]["Ben Morehead"], 9)
        self.assertEqual(results["rounds"][0]["John Ambrad"], 5)
        self.assertEqual(results["rounds"][0]["Brendan Leder"], 8)
        self.assertEqual(results["rounds"][0]["Reopen Nominations"], 6)

        self.assertEqual(results["rounds"][1]["Matthew Van Oirschot"], 29)
        self.assertEqual(results["rounds"][1]["Brohath Amrithraj"], 45)
        self.assertEqual(results["rounds"][1]["Susan Sun"], 34)
        self.assertEqual(results["rounds"][1]["Joshua Pius"], 77)
        self.assertEqual(results["rounds"][1]["Ben Morehead"], 9)
        self.assertEqual(results["rounds"][1]["John Ambrad"], 0)
        self.assertEqual(results["rounds"][1]["Brendan Leder"], 10)
        self.assertEqual(results["rounds"][1]["Reopen Nominations"], 6)

        self.assertEqual(results["rounds"][2]["Matthew Van Oirschot"], 30)
        self.assertEqual(results["rounds"][2]["Brohath Amrithraj"], 46)
        self.assertEqual(results["rounds"][2]["Susan Sun"], 34)
        self.assertEqual(results["rounds"][2]["Joshua Pius"], 82)
        self.assertEqual(results["rounds"][2]["Ben Morehead"], 0)
        self.assertEqual(results["rounds"][2]["John Ambrad"], 0)
        self.assertEqual(results["rounds"][2]["Brendan Leder"], 11)
        self.assertEqual(results["rounds"][2]["Reopen Nominations"], 6)

        self.assertEqual(results["rounds"][3]["Matthew Van Oirschot"], 30)
        self.assertEqual(results["rounds"][3]["Brohath Amrithraj"], 47)
        self.assertEqual(results["rounds"][3]["Susan Sun"], 35)
        self.assertEqual(results["rounds"][3]["Joshua Pius"], 86)
        self.assertEqual(results["rounds"][3]["Ben Morehead"], 0)
        self.assertEqual(results["rounds"][3]["John Ambrad"], 0)
        self.assertEqual(results["rounds"][3]["Brendan Leder"], 0)
        self.assertEqual(results["rounds"][3]["Reopen Nominations"], 6)

        self.assertEqual(results["rounds"][4]["Matthew Van Oirschot"], 0)
        self.assertEqual(results["rounds"][4]["Brohath Amrithraj"], 49)
        self.assertEqual(results["rounds"][4]["Susan Sun"], 46)
        self.assertEqual(results["rounds"][4]["Joshua Pius"], 92)
        self.assertEqual(results["rounds"][4]["Ben Morehead"], 0)
        self.assertEqual(results["rounds"][4]["John Ambrad"], 0)
        self.assertEqual(results["rounds"][4]["Brendan Leder"], 0)
        self.assertEqual(results["rounds"][4]["Reopen Nominations"], 8)

        self.assertEqual(results["rounds"][5]["Matthew Van Oirschot"], 0)
        self.assertEqual(results["rounds"][5]["Brohath Amrithraj"], 60)
        self.assertEqual(results["rounds"][5]["Susan Sun"], 0)
        self.assertEqual(results["rounds"][5]["Joshua Pius"], 108)
        self.assertEqual(results["rounds"][5]["Ben Morehead"], 0)
        self.assertEqual(results["rounds"][5]["John Ambrad"], 0)
        self.assertEqual(results["rounds"][5]["Brendan Leder"], 0)
        self.assertEqual(results["rounds"][5]["Reopen Nominations"], 10)

        self.assertEqual(len(results["rounds"]), 6)

        self.assertEqual(results["quota"], 106)
        self.assertEqual(results["spoiledBallots"], 1)
        self.assertEqual(results["totalVotes"], 210)
        self.assertEqual(len(voters), 210 + 1)
