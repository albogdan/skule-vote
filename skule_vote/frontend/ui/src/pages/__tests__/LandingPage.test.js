import React from "react";
import { render } from "@testing-library/react";
import { withRouter } from "assets/testing";
import LandingPage from "../LandingPage";

describe("<LandingPage />", () => {
  it("renders landing page", () => {
    const { getByText, getByTestId } = render(withRouter(<LandingPage />));
    expect(getByText("Welcome to SkuleVote")).toBeInTheDocument();
    expect(getByText("Election Details")).toBeInTheDocument();
    expect(getByText(/Single Transferable Vote system/i)).toBeInTheDocument();
    expect(getByTestId("skuleLogo")).toBeInTheDocument();
    expect(getByText("Vote").closest("a")).toHaveAttribute(
      "href",
      "/elections"
    );
  });
});
