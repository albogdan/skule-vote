import React from "react";
import styled from "styled-components";
import { SnackbarProvider } from "notistack";
import CssBaseline from "@mui/material/CssBaseline";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import { Route, BrowserRouter, Routes, Navigate } from "react-router-dom";
import ElectionPage from "pages/ElectionPage";
import LandingPage from "pages/LandingPage";
import { CustomAlert } from "components/Alerts";
import Footer from "components/Footer";
import Header from "components/Header";
import { responsive } from "assets/breakpoints";
import { useLocalStorage } from "hooks/GeneralHooks";
import GillSansLight from "fonts/gill-sans-light.otf";
import GillSans from "fonts/gill-sans.otf";
import GillSansMed from "fonts/gill-sans-medium.otf";

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
      props.$isDark
        ? props.palette.secondary.main
        : props.palette.primary.main};
  }

  @font-face {
    font-family: "Gill Sans Custom";
    src: url(${GillSansLight}) format("opentype");
    font-weight: 300;
    font-style: normal;
  }

  @font-face {
    font-family: "Gill Sans Custom";
    src: url(${GillSans}) format("opentype");
    font-weight: 400;
    font-style: normal;
  }

  @font-face {
    font-family: "Gill Sans Custom";
    src: url(${GillSansMed}) format("opentype");
    font-weight: 500;
    font-style: normal;
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
      createTheme({
        typography: {
          fontFamily: [
            "Gill Sans Custon",
            "Gill Sans",
            "Gill Sans MT",
            "Lato",
            "sans-serif",
          ].join(","),
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
            fontWeight: 500,
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
        components: {
          MuiButton: {
            defaultProps: {
              disableElevation: true,
            },
            styleOverrides: {
              root: {
                fontSize: 18,
                fontWeight: 300,
                "@media (max-width:600px)": {
                  fontSize: 16,
                },
              },
              sizeLarge: {
                fontSize: 20,
                "@media (max-width:600px)": {
                  fontSize: 18,
                },
              },
            },
            variants: [
              {
                props: { variant: "filter" },
                style: {
                  padding: `12px 24px`,
                  justifyContent: "flex-start",
                  borderRadius: 0,
                  textTransform: "capitalize",
                },
              },
            ],
          },
          MuiDrawer: {
            styleOverrides: {
              root: {
                "& .MuiDrawer-paper": {
                  backgroundImage: "none",
                },
              },
            },
          },
        },
        palette: {
          mode: isDark ? "dark" : "light",
          primary: {
            main: "#3B739E",
          },
          secondary: {
            main: isDark ? "#C8EDFF" : "#3B6482",
          },
          purple: {
            main: isDark ? "#DCD1DD" : "#4D33A3",
            contrastText: isDark ? "#424242" : "#FFFFFF",
          },
          background: {
            default: isDark ? "#212121 !important" : "#EFEFEF !important",
            paper: isDark ? "#424242" : "#FFFFFF",
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
          <AppWrapper palette={theme.palette} $isDark={isDark}>
            <div>
              <Header isDark={isDark} toggleDark={toggleDark} />
              <AppBody>
                <Routes>
                  <Route exact path="/" element={<LandingPage />} />
                  <Route exact path="/elections" element={<ElectionPage />} />
                  <Route path="*" element={<Navigate to="/" />} />
                </Routes>
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
