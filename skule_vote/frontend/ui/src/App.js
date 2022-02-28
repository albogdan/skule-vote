import React from "react";
import { styled } from "@mui/system";
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
import { useLocalStorage } from "hooks/GeneralHooks";
import GillSansLight from "fonts/gill-sans-light.otf";
import GillSans from "fonts/gill-sans.otf";
import GillSansMed from "fonts/gill-sans-medium.otf";

const AppWrapper = styled("div")(({ theme }) => ({
  minHeight: "100vh",
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  "*": {
    boxSizing: "border-box",
  },
  a: {
    textDecoration: "none",
    color:
      theme.palette.mode === "dark"
        ? theme.palette.secondary.main
        : theme.palette.primary.main,
  },
}));

const AppBody = styled("div")(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  maxWidth: 1200,
  margin: "auto",
  padding: "0 32px",
  [theme.breakpoints.down("md")]: {
    padding: "0 16px",
  },
  [theme.breakpoints.down("sm")]: {
    padding: "0 12px",
  },
}));

export const UOFT_LOGIN =
  "https://portal.engineering.utoronto.ca/weblogin/sites/apsc/vote.asp";

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
            "Gill Sans Custom",
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
          MuiCssBaseline: {
            styleOverrides: `
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

            `,
          },
          MuiButton: {
            defaultProps: {
              disableElevation: true,
              variant: "contained",
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
          <AppWrapper>
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
