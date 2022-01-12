import React from "react";
import { render, waitFor, fireEvent } from "@testing-library/react";
import EnhancedBallotModal, {
  BallotModal,
  ConfirmSpoilModal,
  BallotRulingAlert,
} from "components/BallotModal";
import { useHandleSubmit } from "hooks/ElectionHooks";
import { referendum, president, vp, engsciPres } from "assets/mocks";

jest.mock("hooks/ElectionHooks");

describe("<BallotModal />", () => {
  it("renders BallotModal for a referendum", () => {
    const {
      getByText,
      queryByText,
      getByLabelText,
      queryByLabelText,
      getByRole,
    } = render(
      <BallotModal
        open={true}
        isReferendum={true}
        sortedCandidates={referendum.candidates}
        electionName={referendum.election_name}
        electionId={referendum.id}
      />
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
    expect(selector.querySelector("span").innerHTML).toEqual("​");
    expect(
      queryByLabelText(/Do you support this candidate?/i)
    ).not.toBeInTheDocument();
    expect(queryByLabelText(/Rank/i)).not.toBeInTheDocument();
    expect(queryByText("Yes")).not.toBeInTheDocument();
    expect(queryByText("No")).not.toBeInTheDocument();
    expect(getByText("Selected Ranking")).toBeInTheDocument();
    expect(getByText(/Please confirm that your/i)).toBeInTheDocument();
    expect(getByText(/No choice selected/i)).toBeInTheDocument();
    expect(getByText(/Cancel/)).toBeInTheDocument();
    expect(getByText(/Spoil ballot/)).toBeInTheDocument();
    expect(getByText(/Cast ballot/).closest("button")).toBeDisabled();
  });

  it("renders BallotModal for an election with a single candidate", () => {
    const { getByText, queryByLabelText, getByLabelText, getByRole } = render(
      <BallotModal
        open={true}
        isReferendum={false}
        sortedCandidates={president.candidates}
        electionName={president.election_name}
        electionId={president.id}
      />
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
    expect(selector.querySelector("span").innerHTML).toEqual("​");
    expect(
      queryByLabelText(/Do you support this referendum?/i)
    ).not.toBeInTheDocument();
    expect(queryByLabelText(/Rank/i)).not.toBeInTheDocument();
  });

  it("renders BallotModal for an election with a multiple candidates", () => {
    const { getByText, queryByLabelText, getByLabelText, getAllByRole } =
      render(
        <BallotModal
          open={true}
          isReferendum={false}
          sortedCandidates={vp.candidates}
          electionName={vp.election_name}
          electionId={vp.id}
        />
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
      expect(s.querySelector("span").innerHTML).toEqual("​");
    }
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
      <BallotModal
        open={true}
        handleSubmit={handleSubmitSpy}
        handleClose={handleCloseSpy}
        isReferendum={false}
        sortedCandidates={vp.candidates}
        electionName={vp.election_name}
        electionId={vp.id}
      />
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

  it("votes for candidates and submits", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, getByRole, findByText } = render(
      <BallotModal
        open={true}
        handleSubmit={handleSubmitSpy}
        handleClose={handleCloseSpy}
        isReferendum={false}
        sortedCandidates={vp.candidates}
        electionName={vp.election_name}
        electionId={vp.id}
      />
    );

    expect(getByText(vp.election_name)).toBeInTheDocument();

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
      expect(handleSubmitSpy).toHaveBeenCalledWith(vp.id, { 0: 0, 1: 1 });
      expect(handleCloseSpy).toHaveBeenCalled();
    });
  });

  it("votes for same candidate twice and renders error", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, getAllByText, getByRole, findByText } = render(
      <BallotModal
        open={true}
        handleSubmit={handleSubmitSpy}
        handleClose={handleCloseSpy}
        isReferendum={false}
        sortedCandidates={vp.candidates}
        electionName={vp.election_name}
        electionId={vp.id}
      />
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
      <BallotModal
        open={true}
        handleSubmit={handleSubmitSpy}
        handleClose={handleCloseSpy}
        isReferendum={false}
        sortedCandidates={vp.candidates}
        electionName={vp.election_name}
        electionId={vp.id}
      />
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
      <BallotModal
        open={true}
        handleSubmit={handleSubmitSpy}
        handleClose={handleCloseSpy}
        isReferendum={false}
        sortedCandidates={president.candidates}
        electionName={president.election_name}
        electionId={president.id}
      />
    );

    expect(getByText(president.election_name)).toBeInTheDocument();
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
      <BallotModal
        open={true}
        handleSubmit={handleSubmitSpy}
        handleClose={handleCloseSpy}
        isReferendum={true}
        sortedCandidates={referendum.candidates}
        electionName={referendum.election_name}
        electionId={referendum.id}
      />
    );

    expect(getByText(referendum.election_name)).toBeInTheDocument();
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
      <BallotModal
        open={true}
        isReferendum={false}
        sortedCandidates={vp.candidates}
        electionName={vp.election_name}
        electionId={vp.id}
      />
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
      <BallotModal
        open={true}
        isReferendum={false}
        sortedCandidates={vp.candidates}
        electionName={vp.election_name}
        electionId={vp.id}
      />
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

describe("<ConfirmSpoilModal />", () => {
  it("renders ConfirmSpoilModal", () => {
    const { getByText } = render(<ConfirmSpoilModal open={true} />);

    expect(
      getByText("Are you sure you want to spoil your ballot?")
    ).toBeInTheDocument();
    expect(getByText(/Cancel/)).toBeInTheDocument();
    expect(getByText(/Spoil ballot/)).toBeInTheDocument();
  });

  it("confirms to spoil the ballot", async () => {
    const spoilBallotSpy = jest.fn();
    const onCloseSpy = jest.fn();
    const { findByText } = render(
      <ConfirmSpoilModal
        open={true}
        spoilBallot={spoilBallotSpy}
        onClose={onCloseSpy}
      />
    );

    const buttonSpoil = await findByText("Spoil ballot");
    fireEvent.click(buttonSpoil);

    await waitFor(() => {
      expect(spoilBallotSpy).toHaveBeenCalled();
      expect(onCloseSpy).not.toHaveBeenCalled();
    });
  });

  it("cancels the modal", async () => {
    const spoilBallotSpy = jest.fn();
    const onCloseSpy = jest.fn();
    const { findByText } = render(
      <ConfirmSpoilModal
        open={true}
        spoilBallot={spoilBallotSpy}
        onClose={onCloseSpy}
      />
    );

    const buttonSpoil = await findByText("Cancel");
    fireEvent.click(buttonSpoil);

    await waitFor(() => {
      expect(spoilBallotSpy).not.toHaveBeenCalled();
      expect(onCloseSpy).toHaveBeenCalled();
    });
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
    } = render(<EnhancedBallotModal {...props} />);

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
    expect(selector.querySelector("span").innerHTML).toEqual("​");
    expect(queryByLabelText(/Rank/i)).not.toBeInTheDocument();
    expect(queryByText("Yes")).not.toBeInTheDocument();
    expect(queryByText("No")).not.toBeInTheDocument();
    expect(queryByText("Reopen Nominations")).not.toBeInTheDocument();
    expect(getByText("Selected Ranking")).toBeInTheDocument();
    expect(getByText(/Please confirm that your/i)).toBeInTheDocument();
    expect(getByText(/No choice selected/i)).toBeInTheDocument();
    expect(getByText(/Cancel/)).toBeInTheDocument();
    expect(getByText(/Spoil ballot/)).toBeInTheDocument();
    expect(getByText(/Cast ballot/).closest("button")).toBeDisabled();
  });

  it("renders null if ballotInfo is null", () => {
    const modifiedProps = {
      ...props,
      ballotInfo: null,
    };

    const { container } = render(<EnhancedBallotModal {...modifiedProps} />);
    expect(container.innerHTML).toBe("");
  });
});

describe("<BallotRulingAlert />", () => {
  it("renders period because ruling does not end with one and link is included", () => {
    const { getByTestId } = render(
      <BallotRulingAlert ruling="This guy is bad   " link="www.link.com" />
    );

    expect(getByTestId("ballotRulingAlert").textContent).toEqual(
      "This guy is bad. Please read the ruling here."
    );
  });

  it("doesnt render period because link is not included", () => {
    const { getByTestId } = render(
      <BallotRulingAlert ruling="  This guy is bad" link="" />
    );

    expect(getByTestId("ballotRulingAlert").textContent).toEqual(
      "This guy is bad"
    );
  });

  it("doesnt render extra period because ruling ends with one when link is included", () => {
    const { getByTestId } = render(
      <BallotRulingAlert ruling="This guy is bad. " link="www.link.com" />
    );

    expect(getByTestId("ballotRulingAlert").textContent).toEqual(
      "This guy is bad. Please read the ruling here."
    );
  });

  it("doesnt render extra period because ruling ends with one when link isnt included", () => {
    const { getByTestId } = render(
      <BallotRulingAlert ruling="This guy is bad. " link="" />
    );

    expect(getByTestId("ballotRulingAlert").textContent).toEqual(
      "This guy is bad."
    );
  });

  it("renders disqualified default message because there's no ruling message", () => {
    const { getByTestId } = render(
      <BallotRulingAlert ruling="" link="www.link.com" isDQ />
    );

    expect(getByTestId("ballotRulingAlert").textContent).toEqual(
      "This candidate has been disqualified. Please read the ruling here."
    );
  });

  it("renders disqualified default message if props are empty strings", () => {
    const { getByText } = render(<BallotRulingAlert ruling="" link="" isDQ />);

    expect(
      getByText(
        "This candidate has been disqualified. Contact EngSoc for more information."
      )
    ).toBeInTheDocument();
  });

  it("renders rule violation default message because there's no ruling message", () => {
    const { getByTestId } = render(
      <BallotRulingAlert ruling="" link="www.link.com" />
    );

    expect(getByTestId("ballotRulingAlert").textContent).toEqual(
      "This candidate violated a rule. Please read the ruling here."
    );
  });

  it("renders rule violation default message if props are empty strings", () => {
    const { getByText } = render(<BallotRulingAlert ruling="" link="" />);

    expect(
      getByText(
        "This candidate violated a rule. Contact EngSoc for more information."
      )
    ).toBeInTheDocument();
  });
});
