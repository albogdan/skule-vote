import React from "react";
import { render, fireEvent } from "@testing-library/react";
import ElectionsFilter, {
  ElectionsFilterDrawer,
} from "components/ElectionsFilter";
import { listOfCategories } from "pages/ElectionPage";

describe("<ElectionsFilter />", () => {
  it("renders ElectionsFilter", () => {
    const { getByText } = render(<ElectionsFilter />);
    for (let c of listOfCategories) {
      expect(getByText(c)).toBeInTheDocument();
    }
    expect(getByText("Filter")).toBeInTheDocument();
  });

  it("called setAndCloseFilter when an item is clicked", () => {
    const setAndCloseFilterSpy = jest.fn();
    const { getByText } = render(
      <ElectionsFilter setAndCloseFilter={setAndCloseFilterSpy} />
    );

    const button = getByText("Officer");
    fireEvent.click(button);
    expect(setAndCloseFilterSpy).toHaveBeenCalled();
  });
});

describe("<ElectionsFilterDrawer />", () => {
  it("renders ElectionsFilterDrawer", () => {
    const { getByText } = render(<ElectionsFilterDrawer drawerOpen={true} />);
    for (let c of listOfCategories) {
      expect(getByText(c)).toBeInTheDocument();
    }
    expect(getByText("Filter")).toBeInTheDocument();
  });
  it("calls toggleDrawer when close icon is clicked", () => {
    const toggleDrawerSpy = jest.fn();
    const { getByTestId } = render(
      <ElectionsFilterDrawer toggleDrawer={toggleDrawerSpy} drawerOpen={true} />
    );
    fireEvent.click(getByTestId("drawerClose"));
    expect(toggleDrawerSpy).toHaveBeenCalled();
  });
});
