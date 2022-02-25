import React from "react";
import { BrowserRouter } from "react-router-dom";
import { SnackbarProvider } from "notistack";
import { ThemeProvider, createTheme } from "@mui/material/styles";

export const withRouter = (component, route = null) => {
  if (route) {
    window.history.pushState({}, "", route);
  }

  return <BrowserRouter>{component}</BrowserRouter>;
};

export const withSnackbarProvider = (component) => (
  <SnackbarProvider>{component}</SnackbarProvider>
);

export const withThemeProvider = (component) => {
  const theme = createTheme({});
  return <ThemeProvider theme={theme}>{component}</ThemeProvider>;
};
