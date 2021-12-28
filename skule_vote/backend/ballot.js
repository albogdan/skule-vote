module.exports = {
  // calculate election results
  results: function (ballots, choices, numSeats) {
    var result = {
      winners: [],
      rounds: [],
      quota: 0,
      totalVotes: -1,
      spoiledBallots: 0,
    };

    RON = "Reopen Nominations";

    // YES/NO election (simplest case); i.e. a referendum or one person running
    if (choices.length === 2) {
      var totalVotes = 0,
        spoiledBallots = 0;

      // initialize variables
      var roundObject = {};
      for (var i = 0; i < choices.length; i++) roundObject[choices[i].name] = 0;

      result.rounds.push(roundObject);

      // go through each ballot, which will either be yes, no, or blank (spoil)
      for (var i = 0; i < ballots.length; i++) {
        ranking = ballots[i].ranking;

        // check for spoiled (ranking would be an empty list)
        if (ranking.length !== 0) {
          if (ranking[0] < choices.length) {
            name = choices[ranking[0]].name;
            result.rounds[0][name] += 1;
          } else
            console.log(
              "ERROR - Ballot contained invalid ranking: " + ranking[0]
            );

          totalVotes++;
        } else spoiledBallots++;
      }

      result.totalVotes = totalVotes;
      result.spoiledBallots = spoiledBallots;
      result.quota = Math.floor(totalVotes / 2 + 1); // may be unnecessary for this election, but better to have it and not need it

      ch1 = choices[0].name;
      ch2 = choices[1].name;
      result.winners.push(
        result.rounds[0][ch1] > result.rounds[0][ch2] ? ch1 : ch2
      );

      // check for a tie
      if (result.rounds[0][ch1] === result.rounds[0][ch2])
        result.winners[0] = "NO (TIE)";
    } else if (numSeats === 1) {

    /*  single seat election
        keep eliminating the bottom choice (you cannot eliminate "Reopen Nominations" aka RON), until
        one person gets >50% of the vote, keeping track of intermediate rounds for audit reasons    */
      stillCounting = true; // need to know when to stop looping over ballots
      remainingChoices = []; // starts with all choices; once someone is eliminated it sets name to "Eliminated" to maintain indices
      currentRound = 0;
      (totalVotes = 0), (spoiledBallots = 0);

      // "remainingChoices" has all choices to start
      for (var i = 0; i < choices.length; i++)
        remainingChoices.push(choices[i].name);

      while (stillCounting) {
        // a little redundant, but avoids linkage of "roundObjects"
        roundObject = {};
        for (var i = 0; i < choices.length; i++)
          roundObject[choices[i].name] = 0;

        result.rounds.push(roundObject);

        for (var i = 0; i < ballots.length; i++) {
          ranking = ballots[i].ranking;

          if (ranking.length !== 0) {
            // check for spoiled ballot
            currentRanking = 0;
            keepChecking = true;

            // need to keep going down the list if someone's first choice has been eliminated (perform some checks each time)
            while (keepChecking) {
              if (currentRanking < ranking.length) {
                // check for someone not completing a ballot fully (i.e. spoiling part of it)
                if (ranking[currentRanking] < choices.length) {
                  // check for valid ranking
                  if (
                    remainingChoices[ranking[currentRanking]] != "Eliminated"
                  ) {
                    name = remainingChoices[ranking[currentRanking]];
                    result.rounds[currentRound][name]++;
                    keepChecking = false;
                  } else currentRanking++;
                } else
                  console.log(
                    "ERROR - Ballot contained invalid ranking: " +
                      ranking[currentRanking]
                  );
              } else keepChecking = false; // this ballot is no longer useful
            }

            totalVotes++;
          } else spoiledBallots++;
        }

        // check the results for this round
        (maxVotes = -1), (maxName = ""), (minVotes = 999999);
        for (var i = 0; i < remainingChoices.length; i++) {
          if (remainingChoices[i] != "Eliminated") {
            votes = result.rounds[currentRound][remainingChoices[i]];

            if (votes > maxVotes) {
              maxVotes = votes;
              maxName = remainingChoices[i];
            }
            if (votes < minVotes && remainingChoices[i] != RON)
              minVotes = votes;
          }
        }

        // assign totalVotes after the first pass through the ballots to use any ballot that has a valid first-preference
        // also assign spoiledBallots at this time too
        if (result.totalVotes == -1) {
          result.totalVotes = totalVotes;
          result.spoiledBallots = spoiledBallots;
          result.quota = Math.floor(totalVotes / (numSeats + 1) + 1);
        }

        // check for a winner, otherwise keep going and eliminate everyone with the lowest amount of votes total
        if (maxVotes >= result.quota) {
          // should only be one, but possibility remains for a complete tie
          result.winners = backwardsEliminationProcess(
            -1,
            maxVotes,
            remainingChoices,
            result.rounds,
            currentRound,
            ballots
          );
          stillCounting = false;
        } else {
          backwardsEliminationProcess(
            minVotes,
            -1,
            remainingChoices,
            result.rounds,
            currentRound,
            ballots
          );
          currentRound++;

          // check to make sure there are still valid candidates left
          validCandidates = false;
          for (var i = 0; i < remainingChoices.length; i++) {
            if (
              remainingChoices[i] != "Eliminated" &&
              remainingChoices[i] != RON
            ) {
              validCandidates = true;
              break;
            }
          }

          if (!validCandidates) stillCounting = false;
        }
      }
    } else {

    /*  multi-seat election with more than two candidates
        Note: Case when RON wins something, stop (any other seats are unfilled) */
      stillCounting = true; // need to know when to stop looping over ballots
      remainingChoices = []; // similar as above case, except will also use "Winner" to indicate a winner of one of the seats
      currentRound = 0;
      (totalVotes = 0), (spoiledBallots = 0);
      (totalWinners = 0), (winnerObject = {}); // keeps track of candidates votes when they win the election

      // "remainingChoices" has all choices to start
      for (var i = 0; i < choices.length; i++)
        remainingChoices.push(choices[i].name);

      while (stillCounting) {
        // a little redundant, but avoids linkage of "roundObjects"
        roundObject = {};
        for (var i = 0; i < choices.length; i++)
          roundObject[choices[i].name] = 0;

        result.rounds.push(roundObject);

        for (var i = 0; i < ballots.length; i++) {
          ranking = ballots[i].ranking;

          if (ranking.length !== 0) {
            // check for spoiled ballot
            currentRanking = 0;
            keepChecking = true;
            voteValue = 1; // updates as you pass over winners and adjusts accordingly

            // need to keep going down the list if someone's first choice has been eliminated (perform some checks each time)
            while (keepChecking) {
              if (currentRanking < ranking.length) {
                // check for someone not completing a ballot fully (i.e. spoiling part of it)
                if (ranking[currentRanking] < choices.length) {
                  // check for valid ranking
                  name = remainingChoices[ranking[currentRanking]];

                  // this should only be hit after "quota" is set and you're at least on the second round
                  if (name != "Eliminated" && name != "Winner") {
                    result.rounds[currentRound][name] += voteValue;
                    keepChecking = false;
                  } else {
                    if (name == "Winner") {
                      name = choices[ranking[currentRanking]].name;
                      voteValue =
                        (voteValue * (winnerObject[name] - result.quota)) /
                        winnerObject[name];
                    }

                    currentRanking++;
                  }
                } else
                  console.log(
                    "ERROR - Ballot contained invalid ranking: " +
                      ranking[currentRanking]
                  );
              } else keepChecking = false; // this ballot is no longer useful
            }

            totalVotes++;
          } else spoiledBallots++;
        }

        // check the results for this round
        (maxVotes = -1), (minVotes = 999999);
        for (var i = 0; i < remainingChoices.length; i++) {
          if (
            remainingChoices[i] != "Eliminated" &&
            remainingChoices[i] != "Winner"
          ) {
            votes = result.rounds[currentRound][remainingChoices[i]];

            if (votes > maxVotes) maxVotes = votes;
            if (votes < minVotes && remainingChoices[i] != RON)
              minVotes = votes;
          }
        }

        // assign totalVotes after the first pass through the ballots to use any ballot that has a valid first-preference
        // also assign spoiledBallots at this time too
        if (result.totalVotes == -1) {
          result.totalVotes = totalVotes;
          result.spoiledBallots = spoiledBallots;
          result.quota = Math.floor(totalVotes / (numSeats + 1) + 1);
        }

        // check for a winner, otherwise keep going and eliminate everyone with the lowest amount of votes total
        if (maxVotes >= result.quota) {
          winnerList = backwardsEliminationProcess(
            -1,
            maxVotes,
            remainingChoices,
            result.rounds,
            currentRound,
            ballots
          );

          for (var i = 0; i < winnerList.length; i++) {
            totalWinners++;
            result.winners.push(winnerList[i]);
            winnerObject[winnerList[i]] = maxVotes;

            if (totalWinners >= numSeats || winnerList[i] == RON)
              stillCounting = false;
          }
        } else {
          backwardsEliminationProcess(
            minVotes,
            -1,
            remainingChoices,
            result.rounds,
            currentRound,
            ballots
          );

          // check to make sure there are still valid candidates left
          validCandidates = false;
          for (var i = 0; i < remainingChoices.length; i++) {
            if (
              remainingChoices[i] != "Eliminated" &&
              remainingChoices[i] != "Winner" &&
              remainingChoices[i] != RON
            ) {
              validCandidates = true;
              break;
            }
          }

          if (!validCandidates) stillCounting = false;
        }

        currentRound++;
      }
    }
    return result;

    /*  Used for deciding which candidate to eliminate or which one to declare as a winner for a round. Use a backwards elimination
        process for this; in the case of a tie at the start, compare the ballots' 2nd preferences, then 3rd, and so on. If there is
        still a tie after all of this, eliminate all candidates or declare all of them winners for that round. Either way, the CRO
        should review the ballots carefully in cases of "extreme ties" to make the final call if need be.
        Note: either "minVotes" or "maxVotes" will equal -1, so the function decides on the fly which comparison to make.   */
    function backwardsEliminationProcess(
      minVotes,
      maxVotes,
      candidateList,
      roundHistory,
      currentRound,
      ballots
    ) {
      (eliminationList = []), (winnerList = []); // stores the indices of the names in candidateList
      eliminationPath = minVotes != -1 ? true : false; // easy boolean comparison to be used later
      returnList = [];

      for (var i = 0; i < candidateList.length; i++) {
        if (candidateList[i] != "Eliminated" && candidateList[i] != "Winner") {
          if (
            minVotes == roundHistory[currentRound][candidateList[i]] &&
            candidateList[i] != RON
          )
            eliminationList.push(i);
          else if (maxVotes == roundHistory[currentRound][candidateList[i]])
            winnerList.push(i);
        }
      }

      if (eliminationList.length == 1)
        candidateList[eliminationList[0]] = "Eliminated";
      else if (winnerList.length == 1) {
        returnList.push(candidateList[winnerList[0]]);
        candidateList[winnerList[0]] = "Winner";
      } else {
        // first look through the rounds backwards until you reach the first round
        while (currentRound > 0) {
          currentRound--;

          // arbitrary choice of zero index for comparison purposes
          if (eliminationPath) {
            minVotes =
              roundHistory[currentRound][candidateList[eliminationList[0]]];

            for (var i = 1; i < eliminationList.length; i++) {
              if (
                roundHistory[currentRound][candidateList[eliminationList[i]]] <
                minVotes
              )
                minVotes =
                  roundHistory[currentRound][candidateList[eliminationList[i]]];
            }

            eliminationList = checkCandidates(
              minVotes,
              candidateList,
              roundHistory,
              currentRound,
              eliminationList
            );
          } else {
            maxVotes = roundHistory[currentRound][candidateList[winnerList[0]]];

            for (var i = 1; i < winnerList.length; i++) {
              if (
                roundHistory[currentRound][candidateList[winnerList[i]]] >
                maxVotes
              )
                maxVotes =
                  roundHistory[currentRound][candidateList[winnerList[i]]];
            }

            winnerList = checkCandidates(
              maxVotes,
              candidateList,
              roundHistory,
              currentRound,
              winnerList
            );
          }

          if (eliminationList.length == 1 || winnerList.length == 1) break;
        }

        // if you still don't have a single candidate remaining, start looking through 2nd choice onwards (currentRound should equal 0)
        currentRanking = 1;

        // "Object.keys(roundHistory[0]).length" is the max number of choices (i.e. number of candidates)
        while (
          currentRanking < Object.keys(roundHistory[0]).length &&
          eliminationList.length != 1 &&
          winnerList.length != 1
        ) {
          // initialize votes array to line up with votes for candidates being considered for elimination
          votes = [];
          listLength =
            eliminationList.length > 0
              ? eliminationList.length
              : winnerList.length;
          for (var i = 0; i < listLength; i++) votes.push(0);

          for (var i = 0; i < ballots.length; i++) {
            ranking = ballots[i].ranking;

            if (ranking.length !== 0 && currentRanking < ranking.length) {
              // check for spoiled ballot or partially spoiled ballot
              for (var j = 0; j < listLength; j++) {
                if (
                  (eliminationPath &&
                    eliminationList[j] == ranking[currentRanking]) ||
                  (!eliminationPath && winnerList[j] == ranking[currentRanking])
                ) {
                  // check for valid ranking
                  votes[j]++;
                  break;
                }
              }
            }
          }

          (minVotes = votes[0]), (maxVotes = votes[0]), (changed = false); // arbitrary choice of zero indexfor comparison purposes
          for (var i = 1; i < votes.length; i++) {
            if (eliminationPath && votes[i] < minVotes) {
              minVotes = votes[i];
              changed = true;
            } else if (!eliminationPath && votes[i] > maxVotes) {
              maxVotes = votes[i];
              changed = true;
            }
          }

          if (changed) {
            for (var i = 0; i < votes.length; i++) {
              // need to maintain integrity of indices and looping when removing elements
              if (eliminationPath && votes[i] == minVotes) {
                eliminationList.splice(i, 1);
                votes.splice(i, 1);
                i--;
              } else if (!eliminationPath && votes[i] == maxVotes) {
                winnerList.splice(i, 1);
                votes.splice(i, 1);
                i--;
              }
            }
          }

          currentRanking++;
        }

        // always end with going through the list in case you still end up with a tie by the end of the process
        if (eliminationPath) {
          for (var i = 0; i < eliminationList.length; i++)
            candidateList[eliminationList[i]] = "Eliminated";
        } else {
          for (var i = 0; i < winnerList.length; i++) {
            returnList.push(candidateList[winnerList[i]]);
            candidateList[winnerList[i]] = "Winner";
          }
        }
      }

      return returnList;
    }

    function checkCandidates(
      votesToCheck,
      candidateList,
      roundHistory,
      currentRound,
      currentList
    ) {
      newList = [];

      for (var i = 0; i < currentList.length; i++) {
        if (
          votesToCheck ==
          roundHistory[currentRound][candidateList[currentList[i]]]
        )
          newList.push(currentList[i]);
      }

      return newList;
    }
  },
};

/*
Parameters:

"ballots" is every single ballot cast in that election (i.e. array of "ballot")
"ranking" is an array as well, in order (index corresponds to "choice" array)
ballot: {
sid: string (voterID, useless here)
ranking: number[] (index of choice in choices array)
}

"choices" is an array of "choice" (i.e. list of all candidates/options)
choice: {
name: string
statement: string (useless here)
}

numSeats: Number of seats available in election

"totalVotes" is the total votes cast (manually verify with quota after)
each object in "rounds" is 1 round and displays the voteCount for remaining candidates
Returns: {
winners: [] (array of names)
rounds: [{choice1: voteCount, ...}] (index in array = round number)
quota: Number
totalVotes: Number (total number of ballots cast)
spoiledBallots: Number (total number of spoiled ballots)
}
*/
