import React from "react";
import styled from "styled-components";
import Alert from "@material-ui/lab/Alert";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";

const colorMap = {
  info: { fill: "#DDECF6", stroke: "#7FC1E3" },
  warning: { fill: "#FDF0DF", stroke: "#FDC26F" },
  success: { fill: "#DFF3EB", stroke: "#8CD6B7" },
  error: { fill: "#FFD5D5", stroke: "#FF8E8E" },
};

const AlertDiv = styled.div`
  > div {
    background-color: ${(props) => props.fill};
    border-color: ${(props) => props.stroke};
    width: 100%;
    font-size: 16px;
  }
`;

export const CustomAlert = ({ message, type, BallotAlert }) => {
  if (!["info", "warning", "success", "error"].includes(type)) {
    return;
  }
  const CloseBtn = (
    <IconButton
      aria-label="close"
      color="inherit"
      size="small"
      onClick={BallotAlert}
    >
      <CloseIcon fontSize="inherit" />
    </IconButton>
  );

  return (
    <AlertDiv fill={colorMap[type].fill} stroke={colorMap[type].stroke}>
      <Alert
        variant="outlined"
        severity={type}
        action={BallotAlert && CloseBtn}
      >
        {message}
      </Alert>
    </AlertDiv>
  );
};
