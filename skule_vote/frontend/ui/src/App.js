import React from "react";
import styled from "styled-components";
import { SnackbarProvider } from "notistack";
import CssBaseline from "@material-ui/core/CssBaseline";
import { createMuiTheme } from "@material-ui/core/styles";
import { ThemeProvider } from "@material-ui/styles";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import { Route, BrowserRouter, Redirect, Switch } from "react-router-dom";
import ElectionPage from "pages/ElectionPage";
import LandingPage from "pages/LandingPage";
import { CustomAlert } from "components/Alerts";
import Footer from "components/Footer";
import Header from "components/Header";
import { responsive } from "assets/breakpoints";
import { useLocalStorage } from "assets/hooks";

const AppWrapper = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  * {
    box-sizing: border-box;
  }
  a {
    text-decoration: none;
    color: ${(props) =>
      props.isDark
        ? props.theme.palette.secondary.main
        : props.theme.palette.primary.main};
  }
`;

const AppBody = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 1200px;
  margin: auto;
  padding: 0 32px;
  @media ${responsive.mdDown} {
    padding: 0 16px;
  }
  @media ${responsive.smDown} {
    padding: 0 12px;
  }
`;

const App = () => {
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");
  const [isDark, setIsDark] = useLocalStorage(
    "prefersDarkMode",
    prefersDarkMode
  );
  const toggleDark = () => {
    setIsDark(!isDark);
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
            fontSize: 24,
            fontWeight: 300,
            "@media (max-width:600px)": {
              fontSize: 24,
            },
          },
          h3: {
            fontSize: 20,
            fontWeight: 400,
            "@media (max-width:600px)": {
              fontSize: 18,
            },
          },
          body1: {
            fontSize: 18,
            fontWeight: 300,
            "@media (max-width:600px)": {
              fontSize: 16,
            },
          },
          body2: {
            fontSize: 18,
            fontWeight: 400,
            "@media (max-width:600px)": {
              fontSize: 16,
            },
          },
        },
        overrides: {
          MuiButton: {
            root: {
              fontSize: 18,
              fontWeight: 300,
              "@media (max-width:600px)": {
                fontSize: 16,
              },
            },
          },
        },
        palette: {
          type: isDark ? "dark" : "light",
          primary: {
            main: "#3B739E",
          },
          secondary: {
            main: isDark ? "#C8EDFF" : "#3B6482",
          },
          background: {
            default: isDark ? "#212121 !important" : "#EFEFEF !important",
          },
        },
      }),
    [isDark]
  );

  return (
    <ThemeProvider theme={theme}>
      <SnackbarProvider
        content={(key, message) => <CustomAlert id={key} options={message} />}
      >
        <CssBaseline />
        <BrowserRouter>
          <AppWrapper theme={theme} isDark={isDark}>
            <div>
              <Header isDark={isDark} toggleDark={toggleDark} />
              <AppBody>
                <Switch>
                  <Route exact path="/" component={LandingPage} />
                  <Route exact path="/elections" component={ElectionPage} />
                  <Redirect to="/" />
                </Switch>
              </AppBody>
            </div>
            <Footer isDark={isDark} />
          </AppWrapper>
        </BrowserRouter>
      </SnackbarProvider>
    </ThemeProvider>
  );
};

export default App;
