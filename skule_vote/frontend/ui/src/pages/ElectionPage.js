import React from "react";
import styled from "styled-components";
import Typography from "@material-ui/core/Typography";
import Hidden from "@material-ui/core/Hidden";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import Button from "@material-ui/core/Button";
import FilterListIcon from "@material-ui/icons/FilterList";
import BallotFilter, { BallotFilterDrawer } from "components/BallotFilter";
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
  @media ${responsive.smDown} {
    flex-direction: column;
    align-items: center;
    max-width: 400px;
    div {
      width: 100%;
    }
  }
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

const FilterBtnDiv = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 32px;
  max-width: 400px;
  width: 100%;
  p {
    margin-left: 16px;
    font-weight: 400;
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

  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [filterCategory, setFilterCategory] = React.useState("All");
  let filteredListOfElections = listOfElections.filter((ballot) =>
    filterCategory === "All" ? true : filterCategory === ballot.category
  );

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };
  const setAndCloseFilter = (category) => {
    setFilterCategory(category);
    setDrawerOpen(false);
  };

  return (
    <>
      <BallotFilterDrawer
        drawerOpen={drawerOpen}
        toggleDrawer={toggleDrawer}
        filterCategory={filterCategory}
        setAndCloseFilter={setAndCloseFilter}
      />
      <Spacer y={isMobile ? 32 : 64} />
      <Typography variant="h1">Elections</Typography>
      <BallotWrapper>
        <Hidden implementation="css" xsDown>
          <BallotFilter
            filterCategory={filterCategory}
            setAndCloseFilter={setAndCloseFilter}
          />
        </Hidden>
        <Hidden implementation="css" smUp>
          <FilterBtnDiv>
            <Button
              variant="outlined"
              color="secondary"
              disableElevation
              startIcon={<FilterListIcon />}
              onClick={toggleDrawer}
            >
              Filter
            </Button>
            <Typography variant="body1">Filter: {filterCategory}</Typography>
          </FilterBtnDiv>
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
