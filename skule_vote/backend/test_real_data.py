import json

from ballot import calculate_results


# from backend.ballot_new import calculate_results  # Uncomment to test with the new file

# "read_data/2021_VPSL-pre.txt"
# "read_data/2022_Valedictoria.txt"
# "read_data/2021_VPSL-post.txt"


def run():
    for file in ["2021_VPSL-pre.txt"]:
        with open("real_data/" + file, "r") as f:
            # /Users/lisali/Documents/skule-vote/skule_vote/backend/
            lines = f.read()
            election = json.loads(lines)

            ballots = election["Ballots"]["L"]
            choices = election["choices"]["L"]
            numSeats = len(choices)

            choices_clean = []
            for c in choices:
                choice_name = c["M"]["name"]["S"]
                choices_clean.append({"name": choice_name})

            ballots_clean = []
            for b in ballots:
                voter_id = b["M"]["vid"]["S"]
                ranking = []
                for rank in b["M"]["ranking"]["L"]:
                    rank_num = int(rank["N"])
                    ranking.append(rank_num)
                    # print("b", rank, int(rank_num))
                ballots_clean.append({"voter_id": voter_id, "ranking": ranking})

            # print("choices_clean", choices_clean)
            # print("ballots_clean", ballots_clean)

            result = calculate_results(ballots_clean, choices_clean, numSeats)
            # print(f"results for {file}:\n", result)


ballotss = [
    {
        "voter_id": "bzjgYy717Y1zuRdPnkyGe7aalfK9ixrjb76f1Co224hNCDsk8UcyxcB8BORQNP9B",
        "ranking": [0, 1, 2],
    },
    {
        "voter_id": "wwTEKUlDNXVuCVjsKA9rNVmZt0QfTJDAnY0IzWf67zic9CSMopdw2SaRaH6Ma1Da",
        "ranking": [0, 1],
    },
    {
        "voter_id": "GEBjB2CoZT4HTTcpThpS6sk608vZz5himu6qm3GYM5Sbs24loEbLIL4F8KzETc6g",
        "ranking": [0, 1],
    },
    {
        "voter_id": "pEu0x3mNjVgWNCLyiA3YLxuchGODShCplMhuHpqFa3qiI8KwNKrpfvJkIjzZvgqQ",
        "ranking": [0, 1],
    },
    {
        "voter_id": "eIFpDjJOsNhkJd3fO1NU87xptxKCtQZ0TDPDpHX9Nrc4Atio3m4N5YhZvYHuyLpx",
        "ranking": [],
    },
]

BALLOTS = [
    {
        "voter": "<Voter: pKamuoKxf7EpUOJZ1Np9v27UGALJKkqXHlF6COan8rzlIz4F3AUnVhlGDNowPyx7>",
        "candidate": "<Candidate: Reopen Nominations>",
        "rank": 0,
        "election": "<Election: President>",
    },
    {
        "voter": "<Voter: pKamuoKxf7EpUOJZ1Np9v27UGALJKkqXHlF6COan8rzlIz4F3AUnVhlGDNowPyx7>",
        "candidate": "<Candidate: Alex Bogdan>",
        "rank": 1,
        "election": "<Election: President>",
    },
    {
        "voter": "<Voter: pKamuoKxf7EpUOJZ1Np9v27UGALJKkqXHlF6COan8rzlIz4F3AUnVhlGDNowPyx7>",
        "candidate": "<Candidate: Lisa Li>",
        "rank": 2,
        "election": "<Election: President>",
    },
    {
        "voter": "<Voter: svvqVV0yfhBpcnMKnoQexWRyWhvBp3G8wwxhTk6zJ0hkizMhB2cQDcJqdACoLgoz>",
        "candidate": "<Candidate: Reopen Nominations>",
        "rank": 0,
        "election": "<Election: President>",
    },
    {
        "voter": "<Voter: svvqVV0yfhBpcnMKnoQexWRyWhvBp3G8wwxhTk6zJ0hkizMhB2cQDcJqdACoLgoz>",
        "candidate": "<Candidate: Alex Bogdan>",
        "rank": 1,
        "election": "<Election: President>",
    },
    {
        "voter": "<Voter: o7prLAQBqlJOPPNkmfIUk2In3TGLY9dqSf4HccpLpHLArIGzfqOe9qqN7bOiBQ9E>",
        "candidate": "<Candidate: Reopen Nominations>",
        "rank": 0,
        "election": "<Election: President>",
    },
    {
        "voter": "<Voter: o7prLAQBqlJOPPNkmfIUk2In3TGLY9dqSf4HccpLpHLArIGzfqOe9qqN7bOiBQ9E>",
        "candidate": "<Candidate: Alex Bogdan>",
        "rank": 1,
        "election": "<Election: President>",
    },
    {
        "voter": "<Voter: wpVPvEiIuPlBmwfshR7yNdCk5xUgbpoYVfeeS14Pgn6RyXHt4CcYAQzY61fshhUr>",
        "candidate": "<Candidate: Reopen Nominations>",
        "rank": 0,
        "election": "<Election: President>",
    },
    {
        "voter": "<Voter: wpVPvEiIuPlBmwfshR7yNdCk5xUgbpoYVfeeS14Pgn6RyXHt4CcYAQzY61fshhUr>",
        "candidate": "<Candidate: Alex Bogdan>",
        "rank": 1,
        "election": "<Election: President>",
    },
    {
        "voter": "<Voter: f3aSki2BQUWjcgQiR7Ow1JGZRP8tz2VzkArDeU784fiGFfIIhSBXQcGAx1SKGj4p>",
        "candidate": None,
        "rank": None,
        "election": "<Election: President>",
    },
]
# choices [<Candidate: Reopen Nominations>, <Candidate: Alex Bogdan>, <Candidate: Lisa Li>]
# officer President
CHOICES = [
    {
        "id": 81,
        "name": "Reopen Nominations",
        "statement": "Choose this option to reopen nominations.",
        "disqualified_status": False,
        "disqualified_link": None,
        "disqualified_message": None,
        "rule_violation_message": None,
        "rule_violation_link": None,
    },
    {
        "id": 82,
        "name": "Alex Bogdan",
        "statement": "Insert statement here.",
        "disqualified_status": False,
        "disqualified_link": None,
        "disqualified_message": None,
        "rule_violation_message": None,
        "rule_violation_link": None,
    },
    {
        "id": 83,
        "name": "Lisa Li",
        "statement": "Insert statement here.",
        "disqualified_status": False,
        "disqualified_link": None,
        "disqualified_message": None,
        "rule_violation_message": None,
        "rule_violation_link": None,
    },
]

if __name__ == "__main__":
    run()
