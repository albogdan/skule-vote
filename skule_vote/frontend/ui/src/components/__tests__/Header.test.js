import React from "react";
import { render, fireEvent } from "@testing-library/react";
import { withHistoryRouter } from "assets/testing";
import Header from "components/Header";

describe("<Header />", () => {
  it("renders Header on landing page", () => {
    const { getByText, queryByText, getByTestId } = render(
      withHistoryRouter(<Header />, "/")
    );
    expect(getByText("Skule Vote")).toBeInTheDocument();
    expect(getByTestId("darkLightModeIcon")).toBeInTheDocument();
    expect(getByText("Vote")).toBeInTheDocument();
    expect(queryByText("Check status")).not.toBeInTheDocument();
    expect(getByText("Logout")).toBeInTheDocument();
    expect(getByText("Skule Vote").closest("a")).toHaveAttribute("href", "/");
    expect(getByText("Vote").closest("a")).toHaveAttribute(
      "href",
      "/elections"
    );
  });

  it("renders Header on elections page", () => {
    const { getByText, queryByText, getByTestId } = render(
      withHistoryRouter(<Header />, "/elections")
    );
    expect(getByText("Skule Vote")).toBeInTheDocument();
    expect(getByTestId("darkLightModeIcon")).toBeInTheDocument();
    expect(queryByText("Vote")).not.toBeInTheDocument();
    expect(getByText("Check status")).toBeInTheDocument();
    expect(getByText("Logout")).toBeInTheDocument();
    expect(getByText("Skule Vote").closest("a")).toHaveAttribute("href", "/");
  });

  it("called toggleDark when the Dark/Light mode button is clicked", () => {
    const toggleDarkSpy = jest.fn();
    const isDark = true;
    const { getByText } = render(
      withHistoryRouter(
        <Header isDark={isDark} toggleDark={toggleDarkSpy} />,
        "/"
      )
    );

    let button = getByText("Light mode");
    fireEvent.click(button);
    expect(toggleDarkSpy).toHaveBeenCalled();
  });
});
