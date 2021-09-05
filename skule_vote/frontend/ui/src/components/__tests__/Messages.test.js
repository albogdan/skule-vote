import React from "react";
import { render } from "@testing-library/react";
import { readableDate } from "pages/ElectionPage";
import Messages from "components/Messages";

describe("<Messages />", () => {
  const start = "2021-06-12T00:00:00-04:00"; // June 12, 2021
  const end = "2021-06-14T00:00:00-04:00"; // June 14, 2021
  let times;

  beforeEach(() => {
    const [startTime, startTimeStr] = readableDate(start);
    const [, endTimeStr] = readableDate(end);
    times = [startTime, startTimeStr, endTimeStr];
  });

  it("renders messages", () => {
    const { getByText } = render(
      <Messages
        times={times}
        electionIsLive={true}
        messages={[
          { message: "Lisa is cool" },
          { message: "Skule Vote is cool" },
        ]}
      />
    );
    expect(getByText("Lisa is cool")).toBeInTheDocument();
    expect(getByText("Skule Vote is cool")).toBeInTheDocument();
  });

  it("renders message notifying the end of the election", () => {
    jest
      .spyOn(Date, "now")
      .mockImplementation(() => Date.parse("2021-06-13T00:00:00-04:00")); // June 13, 2021

    const { getByText, queryByText } = render(
      <Messages times={times} electionIsLive={true} messages={[]} />
    );
    expect(getByText(`Elections close on ${times[2]}.`)).toBeInTheDocument();
    expect(
      queryByText(`There's an upcoming election starting on ${times[1]}.`)
    ).not.toBeInTheDocument();
  });

  it("renders message notifying the start of an upcoming election", () => {
    jest
      .spyOn(Date, "now")
      .mockImplementation(() => Date.parse("2021-06-10T00:00:00-04:00")); // June 10, 2021

    const { getByText, queryByText } = render(
      <Messages times={times} electionIsLive={false} messages={[]} />
    );
    expect(
      getByText(`There's an upcoming election starting on ${times[1]}.`)
    ).toBeInTheDocument();
    expect(
      queryByText(`Elections close on ${times[2]}.`)
    ).not.toBeInTheDocument();
  });

  it("renders no messages", () => {
    const { queryByText } = render(
      <Messages
        times={[null, null, null]}
        electionIsLive={false}
        messages={[]}
      />
    );
    expect(
      queryByText(/There's an upcoming election starting on/)
    ).not.toBeInTheDocument();
    expect(queryByText(/Elections close on/)).not.toBeInTheDocument();
  });
});
