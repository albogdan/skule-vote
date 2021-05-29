import React from "react";
import { render, waitFor, fireEvent } from "@testing-library/react";
import { BallotModal } from "components/BallotModal";

const referenda = {
  electionName: "Referedum 1",
  electionId: 0,
  category: "Referenda",
  candidates: [
    {
      id: 0,
      candidateName: "Referendum 1",
      statement: "Test",
    },
    {
      id: 1,
      candidateName: "No",
      statement: null,
    },
  ],
};

const president = {
  electionName: "President",
  electionId: 1,
  category: "Officer",
  candidates: [
    {
      id: 0,
      candidateName: "Lisa Li",
      statement: "Test.",
    },
    {
      id: 1,
      candidateName: "No",
      statement: null,
    },
  ],
};

const vp = {
  electionName: "VP Finance",
  electionId: 3,
  category: "Officer",
  candidates: [
    {
      id: 0,
      candidateName: "Lisa Li",
      statement: "Test 1",
      isDisqualified: false,
    },
    {
      id: 1,
      candidateName: "Quin Sykora",
      statement: "Test 2",
      isDisqualified: false,
    },
    {
      id: 2,
      candidateName: "Reopen Nominations",
      statement: "Choose this option to reopen nominations.",
      isDisqualified: false,
    },
  ],
};

describe("<BallotModal />", () => {
  it("renders BallotModal for a referendum", () => {
    const { getByText, queryByText, getByLabelText, queryByLabelText } = render(
      <BallotModal
        open={true}
        isReferendum={true}
        sortedCandidates={referenda.candidates}
        electionName={referenda.electionName}
        electionId={referenda.electionId}
      />
    );

    expect(getByText(referenda.electionName)).toBeInTheDocument();
    expect(getByText(referenda.candidates[0].statement)).toBeInTheDocument();
    expect(getByText("Ballot")).toBeInTheDocument();
    expect(getByText(/Please select as many/i)).toBeInTheDocument();
    expect(
      getByLabelText(/Do you support this referendum?/i)
    ).toBeInTheDocument();
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
    const { getByText, queryByLabelText, getByLabelText } = render(
      <BallotModal
        open={true}
        isReferendum={false}
        sortedCandidates={president.candidates}
        electionName={president.electionName}
        electionId={president.electionId}
      />
    );

    expect(getByText(president.electionName)).toBeInTheDocument();
    expect(getByText(president.candidates[0].statement)).toBeInTheDocument();
    expect(
      getByLabelText(/Do you support this candidate?/i)
    ).toBeInTheDocument();
    expect(
      queryByLabelText(/Do you support this referendum?/i)
    ).not.toBeInTheDocument();
    expect(queryByLabelText(/Rank/i)).not.toBeInTheDocument();
  });

  it("renders BallotModal for an election with a multiple candidates", () => {
    const { getByText, queryByLabelText, getByLabelText } = render(
      <BallotModal
        open={true}
        isReferendum={false}
        sortedCandidates={vp.candidates}
        electionName={vp.electionName}
        electionId={vp.electionId}
      />
    );

    expect(getByText(vp.electionName)).toBeInTheDocument();
    for (let v of vp.candidates) {
      expect(getByText(v.candidateName)).toBeInTheDocument();
      expect(getByText(v.statement)).toBeInTheDocument();
    }
    expect(
      queryByLabelText(/Do you support this candidate?/i)
    ).not.toBeInTheDocument();
    expect(
      queryByLabelText(/Do you support this referendum?/i)
    ).not.toBeInTheDocument();
    expect(getByLabelText("Rank 1")).toBeInTheDocument();
  });

  it("spoils ballot", async () => {
    const handleSubmitSpy = jest.fn();
    const handleCloseSpy = jest.fn();
    const { getByText, findByText } = render(
      <BallotModal
        open={true}
        handleSubmit={handleSubmitSpy}
        handleClose={handleCloseSpy}
        isReferendum={false}
        sortedCandidates={vp.candidates}
        electionName={vp.electionName}
        electionId={vp.electionId}
      />
    );

    expect(getByText(vp.electionName)).toBeInTheDocument();
    expect(getByText(/Cast ballot/).closest("button")).toBeDisabled();
    const buttonSpoil = await findByText("Spoil ballot");
    fireEvent.click(buttonSpoil);

    await waitFor(() => {
      expect(handleSubmitSpy).toHaveBeenCalledWith({
        electionId: vp.electionId,
        ranking: {},
      });
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
        electionName={vp.electionName}
        electionId={vp.electionId}
      />
    );

    expect(getByText(vp.electionName)).toBeInTheDocument();

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

    expect(getByText(/Spoil ballot/).closest("button")).toBeDisabled();
    const buttonSubmit = await findByText(/Cast ballot/i);
    fireEvent.click(buttonSubmit);

    await waitFor(() => {
      expect(handleSubmitSpy).toHaveBeenCalledWith({
        electionId: vp.electionId,
        ranking: {
          0: 0,
          1: 1,
        },
      });
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
        electionName={vp.electionName}
        electionId={vp.electionId}
      />
    );

    expect(getByText(vp.electionName)).toBeInTheDocument();

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

    expect(getByText(/Spoil ballot/).closest("button")).toBeDisabled();
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
    const { getByText, getAllByText, getByRole, findByText } = render(
      <BallotModal
        open={true}
        handleSubmit={handleSubmitSpy}
        handleClose={handleCloseSpy}
        isReferendum={false}
        sortedCandidates={vp.candidates}
        electionName={vp.electionName}
        electionId={vp.electionId}
      />
    );

    expect(getByText(vp.electionName)).toBeInTheDocument();

    const select1 = getByRole("button", { name: /Rank 1/i });
    fireEvent.mouseDown(select1);
    // getByRole("option", { name: "-" }).click();
    const select2 = getByRole("button", { name: /Rank 3/i });
    fireEvent.mouseDown(select2);
    getByRole("option", { name: /Lisa Li/i }).click();

    await waitFor(() => {
      expect(getByText("2. Lisa Li")).toBeInTheDocument();
      expect(getByText("Choices not performed in order")).toBeInTheDocument();
    });

    expect(getByText(/Spoil ballot/).closest("button")).toBeDisabled();
    expect(getByText(/Cast ballot/).closest("button")).toBeDisabled();
    const buttonSubmit = await findByText(/Cast ballot/i);
    fireEvent.click(buttonSubmit);

    await waitFor(() => {
      expect(handleSubmitSpy).not.toHaveBeenCalled();
      expect(handleCloseSpy).not.toHaveBeenCalled();
    });
  });

  // it("renders candidate's rule violation", () => {
  //   vp.candidates.push({
  //     id: 4,
  //     candidateName: "Alex Bogdan",
  //     statement: "Test 2",
  //     isDisqualified: true,
  //     disqualificationRuling: "Disqualified 1",
  //     disqualificationLink: "http://digest.skule.ca/u/16",
  //   });

  //   const { getByText } = render(
  //     <BallotModal
  //       open={true}
  //       isReferendum={false}
  //       sortedCandidates={vp.candidates}
  //       electionName={vp.electionName}
  //       electionId={vp.electionId}
  //     />
  //   );

  //   expect(getByText(vp.electionName)).toBeInTheDocument();
  //   expect(
  //     getByText(vp.candidates[3].disqualificationRuling)
  //   ).toBeInTheDocument();
  //   expect(getByText("here").closest("a")).toHaveAttribute(
  //     "href",
  //     vp.candidates[3].disqualificationLink
  //   );
  // });

  // it("renders candidate's disqualification", () => {
  //   vp.candidates.push({
  //     id: 5,
  //     candidateName: "Armin Ale",
  //     statement: "Test 3",
  //     isDisqualified: false,
  //     ruleViolationRuling: "Warning 1",
  //     ruleViolationLink: "http://digest.skule.ca/u/17",
  //   });

  //   const { getByText, getAllByText } = render(
  //     <BallotModal
  //       open={true}
  //       isReferendum={false}
  //       sortedCandidates={vp.candidates}
  //       electionName={vp.electionName}
  //       electionId={vp.electionId}
  //     />
  //   );

  //   expect(getByText(vp.electionName)).toBeInTheDocument();
  //   expect(getByText(vp.candidates[4].ruleViolationRuling)).toBeInTheDocument();
  //   expect(getAllByText("here")[1].closest("a")).toHaveAttribute(
  //     "href",
  //     vp.candidates[4].ruleViolationLink
  //   );
  // });
});
