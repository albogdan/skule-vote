import React from "react";
import styled from "styled-components";
import Typography from "@material-ui/core/Typography";
import Hidden from "@material-ui/core/Hidden";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import Button from "@material-ui/core/Button";
import FilterListIcon from "@material-ui/icons/FilterList";
import BallotFilter, { BallotFilterDrawer } from "components/BallotFilter";
import Ballot, { NoBallot } from "components/Ballot";
import { CustomAlert } from "components/Alerts";
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
  justify-content: space-between;
  margin-bottom: 32px;
  max-width: 400px;
  width: 100%;
  p {
    margin-left: 16px;
    font-weight: 400;
    text-align: right;
  }
`;

const AlertsDiv = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 800px;
  width: 100%;
  > :not(:last-child) {
    margin-bottom: 8px;
  }
`;

export const listOfCategories = [
  "All",
  "Referenda",
  "Officer",
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
      <Spacer y={isMobile ? 12 : 16} />
      <AlertsDiv>
        <CustomAlert
          type="warning"
          message="Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisinuli."
        />
        <CustomAlert
          type="info"
          message="Elections close on Friday, May 12, 11:59PM EST."
        />
        <CustomAlert
          type="success"
          message="Your vote has successfully been cast."
        />
        <CustomAlert
          type="error"
          message="Unable with vote due to Error: blah"
        />
      </AlertsDiv>
      <Spacer y={isMobile ? 20 : 48} />
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
            <Typography variant="body1">
              Selected Filter: {filterCategory}
            </Typography>
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
