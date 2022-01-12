import React, { forwardRef } from "react";
import styled from "styled-components";
import { useSnackbar } from "notistack";
import Alert from "@mui/material/Alert";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import { useTheme } from "@mui/material/styles";

const fillColorMap = {
  info: "#DDECF6",
  warning: "#FDF0DF",
  success: "#DFF3EB",
  error: "#FBDFDF",
};

const AlertDiv = styled.div`
  > div {
    width: 100%;
    ${(props) => `background-color: ${props.isDark ? "#171717" : props.$fill}`};
    font-size: 16px;
  }
`;

// According to notistack documentation, component must use forwardRef
// in order for transition animations to work
export const CustomAlert = forwardRef((props, ref) => {
  const { message, variant } = props.options;
  const theme = useTheme();
  const { closeSnackbar } = useSnackbar();
  if (!["info", "warning", "success", "error"].includes(variant)) {
    return null;
  }
  const isDark = theme.palette.mode === "dark";
  const CloseBtn = (
    <IconButton
      aria-label="closeAlert"
      color="inherit"
      size="small"
      onClick={() => closeSnackbar(props.id)}
    >
      <CloseIcon data-testid="closeAlert" fontSize="inherit" />
    </IconButton>
  );

  return (
    <AlertDiv ref={ref} $fill={fillColorMap[variant]} isDark={isDark}>
      <Alert variant="outlined" severity={variant} action={CloseBtn}>
        {message}
      </Alert>
    </AlertDiv>
  );
});

// CustomMessage cannot be closed unlike CustomAlert
export const CustomMessage = ({ message, variant }) => {
  const theme = useTheme();
  if (!["info", "warning", "success", "error"].includes(variant)) {
    return null;
  }
  const isDark = theme.palette.mode === "dark";

  return (
    <AlertDiv $fill={fillColorMap[variant]} isDark={isDark}>
      <Alert variant="outlined" severity={variant}>
        {message}
      </Alert>
    </AlertDiv>
  );
};
