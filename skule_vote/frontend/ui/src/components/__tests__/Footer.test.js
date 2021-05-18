import React from "react";
import { render } from "@testing-library/react";
import { withHistoryRouter } from "assets/testing";
import Footer from "components/Footer";

describe("<Footer />", () => {
  it("renders landing footer with white crest on dark mode", () => {
    const { getByText, getByTestId, queryByTestId } = render(
      withHistoryRouter(<Footer isDark={true} />, "/")
    );
    expect(
      getByText("University of Toronto Engineering Society")
    ).toBeInTheDocument();
    expect(getByText(/This website was designed/)).toBeInTheDocument();
    expect(getByTestId("whiteCrest")).toBeInTheDocument();
    expect(queryByTestId("blackCrest")).not.toBeInTheDocument();
  });

  it("renders landing footer with black crest on light mode", () => {
    const { getByText, getByTestId, queryByTestId } = render(
      withHistoryRouter(<Footer isDark={false} />, "/")
    );
    expect(
      getByText("University of Toronto Engineering Society")
    ).toBeInTheDocument();
    expect(getByText(/This website was designed/)).toBeInTheDocument();
    expect(getByTestId("blackCrest")).toBeInTheDocument();
    expect(queryByTestId("whiteCrest")).not.toBeInTheDocument();
  });

  it("renders small footer", () => {
    const { getByText, queryByText } = render(
      withHistoryRouter(<Footer />, "/elections")
    );
    expect(
      queryByText("University of Toronto Engineering Society")
    ).not.toBeInTheDocument();
    expect(queryByText(/This website was designed/)).not.toBeInTheDocument();
    expect(getByText(/By continuing to use/)).toBeInTheDocument();
  });
});
