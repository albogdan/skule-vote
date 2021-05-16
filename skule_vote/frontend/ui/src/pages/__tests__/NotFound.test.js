import React from "react";
import { render } from "@testing-library/react";
import NotFound from "../NotFound";

it("renders 404 page", () => {
  const { getByText } = render(<NotFound />);
  expect(getByText("Error 404")).toBeInTheDocument();
});
