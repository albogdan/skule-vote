import React from "react";
import { render } from "@testing-library/react";
import ElectionPage from "pages/ElectionPage";
import { mockElections } from "assets/mocks";

describe("<ElectionPage />", () => {
  it("renders election page", () => {
    const { getByText } = render(
      <ElectionPage listOfElections={mockElections} />
    );
    expect(getByText("Elections")).toBeInTheDocument();
    expect(getByText("Filter")).toBeInTheDocument();
    for (let e of mockElections) {
      expect(getByText(e.electionName)).toBeInTheDocument();
    }
  });
});
