import React, { useState } from "react";
import styled from "styled-components";
import CssBaseline from "@material-ui/core/CssBaseline";
import { createMuiTheme, withStyles } from "@material-ui/core/styles";
import { ThemeProvider } from "@material-ui/styles";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import { Route, BrowserRouter, Redirect, Switch } from "react-router-dom";
import ElectionPage from "pages/ElectionPage";
import LandingPage from "pages/LandingPage";
import NotFound from "pages/NotFound";
import Footer from "components/Footer";
import Header from "components/Header";

const AppWrapper = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  * {
    box-sizing: border-box;
  }
`;

const AppBody = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 1200px;
  margin: auto;
  padding: 0 32px;
`;

const App = () => {
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");
  const [darkState, setDarkState] = useState(prefersDarkMode);
  const toggleDark = () => {
    setDarkState(!darkState);
  };

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
            fontWeight: 300,
            "@media (max-width:600px)": {
              fontSize: 24,
            },
          },
          body1: {
            fontSize: 16,
            fontWeight: 300,
            "@media (max-width:600px)": {
              fontSize: 14,
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
          background: {
            default: darkState ? "#212121 !important" : "#EFEFEF !important",
          },
        },
      }),
    [darkState]
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AppWrapper>
          <div>
            <Header isDark={darkState} toggleDark={toggleDark} />
            <AppBody>
              <Switch>
                <Route exact path="/" component={LandingPage} />
                <Route exact path="/elections" component={ElectionPage} />
                <Route exact path="/404" component={NotFound} />
                <Redirect to="/404" />
              </Switch>
            </AppBody>
          </div>
          <Footer />
        </AppWrapper>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
