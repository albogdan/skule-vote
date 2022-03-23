import React, { useEffect } from "react";
import { styled } from "@mui/system";
import Typography from "@mui/material/Typography";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";
import Button from "@mui/material/Button";
import FilterListIcon from "@mui/icons-material/FilterList";
import Box from "@mui/material/Box";
import ElectionsFilter, {
  ElectionsFilterDrawer,
} from "components/ElectionsFilter";
import ElectionCard, { NoElectionsCard } from "components/ElectionCard";
import EnhancedBallotModal from "components/BallotModal";
import Messages from "components/Messages";
import { Spacer } from "assets/layout";
import {
  useGetElectionSession,
  useGetEligibleElections,
  useGetMessages,
} from "hooks/ElectionHooks";
import { useHandleSubmit } from "hooks/ElectionHooks";

const ElectionsWrapper = styled("div")(({ theme }) => ({
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "center",
  marginTop: 32,
  width: "100%",
  [theme.breakpoints.down("sm")]: {
    flexDirection: "column",
    alignItems: "center",
    maxWidth: 400,
  },
}));

const CardDiv = styled("div")({
  display: "flex",
  flexDirection: "column",
  maxWidth: 400,
  width: "100%",
  "> button:not(:last-child)": {
    marginBottom: 16,
  },
});

const FilterBtnDiv = styled("div")({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  marginBottom: 32,
  maxWidth: 400,
  width: "100%",
  p: {
    marginLeft: 16,
    textAlign: "right",
  },
});

export const listOfCategories = {
  all: "All",
  referenda: "Referenda",
  officer: "Officer",
  board_of_directors: "Board of Directors",
  discipline_club: "Discipline Club",
  class_representative: "Class Representatives",
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
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [filterCategory, setFilterCategory] = React.useState("All");
  const [electionSession, setElectionSession] = React.useState({});
  const [eligibleElections, setEligibleElections] = React.useState({});
  const [messages, setMessages] = React.useState([]);

  const handleSubmit = useHandleSubmit(setEligibleElections);
  const getElectionSession = useGetElectionSession();
  const getEligibleElections = useGetEligibleElections();
  const getMessages = useGetMessages();

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

  useEffect(() => {
    async function fetchElection() {
      const getEligibleElecs = await getEligibleElections();
      const getElecSession = await getElectionSession();
      const getMsgs = await getMessages();
      if (getElecSession != null) {
        setElectionSession(getElecSession);
      }
      if (getEligibleElecs != null) {
        setEligibleElections(getEligibleElecs);
      }
      if (getMsgs != null) {
        setMessages(getMsgs);
      }
      // Call this every minute
      setTimeout(() => {
        fetchElection();
      }, 60000);
    }
    fetchElection();
  }, [getElectionSession, getEligibleElections, getMessages]);

  return (
    <>
      {eligibleElections?.[ballotElectionId] && (
        <EnhancedBallotModal
          open={open}
          handleSubmit={handleSubmit}
          handleClose={handleClose}
          ballotInfo={eligibleElections[ballotElectionId]}
        />
      )}
      <ElectionsFilterDrawer
        drawerOpen={drawerOpen}
        toggleDrawer={toggleDrawer}
        filterCategory={filterCategory}
        setAndCloseFilter={setAndCloseFilter}
        eligibleElections={eligibleElections}
      />
      <Spacer y={isMobile ? 12 : 16} />
      <Messages
        electionIsLive={electionIsLive}
        times={[startTime, startTimeStr, endTimeStr]}
        messages={messages}
      />
      <Spacer y={isMobile ? 20 : 48} />
      <Typography variant="h1">Elections</Typography>
      <ElectionsWrapper>
        <Box sx={{ display: { xs: "none", sm: "block" } }}>
          <ElectionsFilter
            eligibleElections={eligibleElections}
            filterCategory={filterCategory}
            setAndCloseFilter={setAndCloseFilter}
          />
        </Box>
        <Box sx={{ display: { xs: "block", sm: "none" }, width: "100%" }}>
          <FilterBtnDiv>
            <Button
              variant="outlined"
              color="secondary"
              startIcon={<FilterListIcon />}
              onClick={toggleDrawer}
            >
              Filter
            </Button>
            <Typography variant="body2">
              Selected Filter: {filterCategory}
            </Typography>
          </FilterBtnDiv>
        </Box>
        <CardDiv>
          {filteredEligibleElections.length === 0 ? (
            <NoElectionsCard filterCategory={filterCategory} />
          ) : (
            filteredEligibleElections.map((election, i) => (
              <ElectionCard
                key={i}
                title={election.election_name}
                seatsAvailable={election.seats_available}
                openModal={() => {
                  setOpen(true);
                  setBallotElectionId(election.id);
                }}
                category={election.category}
                numCandidates={election.candidates.length}
              />
            ))
          )}
        </CardDiv>
      </ElectionsWrapper>
    </>
  );
};

export default ElectionPage;
