import React from "react";
import styled from "styled-components";

const StyledDiv = styled.div`
  width: 1px;
  height: 1px;
  padding-top: ${({ y }) => y}px;
  padding-left: ${({ x }) => x}px;
  display: ${({ x }) => (x ? "inline-block" : "block")};
`;

export const Spacer = ({ x = 0, y = 0 }) => <StyledDiv x={x} y={y} />;
