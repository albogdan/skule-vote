import React from "react";
import styled from "styled-components";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import { Link, useLocation } from "react-router-dom";
import Brightness6Icon from "@mui/icons-material/Brightness6";
import useMediaQuery from "@mui/material/useMediaQuery";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import { useGetEligibility } from "hooks/GeneralHooks";
import { ReactComponent as SkuleVoteLogo } from "images/SkuleVoteLogo.svg";
import { responsive } from "assets/breakpoints";

const Nav = styled.div`
  display: flex;
  white-space: nowrap;
  button {
    color: white;
    padding: 18px 15px;
    border-radius: 0;
    font-size: 16px;
    @media ${responsive.smDown} {
      font-size: 14px;
      padding: 16px 12px;
    }
  }
`;

const LogoWhite = styled(SkuleVoteLogo)`
  height: 25px;
  width: auto;
  padding-top: 3px;
  margin-right: 16px;
  @media ${responsive.smDown} {
    padding-top: 5px;
  }
`;

const Header = ({ isDark, toggleDark }) => {
  const isMobile = useMediaQuery(responsive.smDown);
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
              <a href="https://portal.engineering.utoronto.ca/weblogin/sites/apsc/vote.asp">
                <Button aria-label="Vote" variant="text">
                  Vote
                </Button>
              </a>
            </nav>
          )}
        </Nav>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
