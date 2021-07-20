import React from "react";
import { render, waitFor } from "@testing-library/react";
import ElectionPage from "pages/ElectionPage";
import {
  useGetElectionSession,
  useGetEligibleElections,
} from "hooks/ElectionHooks";
import { readableDate } from "pages/ElectionPage";
import { withSnackbarProvider } from "assets/testing";
import { electionSession, eligibleElections } from "assets/mocks";

jest.mock("hooks/ElectionHooks");

describe("<ElectionPage />", () => {
  let startTimeStr;
  let endTimeStr;

  beforeEach(() => {
    [, startTimeStr] = readableDate(electionSession.start_time);
    [, endTimeStr] = readableDate(electionSession.end_time);
    const getElectionSession = jest.fn(() => electionSession);
    const getEligibleElections = jest.fn(() => eligibleElections);
    useGetElectionSession.mockImplementation(() => {
      return getElectionSession;
    });
    useGetEligibleElections.mockImplementation(() => {
      return getEligibleElections;
    });
  });

  it("renders election page with ballots during an election session", async () => {
    jest
      .spyOn(Date, "now")
      .mockImplementation(() => Date.parse("2021-06-13T00:00:00-04:00")); // June 13, 2021

    const { getByText, getAllByText } = render(
      withSnackbarProvider(<ElectionPage />)
    );

    expect(getByText("Elections")).toBeInTheDocument();
    expect(getAllByText("Filter")).toHaveLength(2);
    expect(getByText("Selected Filter: All")).toBeInTheDocument();
    await waitFor(() => {
      for (let e of Object.values(eligibleElections)) {
        expect(getByText(e.election_name)).toBeInTheDocument();
      }
    });
  });

  it("renders election page with no ballots when there is no active election session", async () => {
    jest
      .spyOn(Date, "now")
      .mockImplementation(() => Date.parse("2021-06-10T00:00:00-04:00")); // June 10, 2021
    const getEligibleElections = jest.fn(() => {});
    useGetEligibleElections.mockImplementation(() => {
      return getEligibleElections;
    });

    const { getByText, queryByText, getAllByText } = render(
      withSnackbarProvider(<ElectionPage />)
    );

    expect(getByText("Elections")).toBeInTheDocument();
    expect(getAllByText("Filter")).toHaveLength(2);
    expect(getByText("Selected Filter: All")).toBeInTheDocument();
    await waitFor(() => {
      expect(
        getByText(
          "There are no elections that you are currently eligible to vote in."
        )
      ).toBeInTheDocument();
      for (let e of Object.values(eligibleElections)) {
        expect(queryByText(e.election_name)).not.toBeInTheDocument();
      }
    });
  });

  it("renders <Messages /> regarding election end time", async () => {
    jest
      .spyOn(Date, "now")
      .mockImplementation(() => Date.parse("2021-06-13T00:00:00-04:00")); // June 13, 2021

    const { getByText } = render(withSnackbarProvider(<ElectionPage />));

    await waitFor(() => {
      expect(
        getByText(`Elections close on ${endTimeStr}.`)
      ).toBeInTheDocument();
    });
  });

  it("renders <Messages /> regarding upcoming election start time", async () => {
    jest
      .spyOn(Date, "now")
      .mockImplementation(() => Date.parse("2021-06-10T00:00:00-04:00")); // June 10, 2021

    const { getByText } = render(withSnackbarProvider(<ElectionPage />));
    await waitFor(() => {
      expect(
        getByText(`There's an upcoming election starting on ${startTimeStr}.`)
      ).toBeInTheDocument();
    });
  });
});
