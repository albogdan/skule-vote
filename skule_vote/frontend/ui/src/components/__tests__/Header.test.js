import React from "react";
import { render, fireEvent } from "@testing-library/react";
import Header from "components/Header";
import { withRouter } from "assets/testing";

describe("<Header />", () => {
  it("renders header with nav bar", () => {
    const { getByText, getByTestId } = render(withRouter(<Header />));
    expect(getByText("Skule Vote")).toBeInTheDocument();
    expect(getByTestId("darkLightModeIcon")).toBeInTheDocument();
    expect(getByText("Vote")).toBeInTheDocument();
    expect(getByText("Check status")).toBeInTheDocument();
    expect(getByText("Logout")).toBeInTheDocument();
    expect(getByText("Skule Vote").closest("a")).toHaveAttribute("href", "/");
    expect(getByText("Vote").closest("a")).toHaveAttribute(
      "href",
      "/elections"
    );
  });

  it("called toggleDark when the Dark/Light mode button is clicked", () => {
    const toggleDarkSpy = jest.fn();
    const isDark = true;
    const { getByText } = render(
      withRouter(<Header isDark={isDark} toggleDark={toggleDarkSpy} />)
    );

    let button = getByText("Light mode");
    fireEvent.click(button);
    expect(toggleDarkSpy).toHaveBeenCalled();
  });
});
