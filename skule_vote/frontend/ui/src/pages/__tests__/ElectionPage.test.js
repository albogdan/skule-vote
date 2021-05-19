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
    expect(getAllByText(/Filter/i)).toHaveLength(3);
    for (let e of mockElections) {
      expect(getByText(e.electionName)).toBeInTheDocument();
    }
  });
});
