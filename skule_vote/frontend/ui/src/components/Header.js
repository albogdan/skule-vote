import React from "react";
import styled from "styled-components";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import { Link, useLocation } from "react-router-dom";
import Brightness6Icon from "@material-ui/icons/Brightness6";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import Button from "@material-ui/core/Button";
import IconButton from "@material-ui/core/IconButton";
import { responsive } from "assets/breakpoints";

const SkuleVote = styled.h1`
  font-weight: 600;
  font-size: 16px;
  white-space: nowrap;
  margin-right: 16px;
  color: white;
`;

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

const FlexToolbar = styled(Toolbar)`
  display: flex;
  justify-content: space-between;
`;

const Header = ({ isDark, toggleDark }) => {
  const isMobile = useMediaQuery(responsive.smDown);
  const location = useLocation();

  const darkLightModeButton = isMobile ? (
    <IconButton
      aria-label="Dark/Light mode"
      onClick={() => toggleDark()}
      data-testid="darkLightModeIcon"
    >
      <Brightness6Icon />
    </IconButton>
  ) : (
    <Button
      aria-label={isDark ? "Light mode" : "Dark mode"}
      startIcon={<Brightness6Icon data-testid="darkLightModeIcon" />}
      onClick={() => toggleDark()}
    >
      {isDark ? "Light mode" : "Dark mode"}
    </Button>
  );

  return (
    <AppBar color={!isDark ? "primary" : "inherit"} position="sticky">
      <FlexToolbar>
        <Link to={"/"}>
          <SkuleVote>Skule Vote</SkuleVote>
        </Link>
        <Nav>
          {darkLightModeButton}
          {location.pathname === "/elections" ? (
            <Button aria-label="Check status">Check status</Button>
          ) : (
            <nav>
              <Link to={"/elections"}>
                <Button aria-label="Vote">Vote</Button>
              </Link>
            </nav>
          )}
          <Button aria-label="Logout">Logout</Button>
        </Nav>
      </FlexToolbar>
    </AppBar>
  );
};

export default Header;
