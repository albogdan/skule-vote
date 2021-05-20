import React from "react";
import { render } from "@testing-library/react";
import ElectionCard, { NoElectionsCard } from "components/ElectionCard";

describe("<ElectionCard />", () => {
  it("renders ElectionCard with given position and >1 number of candidates", () => {
    const title = "VP Student Life";
    const numCandidates = 3;

    const { getByText } = render(
      <ElectionCard title={title} numCandidates={numCandidates} />
    );
    expect(getByText(title)).toBeInTheDocument();
    expect(getByText(`${numCandidates} Candidates`)).toBeInTheDocument();
  });

  it("renders ElectionCard with given position and 1 candidate", () => {
    const title = "VP Communications";
    const numCandidates = 1;

    const { getByText } = render(
      <ElectionCard title={title} numCandidates={numCandidates} />
    );
    expect(getByText(title)).toBeInTheDocument();
    expect(getByText(`${numCandidates} Candidate`)).toBeInTheDocument();
  });

  it("renders ElectionCard with given referenda", () => {
    const title = "Referenda 1";
    const numCandidates = 0;

    const { getByText, queryByText } = render(
      <ElectionCard title={title} numCandidates={numCandidates} />
    );
    expect(getByText(title)).toBeInTheDocument();
    expect(queryByText(/Candidate/i)).not.toBeInTheDocument();
  });
});

describe("<NoElectionsCard />", () => {
  it("renders NoElectionsCard message if filterCategory is All", () => {
    const { getByText } = render(<NoElectionsCard filterCategory="All" />);
    expect(
      getByText(
        "There are no elections that you are currently eligible to vote in."
      )
    ).toBeInTheDocument();
  });

  it("renders NoElectionsCard message if filterCategory is Referenda", () => {
    const { getByText } = render(
      <NoElectionsCard filterCategory="Referenda" />
    );
    expect(
      getByText(
        "There are no Referenda that you are currently eligible to vote in."
      )
    ).toBeInTheDocument();
  });

  it("renders NoElectionsCard message if filterCategory is any other type of election", () => {
    const { getByText } = render(<NoElectionsCard filterCategory="Officer" />);
    expect(
      getByText(
        "There are no Officer elections that you are currently eligible to vote in."
      )
    ).toBeInTheDocument();
  });
});
