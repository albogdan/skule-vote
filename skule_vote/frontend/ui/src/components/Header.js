import React from "react";
import styled from "styled-components";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import { Link } from "react-router-dom";
import Brightness6Icon from "@material-ui/icons/Brightness6";
import Button from "@material-ui/core/Button";

const SkuleVote = styled.h1`
  font-weight: bold;
  font-size: 16px;
`;

const Nav = styled.div`
  display: flex;
  white-space: nowrap;
  button {
    color: white;
    padding: 20px 15px;
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
  const darkLightModeButton = isDark ? (
    <Button
      aria-label="Light mode"
      startIcon={<Brightness6Icon />}
      onClick={() => toggleDark()}
    >
      Light mode
    </Button>
  ) : (
    <Button
      aria-label="Dark mode"
      startIcon={<Brightness6Icon />}
      onClick={() => toggleDark()}
    >
      Dark mode
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

// const mapStateToProps = (state) => ({
//   pathname: state.router.location.pathname,
// });

// const Header = connect(mapStateToProps)(UnconnectedHeader);

export default Header;
