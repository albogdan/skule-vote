import React from "react";
import { render, waitFor, fireEvent } from "@testing-library/react";
import { PleaseRankModal, ConfirmSpoilModal } from "components/BallotSubmodals";
import { withThemeProvider } from "assets/testing";

jest.mock("hooks/ElectionHooks");

describe("<ConfirmSpoilModal />", () => {
  it("renders ConfirmSpoilModal", () => {
    const { getByText } = render(<ConfirmSpoilModal open={true} />);

    expect(
      getByText("Are you sure you want to spoil your ballot?")
    ).toBeInTheDocument();
    expect(getByText(/Back/)).toBeInTheDocument();
    expect(getByText(/Spoil ballot/)).toBeInTheDocument();
  });

  it("confirms to spoil the ballot", async () => {
    const spoilBallotSpy = jest.fn();
    const onCloseSpy = jest.fn();
    const { findByText } = render(
      withThemeProvider(
        <ConfirmSpoilModal
          open={true}
          spoilBallot={spoilBallotSpy}
          onClose={onCloseSpy}
        />
      )
    );
    const buttonSpoil = await findByText("Spoil ballot");
    fireEvent.click(buttonSpoil);

    await waitFor(() => {
      expect(spoilBallotSpy).toHaveBeenCalled();
      expect(onCloseSpy).not.toHaveBeenCalled();
    });
  });

  it("closes the modal", async () => {
    const spoilBallotSpy = jest.fn();
    const onCloseSpy = jest.fn();
    const { findByText } = render(
      withThemeProvider(
        <ConfirmSpoilModal
          open={true}
          spoilBallot={spoilBallotSpy}
          onClose={onCloseSpy}
        />
      )
    );
    const buttonSpoil = await findByText("Back");
    fireEvent.click(buttonSpoil);

    await waitFor(() => {
      expect(spoilBallotSpy).not.toHaveBeenCalled();
      expect(onCloseSpy).toHaveBeenCalled();
    });
  });
});

describe("<PleaseRankModal />", () => {
  it("renders PleaseRankModal", () => {
    const { getByText } = render(<PleaseRankModal open={true} />);

    expect(
      getByText("You didn't rank all your choices. Would you like to go back?")
    ).toBeInTheDocument();
    expect(getByText(/No, cast my vote/)).toBeInTheDocument();
    expect(getByText(/Yes, take me back/)).toBeInTheDocument();
  });

  it("confirms to cast the ballot", async () => {
    const castBallotSpy = jest.fn();
    const onCloseSpy = jest.fn();
    const { findByText } = render(
      withThemeProvider(
        <PleaseRankModal
          open={true}
          castBallot={castBallotSpy}
          onClose={onCloseSpy}
        />
      )
    );
    const buttonSpoil = await findByText("No, cast my vote");
    fireEvent.click(buttonSpoil);

    await waitFor(() => {
      expect(castBallotSpy).toHaveBeenCalled();
      expect(onCloseSpy).not.toHaveBeenCalled();
    });
  });

  it("closes the modal", async () => {
    const castBallotSpy = jest.fn();
    const onCloseSpy = jest.fn();
    const { findByText } = render(
      withThemeProvider(
        <PleaseRankModal
          open={true}
          castBallot={castBallotSpy}
          onClose={onCloseSpy}
        />
      )
    );
    const buttonSpoil = await findByText("Yes, take me back");
    fireEvent.click(buttonSpoil);

    await waitFor(() => {
      expect(castBallotSpy).not.toHaveBeenCalled();
      expect(onCloseSpy).toHaveBeenCalled();
    });
  });
});
