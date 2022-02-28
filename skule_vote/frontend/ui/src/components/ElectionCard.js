import React from "react";
import { styled } from "@mui/system";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";

const BaseCard = styled(Paper)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  maxWidth: 400,
  width: "100%",
  padding: 24,
  boxShadow: "none",
  textAlign: "center",
  [theme.breakpoints.down("sm")]: {
    padding: 16,
  },
}));

const ElectionButton = styled(Button)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  backgroundColor: theme.palette.background.paper,
  color: "inherit",
  textTransform: "none",
  maxWidth: 400,
  padding: 24,
  boxShadow: "none",
  [theme.breakpoints.down("sm")]: {
    padding: 16,
  },
  ":hover": {
    opacity: 0.9,
    backgroundColor: theme.palette.background.paper,
    boxShadow:
      "0px 2px 4px rgba(0, 0, 0, 0.14), 0px 3px 4px rgba(0, 0, 0, 0.12)",
  },
}));

const ElectionCard = ({
  category,
  title,
  seatsAvailable,
  openModal,
  numCandidates,
}) => {
  return (
    <ElectionButton onClick={openModal} color="primary">
      <Typography variant="body2">{title}</Typography>
      {category !== "referenda" && (
        <Typography variant="subtitle1" sx={{ mt: 0.5, opacity: 0.65 }}>
          {seatsAvailable} position{seatsAvailable > 1 && "s"} to be filled
          &nbsp;|&nbsp; {numCandidates - 1} candidate
          {numCandidates > 2 && "s"}
        </Typography>
      )}
    </ElectionButton>
  );
};

export const NoElectionsCard = ({ filterCategory }) => {
  const message =
    filterCategory === "All"
      ? "There are no elections that you are currently eligible to vote in."
      : `There are no ${filterCategory} ${
          filterCategory === "Referenda" ? "" : "elections"
        } that you are currently eligible to vote in.`;

  return (
    <BaseCard>
      <Typography variant="body1">{message}</Typography>
    </BaseCard>
  );
};

export default ElectionCard;
