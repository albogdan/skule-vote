import React from "react";
import { styled } from "@mui/system";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Modal from "@mui/material/Modal";
import WarningIcon from "@mui/icons-material/Warning";
import Stack from "@mui/material/Stack";

const TwoButtonDiv = styled("div")(({ theme }) => ({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  width: "100%",
  "> button:last-child": {
    marginLeft: 4,
    [theme.breakpoints.down("xs")]: {
      marginLeft: 0,
      marginTop: 16,
    },
  },
  [theme.breakpoints.down("xs")]: {
    flexDirection: "column",
    button: {
      width: "100%",
    },
  },
}));

export const ModalPaper = styled(Paper)(({ theme }) => ({
  position: "absolute",
  padding: 32,
  margin: "50px auto",
  maxWidth: 900,
  width: "100%",
  maxHeight: "calc(100% - 100px)",
  left: 0,
  right: 0,
  overflowY: "auto",
  outline: "none",
  [theme.breakpoints.down("sm")]: {
    padding: "24px 16px 40px",
    margin: "24px auto",
    maxHeight: "calc(100% - 48px)",
  },
  hr: {
    margin: "24px 0",
    [theme.breakpoints.down("sm")]: {
      margin: "16px 0",
    },
  },
  "h1, h2": {
    fontWeight: 400,
  },
  h3: {
    margin: "16px 0 8px",
    [theme.breakpoints.down("sm")]: {
      marginTop: 16,
    },
  },
}));

const SubModalPaper = styled(ModalPaper)(({ theme }) => ({
  marginTop: "100px !important",
  maxWidth: 500,
  [theme.breakpoints.down("sm")]: {
    padding: "32px 16px 16px",
  },
}));

const SpoilBallotBtnFilled = styled(Button)(({ theme }) => ({
  color: "#fff",
  backgroundColor: "#5f518d !important",
  ":hover": {
    backgroundColor: "#51496b !important",
  },
}));

// Modal that opens to confirm you want to spoil your ballot
// open: boolean, onClose: func, spoilBallot: func
export const ConfirmSpoilModal = ({ open, onClose, spoilBallot }) => (
  <Modal
    open={open}
    onClose={onClose}
    aria-labelledby="confirm-spoil-modal"
    aria-describedby="confirm-spoil-modal"
  >
    <SubModalPaper>
      <Typography variant="h3">
        Are you sure you want to spoil your ballot?
      </Typography>
      <Divider />
      <TwoButtonDiv>
        <Button variant="outlined" color="secondary" onClick={() => onClose()}>
          Back
        </Button>
        <SpoilBallotBtnFilled
          onClick={() => spoilBallot()}
          data-testid="spoilModalConfirm"
        >
          Spoil ballot
        </SpoilBallotBtnFilled>
      </TwoButtonDiv>
    </SubModalPaper>
  </Modal>
);

// Modal that opens to confirm you want to cast your ballot even though you didn't rank every candidate
// open: boolean, onClose: func, castBallot: func
export const PleaseRankModal = ({ open, onClose, castBallot }) => (
  <Modal
    open={open}
    onClose={onClose}
    aria-labelledby="rank-all-modal"
    aria-describedby="rank-all-modal"
  >
    <SubModalPaper>
      <Stack direction="row" alignItems="flex-start" spacing={2} mt={2}>
        <WarningIcon color="warning" />
        <Typography variant="h3">
          You didn't rank all your choices. Would you like to go back?
        </Typography>
      </Stack>
      <Divider />
      <TwoButtonDiv>
        <Button
          variant="outlined"
          color="secondary"
          onClick={() => castBallot()}
          data-testid="pleaseRankModalConfirm"
        >
          No, cast my vote
        </Button>
        <Button color="primary" onClick={() => onClose()}>
          Yes, take me back
        </Button>
      </TwoButtonDiv>
    </SubModalPaper>
  </Modal>
);
