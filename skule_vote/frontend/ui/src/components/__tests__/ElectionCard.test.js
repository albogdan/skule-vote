import React from "react";
import { render } from "@testing-library/react";
import ElectionCard, { NoElectionsCard } from "components/ElectionCard";
import { withThemeProvider } from "assets/testing";

describe("<ElectionCard />", () => {
  it("renders ElectionCard with given position and >1 number of seats available", () => {
    const title = "VP Student Life";
    const seatsAvailable = 3;
    const numCandidates = 4;
    const category = "officer";

    const { getByText } = render(
      withThemeProvider(
        <ElectionCard
          title={title}
          seatsAvailable={seatsAvailable}
          numCandidates={numCandidates}
          category={category}
        />
      )
    );

    expect(getByText(title)).toBeInTheDocument();
    expect(getByText(/3 positions to be filled/i)).toBeInTheDocument();
    expect(getByText(/3 candidates/)).toBeInTheDocument();
  });

  it("renders ElectionCard with given position and 1 seat available", () => {
    const title = "VP Communications";
    const seatsAvailable = 1;
    const numCandidates = 2; // 2 because the other candidate is ron
    const category = "officer";

    const { getByText } = render(
      withThemeProvider(
        <ElectionCard
          title={title}
          seatsAvailable={seatsAvailable}
          numCandidates={numCandidates}
          category={category}
        />
      )
    );
    expect(getByText(title)).toBeInTheDocument();
    expect(getByText(/1 position to be filled/i)).toBeInTheDocument();
    expect(getByText(/1 candidate/i)).toBeInTheDocument();
  });

  it("renders ElectionCard with given referenda", () => {
    const title = "Referenda 1";
    const seatsAvailable = 1;
    const numCandidates = 2;
    const category = "referenda";

    const { getByText, queryByText } = render(
      withThemeProvider(
        <ElectionCard
          title={title}
          seatsAvailable={seatsAvailable}
          numCandidates={numCandidates}
          category={category}
        />
      )
    );
    expect(getByText(title)).toBeInTheDocument();
    expect(queryByText(/available/i)).not.toBeInTheDocument();
    expect(queryByText(/candidate/i)).not.toBeInTheDocument();
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
