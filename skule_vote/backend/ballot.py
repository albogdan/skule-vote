import math

#   results: function (ballots, choices, numSeats:

RON = "Reopen Nominations"


def calculate_results(ballots, choices, numSeats):
    result = {
        "winners": [],
        "rounds": [],
        "quota": 0,
        "totalVotes": -1,
        "spoiledBallots": 0,
    }

    # YES/NO election (simplest case) i.e. a referendum or one person running
    if len(choices) == 2:
        totalVotes, spoiledBallots = 0, 0

        # initialize variables
        roundObject = {}
        for i in range(len(choices)):
            roundObject[choices[i]["name"]] = 0

        result["rounds"].append(roundObject)
        # go through each ballot, which will either be yes, no, or blank (spoil)
        for i in range(len(ballots)):
            ranking = ballots[i]["ranking"]

            # check for spoiled (ranking would be an empty list)
            if len(ranking) != 0:
                if ranking[0] < len(choices):
                    name = choices[ranking[0]]["name"]
                    result["rounds"][0][name] += 1
                else:
                    print(f"ERROR - Ballot contained invalid ranking: {ranking[0]}")

                totalVotes += 1
            else:
                spoiledBallots += 1

        result["totalVotes"] = totalVotes
        result["spoiledBallots"] = spoiledBallots
        result["quota"] = math.floor(
            totalVotes / 2 + 1
        )  # may be unnecessary for this election, but better to have it and not need it

        ch1, ch2 = choices[0]["name"], choices[1]["name"]
        result["winners"].append(
            ch1 if (result["rounds"][0][ch1] > result["rounds"][0][ch2]) else ch2
        )

        # // check for a tie
        if result["rounds"][0][ch1] == result["rounds"][0][ch2]:
            result["winners"][0] = "NO (TIE)"

    # single seat election
    #     keep eliminating the bottom choice (you cannot eliminate "Reopen Nominations" aka RON), until
    #     one person gets >50% of the vote, keeping track of intermediate rounds for audit reasons    */
    elif numSeats == 1:

        stillCounting = True  # need to know when to stop looping over ballots
        remainingChoices = (
            []
        )  # starts with all choices once someone is eliminated it sets name to "Eliminated" to maintain indices
        currentRound, totalVotes, spoiledBallots = 0, 0, 0

        # // "remainingChoices" has all choices to start
        for i in range(len(choices)):
            remainingChoices.append(choices[i]["name"])

        while stillCounting:

            # // a little redundant, but avoids linkage of "roundObjects"
            roundObject = {}
            for i in range(len(choices)):
                roundObject[choices[i]["name"]] = 0

            result["rounds"].append(roundObject)

            for i in range(len(ballots)):
                ranking = ballots[i]["ranking"]

                if len(ranking) != 0:  # check for spoiled ballot
                    currentRanking = 0
                    keepChecking = True

                    # need to keep going down the list if someone's first choice has been eliminated (perform some checks each time)
                    while keepChecking:
                        if currentRanking < len(
                            ranking
                        ):  # check for someone not completing a ballot fully (i.e. spoiling part of it)
                            if ranking[currentRanking] < len(
                                choices
                            ):  # check for valid ranking
                                if (
                                    remainingChoices[ranking[currentRanking]]
                                    != "Eliminated"
                                ):
                                    name = remainingChoices[ranking[currentRanking]]
                                    result["rounds"][currentRound][name] += 1
                                    keepChecking = False
                                else:
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

            # check the results for this round
            maxVotes = -1
            maxName = ""
            minVotes = 999999
            for i in range(len(remainingChoices)):
                if remainingChoices[i] != "Eliminated":
                    votes = result["rounds"][currentRound][remainingChoices[i]]

                    if votes > maxVotes:
                        maxVotes = votes
                        maxName = remainingChoices[i]
                    if votes < minVotes and remainingChoices[i] != RON:
                        minVotes = votes

            # assign totalVotes after the first pass through the ballots to use any ballot that has a valid first-preference
            # also assign spoiledBallots at this time too
            if result["totalVotes"] == -1:
                result["totalVotes"] = totalVotes
                result["spoiledBallots"] = spoiledBallots
                result["quota"] = math.floor(totalVotes / (numSeats + 1) + 1)

            # check for a winner, otherwise keep going and eliminate everyone with the lowest amount of votes total
            if maxVotes >= result["quota"]:
                # should only be one, but possibility remains for a complete tie
                result["winners"] = backwardsEliminationProcess(
                    -1,
                    maxVotes,
                    remainingChoices,
                    result["rounds"],
                    currentRound,
                    ballots,
                )
                stillCounting = False

            else:
                backwardsEliminationProcess(
                    minVotes,
                    -1,
                    remainingChoices,
                    result["rounds"],
                    currentRound,
                    ballots,
                )
                currentRound += 1

                # check to make sure there are still valid candidates left
                validCandidates = False
                for i in range(len(remainingChoices)):
                    if (
                        remainingChoices[i] != "Eliminated"
                        and remainingChoices[i] != RON
                    ):
                        validCandidates = True
                        break

                if not validCandidates:
                    stillCounting = False

    #  multi-seat election with more than two candidates
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

            result["rounds"].append(roundObject)

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
                                    result["rounds"][currentRound][name] += voteValue
                                    keepChecking = False
                                else:
                                    if name == "Winner":
                                        name = choices[ranking[currentRanking]]["name"]
                                        voteValue = (
                                            voteValue
                                            * (winnerObject[name] - result["quota"])
                                            / (winnerObject[name])
                                        )

                                    currentRanking += 1
                            else:
                                print(
                                    f"ERROR - Ballot contained invalid ranking: {ranking[currentRanking]}"
                                )
                                # Figure out what we're doing in this edge case, below is temp for now
                                keepChecking = False
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
                    votes = result["rounds"][currentRound][remainingChoices[i]]

                    if votes > maxVotes:
                        maxVotes = votes
                    if votes < minVotes and remainingChoices[i] != RON:
                        minVotes = votes

            # assign totalVotes after the first pass through the ballots to use any ballot that has a valid first-preference
            # also assign spoiledBallots at this time too
            if result["totalVotes"] == -1:
                result["totalVotes"] = totalVotes
                result["spoiledBallots"] = spoiledBallots
                result["quota"] = math.floor(totalVotes / (numSeats + 1) + 1)

            # check for a winner, otherwise keep going and eliminate everyone with the lowest amount of votes total
            if maxVotes >= result["quota"]:
                winnerList = backwardsEliminationProcess(
                    -1,
                    maxVotes,
                    remainingChoices,
                    result["rounds"],
                    currentRound,
                    ballots,
                )

                for i in range(len(winnerList)):
                    totalWinners += 1
                    result["winners"].append(winnerList[i])
                    winnerObject[winnerList[i]] = maxVotes

                    if totalWinners >= numSeats or winnerList[i] == RON:
                        stillCounting = False
            else:
                backwardsEliminationProcess(
                    minVotes,
                    -1,
                    remainingChoices,
                    result["rounds"],
                    currentRound,
                    ballots,
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

    return result


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

    for i in range(len(candidateList)):
        if candidateList[i] != "Eliminated" and candidateList[i] != "Winner":
            if (
                minVotes == roundHistory[currentRound][candidateList[i]]
                and candidateList[i] != RON
            ):
                eliminationList.append(i)
            elif maxVotes == roundHistory[currentRound][candidateList[i]]:
                winnerList.append(i)

    if len(eliminationList) == 1:
        candidateList[eliminationList[0]] = "Eliminated"
        return
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

                # check for spoiled ballot or partially spoiled ballot
                if len(ranking) != 0 and currentRanking < len(ranking):
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
                i = 0
                while i < len(votes):
                    if eliminationPath and votes[i] == minVotes:
                        eliminationList.pop(i)
                        votes.pop(i)
                    elif not eliminationPath and votes[i] == maxVotes:
                        winnerList.pop(i)
                        votes.pop(i)
                    else:
                        i += 1

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
