import React from "react";
import { render } from "@testing-library/react";
import ElectionPage from "../ElectionPage";

it("renders election page", () => {
  const { getByText } = render(<ElectionPage />);
  expect(getByText("Election Page")).toBeInTheDocument();
});
