import React from "react";
import styled from "styled-components";
import Typography from "@material-ui/core/Typography";
import Hidden from "@material-ui/core/Hidden";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import Button from "@material-ui/core/Button";
import FilterListIcon from "@material-ui/icons/FilterList";
import { CustomMessage } from "components/Alerts";
import ElectionsFilter, {
  ElectionsFilterDrawer,
} from "components/ElectionsFilter";
import ElectionCard, { NoElectionsCard } from "components/ElectionCard";
import EnhancedBallotModal from "components/BallotModal";
import { Spacer } from "assets/layout";
import { mockElections } from "assets/mocks";
import { responsive } from "assets/breakpoints";

const ElectionsWrapper = styled.div`
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

const CardDiv = styled.div`
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
    text-align: right;
  }
`;

const MessagesDiv = styled.div`
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
  let filteredListOfElections = listOfElections.filter((election) =>
    filterCategory === "All" ? true : filterCategory === election.category
  );

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };
  const setAndCloseFilter = (category) => {
    setFilterCategory(category);
    setDrawerOpen(false);
  };
  const [open, setOpen] = React.useState(false);
  const [ballotElectionId, setBallotElectionId] = React.useState(null);
  const handleClose = () => {
    setOpen(false);
    setBallotElectionId(null);
  };

  return (
    <>
      <EnhancedBallotModal
        open={open}
        handleClose={handleClose}
        id={ballotElectionId}
      />
      <ElectionsFilterDrawer
        drawerOpen={drawerOpen}
        toggleDrawer={toggleDrawer}
        filterCategory={filterCategory}
        setAndCloseFilter={setAndCloseFilter}
      />
      <Spacer y={isMobile ? 12 : 16} />
      <MessagesDiv>
        <CustomMessage
          variant="info"
          message="Elections close on Friday, May 12, 11:59PM EST."
        />
      </MessagesDiv>
      <Spacer y={isMobile ? 20 : 48} />
      <Typography variant="h1">Elections</Typography>
      <ElectionsWrapper>
        <Hidden implementation="css" xsDown>
          <ElectionsFilter
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
            <Typography variant="body2">
              Selected Filter: {filterCategory}
            </Typography>
          </FilterBtnDiv>
        </Hidden>
        <CardDiv>
          {filteredListOfElections.map((election, i) => (
            <ElectionCard
              key={i}
              title={election.electionName}
              numCandidates={election.numCandidates}
              openModal={() => {
                setOpen(true);
                setBallotElectionId(election.electionId);
              }}
            />
          ))}
          {filteredListOfElections.length === 0 && (
            <NoElectionsCard filterCategory={filterCategory} />
          )}
        </CardDiv>
      </ElectionsWrapper>
    </>
  );
};

export default ElectionPage;
