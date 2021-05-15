import React, { useState } from "react";
import { createMuiTheme, withStyles } from "@material-ui/core/styles";
import { ThemeProvider } from "@material-ui/styles";
import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import useMediaQuery from "@material-ui/core/useMediaQuery";

const AppPaper = withStyles({
  root: {
    minHeight: "100vh",
  },
})(Paper);

const App = () => {
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");
  const [darkState, setDarkState] = useState(prefersDarkMode);

  const theme = React.useMemo(
    () =>
      createMuiTheme({
        typography: {
          fontFamily: `"Gill Sans", "Gill Sans MT", "Lato", sans-serif`,

          h1: {
            fontSize: 45,
            fontWeight: 300,
            "@media (max-width:600px)": {
              fontSize: 32,
            },
          },
          h2: {
            fontSize: 32,
            fontWeight: 500,
            "@media (max-width:600px)": {
              fontSize: 24,
            },
          },
          body1: {
            fontSize: 20,
            fontWeight: 300,
            "@media (max-width:600px)": {
              fontSize: 16,
            },
          },
        },
        palette: {
          type: darkState ? "dark" : "light",
          primary: {
            main: "#3B739E",
          },
          secondary: {
            main: darkState ? "#C8EDFF" : "#3B6482",
          },
          error: {
            main: "#980606",
          },
          warning: {
            main: "#AC5403",
          },
          success: {
            main: "#207250",
          },
          info: {
            main: "#3B6482",
          },
        },
      }),
    [darkState]
  );

  return (
    <ThemeProvider theme={theme}>
      <AppPaper square={true}>
        <header>Skule Vote</header>

        <div
          style={{
            maxWidth: "500px",
            margin: "auto",
            marginTop: 100,
            padding: 50,
          }}
        >
          <Typography variant="h1">h1: This is a dark mode test</Typography>
          <Typography variant="h2">h2: Font should shrink on mobile</Typography>
          <Typography variant="body1">body1: WEEEEE</Typography>
          <Button
            color="primary"
            variant="contained"
            onClick={() => setDarkState(!darkState)}
          >
            Use this to toggle dark mode
          </Button>
          <Button color="secondary" variant="contained">
            This color should change
          </Button>
        </div>
      </AppPaper>
    </ThemeProvider>
  );
};

export default App;
