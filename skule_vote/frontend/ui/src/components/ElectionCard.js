import React from "react";
import styled from "styled-components";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import { responsive } from "assets/breakpoints";

const BaseCard = styled(Paper)`
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 400px;
  width: 100%;
  padding: 24px;
  box-shadow: none;
  text-align: center;
  @media ${responsive.smDown} {
    padding: 16px;
  }
`;

const Card = styled(BaseCard)`
  cursor: pointer;
  &:hover {
    opacity: 0.9;
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.14), 0px 3px 4px rgba(0, 0, 0, 0.12);
  }
`;

const Subtitle = styled(Typography)`
  margin-top: 4px;
  opacity: 0.65;
`;

const ElectionCard = ({ title, numCandidates, openModal }) => {
  let subtitle;
  if (numCandidates > 1) {
    subtitle = `${numCandidates} Candidates`;
  } else if (numCandidates === 1) {
    subtitle = `${numCandidates} Candidate`;
  }
  return (
    <Card onClick={openModal}>
      <Typography variant="body2">{title}</Typography>
      {subtitle && <Subtitle variant="subtitle1">{subtitle}</Subtitle>}
    </Card>
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
