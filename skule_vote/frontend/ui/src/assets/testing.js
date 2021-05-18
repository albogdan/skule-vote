import React from "react";
import { BrowserRouter, Router } from "react-router-dom";
import { createMemoryHistory } from "history";

export const withRouter = (component) => (
  <BrowserRouter>{component}</BrowserRouter>
);

export const withHistoryRouter = (component, route) => {
  const history = createMemoryHistory();
  history.push(route);
  return <Router history={history}>{component}</Router>;
};
