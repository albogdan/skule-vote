import React from "react";
import styled from "styled-components";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import { Link } from "react-router-dom";
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
`;

const Nav = styled.div`
  display: flex;
  white-space: nowrap;
  button {
    color: white;
    padding: 20px 15px;
    border-radius: 0;
    @media ${responsive.smDown} {
      padding: 16px 12px;
    }
  }
  a {
    text-decoration: none;
  }
`;

const FlexToolbar = styled(Toolbar)`
  display: flex;
  justify-content: space-between;
`;

const Header = ({ isDark, toggleDark }) => {
  const isMobile = useMediaQuery(responsive.smDown);
  const darkLightModeButton = isMobile ? (
    <IconButton aria-label="Dark/Light mode" onClick={() => toggleDark()}>
      <Brightness6Icon />
    </IconButton>
  ) : (
    <Button
      aria-label={isDark ? "Light mode" : "Dark mode"}
      startIcon={<Brightness6Icon />}
      onClick={() => toggleDark()}
    >
      {isDark ? "Light mode" : "Dark mode"}
    </Button>
  );

  return (
    <AppBar color={!isDark ? "primary" : "inherit"} position="sticky">
      <FlexToolbar>
        <SkuleVote>Skule Vote</SkuleVote>
        <Nav>
          {darkLightModeButton}
          <nav>
            <Link to={"/what-ever-login-is"}>
              <Button aria-label="Vote">Vote</Button>
            </Link>
          </nav>
          <Button aria-label="Check status">Check status</Button>
          <Button aria-label="Logout">Logout</Button>
        </Nav>
      </FlexToolbar>
    </AppBar>
  );
};

export default Header;
