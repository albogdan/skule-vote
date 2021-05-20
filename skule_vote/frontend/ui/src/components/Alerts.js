import React from "react";
import styled from "styled-components";
import Alert from "@material-ui/lab/Alert";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
import { useTheme } from "@material-ui/core/styles";

const fillColorMap = {
  info: "#DDECF6",
  warning: "#FDF0DF",
  success: "#DFF3EB",
  error: "#FBDFDF",
};

const AlertDiv = styled.div`
  > div {
    ${(props) => !props.isDark && `background-color: ${props.fill}`};
    width: 100%;
    font-size: 16px;
  }
`;

export const CustomAlert = ({ message, type, action }) => {
  const theme = useTheme();
  if (!["info", "warning", "success", "error"].includes(type)) {
    return;
  }
  const isDark = theme.palette.type === "dark";
  const CloseBtn = (
    <IconButton
      aria-label="close"
      color="inherit"
      size="small"
      onClick={action}
    >
      <CloseIcon fontSize="inherit" />
    </IconButton>
  );

  return (
    <AlertDiv fill={fillColorMap[type]} isDark={isDark}>
      <Alert variant="outlined" severity={type} action={action && CloseBtn}>
        {message}
      </Alert>
    </AlertDiv>
  );
};
