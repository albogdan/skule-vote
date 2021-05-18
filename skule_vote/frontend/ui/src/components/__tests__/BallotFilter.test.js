import React from "react";
import { render, fireEvent } from "@testing-library/react";
import BallotFilter from "components/BallotFilter";
import { listOfCategories } from "pages/ElectionPage";

describe("<BallotFilter />", () => {
  it("renders BallotFilter", () => {
    const { getByText } = render(<BallotFilter />);
    for (let c of listOfCategories) {
      expect(getByText(c)).toBeInTheDocument();
    }
    expect(getByText("Filter")).toBeInTheDocument();
  });

  it("called setFilterCategory when an item is clicked", () => {
    const setFilterCategorySpy = jest.fn();
    const { getByText } = render(
      <BallotFilter setFilterCategory={setFilterCategorySpy} />
    );

    const button = getByText("Officers");
    fireEvent.click(button);
    expect(setFilterCategorySpy).toHaveBeenCalled();
  });
});
