import axios from "axios";
import { useSnackbar } from "notistack";
import { renderHook, act } from "@testing-library/react-hooks";
import {
  useGetElectionSession,
  useGetEligibleElections,
  useGetMessages,
} from "hooks/ElectionHooks";

jest.mock("axios");
jest.mock("notistack");

describe("useGetMessages", () => {
  beforeEach(() => {
    useSnackbar.mockImplementation(() => ({
      enqueueSnackbar: jest.fn(),
    }));
  });

  it("fetches messages successfully from API", async () => {
    const response = {
      status: 200,
      data: ["Hi", "Bye"],
    };
    axios.get.mockResolvedValueOnce(response);
    const { result } = renderHook(() => useGetMessages());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual(response.data[0]);
    });
  });

  it("returns null if status is not 200", async () => {
    const response = {
      status: 404,
    };
    axios.get.mockResolvedValueOnce(response);
    const { result } = renderHook(() => useGetMessages());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual(null);
    });
  });

  it("enqueues snackbar if API errors out", async () => {
    const enqueueSnackbar = jest.fn();
    useSnackbar.mockImplementation(() => ({ enqueueSnackbar }));

    axios.get.mockResolvedValueOnce(Promise.reject(new Error("Network Error")));
    const { result } = renderHook(() => useGetMessages());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual(null);
    });
    await expect(enqueueSnackbar).toHaveBeenCalled();
  });
});

describe("useGetElectionSession", () => {
  beforeEach(() => {
    useSnackbar.mockImplementation(() => ({
      enqueueSnackbar: jest.fn(),
    }));
  });

  it("fetches successfully from API with an election session", async () => {
    const response = {
      status: 200,
      data: [
        {
          name: "Test",
          start_time: "2021-06-19T05:01:02.181Z",
          end_time: "2021-06-19T05:01:02.181Z",
        },
      ],
    };
    axios.get.mockResolvedValueOnce(response);
    const { result } = renderHook(() => useGetElectionSession());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual(response.data[0]);
    });
  });

  it("fetches successfully from API with no election session", async () => {
    const response = {
      status: 200,
      data: [],
    };
    axios.get.mockResolvedValueOnce(response);
    const { result } = renderHook(() => useGetElectionSession());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual({});
    });
  });

  it("returns null if status is not 200", async () => {
    const response = {
      status: 404,
    };
    axios.get.mockResolvedValueOnce(response);
    const { result } = renderHook(() => useGetElectionSession());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual(null);
    });
  });

  it("enqueues snackbar if API errors out", async () => {
    const enqueueSnackbar = jest.fn();
    useSnackbar.mockImplementation(() => ({ enqueueSnackbar }));

    axios.get.mockResolvedValueOnce(Promise.reject(new Error("Network Error")));
    const { result } = renderHook(() => useGetElectionSession());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual(null);
    });
    await expect(enqueueSnackbar).toHaveBeenCalled();
  });
});

describe("useGetEligibleElections", () => {
  beforeEach(() => {
    useSnackbar.mockImplementation(() => ({
      enqueueSnackbar: jest.fn(),
    }));
  });

  it("fetches successfully from API with eligible elections", async () => {
    const response = {
      status: 200,
      data: [
        {
          id: 0,
          election_name: "test",
          category: "referenda",
          seats_available: 1,
          candidates: [
            {
              id: 0,
              name: "Test McTest",
              statement: "Yolo",
              disqualified_status: false,
            },
          ],
        },
      ],
    };
    const responseExpected = {
      0: {
        id: 0,
        election_name: "test",
        category: "referenda",
        seats_available: 1,
        candidates: [
          {
            id: 0,
            name: "Test McTest",
            statement: "Yolo",
            disqualified_status: false,
          },
        ],
      },
    };
    axios.get.mockResolvedValueOnce(response);
    const { result } = renderHook(() => useGetEligibleElections());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual(responseExpected);
    });
  });

  it("fetches successfully from API with no eligible elections", async () => {
    const response = {
      status: 200,
      data: [],
    };
    axios.get.mockResolvedValueOnce(response);
    const { result } = renderHook(() => useGetEligibleElections());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual({});
    });
  });

  it("returns null if status is not 200", async () => {
    const response = {
      status: 404,
    };
    axios.get.mockResolvedValueOnce(response);
    const { result } = renderHook(() => useGetEligibleElections());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual(null);
    });
  });

  it("enqueues snackbar if API errors out", async () => {
    const enqueueSnackbar = jest.fn();
    useSnackbar.mockImplementation(() => ({ enqueueSnackbar }));

    axios.get.mockResolvedValueOnce(Promise.reject(new Error("Network Error")));
    const { result } = renderHook(() => useGetEligibleElections());

    await act(async () => {
      const apiResponse = result.current();
      return expect(apiResponse).resolves.toEqual(null);
    });
    await expect(enqueueSnackbar).toHaveBeenCalled();
  });
});
