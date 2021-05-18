import React from "react";
import styled from "styled-components";
import Typography from "@material-ui/core/Typography";
import Hidden from "@material-ui/core/Hidden";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import BallotFilter from "components/BallotFilter";
import Ballot, { NoBallot } from "components/Ballot";
import { Spacer } from "assets/layout";
import { mockElections } from "assets/mocks";
import { responsive } from "assets/breakpoints";

const BallotWrapper = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: center;
  margin-top: 32px;
  width: 100%;
`;

const BallotDiv = styled.div`
  display: flex;
  flex-direction: column;

  max-width: 400px;
  width: 100%;
  > div:not(:last-child) {
    margin-bottom: 16px;
  }
`;

export const listOfCategories = [
  "All",
  "Referenda",
  "Officers",
  "Board of Directors",
  "Discipline Club",
  "Class Representatives",
  "Other",
];

const ElectionPage = ({ listOfElections = mockElections }) => {
  const isMobile = useMediaQuery(responsive.smDown);

  const [filterCategory, setFilterCategory] = React.useState("All");
  let filteredListOfElections = listOfElections.filter((ballot) =>
    filterCategory === "All" ? true : filterCategory === ballot.category
  );

  return (
    <>
      <Spacer y={isMobile ? 32 : 64} />
      <Typography variant="h1">Elections</Typography>
      <BallotWrapper>
        <Hidden implementation="css" xsDown>
          <BallotFilter
            filterCategory={filterCategory}
            setFilterCategory={setFilterCategory}
          />
        </Hidden>
        <BallotDiv>
          {filteredListOfElections.map((ballot, i) => (
            <Ballot
              key={i}
              title={ballot.electionName}
              numCandidates={ballot.numCandidates}
            />
          ))}
          {filteredListOfElections.length === 0 && (
            <NoBallot filterCategory={filterCategory} />
          )}
        </BallotDiv>
      </BallotWrapper>
    </>
  );
};

export default ElectionPage;
