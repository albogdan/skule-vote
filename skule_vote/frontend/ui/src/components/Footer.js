import React from "react";
import { styled } from "@mui/system";
import Paper from "@mui/material/Paper";
import { useLocation } from "react-router-dom";
import { ReactComponent as EngSocCrestBlack } from "images/EngSocCrestBlack.svg";
import { ReactComponent as EngSocCrestWhite } from "images/EngSocCrestWhite.svg";
import Typography from "@mui/material/Typography";

const FooterPaper = styled(Paper)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  width: "100%",
  padding: 32,
  borderRadius: 0,
  marginTop: 64,
  [theme.breakpoints.down("sm")]: {
    padding: 16,
    alignItems: "center",
    marginTop: 32,
  },
  "> div": {
    display: "flex",
    maxWidth: 1200,
    [theme.breakpoints.down("sm")]: {
      flexDirection: "column",
      alignItems: "center",
    },
  },
}));

const CrestDiv = styled("div")(({ theme }) => ({
  display: "flex",
  width: "100%",
  alignItems: "flex-start",
  marginRight: 32,
  [theme.breakpoints.down("sm")]: {
    marginRight: 0,
    justifyContent: "center",
  },
}));

const Address = styled("div")({
  display: "flex",
  flexDirection: "column",
  "> p": {
    marginBottom: 8,
  },
  "> p:first-of-type": {
    fontWeight: 500,
  },
});

const Acknowledgement = styled("div")(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  maxWidth: 800,
  width: "100%",
  "> p": {
    marginBottom: 8,
  },
  [theme.breakpoints.down("sm")]: {
    marginTop: 24,
    textAlign: "center",
  },
}));

const WhiteCrest = styled(EngSocCrestWhite)({
  width: 75,
  height: "auto",
  marginRight: 24,
});
const BlackCrest = styled(EngSocCrestBlack)({
  width: 75,
  height: "auto",
  marginRight: 24,
});

const SmallFooter = styled(FooterPaper)({
  textAlign: "center",
  "> p": {
    marginBottom: 8,
  },
});

const EmailLink = styled("a")({
  fontWeight: 500,
  ":hover": {
    textDecoration: "underline",
  },
});

const Footer = ({ isDark }) => {
  const today = new Date();
  const year = today.getFullYear();
  const location = useLocation();
  const isLanding = location.pathname === "/";

  if (isLanding) {
    return (
      <FooterPaper>
        <div>
          <CrestDiv>
            {isDark ? (
              <WhiteCrest data-testid="whiteCrest" />
            ) : (
              <BlackCrest data-testid="blackCrest" />
            )}
            <Address>
              <Typography variant="body1">
                University of Toronto Engineering Society
              </Typography>
              <Typography variant="body1">
                B740 Sandford Fleming Building
              </Typography>
              <Typography variant="body1">10 King's College Road</Typography>
              <Typography variant="body1">
                Toronto, Ontario, Canada M5S 3G4
              </Typography>
            </Address>
          </CrestDiv>

          <Acknowledgement>
            <Typography variant="body1">
              This website was designed and developed under the aegis of the
              University of Toronto Engineering Society by a team with many
              contributors, who retain their rights to the underlying
              intellectual property but license it for free and perpetual use by
              the Society.
            </Typography>
            <Typography variant="body1">
              By continuing to use this website you consent to the use of
              anonymous aggregated data for analytics and improving website
              performance.
            </Typography>
            <Typography variant="body1">© {year} Skule™.</Typography>
            <Typography variant="body1">
              Question? Please email the CRO at{" "}
              <EmailLink href="mailto:cro@skule.ca">cro@skule.ca</EmailLink>.
            </Typography>
          </Acknowledgement>
        </div>
      </FooterPaper>
    );
  } else {
    return (
      <SmallFooter>
        <Typography variant="body1">
          By continuing to use this website you consent to the use of anonymous
          aggregated data for analytics and improving website performance.
        </Typography>
        <Typography variant="body1">© {year} Skule™.</Typography>
      </SmallFooter>
    );
  }
};

export default Footer;
