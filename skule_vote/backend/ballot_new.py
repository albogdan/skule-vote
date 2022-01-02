import math

#   results: function (ballots, choices, numSeats:

RON = "Reopen Nominations"


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


def results(ballots, choices, numSeats):
    _winners = []  # array of names
    _rounds = []  # [{choice1: voteCount, ...}] (index in array = round number)
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
        _quota = math.floor(
            totalVotes / 2 + 1
        )  # may be unnecessary for this election, but better to have it and not need it

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
        stillCounting = True  # need to know when to stop looping over ballots
        remainingChoices = [
            c["name"] for c in choices
        ]  # starts with all choices; once someone is eliminated it sets name to "Eliminated" to maintain indices
        currentRound, totalVotes, spoiledBallots = 0, 0, 0

        while stillCounting:
            # A little redundant, but avoids linkage of "roundObjects"
            _rounds.append({c["name"]: 0 for c in choices})  # Adding choices per round

            for ballot in ballots:
                ranking = ballot["ranking"]

                # If ranking is an empty array, they spoiled the ballot
                if not ranking:
                    spoiledBallots += 1
                else:
                    currentRanking = 0

                    # need to keep going down the list if someone's first choice has been eliminated (perform some checks each time)
                    while currentRanking < len(
                        ranking
                    ):  # Check for someone not completing a ballot fully (i.e. spoiling part of it)
                        if ranking[currentRanking] < len(
                            choices
                        ):  # check for valid ranking
                            if (
                                remainingChoices[ranking[currentRanking]]
                                != "Eliminated"
                            ):
                                name = remainingChoices[ranking[currentRanking]]
                                _rounds[currentRound][name] += 1
                                break
                        else:
                            print(
                                f"ERROR - Ballot contained invalid ranking: {ranking[currentRanking]}"
                            )
                            break
                        currentRanking += 1

                    totalVotes += 1

            # check the results for this round
            maxVotes = -1
            maxName = ""
            minVotes = 999999
            for choice in remainingChoices:
                if choice != "Eliminated":
                    votes = _rounds[currentRound][choice]

                    if votes > maxVotes:
                        maxVotes = votes
                        maxName = choice
                    if votes < minVotes and choice != RON:
                        minVotes = votes

            # assign totalVotes after the first pass through the ballots to use any ballot that has a valid first-preference
            # also assign spoiledBallots at this time too
            if _totalVotes == -1:
                _totalVotes = totalVotes
                _spoiledBallots = spoiledBallots
                _quota = math.floor(totalVotes / (numSeats + 1) + 1)

            # check for a winner, otherwise keep going and eliminate everyone with the lowest amount of votes total
            if maxVotes >= _quota:
                # should only be one, but possibility remains for a complete tie
                # backwardsEliminationProcess(minVotes, maxVotes, candidateList, roundHistory, currentRound, ballots)
                _winners = backwardsEliminationProcess(
                    -1, maxVotes, remainingChoices, _rounds, currentRound, ballots
                )
                stillCounting = False

            else:
                backwardsEliminationProcess(
                    minVotes, -1, remainingChoices, _rounds, currentRound, ballots
                )
                currentRound += 1

                # check to make sure there are still valid candidates left
                validCandidates = False
                for choice in remainingChoices:
                    if choice != "Eliminated" and choice != RON:
                        validCandidates = True
                        break

                if not validCandidates:
                    stillCounting = False

    # CASE 3: Multi-seat election with more than two candidates
    #     Note: Case when RON wins something, stop (any other seats are unfilled) */
    else:
        stillCounting = True  # need to know when to stop looping over ballots
        remainingChoices = (
            []
        )  # similar as above case, except will also use "Winner" to indicate a winner of one of the seats
        currentRound, totalVotes, spoiledBallots, totalWinners = 0, 0, 0, 0
        winnerObject = {}  # keeps track of candidates votes when they win the election

        # "remainingChoices" has all choices to start
        for i in range(len(choices)):
            remainingChoices.append(choices[i]["name"])

        while stillCounting:

            # a little redundant, but avoids linkage of "roundObjects"
            roundObject = {}
            for i in range(len(choices)):
                roundObject[choices[i]["name"]] = 0

            _rounds.append(roundObject)

            for i in range(len(ballots)):
                ranking = ballots[i]["ranking"]

                if len(ranking) != 0:  # check for spoiled ballot
                    currentRanking = 0
                    keepChecking = True
                    voteValue = (
                        1  # updates as you pass over winners and adjusts accordingly
                    )

                    # need to keep going down the list if someone's first choice has been eliminated (perform some checks each time)
                    while keepChecking:
                        if currentRanking < len(
                            ranking
                        ):  # check for someone not completing a ballot fully (i.e. spoiling part of it)
                            if ranking[currentRanking] < len(
                                choices
                            ):  # check for valid ranking
                                name = remainingChoices[ranking[currentRanking]]

                                # this should only be hit after "quota" is set and you're at least on the second round
                                if name != "Eliminated" and name != "Winner":
                                    _rounds[currentRound][name] += voteValue
                                    keepChecking = False
                                else:
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
                        else:
                            keepChecking = False  # this ballot is no longer useful

                    totalVotes += 1
                else:
                    spoiledBallots += 1

            # /check the results for this round
            maxVotes = -1
            minVotes = 999999
            for i in range(len(remainingChoices)):
                if (
                    remainingChoices[i] != "Eliminated"
                    and remainingChoices[i] != "Winner"
                ):
                    votes = _rounds[currentRound][remainingChoices[i]]

                    if votes > maxVotes:
                        maxVotes = votes
                    if votes < minVotes and remainingChoices[i] != RON:
                        minVotes = votes

            # assign totalVotes after the first pass through the ballots to use any ballot that has a valid first-preference
            # also assign spoiledBallots at this time too
            if _totalVotes == -1:
                _totalVotes = totalVotes
                _spoiledBallots = spoiledBallots
                _quota = math.floor(totalVotes / (numSeats + 1) + 1)

            # check for a winner, otherwise keep going and eliminate everyone with the lowest amount of votes total
            if maxVotes >= _quota:
                winnerList = backwardsEliminationProcess(
                    -1, maxVotes, remainingChoices, _rounds, currentRound, ballots
                )

                for i in range(len(winnerList)):
                    totalWinners += 1
                    _winners.append(winnerList[i])
                    winnerObject[winnerList[i]] = maxVotes

                    if totalWinners >= numSeats or winnerList[i] == RON:
                        stillCounting = False
            else:
                backwardsEliminationProcess(
                    minVotes, -1, remainingChoices, _rounds, currentRound, ballots
                )

                # check to make sure there are still valid candidates left
                validCandidates = False
                for i in range(len(remainingChoices)):
                    if (
                        remainingChoices[i] != "Eliminated"
                        and remainingChoices[i] != "Winner"
                        and remainingChoices[i] != RON
                    ):
                        validCandidates = True
                        break

                if not validCandidates:
                    stillCounting = False

            currentRound += 1
    return {
        "winner": _winners,
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
    minVotes, maxVotes, candidateList, roundHistory, currentRound, ballots
):
    eliminationList, winnerList = (
        [],
        [],
    )  # stores the indices of the names in candidateList
    eliminationPath = minVotes != -1  # easy boolean comparison to be used later
    returnList = []

    for i, candidate in enumerate(candidateList):
        if candidate != "Eliminated" and candidate != "Winner":
            if minVotes == roundHistory[currentRound][candidate] and candidate != RON:
                eliminationList.append(i)
            elif maxVotes == roundHistory[currentRound][candidate]:
                winnerList.append(i)

    if len(eliminationList) == 1:
        candidateList[eliminationList[0]] = "Eliminated"
    elif len(winnerList) == 1:
        returnList.append(candidateList[winnerList[0]])
        candidateList[winnerList[0]] = "Winner"
    else:
        # first look through the rounds backwards until you reach the first round
        while currentRound > 0:
            currentRound -= 1

            # arbitrary choice of zero index for comparison purposes
            if eliminationPath:
                minVotes = roundHistory[currentRound][candidateList[eliminationList[0]]]

                for i in range(1, len(eliminationList)):
                    if (
                        roundHistory[currentRound][candidateList[eliminationList[i]]]
                        < minVotes
                    ):
                        minVotes = roundHistory[currentRound][
                            candidateList[eliminationList[i]]
                        ]

                eliminationList = checkCandidates(
                    minVotes, candidateList, roundHistory, currentRound, eliminationList
                )
            else:
                maxVotes = roundHistory[currentRound][candidateList[winnerList[0]]]

                for i in range(1, len(winnerList)):
                    if (
                        roundHistory[currentRound][candidateList[winnerList[i]]]
                        > maxVotes
                    ):
                        maxVotes = roundHistory[currentRound][
                            candidateList[winnerList[i]]
                        ]

                winnerList = checkCandidates(
                    maxVotes, candidateList, roundHistory, currentRound, winnerList
                )

            if len(eliminationList) == 1 or len(winnerList) == 1:
                break

        # if you still don't have a single candidate remaining, start looking through 2nd choice onwards (currentRound should equal 0)
        currentRanking = 1

        # len(roundHistory[0].keys()) is the max number of choices (i.e. number of candidates)
        while (
            currentRanking < len(roundHistory[0].keys())
            and len(eliminationList) != 1
            and len(winnerList) != 1
        ):
            # initialize votes array to line up with votes for candidates being considered for elimination
            votes = []
            listLength = (
                len(eliminationList) if len(eliminationList) > 0 else len(winnerList)
            )
            for i in range(listLength):
                votes.append(0)

            for i in range(len(ballots)):
                ranking = ballots[i]["ranking"]

                if len(ranking) != 0 and currentRanking < len(
                    ranking
                ):  # check for spoiled ballot or partially spoiled ballot
                    for j in range(listLength):
                        if (
                            eliminationPath
                            and eliminationList[j] == ranking[currentRanking]
                        ) or (
                            not eliminationPath
                            and winnerList[j] == ranking[currentRanking]
                        ):  # check for valid ranking
                            votes[j] += 1
                            break

            minVotes = votes[0]
            maxVotes = votes[0]
            changed = False  # arbitrary choice of zero index for comparison purposes
            for i in range(1, len(votes)):
                if eliminationPath and votes[i] < minVotes:
                    minVotes = votes[i]
                    changed = True
                elif not eliminationPath and votes[i] > maxVotes:
                    maxVotes = votes[i]
                    changed = True

            if changed:
                for i in range(len(votes)):
                    # need to maintain integrity of indices and looping when removing elements
                    if eliminationPath and votes[i] == minVotes:
                        eliminationList.splice(i, 1)
                        votes.splice(i, 1)
                        i -= 1
                    elif not eliminationPath and votes[i] == maxVotes:
                        winnerList.splice(i, 1)
                        votes.splice(i, 1)
                        i -= 1

            currentRanking += 1

        # always end with going through the list in case you still end up with a tie by the end of the process
        if eliminationPath:
            for i in range(len(eliminationList)):
                candidateList[eliminationList[i]] = "Eliminated"
        else:
            for i in range(len(winnerList)):
                returnList.append(candidateList[winnerList[i]])
                candidateList[winnerList[i]] = "Winner"

    return returnList


def checkCandidates(
    votesToCheck, candidateList, roundHistory, currentRound, currentList
):
    newList = []

    for i in range(len(currentList)):
        if votesToCheck == roundHistory[currentRound][candidateList[currentList[i]]]:
            newList.append(currentList[i])

    return newList