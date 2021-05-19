import React from "react";
import { render, fireEvent } from "@testing-library/react";
import BallotFilter, { BallotFilterDrawer } from "components/BallotFilter";
import { listOfCategories } from "pages/ElectionPage";

describe("<BallotFilter />", () => {
  it("renders BallotFilter", () => {
    const { getByText } = render(<BallotFilter />);
    for (let c of listOfCategories) {
      expect(getByText(c)).toBeInTheDocument();
    }
    expect(getByText("Filter")).toBeInTheDocument();
  });

  it("called setAndCloseFilter when an item is clicked", () => {
    const setAndCloseFilterSpy = jest.fn();
    const { getByText } = render(
      <BallotFilter setAndCloseFilter={setAndCloseFilterSpy} />
    );

    const button = getByText("Officer");
    fireEvent.click(button);
    expect(setAndCloseFilterSpy).toHaveBeenCalled();
  });
});

describe("<BallotFilterDrawer />", () => {
  it("renders BallotFilterDrawer", () => {
    const { getByText } = render(<BallotFilterDrawer drawerOpen={true} />);
    for (let c of listOfCategories) {
      expect(getByText(c)).toBeInTheDocument();
    }
    expect(getByText("Filter")).toBeInTheDocument();
  });
  it("calls toggleDrawer when close icon is clicked", () => {
    const toggleDrawerSpy = jest.fn();
    const { getByTestId } = render(
      <BallotFilterDrawer toggleDrawer={toggleDrawerSpy} drawerOpen={true} />
    );
    fireEvent.click(getByTestId("drawerClose"));
    expect(toggleDrawerSpy).toHaveBeenCalled();
  });
});
