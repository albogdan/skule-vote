import React from "react";
import styled from "styled-components";
import Paper from "@material-ui/core/Paper";
import { useLocation } from "react-router-dom";
import { ReactComponent as EngSocCrestBlack } from "images/EngSocCrestBlack.svg";
import { ReactComponent as EngSocCrestWhite } from "images/EngSocCrestWhite.svg";
import { responsive } from "assets/breakpoints";
import Typography from "@material-ui/core/Typography";

const FooterPaper = styled(Paper)`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  padding: 32px;
  border-radius: 0 !important;
  margin-top: 64px;
  @media ${responsive.smDown} {
    padding: 16px;
    align-items: center;
    margin-top: 32px;
  }
  > div {
    margin-auto;
    display: flex;
    max-width: 1200px;
    @media ${responsive.smDown} {
      flex-direction: column;
      align-items: center;
    }
  }
`;

const CrestDiv = styled.div`
  display: flex;
  width: 100%;
  align-items: flex-start;
  margin-right: 32px;
  @media ${responsive.smDown} {
    margin-right: 0;
    justify-content: center;
  }
`;

const Address = styled.div`
  display: flex;
  flex-direction: column;
  > p {
    margin-bottom: 8px;
  }
  > :first-child {
    font-weight: 500 !important;
  }
`;

const Acknowledgement = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 800px;
  width: 100%;
  > p {
    margin-bottom: 8px;
  }
  @media ${responsive.smDown} {
    margin-top: 24px;
    text-align: center;
  }
`;

const WhiteCrest = styled(EngSocCrestWhite)`
  width: 75px;
  height: auto;
  margin-right: 24px;
`;
const BlackCrest = styled(EngSocCrestBlack)`
  width: 75px;
  height: auto;
  margin-right: 24px;
`;

const SmallFooter = styled(FooterPaper)`
  text-align: center;
  > p {
    margin-bottom: 8px;
  }
`;

const EmailLink = styled.a`
  &:hover {
    text-decoration: underline;
  }
`;

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
