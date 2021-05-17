import React from "react";
import { render } from "@testing-library/react";
import Footer from "components/Footer";

describe("<Footer />", () => {
  it("renders footer", () => {
    const { getByText } = render(<Footer />);
    expect(getByText("This is the footer")).toBeInTheDocument();
  });
});
