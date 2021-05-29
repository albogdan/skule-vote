import React from "react";
import { render, fireEvent } from "@testing-library/react";
import { CustomAlert } from "components/Alerts";

describe("<CustomAlert />", () => {
  it("renders CustomAlert", () => {
    const msg = "Your vote has successfully been cast";
    const { getByText, queryByTestId } = render(
      <CustomAlert message={msg} type="info" />
    );
    expect(getByText(msg)).toBeInTheDocument();
    expect(queryByTestId("closeAlert")).not.toBeInTheDocument();
  });

  it("renders nothing if type is not info, sucess, error, or warning", () => {
    const msg = "Your vote has successfully been cast";
    const { queryByText, queryByTestId } = render(
      <CustomAlert message={msg} type="blah" />
    );
    expect(queryByText(msg)).not.toBeInTheDocument();
    expect(queryByTestId("closeAlert")).not.toBeInTheDocument();
  });

  it("renders close icon and called actionSpy if pressed", () => {
    const actionSpy = jest.fn();
    const msg = "Your vote has successfully been cast";
    const { getByTestId } = render(
      <CustomAlert message={msg} type="error" action={actionSpy} />
    );
    fireEvent.click(getByTestId("closeAlert"));
    expect(actionSpy).toHaveBeenCalled();
  });
});
