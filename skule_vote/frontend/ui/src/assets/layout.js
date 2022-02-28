import React from "react";
import { styled } from "@mui/system";

const StyledDiv = styled("div", {
  shouldForwardProp: (propName) => propName !== "x" || propName !== "y",
})(({ x, y }) => ({
  width: 1,
  height: 1,
  paddingTop: y,
  paddingLeft: x,
  display: x ? "inline-block" : "block",
}));

export const Spacer = ({ x = 0, y = 0 }) => <StyledDiv x={x} y={y} />;
