import React from "react";
import { useMount } from "react-use";
import styled from "styled-components";
import Typography from "@material-ui/core/Typography";
import Hidden from "@material-ui/core/Hidden";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import Button from "@material-ui/core/Button";
import FilterListIcon from "@material-ui/icons/FilterList";
import ElectionsFilter, {
  ElectionsFilterDrawer,
} from "components/ElectionsFilter";
import ElectionCard, { NoElectionsCard } from "components/ElectionCard";
import EnhancedBallotModal from "components/BallotModal";
import Messages from "components/Messages";
import { Spacer } from "assets/layout";
import { mockElections } from "assets/mocks";
import { responsive } from "assets/breakpoints";
import {
  useGetElectionSession,
  useGetEligibleElections,
} from "hooks/ElectionHooks";

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

export const listOfCategories = {
  all: "All",
  referenda: "Referenda",
  officer: "Officer",
  board_of_directors: "Board of Directors",
  discipline_club: "Discipline Club",
  class_representatives: "Class Representatives",
  other: "Other",
};

export function readableDate(date) {
  if (date == null) {
    return [null, null];
  }
  const dateObj = new Date(date);
  const readableDate = dateObj.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    timeZoneName: "short",
  });
  return [dateObj, readableDate];
}

const ElectionPage = () => {
  const isMobile = useMediaQuery(responsive.smDown);

  const getElectionSession = useGetElectionSession();
  const getEligibleElections = useGetEligibleElections();

  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [filterCategory, setFilterCategory] = React.useState("All");
  const [electionSession, setElectionSession] = React.useState({});
  const [eligibleElections, setEligibleElections] = React.useState({});

  const [startTime, startTimeStr] = readableDate(electionSession?.start_time);
  const [endTime, endTimeStr] = readableDate(electionSession?.end_time);
  const electionIsLive =
    startTime && Date.now() >= startTime && Date.now() <= endTime;

  let filteredEligibleElections = Object.values(eligibleElections).filter(
    (election) =>
      filterCategory === "All"
        ? true
        : filterCategory === listOfCategories[election.category]
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

  useMount(() => {
    async function fetchElection() {
      const getElecSession = await getElectionSession();
      const getEligibleElecs = await getEligibleElections();
      if (getElecSession != null) {
        setElectionSession(getElecSession);
      }
      if (getEligibleElecs != null) {
        setEligibleElections(getEligibleElecs);
      }
      // Call this every minute
      setTimeout(() => {
        fetchElection();
      }, 60000);
    }
    fetchElection();
  });
  return (
    <>
      <EnhancedBallotModal
        open={open}
        handleClose={handleClose}
        ballotInfo={eligibleElections[ballotElectionId]}
      />
      <ElectionsFilterDrawer
        drawerOpen={drawerOpen}
        toggleDrawer={toggleDrawer}
        filterCategory={filterCategory}
        setAndCloseFilter={setAndCloseFilter}
      />
      <Spacer y={isMobile ? 12 : 16} />
      <Messages
        electionIsLive={electionIsLive}
        times={[startTime, startTimeStr, endTimeStr]}
      />
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
          {filteredEligibleElections.length === 0 ? (
            <NoElectionsCard filterCategory={filterCategory} />
          ) : (
            filteredEligibleElections.map((election, i) => (
              <ElectionCard
                key={i}
                title={election.election_name}
                numCandidates={election.seats_available}
                openModal={() => {
                  setOpen(true);
                  setBallotElectionId(election.id);
                }}
              />
            ))
          )}
        </CardDiv>
      </ElectionsWrapper>
    </>
  );
};

export default ElectionPage;
