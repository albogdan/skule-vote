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
  color: white;
`;

const Nav = styled.div`
  display: flex;
  white-space: nowrap;
`;

const NavBtn = styled(Button)`
  font-size: 14px;
  color: white;
  padding: 20px 15px;
  border-radius: 0;
  @media ${responsive.smDown} {
    padding: 16px 12px;
  }
`;

const FlexToolbar = styled(Toolbar)`
  display: flex;
  justify-content: space-between;
`;

const Header = ({ isDark, toggleDark }) => {
  const isMobile = useMediaQuery(responsive.smDown);
  const darkLightModeButton = isMobile ? (
    <IconButton
      aria-label="Dark/Light mode"
      onClick={() => toggleDark()}
      data-testid="darkLightModeIcon"
    >
      <Brightness6Icon />
    </IconButton>
  ) : (
    <NavBtn
      aria-label={isDark ? "Light mode" : "Dark mode"}
      startIcon={<Brightness6Icon data-testid="darkLightModeIcon" />}
      onClick={() => toggleDark()}
    >
      {isDark ? "Light mode" : "Dark mode"}
    </NavBtn>
  );

  return (
    <AppBar color={!isDark ? "primary" : "inherit"} position="sticky">
      <FlexToolbar>
        <Link to={"/"}>
          <SkuleVote>Skule Vote</SkuleVote>
        </Link>
        <Nav>
          {darkLightModeButton}
          <nav>
            <Link to={"/elections"}>
              <NavBtn aria-label="Vote">Vote</NavBtn>
            </Link>
          </nav>
          <NavBtn aria-label="Check status">Check status</NavBtn>
          <NavBtn aria-label="Logout">Logout</NavBtn>
        </Nav>
      </FlexToolbar>
    </AppBar>
  );
};

export default Header;
