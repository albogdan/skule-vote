import React, { Fragment, useRef } from "react";
import { styled } from "@mui/system";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import ClearIcon from "@mui/icons-material/Clear";
import IconButton from "@mui/material/IconButton";
import Modal from "@mui/material/Modal";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import FormHelperText from "@mui/material/FormHelperText";
import Stack from "@mui/material/Stack";
import { Spacer } from "assets/layout";
import { BallotRulingAlert } from "components/Alerts";
import { ConfirmSpoilModal, PleaseRankModal } from "components/BallotSubmodals";
import { ModalPaper } from "components/BallotSubmodals";

export const REOPEN_NOMINATIONS = "Reopen Nominations";

const SelectorDiv = styled("div")({
  display: "flex",
  flexDirection: "column",
  width: "100%",
  "> div": {
    marginTop: 12,
    maxWidth: 350,
  },
});

const ThreeButtonDiv = styled("div")(({ theme }) => ({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  width: "100%",
  div: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    "> :last-child": {
      marginLeft: 16,
      "@media (max-width: 460px)": {
        marginLeft: 0,
      },
      [theme.breakpoints.down("xs")]: {
        marginTop: 24,
      },
    },
  },

  "@media (max-width: 460px)": {
    flexDirection: "column",
    alignItems: "flex-start",
    div: {
      width: "100%",
      marginTop: 24,
    },
  },

  [theme.breakpoints.down("xs")]: {
    button: {
      width: "100%",
    },
    div: {
      flexDirection: "column",
    },
  },
}));

const ErrorText = styled(Typography)(({ theme }) => ({
  "> p": theme.palette.mode === "dark" ? "color: #fbdfdf !important" : "",
}));

const SpoilBallotBtn = styled(Button)(({ theme }) => ({
  color: theme.palette.purple.main,
  borderColor: theme.palette.purple.main,
}));

const BlueCard = styled("div")(({ theme }) => ({
  backgroundColor:
    theme.palette.mode === "dark" ? theme.palette.primary.main : "#DDECF6",
  borderRadius: 4,
  padding: 20,
  width: "fit-content",
}));

// Randomize array in-place using Durstenfeld shuffle algorithm
const shuffleArray = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};

// Candidate names and statements
// isReferendum: boolean, candidates: Array<{}>,
const Statements = ({ isReferendum, candidates }) => (
  <>
    {!isReferendum && (
      <Typography variant="h2" mb={2}>
        Candidates &amp; Statements
      </Typography>
    )}
    {candidates.map((candidate) => (
      <Fragment key={candidate.id}>
        {!isReferendum && (
          <Typography variant="h3">{candidate.name}</Typography>
        )}
        {candidate.disqualified_status && (
          <>
            <BallotRulingAlert
              ruling={candidate.disqualified_message}
              link={candidate.disqualified_link}
              isDQ
            />
            <Spacer y={4} />
          </>
        )}
        {(candidate.rule_violation_message ||
          candidate.rule_violation_link) && (
          <>
            <BallotRulingAlert
              ruling={candidate.rule_violation_message}
              link={candidate.rule_violation_link}
            />
            <Spacer y={4} />
          </>
        )}
        {candidate.statement ? (
          candidate.statement.split("\n").map((item, i) => (
            <Typography key={i} variant="body1" sx={{ mb: 1.5 }}>
              {item}
            </Typography>
          ))
        ) : (
          <Typography variant="body1" sx={{ mb: 1.5, fontStyle: "italic" }}>
            This candidate did not provide a statement.
          </Typography>
        )}
      </Fragment>
    ))}
  </>
);

// i: number, candidates: Array<{}>, ranking: {[number]: number},
// isReferendum: boolean, changeRanking: func
const Selector = ({ i, candidates, ranking, isReferendum, changeRanking }) => {
  const [selectVal, setSelectVal] = React.useState(ranking[i] ?? "");
  const handleRankOnchange = (event) => {
    setSelectVal(event.target.value);
    changeRanking(i, event.target.value);
  };

  const label = isReferendum
    ? "Do you support this referendum?"
    : candidates.length === 2
    ? "Do you support this candidate?"
    : `Rank ${i + 1}`;

  const duplicateSelected =
    Object.values(ranking).filter((x) => x === selectVal).length > 1;
  const outOfOrder =
    i !== 0 &&
    selectVal !== "" &&
    !Object.keys(ranking).includes((i - 1).toString());

  return (
    <FormControl
      variant="outlined"
      key={i}
      error={duplicateSelected || outOfOrder}
    >
      <InputLabel id={`rank-${i}-label`} color="secondary">
        {label}
      </InputLabel>
      <Select
        labelId={`rank-${i}-label`}
        id={`rank-${i}-select`}
        value={selectVal ?? ""}
        onChange={handleRankOnchange}
        label={label}
        color="secondary"
      >
        <MenuItem value="" key="-">
          -
        </MenuItem>
        {candidates.map((candidate) => (
          <MenuItem value={candidate.id} key={candidate.id}>
            {candidates.length === 2 && candidate.statement != null
              ? "Yes"
              : candidate.name}
          </MenuItem>
        ))}
      </Select>
      {duplicateSelected && (
        <ErrorText variant="subtitle2">
          <FormHelperText>
            Same candidate selected multiple times
          </FormHelperText>
        </ErrorText>
      )}
      {outOfOrder && (
        <ErrorText variant="subtitle2">
          <FormHelperText>Choices not performed in order</FormHelperText>
        </ErrorText>
      )}
    </FormControl>
  );
};

// isReferendum: boolean, candidates: Array<{}>, ranking: {[number]: number}, changeRanking: func
const BallotDropdowns = ({
  isReferendum,
  candidates,
  ranking,
  changeRanking,
}) => {
  return (
    <>
      <Typography variant="h2">Ballot</Typography>
      <Typography variant="body1">
        {candidates.length === 2
          ? "Please select your choice using the dropdown menu."
          : "Please select as many choices as you want using the dropdown menus. You are encouraged to rank all of the above choices."}
      </Typography>
      <SelectorDiv>
        {candidates.map(
          (candidate, i) =>
            candidate.statement != null && (
              <Selector
                key={i}
                i={i}
                candidates={candidates}
                changeRanking={changeRanking}
                ranking={ranking}
                isReferendum={isReferendum}
              />
            )
        )}
      </SelectorDiv>
    </>
  );
};

// Summarizes who/what user voted for
// isReferendum: boolean, ranking: {[number]: number}, candidates: Array<{}>
const SelectedRanking = ({ isReferendum, ranking, candidates }) => {
  // idToNameMap: {[id: number]: [name: string]}
  const idToNameMap = React.useMemo(
    () =>
      candidates.reduce((accum, val) => {
        accum[val.id] = val.name;
        return accum;
      }, {}),
    [candidates]
  );
  const rankingLen = Object.keys(ranking).length;
  return (
    <>
      <Typography variant="h2">
        {candidates.length === 2 ? "Selected Choice" : "Selected Ranking"}
      </Typography>
      <Typography variant="body1" sx={{ mb: 0.5 }}>
        Please confirm that your choice(s) are correctly reflected here and cast
        your ballot.
      </Typography>
      <Typography variant="body1">
        You can submit a blank ballot by pressing "Spoil Ballot".
      </Typography>
      <br />
      {/* Case: nothing has been selected yet */}
      {rankingLen === 0 && (
        <Typography variant="body1" sx={{ fontStyle: "italic" }}>
          No choice selected
        </Typography>
      )}
      {/* Case: is a single candidate or referendum and vote has been selected */}
      {rankingLen === 1 && candidates.length === 2 && (
        <BlueCard>
          <Typography variant="body2">
            {isReferendum
              ? "Do you support this referendum?"
              : "Do you support this candidate?"}
            &nbsp;
            {Object.values(ranking)[0] ===
            candidates.filter((candidate) => candidate.statement != null)[0].id
              ? "Yes"
              : idToNameMap[Object.values(ranking)[0]]}
          </Typography>
        </BlueCard>
      )}
      {/* Case: multiple candidates and vote(s) has been selected */}
      {rankingLen > 0 && candidates.length > 2 && (
        <BlueCard>
          {Object.entries(ranking).map((rank) => (
            <Typography variant="body2" key={rank[0]}>
              {parseInt(rank[0], 10) + 1}. {idToNameMap?.[rank[1]] ?? "Error"}
              {/* The above error should never happen */}
            </Typography>
          ))}
        </BlueCard>
      )}
    </>
  );
};

// handleClose: func, handleSubmit: func, open: boolean, isReferendum: boolean,
// sortedCandidates: Array<{}>, electionName: string, electionId: number
export const BallotModal = ({
  handleClose,
  handleSubmit,
  open,
  isReferendum,
  sortedCandidates,
  electionName,
  electionId,
  ronId,
}) => {
  const [ranking, setRanking] = React.useState({});
  const rankingLen = Object.keys(ranking).length;

  const [openConfirmSpoil, setOpenConfirmSpoil] = React.useState(false);
  const [openPleaseRank, setOpenPleaseRank] = React.useState(false);

  const changeRanking = (i, val) => {
    setRanking((prevState) => {
      if (val === "") {
        delete prevState[i];
      } else {
        prevState[i] = val;
      }
      // Need to make a copy of the object so the modal can rerender
      return Object.assign({}, prevState);
    });
  };

  const castBallot = () => {
    handleSubmit(electionId, ranking);
    closeForm();
  };

  const handleCastBallot = () => {
    if (
      rankingLen < sortedCandidates.length &&
      sortedCandidates.length > 2 &&
      !Object.values(ranking).includes(ronId ?? -1)
    ) {
      setOpenPleaseRank(true);
    } else {
      castBallot();
    }
  };

  const spoilBallot = () => {
    handleSubmit(electionId, {});
    closeForm();
  };

  const closeForm = () => {
    handleClose();
    setRanking({});
  };

  return (
    <>
      <PleaseRankModal
        open={openPleaseRank}
        onClose={() => setOpenPleaseRank(false)}
        castBallot={castBallot}
      />
      <ConfirmSpoilModal
        open={openConfirmSpoil}
        onClose={() => setOpenConfirmSpoil(false)}
        spoilBallot={spoilBallot}
      />
      <Modal
        open={open}
        onClose={() => closeForm()}
        aria-labelledby={`ballot-modal-${electionName}`}
        aria-describedby="ballot-modal"
      >
        <ModalPaper>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="flex-start"
            sx={{ width: "100%" }}
          >
            <Typography variant="h1">{electionName}</Typography>
            <IconButton
              data-testid="drawerClose"
              onClick={() => closeForm()}
              role="close"
              size="large"
            >
              <ClearIcon />
            </IconButton>
          </Stack>
          <Divider />
          <Statements
            isReferendum={isReferendum}
            candidates={sortedCandidates}
          />
          <Divider />
          <BallotDropdowns
            isReferendum={isReferendum}
            candidates={sortedCandidates}
            changeRanking={changeRanking}
            ranking={ranking}
          />
          <Divider />
          <SelectedRanking
            isReferendum={isReferendum}
            ranking={ranking}
            candidates={sortedCandidates}
          />
          <Divider />
          <ThreeButtonDiv>
            <SpoilBallotBtn
              variant="outlined"
              onClick={() => setOpenConfirmSpoil(true)}
            >
              Spoil ballot
            </SpoilBallotBtn>
            <div>
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => closeForm()}
              >
                Cancel
              </Button>
              <Button
                color="primary"
                onClick={() => handleCastBallot()}
                // checks if choices are not in order or there are duplicate votes for the same person
                disabled={
                  parseInt(Object.keys(ranking).slice(-1)[0], 10) !==
                    rankingLen - 1 ||
                  new Set(Object.values(ranking)).size !== rankingLen
                }
              >
                Cast ballot
              </Button>
            </div>
          </ThreeButtonDiv>
        </ModalPaper>
      </Modal>
    </>
  );
};

// handleSubmit: func, handleClose: func, open: boolean, ballotInfo: {}
const EnhancedBallotModal = ({
  handleSubmit,
  handleClose,
  open,
  ballotInfo,
}) => {
  const { category, candidates, election_name, id } = ballotInfo;
  const isReferendum = category === "referenda";

  let candidatesList = [];
  // Seperate ron from non-ron candidates
  const ron = candidates.filter(
    (candidate) => candidate.name === REOPEN_NOMINATIONS
  )[0];
  // Randomly shuffle the list of non-ron candidates
  let nonRon = useRef(
    shuffleArray(
      candidates.filter((candidate) => candidate.name !== REOPEN_NOMINATIONS)
    )
  ).current;

  // Append RON to the end
  if (!isReferendum && candidates.length > 2) {
    candidatesList = nonRon.concat(ron);
  } else if (candidates.length === 2) {
    // Replace ron with No
    const noSelection = {
      id: ron.id,
      name: "No",
      statement: null,
    };
    candidatesList = nonRon.concat(noSelection);
  }

  return (
    <BallotModal
      handleClose={handleClose}
      handleSubmit={handleSubmit}
      open={open}
      isReferendum={isReferendum}
      sortedCandidates={candidatesList}
      electionName={election_name}
      electionId={id}
      ronId={ron.id}
    />
  );
};

export default EnhancedBallotModal;
