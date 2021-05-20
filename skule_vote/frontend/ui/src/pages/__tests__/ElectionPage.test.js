import React from "react";
import { render } from "@testing-library/react";
import ElectionPage from "pages/ElectionPage";
import { mockElections } from "assets/mocks";

describe("<ElectionPage />", () => {
  it("renders election page", () => {
    const { getByText, getAllByText } = render(
      <ElectionPage listOfElections={mockElections} />
    );
    expect(getByText("Elections")).toBeInTheDocument();
    expect(getAllByText("Filter")).toHaveLength(2);
    expect(getByText("Selected Filter: All")).toBeInTheDocument();
    for (let e of mockElections) {
      expect(getByText(e.electionName)).toBeInTheDocument();
    }
  });
});
