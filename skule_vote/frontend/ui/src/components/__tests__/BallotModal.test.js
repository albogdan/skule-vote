import React from "react";
import { render, waitFor, fireEvent } from "@testing-library/react";
import EnhancedBallotModal, {
  BallotModal,
  ConfirmSpoilModal,
} from "components/BallotModal";
import { useHandleSubmit } from "hooks/ElectionHooks";
import { withThemeProvider } from "assets/testing";
import { referendum, president, vp, engsciPres } from "assets/mocks";

jest.mock("hooks/ElectionHooks");

// You literally cannot see this character otherwise, it's not equivalent to ""
const zeroWidthSpace = document.createElement("div");
zeroWidthSpace.innerHTML = "&#8203;";

describe("<BallotModal />", () => {
  it("renders BallotModal for a referendum", () => {
    const {
      getByText,
      queryByText,
      getByLabelText,
      queryByLabelText,
      getByRole,
    } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          isReferendum={true}
          sortedCandidates={referendum.candidates}
          electionName={referendum.election_name}
          electionId={referendum.id}
        />
      )
    );

    expect(getByText(referendum.election_name)).toBeInTheDocument();
    expect(getByText(referendum.candidates[0].statement)).toBeInTheDocument();
    expect(queryByText("Candidates & Statements")).not.toBeInTheDocument();
    expect(getByText("Ballot")).toBeInTheDocument();
    expect(getByText(/Please select your choice/i)).toBeInTheDocument();
    expect(
      getByLabelText(/Do you support this referendum?/i)
    ).toBeInTheDocument();
    const selector = getByRole("button", {
      name: /Do you support this referendum?/i,
    });
    expect(selector.querySelector("span").innerHTML).toEqual(
      zeroWidthSpace.innerHTML
    );
    expect(
      queryByLabelText(/Do you support this candidate?/i)
    ).not.toBeInTheDocument();
    expect(queryByLabelText(/Rank/i)).not.toBeInTheDocument();
    expect(queryByText("Yes")).not.toBeInTheDocument();
    expect(queryByText("No")).not.toBeInTheDocument();
    expect(getByText("Selected Choice")).toBeInTheDocument();
    expect(queryByText("Selected Ranking")).not.toBeInTheDocument();
    expect(getByText(/Please confirm that your/i)).toBeInTheDocument();
    expect(getByText(/No choice selected/i)).toBeInTheDocument();
    expect(getByText(/Cancel/)).toBeInTheDocument();
    expect(getByText(/Spoil ballot/)).toBeInTheDocument();
    expect(getByText(/Cast ballot/).closest("button")).toBeDisabled();
  });

  it("renders BallotModal for an election with a single candidate", () => {
    const { getByText, queryByLabelText, getByLabelText, getByRole } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          isReferendum={false}
          sortedCandidates={president.candidates}
          electionName={president.election_name}
          electionId={president.id}
        />
      )
    );

    expect(getByText(president.election_name)).toBeInTheDocument();
    expect(getByText(president.candidates[0].statement)).toBeInTheDocument();
    expect(getByText("Candidates & Statements")).toBeInTheDocument();
    expect(getByText(/Please select your choice/i)).toBeInTheDocument();
    expect(
      getByLabelText(/Do you support this candidate?/i)
    ).toBeInTheDocument();
    const selector = getByRole("button", {
      name: /Do you support this candidate?/i,
    });
    expect(selector.querySelector("span").innerHTML).toEqual(
      zeroWidthSpace.innerHTML
    );
    expect(
      queryByLabelText(/Do you support this referendum?/i)
    ).not.toBeInTheDocument();
    expect(queryByLabelText(/Rank/i)).not.toBeInTheDocument();
  });

  it("renders BallotModal for an election with a multiple candidates", () => {
    const { getByText, queryByLabelText, getByLabelText, getAllByRole } =
      render(
        withThemeProvider(
          <BallotModal
            open={true}
            isReferendum={false}
            sortedCandidates={vp.candidates}
            electionName={vp.election_name}
            electionId={vp.id}
          />
        )
      );

    expect(getByText(vp.election_name)).toBeInTheDocument();
    expect(getByText("Candidates & Statements")).toBeInTheDocument();
    expect(getByText(/Please select as many/i)).toBeInTheDocument();
    for (let v of vp.candidates) {
      expect(getByText(v.name)).toBeInTheDocument();
      expect(getByText(v.statement)).toBeInTheDocument();
    }
    const selectors = getAllByRole("button", { name: /Rank/i });
    for (let s of selectors) {
      expect(s.querySelector("span").innerHTML).toEqual(
        zeroWidthSpace.innerHTML
      );
    }
    expect(getByText("Selected Ranking")).toBeInTheDocument();
    expect(
      queryByLabelText(/Do you support this candidate?/i)
    ).not.toBeInTheDocument();
    expect(
      queryByLabelText(/Do you support this referendum?/i)
    ).not.toBeInTheDocument();
    expect(getByLabelText("Rank 1")).toBeInTheDocument();
  });

  it("spoils ballot and confirms on modal", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, findByText, queryByTestId, getByTestId } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          handleSubmit={handleSubmitSpy}
          handleClose={handleCloseSpy}
          isReferendum={false}
          sortedCandidates={vp.candidates}
          electionName={vp.election_name}
          electionId={vp.id}
        />
      )
    );

    expect(getByText(vp.election_name)).toBeInTheDocument();
    expect(queryByTestId("spoilModalConfirm")).not.toBeInTheDocument();
    expect(getByText(/Cast ballot/).closest("button")).toBeDisabled();
    const buttonSpoil = await findByText("Spoil ballot");
    fireEvent.click(buttonSpoil);

    await waitFor(() => {
      expect(getByTestId("spoilModalConfirm")).toBeInTheDocument();
    });

    const buttonSpoilConfirm = getByTestId("spoilModalConfirm");
    fireEvent.click(buttonSpoilConfirm);

    await waitFor(() => {
      expect(handleSubmitSpy).toHaveBeenCalledWith(vp.id, {});
      expect(handleCloseSpy).toHaveBeenCalled();
    });
  });

  it("votes for all candidates and submits", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, getByRole, findByText, queryByTestId } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          handleSubmit={handleSubmitSpy}
          handleClose={handleCloseSpy}
          isReferendum={false}
          sortedCandidates={vp.candidates}
          electionName={vp.election_name}
          electionId={vp.id}
        />
      )
    );

    expect(getByText(vp.election_name)).toBeInTheDocument();
    expect(
      getByText(
        /Please select as many choices as you want using the dropdown menus/i
      )
    ).toBeInTheDocument();
    expect(queryByTestId("pleaseRankModalConfirm")).not.toBeInTheDocument();

    // Select Lisa, Quin, and RON
    const select1 = getByRole("button", { name: /Rank 1/i });
    fireEvent.mouseDown(select1);
    getByRole("option", { name: /Lisa Li/i }).click();
    const select2 = getByRole("button", { name: /Rank 2/i });
    fireEvent.mouseDown(select2);
    getByRole("option", { name: /Quin Sykora/i }).click();
    const select3 = getByRole("button", { name: /Rank 3/i });
    fireEvent.mouseDown(select3);
    getByRole("option", { name: /Reopen Nominations/i }).click();
    await waitFor(() => {
      expect(getByText("1. Lisa Li")).toBeInTheDocument();
      expect(getByText("2. Quin Sykora")).toBeInTheDocument();
      expect(getByText("3. Reopen Nominations")).toBeInTheDocument();
    });

    const buttonSubmit = await findByText(/Cast ballot/i);
    fireEvent.click(buttonSubmit);

    await waitFor(() => {
      expect(handleSubmitSpy).toHaveBeenCalledWith(vp.id, { 0: 0, 1: 1, 2: 2 });
      expect(handleCloseSpy).toHaveBeenCalled();
    });
  });

  it("votes for some candidates, sees 'please rank all' modal, and submits", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, getByRole, findByText, getByTestId, queryByTestId } =
      render(
        withThemeProvider(
          <BallotModal
            open={true}
            handleSubmit={handleSubmitSpy}
            handleClose={handleCloseSpy}
            isReferendum={false}
            sortedCandidates={vp.candidates}
            electionName={vp.election_name}
            electionId={vp.id}
          />
        )
      );

    expect(getByText(vp.election_name)).toBeInTheDocument();
    expect(queryByTestId("pleaseRankModalConfirm")).not.toBeInTheDocument();

    // Select Lisa and Quin
    const select1 = getByRole("button", { name: /Rank 1/i });
    fireEvent.mouseDown(select1);
    getByRole("option", { name: /Lisa Li/i }).click();
    const select2 = getByRole("button", { name: /Rank 2/i });
    fireEvent.mouseDown(select2);
    getByRole("option", { name: /Quin Sykora/i }).click();
    await waitFor(() => {
      expect(getByText("1. Lisa Li")).toBeInTheDocument();
      expect(getByText("2. Quin Sykora")).toBeInTheDocument();
    });

    const buttonSubmit = await findByText(/Cast ballot/i);
    fireEvent.click(buttonSubmit);

    await waitFor(() => {
      expect(handleSubmitSpy).not.toHaveBeenCalled();
      expect(handleCloseSpy).not.toHaveBeenCalled();
      expect(getByTestId("pleaseRankModalConfirm")).toBeInTheDocument();
    });

    const buttonPleaseRankModalConfirm = getByTestId("pleaseRankModalConfirm");
    fireEvent.click(buttonPleaseRankModalConfirm);

    await waitFor(() => {
      expect(handleSubmitSpy).toHaveBeenCalledWith(vp.id, { 0: 0, 1: 1 });
      expect(handleCloseSpy).toHaveBeenCalled();
    });
  });

  it("votes for some candidates, sees 'please rank all' modal, and goes back", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, getByRole, findByText, getByTestId, queryByTestId } =
      render(
        withThemeProvider(
          <BallotModal
            open={true}
            handleSubmit={handleSubmitSpy}
            handleClose={handleCloseSpy}
            isReferendum={false}
            sortedCandidates={vp.candidates}
            electionName={vp.election_name}
            electionId={vp.id}
          />
        )
      );

    expect(getByText(vp.election_name)).toBeInTheDocument();
    expect(queryByTestId("pleaseRankModalConfirm")).not.toBeInTheDocument();

    // Select Lisa and Quin
    const select1 = getByRole("button", { name: /Rank 1/i });
    fireEvent.mouseDown(select1);
    getByRole("option", { name: /Lisa Li/i }).click();
    const select2 = getByRole("button", { name: /Rank 2/i });
    fireEvent.mouseDown(select2);
    getByRole("option", { name: /Quin Sykora/i }).click();
    await waitFor(() => {
      expect(getByText("1. Lisa Li")).toBeInTheDocument();
      expect(getByText("2. Quin Sykora")).toBeInTheDocument();
    });

    const buttonSubmit = await findByText(/Cast ballot/i);
    fireEvent.click(buttonSubmit);

    await waitFor(() => {
      expect(handleSubmitSpy).not.toHaveBeenCalled();
      expect(handleCloseSpy).not.toHaveBeenCalled();
      expect(getByTestId("pleaseRankModalConfirm")).toBeInTheDocument();
    });

    // const buttonPleaseRankModalConfirm = getByTestId("pleaseRankModalConfirm");
    const takeMeBack = await findByText(/No, take me back/i);
    fireEvent.click(takeMeBack);

    await waitFor(() => {
      expect(handleSubmitSpy).not.toHaveBeenCalled();
      expect(handleCloseSpy).not.toHaveBeenCalled();
      expect(queryByTestId("pleaseRankModalConfirm")).not.toBeInTheDocument();
    });
  });

  it("votes for same candidate twice and renders error", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, getAllByText, getByRole, findByText } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          handleSubmit={handleSubmitSpy}
          handleClose={handleCloseSpy}
          isReferendum={false}
          sortedCandidates={vp.candidates}
          electionName={vp.election_name}
          electionId={vp.id}
        />
      )
    );

    expect(getByText(vp.election_name)).toBeInTheDocument();

    // Votes for Lisa twice
    const select1 = getByRole("button", { name: /Rank 1/i });
    fireEvent.mouseDown(select1);
    getByRole("option", { name: /Lisa Li/i }).click();
    const select2 = getByRole("button", { name: /Rank 2/i });
    fireEvent.mouseDown(select2);
    getByRole("option", { name: /Lisa Li/i }).click();

    await waitFor(() => {
      expect(getByText("1. Lisa Li")).toBeInTheDocument();
      expect(getByText("2. Lisa Li")).toBeInTheDocument();
      expect(
        getAllByText("Same candidate selected multiple times").length
      ).toBe(2);
    });

    expect(getByText(/Cast ballot/).closest("button")).toBeDisabled();
    const buttonSubmit = await findByText(/Cast ballot/i);
    fireEvent.click(buttonSubmit);

    await waitFor(() => {
      expect(handleSubmitSpy).not.toHaveBeenCalled();
      expect(handleCloseSpy).not.toHaveBeenCalled();
    });
  });

  it("votes for candidates in wrong order and renders error", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, getByRole, findByText } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          handleSubmit={handleSubmitSpy}
          handleClose={handleCloseSpy}
          isReferendum={false}
          sortedCandidates={vp.candidates}
          electionName={vp.election_name}
          electionId={vp.id}
        />
      )
    );

    expect(getByText(vp.election_name)).toBeInTheDocument();
    const select2 = getByRole("button", { name: /Rank 2/i });
    fireEvent.mouseDown(select2);
    getByRole("option", { name: /Lisa Li/i }).click();

    await waitFor(() => {
      expect(getByText("2. Lisa Li")).toBeInTheDocument();
      expect(getByText("Choices not performed in order")).toBeInTheDocument();
    });

    expect(getByText(/Cast ballot/).closest("button")).toBeDisabled();
    const buttonSubmit = await findByText(/Cast ballot/i);
    fireEvent.click(buttonSubmit);

    await waitFor(() => {
      expect(handleSubmitSpy).not.toHaveBeenCalled();
      expect(handleCloseSpy).not.toHaveBeenCalled();
    });
  });

  it("votes for election with a single candidate", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, getByRole, findByText } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          handleSubmit={handleSubmitSpy}
          handleClose={handleCloseSpy}
          isReferendum={false}
          sortedCandidates={president.candidates}
          electionName={president.election_name}
          electionId={president.id}
        />
      )
    );

    expect(getByText(president.election_name)).toBeInTheDocument();
    expect(
      getByText(/Please select your choice using the dropdown menu/i)
    ).toBeInTheDocument();
    const select1 = getByRole("button", {
      name: /Do you support this candidate?/i,
    });
    fireEvent.mouseDown(select1);
    getByRole("option", { name: "Yes" }).click();

    await waitFor(() => {
      expect(
        getByText("Do you support this candidate? Yes")
      ).toBeInTheDocument();
    });

    const select2 = getByRole("button", {
      name: /Do you support this candidate?/i,
    });
    fireEvent.mouseDown(select2);
    getByRole("option", { name: "No" }).click();

    await waitFor(() => {
      expect(
        getByText("Do you support this candidate? No")
      ).toBeInTheDocument();
    });

    const buttonSubmit = await findByText("Cast ballot");
    fireEvent.click(buttonSubmit);

    await waitFor(() => {
      expect(handleSubmitSpy).toHaveBeenCalledWith(president.id, { 0: 1 });
      expect(handleCloseSpy).toHaveBeenCalled();
    });
  });

  it("votes in a referendum", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, getByRole, findByText } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          handleSubmit={handleSubmitSpy}
          handleClose={handleCloseSpy}
          isReferendum={true}
          sortedCandidates={referendum.candidates}
          electionName={referendum.election_name}
          electionId={referendum.id}
        />
      )
    );

    expect(getByText(referendum.election_name)).toBeInTheDocument();
    expect(
      getByText(/Please select your choice using the dropdown menu/i)
    ).toBeInTheDocument();
    const select1 = getByRole("button", {
      name: /Do you support this referendum?/i,
    });
    fireEvent.mouseDown(select1);
    getByRole("option", { name: "Yes" }).click();

    await waitFor(() => {
      expect(
        getByText("Do you support this referendum? Yes")
      ).toBeInTheDocument();
    });

    const select2 = getByRole("button", {
      name: /Do you support this referendum?/i,
    });
    fireEvent.mouseDown(select2);
    getByRole("option", { name: "No" }).click();

    await waitFor(() => {
      expect(
        getByText("Do you support this referendum? No")
      ).toBeInTheDocument();
    });

    const buttonSubmit = await findByText("Cast ballot");
    fireEvent.click(buttonSubmit);

    await waitFor(() => {
      expect(handleSubmitSpy).toHaveBeenCalledWith(referendum.id, { 0: 1 });
      expect(handleCloseSpy).toHaveBeenCalled();
    });
  });

  it("renders candidate's rule violation", () => {
    vp.candidates.push({
      id: 4,
      name: "Alex Bogdan",
      statement: "Test 2",
      disqualified_status: true,
      disqualified_message: "Disqualified 1",
      disqualified_link: "http://digest.skule.ca/u/16",
    });

    const { getByText } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          isReferendum={false}
          sortedCandidates={vp.candidates}
          electionName={vp.election_name}
          electionId={vp.id}
        />
      )
    );

    expect(getByText(vp.election_name)).toBeInTheDocument();
    expect(
      getByText(vp.candidates[3].disqualified_message)
    ).toBeInTheDocument();
    expect(getByText("here").closest("a")).toHaveAttribute(
      "href",
      vp.candidates[3].disqualified_link
    );
  });

  it("renders candidate's disqualification", () => {
    vp.candidates.push({
      id: 5,
      name: "Armin Ale",
      statement: "Test 3",
      disqualified_status: false,
      rule_violation_message: "Warning 1",
      rule_violation_link: "http://digest.skule.ca/u/17",
    });

    const { getByText, getAllByText } = render(
      withThemeProvider(
        <BallotModal
          open={true}
          isReferendum={false}
          sortedCandidates={vp.candidates}
          electionName={vp.election_name}
          electionId={vp.id}
        />
      )
    );

    expect(getByText(vp.election_name)).toBeInTheDocument();
    expect(
      getByText(vp.candidates[4].rule_violation_message)
    ).toBeInTheDocument();
    expect(getAllByText("here")[1].closest("a")).toHaveAttribute(
      "href",
      vp.candidates[4].rule_violation_link
    );
  });
});

describe("<EnhancedBallotModal />", () => {
  let props;

  beforeEach(() => {
    props = {
      handleSubmit: jest.fn(),
      handleClose: jest.fn(),
      open: true,
      ballotInfo: engsciPres,
    };
    useHandleSubmit.mockImplementation(() => {
      return jest.fn();
    });
  });

  it("renders EnhancedBallotModal", () => {
    const {
      getByText,
      queryByText,
      getByLabelText,
      queryByLabelText,
      getByRole,
    } = render(withThemeProvider(<EnhancedBallotModal {...props} />));

    expect(getByText(engsciPres.election_name)).toBeInTheDocument();
    expect(getByText(engsciPres.candidates[0].statement)).toBeInTheDocument();
    expect(queryByText("Candidates & Statements")).toBeInTheDocument();
    expect(getByText("Ballot")).toBeInTheDocument();
    expect(getByText(/Please select your choice/i)).toBeInTheDocument();
    expect(
      getByLabelText(/Do you support this candidate?/i)
    ).toBeInTheDocument();
    const selector = getByRole("button", {
      name: /Do you support this candidate?/i,
    });
    expect(selector.querySelector("span").innerHTML).toEqual(
      zeroWidthSpace.innerHTML
    );
    expect(queryByLabelText(/Rank/i)).not.toBeInTheDocument();
    expect(queryByText("Yes")).not.toBeInTheDocument();
    expect(queryByText("No")).not.toBeInTheDocument();
    expect(queryByText("Reopen Nominations")).not.toBeInTheDocument();
    expect(getByText("Selected Choice")).toBeInTheDocument();
    expect(queryByText("Selected Ranking")).not.toBeInTheDocument();
    expect(getByText(/Please confirm that your/i)).toBeInTheDocument();
    expect(getByText(/No choice selected/i)).toBeInTheDocument();
    expect(getByText(/Cancel/)).toBeInTheDocument();
    expect(getByText(/Spoil ballot/)).toBeInTheDocument();
    expect(getByText(/Cast ballot/).closest("button")).toBeDisabled();
  });
});
