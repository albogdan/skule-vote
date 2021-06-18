import axios from "axios";
import notistack, { useSnackbar } from "notistack";
import { renderHook, act } from "@testing-library/react-hooks";
import { useGetElectionSession } from "hooks/ElectionHooks";
import { waitFor } from "@testing-library/react";

jest.mock("axios");

// jest.mock("notistack");

const mockEnqueueSnackbar = jest.fn();
jest.mock("notistack", () => ({
  ...jest.requireActual("notistack"),
  useSnackbar: () => ({ enqueueSnackbar: mockEnqueueSnackbar }),
}));

describe("useGetElectionSession", () => {
  // beforeEach(() => {
  //   useSnackbar.mockImplementation(() => ({ enqueueSnackbar: jest.fn() }));
  // });

  it("fetches successfully from API with an election session", async () => {
    const response = {
      status: 200,
      data: [
        {
          name: "Test",
          start_time: "",
          end_time: "",
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

  it("fetches erroneously data from an API", async () => {
    // const enqueueSnackbar = jest.fn();
    // useSnackbar.mockImplementation(() => ({ enqueueSnackbar }));

    axios.get.mockResolvedValueOnce(Promise.reject(new Error("Network Error")));
    const { result } = renderHook(() => useGetElectionSession());

    await act(async () => {
      const apiResponse = result.current();
      // expect(mockEnqueueSnackbar).toHaveBeenCalled();
      return expect(apiResponse).resolves.toEqual(null);
    });

    await expect(mockEnqueueSnackbar).toHaveBeenCalled();

    // await waitFor(() => expect(mockEnqueueSnackbar).toHaveBeenCalled());
  });
});

// axios.get.mockImplementationOnce()
// await getElectionSession();

// await
// await waitFor(() => {
//   expect(enqueueSnackbar).toHaveBeenCalled();
//   return expect(getElectionSession()).resolves.toEqual(null);
// });

// await expect(getElectionSession()).resolves.toEqual(response.data[0]);
//

// You need to mock the closeSnackbar function, something like this:
