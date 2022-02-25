import React, { Fragment, useRef } from "react";
import styled from "styled-components";
import Paper from "@mui/material/Paper";
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
import { Spacer } from "assets/layout";
import { CustomMessage } from "components/Alerts";
import { responsive } from "assets/breakpoints";
import { useTheme } from "@mui/material/styles";

export const REOPEN_NOMINATIONS = "Reopen Nominations";

const ModalPaper = styled(Paper)`
  position: absolute;
  padding: 32px;
  margin: 50px auto;
  max-width: 900px;
  width: 100%;
  max-height: calc(100% - 100px);
  left: 0;
  right: 0;
  overflow-y: auto;
  outline: none;
  @media ${responsive.smDown} {
    padding: 16px;
    margin: 12px;
    width: calc(100% - 24px);
    max-height: calc(100% - 24px);
  }
  hr {
    margin: 24px 0;
    @media ${responsive.smDown} {
      margin: 16px 0;
    }
  }
  h1,
  h2 {
    font-weight: 400;
  }
  h3 {
    margin: 16px 0 8px;
    @media ${responsive.smDown} {
      margin-top: 16px;
    }
  }
`;

const SpoilModalPaper = styled(ModalPaper)`
  max-width: 450px;
  margin-top: 100px;
`;

const HeaderDiv = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
`;

const SelectorDiv = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  > div {
    margin-top: 12px;
    max-width: 350px;
  }
`;

const TwoButtonDiv = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  div {
    > :last-child {
      margin-left: 16px;
    }
  }
`;

const ThreeButtonDiv = styled(TwoButtonDiv)`
  @media (max-width: 460px) {
    flex-direction: column;
    align-items: flex-start;
    div {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 24px;
      > :last-child {
        margin-left: 0;
      }
    }
  }
`;

const ErrorText = styled(Typography)`
  > p {
    ${(props) => props.$isDark && "color: #fbdfdf !important;"}
  }
`;

const SpoilBallotBtn = styled(Button)`
  color: ${(props) => (props.$isDark ? "#DCD1DD" : "#4D33A3")} !important;
  border-color: ${(props) =>
    props.$isDark ? "#DCD1DD" : "#4D33A3"} !important;
`;

const SpoilBallotBtnFilled = styled(Button)`
  color: #fff;
  background-color: #5f518d !important;
  &:hover {
    background-color: #51496b !important;
  }
`;

const BlueCard = styled.div`
  background-color: ${(props) =>
    props.$theme.palette.mode === "dark"
      ? props.$theme.palette.primary.main
      : "#DDECF6"};
  border-radius: 4px;
  padding: 20px;
  width: fit-content;
`;

// Randomize array in-place using Durstenfeld shuffle algorithm
const shuffleArray = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};

const RulingA = ({ href, children }) => (
  <a
    href={href}
    style={{ color: "inherit" }}
    target="_blank"
    rel="noopener noreferrer"
  >
    {children}
  </a>
);

// Orange alert that appears below candidate's name if they have a disqualification or rule violation message
// ruling: string, link?: string, isDQ?: bool
export const BallotRulingAlert = ({ ruling, link, isDQ }) => {
  let message;
  const defaultMessage = isDQ
    ? "This candidate has been disqualified."
    : "This candidate violated a rule.";
  if (!ruling && !link) {
    message = `${defaultMessage} Contact EngSoc for more information.`;
  } else if (!ruling) {
    message = (
      <span data-testid="ballotRulingAlert">
        {defaultMessage} Please read the ruling{" "}
        <RulingA href={link}>here</RulingA>.
      </span>
    );
  } else {
    ruling = ruling.trim();
    const hasPeriod = ruling.slice(-1) === ".";
    message = (
      <span data-testid="ballotRulingAlert">
        {ruling}
        {link && (
          <span>
            {hasPeriod ? " " : ". "}Please read the ruling{" "}
            <RulingA href={link}>here</RulingA>.
          </span>
        )}
      </span>
    );
  }
  return <CustomMessage variant="warning" message={message} />;
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
    {candidates.map(
      (candidate) =>
        candidate.statement != null && (
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
            <Typography variant="body1">{candidate.statement}</Typography>
          </Fragment>
        )
    )}
  </>
);

// i: number, candidates: Array<{}>, ranking: {[number]: number},
// isReferendum: boolean, changeRanking: func, isDark: boolean
const Selector = ({
  i,
  candidates,
  ranking,
  isReferendum,
  changeRanking,
  isDark,
}) => {
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
        <MenuItem value="">-</MenuItem>
        {candidates.map((candidate) => (
          <MenuItem value={candidate.id} key={candidate.id}>
            {candidates.length === 2 && candidate.statement != null
              ? "Yes"
              : candidate.name}
          </MenuItem>
        ))}
      </Select>
      {duplicateSelected && (
        <ErrorText variant="subtitle2" $isDark={isDark}>
          <FormHelperText>
            Same candidate selected multiple times
          </FormHelperText>
        </ErrorText>
      )}
      {outOfOrder && (
        <ErrorText variant="subtitle2" $isDark={isDark}>
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
  isDark,
}) => {
  return (
    <>
      <Typography variant="h2">Ballot</Typography>
      <Typography variant="body1">
        {candidates.length === 2
          ? "Please select your choice using the dropdown menu."
          : "Please select as many choices as you want using the dropdown menus."}
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
                isDark={isDark}
              />
            )
        )}
      </SelectorDiv>
    </>
  );
};

// Summarizes who/what user voted for
// isReferendum: boolean, ranking: {[number]: number}, candidates: Array<{}>, isDark: boolean
const SelectedRanking = ({ isReferendum, ranking, candidates, isDark }) => {
  const theme = useTheme();
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
      <Typography variant="body1">
        Please confirm that your choice(s) are correctly reflected here and cast
        your ballot.
      </Typography>
      <br />
      {/* Case: nothing has been selected yet */}
      {rankingLen === 0 && (
        <Typography variant="body1">
          No choice selected
          <br />
          (You can submit a blank ballot by pressing "Spoil Ballot")
        </Typography>
      )}
      {/* Case: is a single candidate or referendum and vote has been selected */}
      {rankingLen === 1 && candidates.length === 2 && (
        <BlueCard $theme={theme}>
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
        <BlueCard $theme={theme}>
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

// Modal that opens to confirm you want to spoil your ballot
// open: boolean, onClose: func, spoilBallot: func, isDark: boolean
export const ConfirmSpoilModal = ({ open, onClose, spoilBallot, isDark }) => (
  <Modal
    open={open}
    onClose={onClose}
    aria-labelledby="confirm-spoil-modal"
    aria-describedby="confirm-spoil-modal"
  >
    <SpoilModalPaper>
      <Typography variant="h3">
        Are you sure you want to spoil your ballot?
      </Typography>
      <Divider />
      <TwoButtonDiv>
        <Button variant="outlined" color="secondary" onClick={() => onClose()}>
          Cancel
        </Button>
        <SpoilBallotBtnFilled
          variant="contained"
          onClick={() => spoilBallot()}
          data-testid="spoilModalConfirm"
        >
          Spoil ballot
        </SpoilBallotBtnFilled>
      </TwoButtonDiv>
    </SpoilModalPaper>
  </Modal>
);

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
}) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === "dark";

  const [ranking, setRanking] = React.useState({});
  const rankingLen = Object.keys(ranking).length;

  const [openConfirmSpoil, setOpenConfirmSpoil] = React.useState(false);

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
  const spoilBallot = () => {
    handleSubmit(electionId, {});
    closeForm();
  };

  const closeForm = () => {
    handleClose();
    setRanking({});
  };

  const handleCloseConfirmSpoil = () => {
    setOpenConfirmSpoil(false);
  };

  return (
    <>
      <ConfirmSpoilModal
        open={openConfirmSpoil}
        onClose={handleCloseConfirmSpoil}
        spoilBallot={spoilBallot}
        isDark={isDark}
      />
      <Modal
        open={open}
        onClose={() => closeForm()}
        aria-labelledby={`ballot-modal-${electionName}`}
        aria-describedby="ballot-modal"
      >
        <ModalPaper>
          <HeaderDiv>
            <Typography variant="h1">{electionName}</Typography>
            <IconButton
              data-testid="drawerClose"
              onClick={() => closeForm()}
              role="close"
              size="large"
            >
              <ClearIcon />
            </IconButton>
          </HeaderDiv>
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
            isDark={isDark}
          />
          <Divider />
          <SelectedRanking
            isReferendum={isReferendum}
            ranking={ranking}
            candidates={sortedCandidates}
            isDark={isDark}
          />
          <Divider />
          <ThreeButtonDiv>
            <SpoilBallotBtn
              variant="outlined"
              $isDark={isDark}
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
                variant="contained"
                color="primary"
                onClick={() => castBallot()}
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
    />
  );
};

export default EnhancedBallotModal;
