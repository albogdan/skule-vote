import React from "react";
import { styled } from "@mui/system";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import { Link, useLocation } from "react-router-dom";
import Brightness6Icon from "@mui/icons-material/Brightness6";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import { useGetEligibility } from "hooks/GeneralHooks";
import { UOFT_LOGIN } from "App";
import { ReactComponent as SkuleVoteLogo } from "images/SkuleVoteLogo.svg";

const Nav = styled("div")(({ theme }) => ({
  display: "flex",
  whiteSpace: "nowrap",
  button: {
    color: "white",
    padding: "18px 15px",
    borderRadius: 0,
    fontSize: 16,
    [theme.breakpoints.down("sm")]: {
      fontSize: 14,
      padding: "16px 12px",
    },
  },
}));

const LogoWhite = styled(SkuleVoteLogo)(({ theme }) => ({
  height: 25,
  width: "auto",
  paddingTop: 3,
  marginRight: 16,
  [theme.breakpoints.down("sm")]: {
    paddingTop: 5,
  },
}));

const Header = ({ isDark, toggleDark }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const location = useLocation();
  const getEligibility = useGetEligibility();

  const darkLightModeButton = isMobile ? (
    <IconButton
      aria-label="Dark/Light mode"
      onClick={() => toggleDark()}
      data-testid="darkLightModeIcon"
      size="large"
    >
      <Brightness6Icon />
    </IconButton>
  ) : (
    <Button
      aria-label={isDark ? "Light mode" : "Dark mode"}
      startIcon={<Brightness6Icon data-testid="darkLightModeIcon" />}
      onClick={() => toggleDark()}
      variant="text"
    >
      {isDark ? "Light mode" : "Dark mode"}
    </Button>
  );

  const isLocal =
    (process?.env?.REACT_APP_DEV_SERVER_URL ?? "").includes("localhost") ||
    (process?.env?.REACT_APP_DEV_SERVER_URL ?? "").includes("127.0.0.1");

  return (
    <AppBar
      color={!isDark ? "primary" : "inherit"}
      position="sticky"
      enableColorOnDark
    >
      <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
        <Link to="/">
          <LogoWhite data-testid="skuleVoteLogo" />
        </Link>
        <Nav>
          {darkLightModeButton}
          {location.pathname === "/elections" ? (
            <Button
              aria-label="Check eligibility"
              onClick={() => getEligibility()}
              variant="text"
            >
              Check eligibility
            </Button>
          ) : (
            <nav>
              {isLocal ? (
                <Link to="/elections">
                  <Button aria-label="Vote" variant="text">
                    Vote
                  </Button>
                </Link>
              ) : (
                <a href={UOFT_LOGIN}>
                  <Button aria-label="Vote" variant="text">
                    Vote
                  </Button>
                </a>
              )}
            </nav>
          )}
        </Nav>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
