import React from "react";
import { styled } from "@mui/system";
import { CustomMessage } from "components/Alerts";

const MessagesDiv = styled("div")({
  display: "flex",
  flexDirection: "column",
  maxWidth: 800,
  width: "100%",
  "> :not(:last-child)": {
    marginBottom: 8,
  },
});

const Messages = ({ electionIsLive, times, messages }) => {
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
      {messages.map((msg, i) => (
        <CustomMessage variant="info" message={msg.message} key={i} />
      ))}
    </MessagesDiv>
  );
};

export default Messages;
