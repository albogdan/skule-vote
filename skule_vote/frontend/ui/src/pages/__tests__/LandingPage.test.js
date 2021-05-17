import React from "react";
import { render } from "@testing-library/react";
import LandingPage from "../LandingPage";

describe("<LandingPage />", () => {
  it("renders landing page", () => {
    const { getByText } = render(<LandingPage />);
    expect(getByText("Welcome to SkuleVote")).toBeInTheDocument();
  });
});
