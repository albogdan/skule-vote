import React from "react";
import styled from "styled-components";
import { CustomMessage } from "components/Alerts";

const MessagesDiv = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 800px;
  width: 100%;
  > :not(:last-child) {
    margin-bottom: 8px;
  }
`;

const Messages = ({ electionIsLive, times }) => {
  const [startTime, startTimeStr, endTimeStr] = times;
  return (
    <MessagesDiv>
      {electionIsLive && (
        <CustomMessage
          variant="info"
          message={`Elections close on ${endTimeStr}.`}
        />
      )}
      {startTime != null && startTime > Date.now() && (
        <CustomMessage
          variant="info"
          message={`There's an upcoming election starting on ${startTimeStr}.`}
        />
      )}
    </MessagesDiv>
  );
};

export default Messages;
