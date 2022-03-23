import React from "react";
import { render, fireEvent } from "@testing-library/react";
import ElectionsFilter, {
  ElectionsFilterDrawer,
} from "components/ElectionsFilter";
import { listOfCategories } from "pages/ElectionPage";
import { eligibleElections } from "assets/mocks";

describe("<ElectionsFilter />", () => {
  it("renders ElectionsFilter", () => {
    const { getByText } = render(
      <ElectionsFilter eligibleElections={eligibleElections} />
    );
    for (let c of Object.values(listOfCategories)) {
      expect(getByText(c)).toBeInTheDocument();
    }
    expect(getByText("Filter")).toBeInTheDocument();
  });

  it("called setAndCloseFilter when an item is clicked", () => {
    const setAndCloseFilterSpy = jest.fn();
    const { getByText } = render(
      <ElectionsFilter
        setAndCloseFilter={setAndCloseFilterSpy}
        eligibleElections={eligibleElections}
      />
    );

    const button = getByText("Officer");
    fireEvent.click(button);
    expect(setAndCloseFilterSpy).toHaveBeenCalled();
  });
});

describe("<ElectionsFilterDrawer />", () => {
  it("renders ElectionsFilterDrawer", () => {
    const { getByText } = render(
      <ElectionsFilterDrawer
        drawerOpen={true}
        eligibleElections={eligibleElections}
      />
    );
    for (let c of Object.values(listOfCategories)) {
      expect(getByText(c)).toBeInTheDocument();
    }
    expect(getByText("Filter")).toBeInTheDocument();
  });
  it("calls toggleDrawer when close icon is clicked", () => {
    const toggleDrawerSpy = jest.fn();
    const { getByTestId } = render(
      <ElectionsFilterDrawer
        toggleDrawer={toggleDrawerSpy}
        drawerOpen={true}
        eligibleElections={eligibleElections}
      />
    );
    fireEvent.click(getByTestId("drawerClose"));
    expect(toggleDrawerSpy).toHaveBeenCalled();
  });
});
