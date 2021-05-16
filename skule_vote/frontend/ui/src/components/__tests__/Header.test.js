import React from "react";
import { render } from "@testing-library/react";
import Header from "components/Header";

describe("<Header />", () => {
  it("renders header with nav bar", () => {
    const { getByText } = render(<Header />);
    expect(getByText("Skule Vote")).toBeInTheDocument();
    expect(getByText("Vote")).toBeInTheDocument();
    expect(getByText("Check status")).toBeInTheDocument();
    expect(getByText("Logout")).toBeInTheDocument();
  });
});
