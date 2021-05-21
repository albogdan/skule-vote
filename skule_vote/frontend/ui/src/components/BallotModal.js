import React from "react";
import styled from "styled-components";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import ClearIcon from "@material-ui/icons/Clear";
import IconButton from "@material-ui/core/IconButton";
import Modal from "@material-ui/core/Modal";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";
import { responsive } from "assets/breakpoints";

import { MockBallotVP } from "assets/mocks";

// const useStyles = makeStyles((theme) => ({
//   paper: {
//     position: "absolute",
//     width: 400,
//     backgroundColor: theme.palette.background.paper,
//     border: "2px solid #000",
//     boxShadow: theme.shadows[5],
//     padding: theme.spacing(2, 4, 3),
//   },
// }));
const ModalPaper = styled(Paper)`
  position: absolute;
  padding: 32px;
  margin: 100px auto;
  max-width: 900px;
  width: 100%;
  hr {
    margin: 24px 0;
  }
  h1,
  h2 {
    font-weight: 400;
  }
`;

const HeaderDiv = styled.div`
  display: flex;
  justify-content: space-between;
  width: 100%;
`;

const Statements = ({ isReferendum, candidates }) => {
  return (
    <>
      {!isReferendum && (
        <Typography variant="h2">Candidates &amp; Statements</Typography>
      )}
    </>
  );
};

const BallotDropdowns = ({ isReferendum, candidates }) => {
  return (
    <>
      {" "}
      <Typography variant="h2">Ballot</Typography>
      <Typography variant="body1">
        Please select as many choices as you want using the dropdown menus
      </Typography>
    </>
  );
};

const SelectedRanking = ({ isReferendum }) => {
  return (
    <>
      <Typography variant="h2">Selected Ranking</Typography>
      <Typography variant="body1">
        Please confirm that your choice(s) are correctly reflected here and
        submit
      </Typography>
    </>
  );
};

const Selector = () => (
  <FormControl variant="outlined" className={classes.formControl}>
    <InputLabel id="demo-simple-select-outlined-label">Age</InputLabel>
    <Select
      labelId="demo-simple-select-outlined-label"
      id="demo-simple-select-outlined"
      value={age}
      onChange={handleChange}
      label="Age"
    >
      <MenuItem value="">
        <em>None</em>
      </MenuItem>
      <MenuItem value={10}>Ten</MenuItem>
      <MenuItem value={20}>Twenty</MenuItem>
      <MenuItem value={30}>Thirty</MenuItem>
    </Select>
  </FormControl>
);
const BallotModal = ({ handleClose, open, ballotInfo = MockBallotVP }) => {
  const { electionName, election_id, category, candidates } = ballotInfo;
  const isReferendum = category === "Referenda";

  return (
    <Modal
      open={open}
      onClose={handleClose}
      aria-labelledby="simple-modal-title"
      aria-describedby="simple-modal-description"
    >
      <ModalPaper>
        <HeaderDiv>
          <Typography variant="h1">{electionName}</Typography>
          <IconButton
            data-testid="drawerClose"
            onClick={handleClose}
            role="close"
          >
            <ClearIcon />
          </IconButton>
        </HeaderDiv>
        <Divider />
        <Statements isReferendum={isReferendum} candidates={candidates} />
        <Divider />
        <BallotDropdowns isReferendum={isReferendum} candidates={candidates} />
        <Divider />
        <SelectedRanking isReferendum={isReferendum} />
        <Divider />
      </ModalPaper>
    </Modal>
  );
};

export default BallotModal;
