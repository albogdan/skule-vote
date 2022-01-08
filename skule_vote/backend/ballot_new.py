import math

#   results: function (ballots, choices, numSeats:

RON = "Reopen Nominations"


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


def calculate_results(ballots, choices, numSeats):
    _winners = []  # Array of winner's names
    _rounds = []  # [{choice1Name: voteCount, ...}] (index in array = round number)
    _quota = 0  # Number
    _totalVotes = -1  # Number (total number of ballots cast)
    _spoiledBallots = 0  # Number (total number of spoiled ballots)

    # CASE 1: YES/NO election i.e. a referendum or one person running
    if len(choices) == 2:
        totalVotes, spoiledBallots = 0, 0
        _rounds.append({c["name"]: 0 for c in choices})  # Adding round 0 choices

        # Go through each ballot, which will either be yes, no, or blank (spoil)
        for ballot in ballots:
            ranking = ballot["ranking"]

            # If ranking is an empty array, they spoiled the ballot
            if not ranking:
                spoiledBallots += 1
            else:
                if ranking[0] < len(choices):
                    name = choices[ranking[0]]["name"]
                    _rounds[0][name] += 1
                else:
                    print(f"ERROR - Ballot contained invalid ranking: {ranking[0]}")
                totalVotes += 1

        _totalVotes = totalVotes
        _spoiledBallots = spoiledBallots
        # Quota may be unnecessary for this election, but better to have it and not need it
        _quota = math.floor(totalVotes / 2 + 1)

        ch1 = choices[0]["name"]
        ch2 = choices[1]["name"]
        if _rounds[0][ch1] == _rounds[0][ch2]:  # Check for a tie
            _winners.append("NO (TIE)")
        else:
            _winners.append(ch1 if (_rounds[0][ch1] > _rounds[0][ch2]) else ch2)

    # CASE 2: Single seat election
    # >>> Keep eliminating the bottom choice (you cannot eliminate "Reopen Nominations" aka RON), until
    #     one person gets >50% of the vote, keeping track of intermediate rounds for audit reasons    */
    elif numSeats == 1:
        # Need to know when to stop looping over ballots
        stillCounting = True
        # Start with all choices; once someone is eliminated it sets name to "Eliminated" to maintain indices
        remainingChoices = [c["name"] for c in choices]
        currentRound, totalVotes, spoiledBallots = 0, 0, 0

        while stillCounting:
            _rounds.append({c["name"]: 0 for c in choices})  # Adding choices per round

            for ballot in ballots:
                ranking = ballot["ranking"]

                # If ranking is an empty array, they spoiled the ballot
                if not ranking:
                    spoiledBallots += 1
                else:
                    currentRanking = 0

                    # Keep going down the list if someone's first choice has been eliminated (perform some checks each time)
                    # Check for someone not completing a ballot fully (i.e. spoiling part of it)
                    while currentRanking < len(ranking):
                        # Check for valid ranking
                        if ranking[currentRanking] < len(choices):
                            name = remainingChoices[ranking[currentRanking]]
                            if name != "Eliminated":
                                _rounds[currentRound][name] += 1
                                break
                        else:
                            print(
                                f"ERROR - Ballot contained invalid ranking: {ranking[currentRanking]}"
                            )
                            # TODO: Figure out what we're doing in this edge case, below is temp for now
                            break
                        currentRanking += 1

                    totalVotes += 1

            # Check the results for this round
            maxVotes, minVotes = -1, 999999
            for choice in remainingChoices:
                if choice != "Eliminated":
                    votes = _rounds[currentRound][choice]

                    if votes > maxVotes:
                        maxVotes = votes
                    if votes < minVotes and choice != RON:
                        minVotes = votes

            # Assign totalVotes after the first pass through the ballots to use any ballot that has a valid first-preference
            # Also assign spoiledBallots at this time too
            if _totalVotes == -1:
                _totalVotes = totalVotes
                _spoiledBallots = spoiledBallots
                _quota = math.floor(totalVotes / (numSeats + 1) + 1)

            # Check for a winner, otherwise keep going and eliminate everyone with the lowest amount of votes total
            if maxVotes >= _quota:
                _winners = backwardsEliminationProcess(
                    -1, maxVotes, remainingChoices, _rounds, currentRound, ballots
                )
                stillCounting = False
            else:
                backwardsEliminationProcess(
                    minVotes, -1, remainingChoices, _rounds, currentRound, ballots
                )
                currentRound += 1

                # Make sure there are still valid candidates left
                validCandidates = filter(
                    lambda x: (x != "Eliminated" and x != RON), remainingChoices
                )
                if not list(validCandidates):
                    stillCounting = False

    # CASE 3: Multi-seat election with more than two candidates
    # >>> Note: Case when RON wins something, stop counting further rounds (remaining seats are unfilled) */
    else:
        stillCounting = True  # Need to know when to stop looping over ballots
        # Their name will be replaced with "Winner" to indicate a winner of one of the seats
        remainingChoices = [c["name"] for c in choices]
        currentRound, totalVotes, spoiledBallots, totalWinners = 0, 0, 0, 0
        winnerObject = {}  # Keeps track of winning candidates' votes

        while stillCounting:
            _rounds.append({c["name"]: 0 for c in choices})  # Adding choices per round

            for i in range(len(ballots)):
                ranking = ballots[i]["ranking"]

                # If ranking is an empty array, they spoiled the ballot
                if not ranking:
                    spoiledBallots += 1
                else:
                    currentRanking = 0
                    keepChecking = True
                    # VoteValue updates as you pass over winners and adjusts accordingly
                    voteValue = 1

                    # Keep going down the list if someone's first choice has been eliminated (perform some checks each time)
                    while keepChecking:
                        # Check for someone not completing a ballot fully (i.e. spoiling part of it)
                        if currentRanking < len(ranking):
                            # Check for valid ranking
                            if ranking[currentRanking] < len(choices):
                                name = remainingChoices[ranking[currentRanking]]
                                if name != "Eliminated" and name != "Winner":
                                    _rounds[currentRound][name] += voteValue
                                    keepChecking = False
                                else:
                                    # This should only be hit after "quota" is set and you're at least on the second round
                                    if name == "Winner":
                                        name = choices[ranking[currentRanking]]["name"]
                                        voteValue = (
                                            voteValue
                                            * (winnerObject[name] - _quota)
                                            / (winnerObject[name])
                                        )

                                    currentRanking += 1
                            else:
                                print(
                                    f"ERROR - Ballot contained invalid ranking: {ranking[currentRanking]}"
                                )
                                # TODO: Figure out what we're doing in this edge case, below is temp for now
                                break
                        else:
                            # This ballot is no longer useful
                            keepChecking = False

                    totalVotes += 1

            # Check the results for this round
            maxVotes, minVotes = -1, 999999
            for choice in remainingChoices:
                if choice != "Eliminated" and choice != "Winner":
                    votes = _rounds[currentRound][choice]

                    if votes > maxVotes:
                        maxVotes = votes
                    if votes < minVotes and choice != RON:
                        minVotes = votes

            # Assign totalVotes after the first pass through the ballots to use any ballot that has a valid first-preference
            # Also assign spoiledBallots at this time too
            if _totalVotes == -1:
                _totalVotes = totalVotes
                _spoiledBallots = spoiledBallots
                _quota = math.floor(totalVotes / (numSeats + 1) + 1)

            # Check for a winner, otherwise keep going and eliminate everyone with the lowest amount of votes total
            if maxVotes >= _quota:
                winnerList = backwardsEliminationProcess(
                    -1, maxVotes, remainingChoices, _rounds, currentRound, ballots
                )

                totalWinners += len(winnerList)
                _winners.extend(winnerList)
                for winner in winnerList:
                    winnerObject[winner] = maxVotes

                if totalWinners >= numSeats or RON in winnerList:
                    stillCounting = False

            else:
                backwardsEliminationProcess(
                    minVotes, -1, remainingChoices, _rounds, currentRound, ballots
                )

                # Make sure there are still valid candidates left
                validCandidates = filter(
                    lambda x: (x != "Eliminated" and x != "Winner" and x != RON),
                    remainingChoices,
                )
                if not list(validCandidates):
                    stillCounting = False

            currentRound += 1

    return {
        "winners": _winners,
        "rounds": _rounds,
        "quota": _quota,
        "totalVotes": _totalVotes,
        "spoiledBallots": _spoiledBallots,
    }


# /*  Used for deciding which candidate to eliminate or which one to declare as a winner for a round. Use a backwards elimination
#     process for this in the case of a tie at the start, compare the ballots' 2nd preferences, then 3rd, and so on. If there is
#     still a tie after all of this, eliminate all candidates or declare all of them winners for that round. Either way, the CRO
#     should review the ballots carefully in cases of "extreme ties" to make the final call if need be.
#     Note: either "minVotes" or "maxVotes" will equal -1, so the function decides on the fly which comparison to make.   */
def backwardsEliminationProcess(
    minVotes, maxVotes, candidateList, _rounds, currentRound, ballots
):
    # Stores the indices of the names from candidateList
    eliminationList, winnerList = [], []
    # Determine if we're looking for a winner or someone to eliminate
    isElimination = minVotes != -1
    returnList = []

    for i, candidate in enumerate(candidateList):
        if candidate != "Eliminated" and candidate != "Winner":
            numVotes = _rounds[currentRound][candidate]
            if minVotes == numVotes and candidate != RON:
                eliminationList.append(i)
            elif maxVotes == numVotes:
                winnerList.append(i)

    if len(eliminationList) == 1:
        candidateList[eliminationList[0]] = "Eliminated"
        return
    elif len(winnerList) == 1:
        returnList.append(candidateList[winnerList[0]])
        candidateList[winnerList[0]] = "Winner"
        return returnList
    else:
        # First look through the rounds backwards until you reach the first round
        while currentRound > 0:
            currentRound -= 1
            currRoundVotes = _rounds[currentRound]

            if isElimination:
                minVotes = min(
                    [currRoundVotes[candidateList[elim]] for elim in eliminationList]
                )
                eliminationList = checkCandidates(
                    minVotes, candidateList, currRoundVotes, eliminationList
                )
            else:
                maxVotes = max(
                    [currRoundVotes[candidateList[winner]] for winner in winnerList]
                )
                winnerList = checkCandidates(
                    maxVotes, candidateList, currRoundVotes, winnerList
                )

            if len(eliminationList) == 1 or len(winnerList) == 1:
                break

        # If there is still more than 1 winner or more than 1 person to eliminate, start
        # looking through every ballot starting from their 2nd choice onwards
        currentRanking = 1

        # len(_rounds[0]) is the max number of choices (i.e. number of candidates)
        while (
            currentRanking < len(_rounds[0])
            and len(eliminationList) != 1
            and len(winnerList) != 1
        ):
            # One of the lists has length 0 and the other is populated, depending if we're looking for
            # a winner or someone to eliminate
            listLength = max(len(eliminationList), len(winnerList))
            # Initialize votes array to line up with votes for candidates being considered for elimination
            votes = [0 for _ in range(listLength)]

            for ballot in ballots:
                ranking = ballot["ranking"]

                # Check for spoiled ballot or partially spoiled ballot
                if len(ranking) != 0 and currentRanking < len(ranking):
                    for j in range(listLength):
                        if (
                            isElimination
                            and eliminationList[j] == ranking[currentRanking]
                        ) or (
                            not isElimination
                            and winnerList[j] == ranking[currentRanking]
                        ):  # check for valid ranking
                            votes[j] += 1
                            break

            # If candidates have a different number of votes (len(set(votes)) > 1), update eliminationList/winnerList, else
            # they stay the same
            if len(set(votes)) > 1:
                if isElimination:
                    minVotes = min(votes)
                    eliminationList = [
                        e for i, e in enumerate(eliminationList) if votes[i] != minVotes
                    ]
                else:
                    maxVotes = max(votes)
                    winnerList = [
                        w for i, w in enumerate(winnerList) if votes[i] != maxVotes
                    ]

            currentRanking += 1

        # Always end with going through the list in case you still end up with a tie by the end of the process
        if isElimination:
            for elim in eliminationList:
                candidateList[elim] = "Eliminated"
        else:
            for winner in winnerList:
                returnList.append(candidateList[winner])
                candidateList[winner] = "Winner"

    return returnList


def checkCandidates(voteThreshold, candidateList, currRoundVotes, currentList):
    newList = [
        curr
        for curr in currentList
        if voteThreshold == currRoundVotes[candidateList[curr]]
    ]
    return newList
