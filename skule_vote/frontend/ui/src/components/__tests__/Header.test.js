import React from "react";
import { render, fireEvent } from "@testing-library/react";
import { withRouter } from "assets/testing";
import Header from "components/Header";
import { useGetEligibility } from "hooks/GeneralHooks";

jest.mock("notistack", () => ({
  useSnackbar: () => ({ enqueueSnackbar: jest.fn() }),
}));

jest.mock("hooks/GeneralHooks", () => ({
  useGetEligibility: jest.fn(() => jest.fn()),
}));

describe("<Header />", () => {
  const OLD_ENV = process.env;

  beforeEach(() => {
    jest.resetModules(); // Clears the cache
    process.env = { ...OLD_ENV }; // Make a copy
  });

  afterAll(() => {
    process.env = OLD_ENV; // Restore old environment
  });

  it("renders Header on landing page on local", () => {
    process.env.REACT_APP_DEV_SERVER_URL = "http://localhost:8000";
    const { getByText, queryByText, getByTestId } = render(
      withRouter(<Header />, "/")
    );
    expect(getByTestId("skuleVoteLogo")).toBeInTheDocument();
    expect(getByTestId("darkLightModeIcon")).toBeInTheDocument();
    expect(getByText("Vote")).toBeInTheDocument();
    expect(queryByText("Check eligibility")).not.toBeInTheDocument();
    expect(getByTestId("skuleVoteLogo").closest("a")).toHaveAttribute(
      "href",
      "/"
    );
    expect(getByText("Vote").closest("a")).toHaveAttribute(
      "href",
      "/elections"
    );
  });

  it("renders Header on landing page on prod", () => {
    process.env.REACT_APP_DEV_SERVER_URL = "vote.skule.ca";
    const { getByText, queryByText, getByTestId } = render(
      withRouter(<Header />, "/")
    );
    expect(getByTestId("skuleVoteLogo")).toBeInTheDocument();
    expect(getByTestId("darkLightModeIcon")).toBeInTheDocument();
    expect(getByText("Vote")).toBeInTheDocument();
    expect(queryByText("Check eligibility")).not.toBeInTheDocument();
    expect(getByTestId("skuleVoteLogo").closest("a")).toHaveAttribute(
      "href",
      "/"
    );
    expect(getByText("Vote").closest("a")).toHaveAttribute(
      "href",
      "https://portal.engineering.utoronto.ca/weblogin/sites/apsc/vote.asp"
    );
  });

  it("renders Header on elections page", () => {
    const { getByText, queryByText, getByTestId } = render(
      withRouter(<Header />, "/elections")
    );
    expect(getByTestId("skuleVoteLogo")).toBeInTheDocument();
    expect(getByTestId("darkLightModeIcon")).toBeInTheDocument();
    expect(queryByText("Vote")).not.toBeInTheDocument();
    expect(getByText("Check eligibility")).toBeInTheDocument();
    expect(getByTestId("skuleVoteLogo").closest("a")).toHaveAttribute(
      "href",
      "/"
    );
  });

  it("calls toggleDark when the Dark/Light mode button is clicked", () => {
    const toggleDarkSpy = jest.fn();
    const isDark = true;
    const { getByText } = render(
      withRouter(<Header isDark={isDark} toggleDark={toggleDarkSpy} />, "/")
    );

    let button = getByText("Light mode");
    fireEvent.click(button);
    expect(toggleDarkSpy).toHaveBeenCalled();
  });

  it("calls getEligibility when the Check eligibility button is clicked", () => {
    const getEligibility = jest.fn();
    useGetEligibility.mockImplementation(() => {
      return getEligibility;
    });

    const { getByText } = render(withRouter(<Header />, "/elections"));

    let button = getByText("Check eligibility");
    fireEvent.click(button);
    expect(getEligibility).toHaveBeenCalled();
  });
});
