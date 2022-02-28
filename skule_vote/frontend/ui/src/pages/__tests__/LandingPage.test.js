import React from "react";
import { render } from "@testing-library/react";
import { withRouter } from "assets/testing";
import LandingPage from "../LandingPage";

describe("<LandingPage />", () => {
  const OLD_ENV = process.env;

  beforeEach(() => {
    jest.resetModules(); // Clears the cache
    process.env = { ...OLD_ENV }; // Make a copy
  });

  afterAll(() => {
    process.env = OLD_ENV; // Restore old environment
  });

  it("renders landing page on local", () => {
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

  it("renders landing page on prod", () => {
    process.env.REACT_APP_DEV_SERVER_URL = "not local";
    const { getByText, getByTestId } = render(withRouter(<LandingPage />));
    expect(getByText("Welcome to SkuleVote")).toBeInTheDocument();
    expect(getByText("Election Details")).toBeInTheDocument();
    expect(getByText(/Single Transferable Vote system/i)).toBeInTheDocument();
    expect(getByTestId("skuleLogo")).toBeInTheDocument();
    expect(getByText("Vote").closest("a")).toHaveAttribute(
      "href",
      "https://portal.engineering.utoronto.ca/weblogin/sites/apsc/vote.asp"
    );
  });
});
