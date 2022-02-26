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
  let theme = createTheme({});

  theme = {
    ...theme,
    palette: {
      ...theme.palette,
      purple: {
        main: "#DCD1DD",
        contrastText: "#424242",
      },
    },
  };
  return <ThemeProvider theme={theme}>{component}</ThemeProvider>;
};
