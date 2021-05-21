export const mockElections = [
  {
    electionName: "Referedum 1",
    numCandidates: 0,
    election_id: 0,
    category: "Referenda",
  },
  {
    electionName: "Referedum 2",
    numCandidates: 0,
    election_id: 1,
    category: "Referenda",
  },
  {
    electionName: "President",
    numCandidates: 2,
    election_id: 2,
    category: "Officer",
  },
  {
    electionName: "VP Finance",
    numCandidates: 1,
    election_id: 3,
    category: "Officer",
  },
  {
    electionName: "VP Communication",
    numCandidates: 1,
    election_id: 4,
    category: "Officer",
  },
  {
    electionName: "VP Academic",
    numCandidates: 1,
    election_id: 5,
    category: "Officer",
  },
  {
    electionName: "VP Student Life",
    numCandidates: 1,
    election_id: 6,
    category: "Officer",
  },
  {
    electionName: "Board of Directors 1",
    numCandidates: 1,
    election_id: 7,
    category: "Board of Directors",
  },
  {
    electionName: "Board of Directors 2",
    numCandidates: 1,
    election_id: 8,
    category: "Board of Directors",
  },
  {
    electionName: "Discipline Club 1",
    numCandidates: 3,
    election_id: 9,
    category: "Discipline Club",
  },
  {
    electionName: "Discipline Club 2",
    numCandidates: 1,
    election_id: 10,
    category: "Discipline Club",
  },
];

export const MockBallotReferenda = {
  electionName: "Referedum 1",
  numCandidates: 0,
  election_id: 0,
  category: "Referenda",
};
export const MockBallotPresident = {
  electionName: "Referedum 2",
  numCandidates: 1,
  election_id: 1,
  category: "Referenda",
};
export const MockBallotVP = {
  electionName: "VP Finance",
  numCandidates: 1,
  election_id: 3,
  category: "Officer",
  candidates: [{ candidateName: "Lisa", statement: "Blah" }],
};
