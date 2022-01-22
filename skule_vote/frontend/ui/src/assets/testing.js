import React from "react";
import { BrowserRouter } from "react-router-dom";
import { SnackbarProvider } from "notistack";

export const withRouter = (component, route = null) => {
  if (route) {
    window.history.pushState({}, "", route);
  }

  return <BrowserRouter>{component}</BrowserRouter>;
};

export const withSnackbarProvider = (component) => (
  <SnackbarProvider>{component}</SnackbarProvider>
);
