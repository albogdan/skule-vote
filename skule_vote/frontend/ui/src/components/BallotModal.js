import React, { Fragment } from "react";
import styled from "styled-components";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import Divider from "@material-ui/core/Divider";
import ClearIcon from "@material-ui/icons/Clear";
import IconButton from "@material-ui/core/IconButton";
import Modal from "@material-ui/core/Modal";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import FormHelperText from "@material-ui/core/FormHelperText";
import { Spacer } from "assets/layout";
import { useHandleSubmit } from "assets/hooks";
import { CustomMessage } from "components/Alerts";
import { responsive } from "assets/breakpoints";
import { useTheme } from "@material-ui/core/styles";

import {
  MockBallotVP,
  MockBallotReferenda,
  MockBallotPresident,
} from "assets/mocks";

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

const ButtonDiv = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  div {
    > :last-child {
      margin-left: 16px;
    }
  }
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
  color: ${(props) => (props.$isDark ? "#DCD1DD" : "#4D33A3")};
  border-color: ${(props) => (props.$isDark ? "#DCD1DD" : "#4D33A3")};
`;

// Randomize array in-place using Durstenfeld shuffle algorithm
const shuffleArray = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};

// Orange alert that appears below candidate's name if they have a disqualification or rule violation message
// ruling: string, link: string
const BallotRulingAlert = ({ ruling, link }) => {
  const message = (
    <>
      {ruling}
      {link && (
        <span>
          &nbsp;Please read the ruling&nbsp;
          <a
            href={link}
            style={{ color: "inherit" }}
            target="_blank"
            rel="noreferrer"
          >
            here
          </a>
          .
        </span>
      )}
    </>
  );
  return <CustomMessage variant="warning" message={message} />;
};

// Candidate names and statements
// isReferendum: boolean, candidates: Array<{}>,
const Statements = ({ isReferendum, candidates }) => (
  <>
    {!isReferendum && (
      <Typography variant="h2">Candidates &amp; Statements</Typography>
    )}
    {candidates.map(
      (candidate) =>
        candidate.statement != null && (
          <Fragment key={candidate.id}>
            {!isReferendum && (
              <Typography variant="h3">{candidate.candidateName}</Typography>
            )}
            {candidate.disqualificationRuling && (
              <>
                <BallotRulingAlert
                  ruling={candidate.disqualificationRuling}
                  link={candidate.disqualificationLink}
                />
                <Spacer y={4} />
              </>
            )}
            {candidate.ruleViolationRuling && (
              <>
                <BallotRulingAlert
                  ruling={candidate.ruleViolationRuling}
                  link={candidate.ruleViolationLink}
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

// i: number, candidates: Array<{}>, ranking: {[number]: number}, isReferendum: boolean, changeRanking: func
const Selector = ({ i, candidates, ranking, isReferendum, changeRanking }) => {
  const theme = useTheme();
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
              : candidate.candidateName}
          </MenuItem>
        ))}
      </Select>
      {duplicateSelected && (
        <ErrorText variant="subtitle2" $isDark={theme.palette.type === "dark"}>
          <FormHelperText>
            Same candidate selected multiple times
          </FormHelperText>
        </ErrorText>
      )}
      {outOfOrder && (
        <ErrorText variant="subtitle2" $isDark={theme.palette.type === "dark"}>
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
        Please select as many choices as you want using the dropdown menus.
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
        accum[val.id] = val.candidateName;
        return accum;
      }, {}),
    [candidates]
  );
  const rankingLen = Object.keys(ranking).length;
  return (
    <>
      <Typography variant="h2">Selected Ranking</Typography>
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
        <Typography variant="body2">
          {isReferendum
            ? "Do you support this referendum?"
            : "Do you support this candidate?"}
          &nbsp;
          {Object.values(ranking)[0] ===
          candidates.filter((candidate) => candidate.statement != null)[0].id
            ? "Yes"
            : idToNameMap[ranking[0]]}
        </Typography>
      )}
      {/* Case: multiple candidates and vote(s) has been selected */}
      {rankingLen > 0 &&
        candidates.length > 2 &&
        Object.entries(ranking).map((rank) => (
          <Typography variant="body2" key={rank[0]}>
            {parseInt(rank[0], 10) + 1}. {idToNameMap?.[rank[1]] ?? "error bro"}
          </Typography>
        ))}
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
      <ButtonDiv>
        <Button
          variant="outlined"
          color="secondary"
          onClick={() => onClose()}
          disableElevation
        >
          Cancel
        </Button>
        <SpoilBallotBtn
          $isDark={isDark}
          variant="outlined"
          onClick={() => spoilBallot()}
          data-testid="spoilModalConfirm"
          disableElevation
        >
          Spoil ballot
        </SpoilBallotBtn>
      </ButtonDiv>
    </SpoilModalPaper>
  </Modal>
);

// handleClose: func, handleSubmit: func, open: boolean, isReferendum: boolean,
// sortedCandidates: Array<{}>, electionName: string
export const BallotModal = ({
  handleClose,
  handleSubmit,
  open,
  isReferendum,
  sortedCandidates,
  electionName,
}) => {
  const theme = useTheme();
  const isDark = theme.palette.type === "dark";

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
    handleSubmit(ranking);
    closeForm();
  };
  const spoilBallot = () => {
    handleSubmit({});
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
          />
          <Divider />
          <SelectedRanking
            isReferendum={isReferendum}
            ranking={ranking}
            candidates={sortedCandidates}
          />
          <Divider />
          <ButtonDiv>
            <SpoilBallotBtn
              $isDark={isDark}
              variant="outlined"
              onClick={() => setOpenConfirmSpoil(true)}
              disableElevation
            >
              Spoil ballot
            </SpoilBallotBtn>
            <div>
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => closeForm()}
                disableElevation
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
                disableElevation
              >
                Cast ballot
              </Button>
            </div>
          </ButtonDiv>
        </ModalPaper>
      </Modal>
    </>
  );
};

const EnhancedBallotModal = ({ handleClose, open, id }) => {
  const handleSubmit = useHandleSubmit(id);
  // Remove this later with get from API
  const mockElections = {
    0: MockBallotReferenda,
    2: MockBallotPresident,
    3: MockBallotVP,
  };
  if (id == null || !Object.keys(mockElections).includes(id.toString())) {
    return null;
  }
  const ballotInfo = mockElections[id];

  const { category, candidates, electionName } = ballotInfo;
  const isReferendum = category === "Referenda";

  let candidatesList = [];
  // Seperate ron from non-ron candidates
  const ron = candidates.filter(
    (candidate) => candidate.candidateName === "Reopen Nominations"
  )[0];
  let nonRon = candidates.filter(
    (candidate) => candidate.candidateName !== "Reopen Nominations"
  );

  if (!isReferendum && candidates.length > 2) {
    // Randomly shuffle the list, then append RON to the end
    nonRon = shuffleArray(nonRon);
    candidatesList = nonRon.concat(ron);
  } else if (candidates.length === 2) {
    // Replace ron with No
    const noSelection = {
      id: ron.id,
      candidateName: "No",
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
      electionName={electionName}
    />
  );
};

export default EnhancedBallotModal;
