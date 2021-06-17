import React from "react";
import { render, fireEvent } from "@testing-library/react";
import { useSnackbar } from "notistack";
import { CustomMessage, CustomAlert } from "components/Alerts";

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
