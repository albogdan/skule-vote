import React from "react";
import { render } from "@testing-library/react";
import ElectionPage from "pages/ElectionPage";
import { useSnackbar } from "notistack";
import { mockElections } from "assets/mocks";

jest.mock("notistack", () => ({
  ...jest.requireActual("notistack"),
  useSnackbar: jest.fn(),
}));

describe("<ElectionPage />", () => {
  it("renders election page", () => {
    const enqueueSnackbar = jest.fn();
    useSnackbar.mockImplementation(() => ({ enqueueSnackbar }));

    const { getByText, getAllByText } = render(
      <ElectionPage listOfElections={mockElections} />
    );
    expect(getByText("Elections")).toBeInTheDocument();
    expect(getAllByText("Filter")).toHaveLength(2);
    expect(getByText("Selected Filter: All")).toBeInTheDocument();
    for (let e of mockElections) {
      expect(getByText(e.electionName)).toBeInTheDocument();
    }
  });
});
