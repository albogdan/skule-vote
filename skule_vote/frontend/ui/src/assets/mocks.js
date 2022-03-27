// Use these for BallotModal
export const referendum = {
  election_name: "Referedum 1",
  id: 0,
  category: "referenda",
  candidates: [
    {
      id: 0,
      name: "Referendum 1",
      statement: "Test",
    },
    {
      id: 1,
      name: "No",
      statement: null,
    },
  ],
};

export const president = {
  election_name: "President",
  id: 1,
  category: "officer",
  candidates: [
    {
      id: 0,
      name: "Lisa Li",
      statement: "Test.",
    },
    {
      id: 1,
      name: "No",
      statement: null,
    },
  ],
};

export const vp = {
  election_name: "VP Finance",
  id: 3,
  category: "officer",
  candidates: [
    {
      id: 0,
      name: "Lisa Li",
      statement: "Test 1",
      disqualified_status: false,
    },
    {
      id: 1,
      name: "Quin Sykora",
      statement: "Test 2",
      disqualified_status: false,
    },
    {
      id: 2,
      name: "Reopen Nominations",
      statement: "Choose this option to reopen nominations.",
      disqualified_status: false,
    },
  ],
};

// Use these for EnhancedBallotModal
export const engsciPres = {
  election_name: "Engsci Club President",
  id: 1,
  category: "officer",
  candidates: [
    {
      id: 0,
      name: "Lisa Li",
      statement: "Test.",
    },
    {
      id: 1,
      name: "Reopen Nominations",
      statement: "Choose this option to reopen nominations.",
    },
  ],
};

export const electionSession = {
  election_session_name: "Test",
  start_time: "2021-06-12T00:00:00-04:00", // June 12, 2021
  end_time: "2021-06-14T00:00:00-04:00", // June 14, 2021
};
export const eligibleElections = {
  10: {
    election_name: "Referedum 1",
    seats_available: 0,
    id: 10,
    category: "referenda",
    candidates: [
      {
        id: 0,
        name: "Referendum 1",
        statement: "Vote pls",
        disqualified_status: false,
      },
      {
        id: 1,
        name: "Reopen Nominations",
        statement: "Choose this option to reopen nominations.",
        disqualified_status: false,
      },
    ],
  },
  12: {
    election_name: "President",
    seats_available: 2,
    id: 12,
    category: "Officer",
    candidates: [
      {
        id: 2,
        name: "Reopen Nominations",
        statement: "Choose this option to reopen nominations.",
        disqualified_status: false,
      },
      {
        id: 3,
        name: "James Holden",
        statement: "My name is James.",
        disqualified_status: false,
      },
    ],
  },
};
