export const mockElections = [
  {
    electionName: "Referedum 1",
    numCandidates: 0,
    electionId: 0,
    category: "Referenda",
  },
  {
    electionName: "Referedum 2",
    numCandidates: 0,
    electionId: 1,
    category: "Referenda",
  },
  {
    electionName: "President",
    numCandidates: 2,
    electionId: 2,
    category: "Officer",
  },
  {
    electionName: "VP Finance",
    numCandidates: 1,
    electionId: 3,
    category: "Officer",
  },
  {
    electionName: "VP Communication",
    numCandidates: 1,
    electionId: 4,
    category: "Officer",
  },
  {
    electionName: "VP Academic",
    numCandidates: 1,
    electionId: 5,
    category: "Officer",
  },
  {
    electionName: "VP Student Life",
    numCandidates: 1,
    electionId: 6,
    category: "Officer",
  },
  {
    electionName: "Board of Directors 1",
    numCandidates: 1,
    electionId: 7,
    category: "Board of Directors",
  },
  {
    electionName: "Board of Directors 2",
    numCandidates: 1,
    electionId: 8,
    category: "Board of Directors",
  },
  {
    electionName: "Discipline Club 1",
    numCandidates: 3,
    electionId: 9,
    category: "Discipline Club",
  },
  {
    electionName: "Discipline Club 2",
    numCandidates: 1,
    electionId: 10,
    category: "Discipline Club",
  },
];

export const MockBallotReferenda = {
  electionName: "Referedum 1",
  numCandidates: 1,
  electionId: 0,
  category: "Referenda",
  candidates: [
    {
      id: 0,
      candidateName: "Referendum 1",
      statement:
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisinuli.",
      isDisqualified: false,
      disqualificationRuling: null,
      disqualificationLink: null,
      ruleViolationRuling: null,
      ruleViolationLink: null,
    },
    {
      id: 1,
      candidateName: "Reopen Nominations",
      statement: "Choose this option to reopen nominations.",
      isDisqualified: false,
      disqualificationRuling: null,
      disqualificationLink: null,
      ruleViolationRuling: null,
      ruleViolationLink: null,
    },
  ],
};
export const MockBallotPresident = {
  electionName: "President",
  numCandidates: 1,
  electionId: 1,
  category: "Officer",
  candidates: [
    {
      id: 0,
      candidateName: "Lisa Li",
      statement:
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisinuli.",
      isDisqualified: false,
      disqualificationRuling: null,
      disqualificationLink: null,
      ruleViolationRuling: null,
      ruleViolationLink: null,
    },
    {
      id: 1,
      candidateName: "Reopen Nominations",
      statement: "Choose this option to reopen nominations.",
      isDisqualified: false,
      disqualificationRuling: null,
      disqualificationLink: null,
      ruleViolationRuling: null,
      ruleViolationLink: null,
    },
  ],
};
export const MockBallotVP = {
  electionName: "VP Finance",
  numCandidates: 5,
  electionId: 3,
  category: "Officer",
  candidates: [
    {
      id: 0,
      candidateName: "Lisa Li",
      statement:
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisinuli.",
      isDisqualified: false,
      disqualificationRuling: null,
      disqualificationLink: null,
      ruleViolationRuling: null,
      ruleViolationLink: null,
    },
    {
      id: 1,
      candidateName: "Alex Bogdan",
      statement:
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisinuli.",
      isDisqualified: true,
      disqualificationRuling:
        "This candidate was disqualified from the election on March 1, as noted in CRO Ruling #1. However, their name has been left on the ballot as the ruling may be appealed by the candidate and a sucessful appeal would overturn the disqualification.",
      disqualificationLink: "http://digest.skule.ca/u/16",
      ruleViolationRuling: null,
      ruleViolationLink: null,
    },
    {
      id: 2,
      candidateName: "Armin Ale",
      statement:
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisinuli.",
      isDisqualified: false,
      disqualificationRuling: null,
      disqualificationLink: null,
      ruleViolationRuling:
        "This candidate has violated election rules on March 1, as noted in CRO Ruling #2.",
      ruleViolationLink: "http://digest.skule.ca/u/16",
    },
    {
      id: 3,
      candidateName: "Quin Sykora",
      statement:
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisinuli.",
      isDisqualified: false,
      disqualificationRuling: null,
      disqualificationLink: null,
      ruleViolationRuling: null,
      ruleViolationLink: null,
    },
    {
      id: 4,
      candidateName: "Reopen Nominations",
      statement: "Choose this option to reopen nominations.",
      isDisqualified: false,
      disqualificationRuling: null,
      disqualificationLink: null,
      ruleViolationRuling: null,
      ruleViolationLink: null,
    },
  ],
};
