import unittest
from ballot import results

class BallotTestCase(unittest.TestCase):
    RON = {"Name": "Reopen nominations", "statement": None}

    

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

    # YES/NO election (simplest case) i.e. a referendum or one person running
    def test_one_candidate_no_tie(self):
        choices = [{"name": "Lisa Li", "statement": "blah"}, self.RON ]
        ballots = [{"sid": 1, "ranking": [0, 1]}, {"sid": 2, "ranking": [0]}, {"sid": 3, "ranking": [1]}, {"sid": 4, "ranking": []}]

        result = results(ballots, choices, 1)
        self.assertEqual(result["winners"], ["Lisa Li"])
        self.assertEqual(result["rounds"], 1)
        self.assertEqual(result["quota"], 3)
        self.assertEqual(result["totalVotes"], len(ballots))
        self.assertEqual(result["spoiledBallots"], 1)


    def test_one_candidate_tie(self):
        choices = [{"name": "Lisa Li", "statement": "blah"}, self.RON ]
        ballots = [{"sid": 1, "ranking": [0, 1]}, {"sid": 2, "ranking": [1, 0]}, {"sid": 3, "ranking": []}]

        result = results(ballots, choices, 1)
        self.assertEqual(result["winners"], ["NO (TIE)"])
        self.assertEqual(result["rounds"], 1)
        self.assertEqual(result["quota"], 3)
        self.assertEqual(result["totalVotes"], len(ballots))
        self.assertEqual(result["spoiledBallots"], 1)

    def test_one_candidate_error(self):
        choices = [{"name": "Lisa Li", "statement": "blah"}, self.RON ]
        ballots = [{"sid": 1, "ranking": [0, 1]}, {"sid": 2, "ranking": [1, 0]}, {"sid": 3, "ranking": []}]

        result = results(ballots, choices, 1)
        self.assertEqual(result["winners"], ["NO (TIE)"])
        self.assertEqual(result["rounds"], 1)
        self.assertEqual(result["quota"], 3)
        self.assertEqual(result["totalVotes"], len(ballots))
        self.assertEqual(result["spoiledBallots"], 1)


if __name__ == '__main__':
    BallotTestCase()
    unittest.main()


# python ballot_tests.py