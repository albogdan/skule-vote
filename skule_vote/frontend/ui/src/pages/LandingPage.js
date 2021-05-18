import React from "react";
import styled from "styled-components";
import { Link } from "react-router-dom";
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import { ReactComponent as SkuleLogoBlue } from "images/SkuleLogoBlue.svg";
import { responsive } from "assets/breakpoints";

const SkuleLogo = styled(SkuleLogoBlue)`
  max-width: 400px;
  width: 100%;
  height: auto;
  margin-right: 64px;
  @media ${responsive.mdDown} {
    margin-right: 0;
    margin-bottom: 16px;
    max-width: 300px;
  }
`;

const LandingDiv = styled.div`
  display: flex;
  max-width: 1000px;
  margin: 100px 0;
  @media ${responsive.mdDown} {
    flex-direction: column;
    align-items: center;
    margin: 64px 0;
  }
`;

const LandingDivText = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  > :first-child {
    margin-bottom: 8px;
  }
  > :last-child {
    margin-top: 32px;
  }
  @media ${responsive.mdDown} {
    align-items: center;
    text-align: center;
    > :last-child {
      margin-top: 16px;
    }
  }
`;

const UrlLink = styled.a`
  &:hover {
    text-decoration: underline;
  }
`;

const ElectionDetailsPaper = styled(Paper)`
  padding: 32px;
  box-shadow: none !important;
  margin-top: 16px;
  @media ${responsive.smDown} {
    padding: 16px;
  }
`;

const ElectionDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const LandingPage = () => {
  return (
    <>
      <LandingDiv>
        <SkuleLogo data-testid="skuleLogo" />
        <LandingDivText>
          <Typography variant="h1">Welcome to SkuleVote</Typography>
          <Typography variant="body1">
            For more information about the Engineering Society and its
            elections, please visit the{" "}
            <UrlLink href="https://skule.ca/" target="_blank" rel="noreferrer">
              Skule
            </UrlLink>{" "}
            or{" "}
            <UrlLink
              href="https://skule.ca/page.php?q=elections"
              target="_blank"
              rel="noreferrer"
            >
              Elections
            </UrlLink>{" "}
            websites.
          </Typography>
          <Link to={"/elections"}>
            <Button color="primary" variant="contained" disableElevation>
              Vote
            </Button>
          </Link>
        </LandingDivText>
      </LandingDiv>

      <ElectionDetails>
        <Typography variant="h2">Election Details</Typography>
        <ElectionDetailsPaper>
          <Typography variant="body1">
            University of Toronto Engineering Society (EngSoc) Elections are run
            according to the Single Transferable Vote system. Unlike other
            systems where voters may only vote for one candidate, in this type
            of election, you may vote for multiple candidates, ranking your
            chosen candidates in order of preference. For the Executive Office
            positions, you may vote for up to the number of candidates running
            for that office. You do NOT have to vote for, or rank, every
            candidate, nor are you required to vote for each office/proposition.
          </Typography>
          <br />
          <Typography variant="body1">
            Your first preference vote will receive a value of one. The quota
            for election is the smallest number of votes necessary to elect the
            required number of candidates (i.e. one for the officers and single
            winner elections, and 4 and 3 for the At Large and Frosh seats
            respectively). This is calculated by using the equation (N/(S+1))+1
            where N is the number of valid first preference votes and S is the
            total number of seats needed to be filled in the election.
            Fractional votes are dropped.
          </Typography>
          <br />
          <Typography variant="body1">
            A candidate is elected if all votes have been transferred and s/he
            has accrued at least a quota of votes. If the voter's preference is
            for a candidate who thus receives more than the quota of votes
            required for election, the surplus value of his/her vote shall be
            transferred to his/her next eligible preference, if applicable. If a
            voter's preference for a candidate is for a candidate eliminated or
            already elected, the current value of the vote will be transferred
            to the voter's next eligible preference.
          </Typography>
          <br />
          <Typography variant="body1">
            Votes are tallied in rounds. The first preferences of all voters are
            tallied first. If no candidate achieves the quota in this round,
            each candidate with the least vote-total is eliminated and each
            voter's vote (which was cast for these eliminated candidates)
            remains at its present value and is transferred to the voter's next
            preference. If the voter has not listed any additional preference or
            was unable to do so, his/her ballot is exhausted/spoiled. This
            process continues, and further tabulation rounds are counted, until
            a candidate reaches quota for a seat.
          </Typography>
          <br />
          <Typography variant="body1">
            For acclaimed seats (i.e. a single candidate) and Levies, you have
            the option of voting Yes, No, and Abstain. Only "Yes" and "No" votes
            are counted. "Spoiling" is the equivalent of not voting on the
            proposition, but the vote is counted towards turnout. Electing Yes
            for either acclaimed or levy elects the candidate to the position
            and means that the prescribed funds will be collected for the
            upcoming school year. For acclaimed seats if No is elected as the
            winner then Nominations for that position are re-opened and the
            election rerun. Voting No on a levy means that money will not be
            collected from the student body for the upcoming school year.
          </Typography>
          <br />
          <Typography variant="body1">
            Special thanks to the development team over the years: Armin Ale,
            Alex Bogdan, Lisa Li, Aleksei Wan, Jonathan Swyers, Robert Fairley,
            Michael Vu, and Rafal Dittwald
          </Typography>
        </ElectionDetailsPaper>
      </ElectionDetails>
    </>
  );
};

export default LandingPage;
