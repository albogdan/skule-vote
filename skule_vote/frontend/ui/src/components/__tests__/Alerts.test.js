import React from "react";
import { render, fireEvent } from "@testing-library/react";
import { useSnackbar } from "notistack";
import {
  CustomMessage,
  CustomAlert,
  BallotRulingAlert,
} from "components/Alerts";

jest.mock("notistack", () => ({
  ...jest.requireActual("notistack"),
  useSnackbar: jest.fn(),
}));

describe("<CustomAlert />", () => {
  const msg = "Your vote has successfully been cast";
  const id = 1;

  it("renders CustomAlert", () => {
    const closeSnackbar = jest.fn();
    useSnackbar.mockImplementation(() => ({ closeSnackbar }));

    const { getByText, queryByTestId } = render(
      <CustomAlert id={id} options={{ message: msg, variant: "info" }} />
    );
    expect(getByText(msg)).toBeInTheDocument();
    expect(queryByTestId("closeAlert")).toBeInTheDocument();
  });

  it("renders nothing if type is not info, sucess, error, or warning", () => {
    const closeSnackbar = jest.fn();
    useSnackbar.mockImplementation(() => ({ closeSnackbar }));

    const { queryByText, queryByTestId } = render(
      <CustomAlert id={id} options={{ message: msg, variant: "blah" }} />
    );
    expect(queryByText(msg)).not.toBeInTheDocument();
    expect(queryByTestId("closeAlert")).not.toBeInTheDocument();
  });

  it("calls closeSnackbar to close itself", async () => {
    const closeSnackbar = jest.fn();
    useSnackbar.mockImplementation(() => ({ closeSnackbar }));

    const { getByTestId, getByText } = render(
      <CustomAlert id={id} options={{ message: msg, variant: "error" }} />
    );
    expect(getByText(msg)).toBeInTheDocument();
    fireEvent.click(getByTestId("closeAlert"));

    expect(closeSnackbar).toHaveBeenCalledWith(id);
  });
});

describe("<CustomMessage />", () => {
  const msg = "Your vote has successfully been cast";
  it("renders CustomMessage", () => {
    const { getByText } = render(
      <CustomMessage message={msg} variant="info" />
    );
    expect(getByText(msg)).toBeInTheDocument();
  });

  it("renders nothing if variant is not info, sucess, error, or warning", () => {
    const { queryByText } = render(
      <CustomMessage message={msg} variant="blah" />
    );
    expect(queryByText(msg)).not.toBeInTheDocument();
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
