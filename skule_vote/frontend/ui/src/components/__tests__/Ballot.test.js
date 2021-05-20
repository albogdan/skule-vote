import React from "react";
import { render } from "@testing-library/react";
import Ballot, { NoBallot } from "components/Ballot";

describe("<Ballot />", () => {
  it("renders Ballot with given position and >1 number of candidates", () => {
    const title = "VP Student Life";
    const numCandidates = 3;

    const { getByText } = render(
      <Ballot title={title} numCandidates={numCandidates} />
    );
    expect(getByText(title)).toBeInTheDocument();
    expect(getByText(`${numCandidates} Candidates`)).toBeInTheDocument();
  });

  it("renders Ballot with given position and 1 candidate", () => {
    const title = "VP Communications";
    const numCandidates = 1;

    const { getByText } = render(
      <Ballot title={title} numCandidates={numCandidates} />
    );
    expect(getByText(title)).toBeInTheDocument();
    expect(getByText(`${numCandidates} Candidate`)).toBeInTheDocument();
  });

  it("renders Ballot with given referenda", () => {
    const title = "Referenda 1";
    const numCandidates = 0;

    const { getByText, queryByText } = render(
      <Ballot title={title} numCandidates={numCandidates} />
    );
    expect(getByText(title)).toBeInTheDocument();
    expect(queryByText(/Candidate/i)).not.toBeInTheDocument();
  });
});

describe("<NoBallot />", () => {
  it("renders NoBallot message if filterCategory is All", () => {
    const { getByText } = render(<NoBallot filterCategory="All" />);
    expect(
      getByText(
        "There are no elections that you are currently eligible to vote in."
      )
    ).toBeInTheDocument();
  });

  it("renders NoBallot message if filterCategory is Referenda", () => {
    const { getByText } = render(<NoBallot filterCategory="Referenda" />);
    expect(
      getByText(
        "There are no Referenda that you are currently eligible to vote in."
      )
    ).toBeInTheDocument();
  });

  it("renders NoBallot message if filterCategory is any other type of election", () => {
    const { getByText } = render(<NoBallot filterCategory="Officer" />);
    expect(
      getByText(
        "There are no Officer elections that you are currently eligible to vote in."
      )
    ).toBeInTheDocument();
  });
});
