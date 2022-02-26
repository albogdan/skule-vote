import React, { forwardRef } from "react";
import { styled } from "@mui/system";
import { useSnackbar } from "notistack";
import Alert from "@mui/material/Alert";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";

const fillColorMap = {
  info: "#DDECF6",
  warning: "#FDF0DF",
  success: "#DFF3EB",
  error: "#FBDFDF",
};

const AlertDiv = styled("div", {
  shouldForwardProp: (propName) => propName !== "fill",
})(({ theme, fill }) => ({
  "> div": {
    width: "100%",
    backgroundColor: theme.palette.mode === "dark" ? "#171717" : fill,
    fontSize: 16,
  },
}));

// According to notistack documentation, component must use forwardRef
// in order for transition animations to work
export const CustomAlert = forwardRef((props, ref) => {
  const { message, variant } = props.options;
  const { closeSnackbar } = useSnackbar();
  if (!["info", "warning", "success", "error"].includes(variant)) {
    return null;
  }
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
    <AlertDiv ref={ref} fill={fillColorMap[variant]}>
      <Alert variant="outlined" severity={variant} action={CloseBtn}>
        {message}
      </Alert>
    </AlertDiv>
  );
});

// CustomMessage cannot be closed unlike CustomAlert
export const CustomMessage = ({ message, variant }) => {
  if (!["info", "warning", "success", "error"].includes(variant)) {
    return null;
  }

  return (
    <AlertDiv fill={fillColorMap[variant]}>
      <Alert variant="outlined" severity={variant}>
        {message}
      </Alert>
    </AlertDiv>
  );
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
