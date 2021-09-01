import { get, post } from "api/api";
import { useSnackbar } from "notistack";
import { statusIsGood } from "hooks/GeneralHooks";

export const useGetElectionSession = () => {
  const { enqueueSnackbar } = useSnackbar();

  return async function getElectionSession() {
    try {
      const response = await get("/api/electionsession/");
      if (statusIsGood(response.status)) {
        return response.data[0] ?? {};
      }
    } catch (e) {
      enqueueSnackbar(
        {
          message: `Failed to fetch election session: ${
            e.response?.data?.detail ?? e.response?.status
          }`,
          variant: "error",
        },
        { variant: "error" }
      );
    }
    return null;
  };
};

export const useGetEligibleElections = () => {
  const { enqueueSnackbar } = useSnackbar();

  return async function getEligibleElections() {
    try {
      const response = await get("/api/elections/");
      if (statusIsGood(response.status)) {
        return response.data == null
          ? {}
          : response.data.reduce((accum, val) => {
              accum[val.id] = val;
              return accum;
            }, {});
      }
    } catch (e) {
      enqueueSnackbar(
        {
          message: `Failed to fetch eligible elections: ${
            e.response?.data?.detail ?? e.response?.status
          }`,
          variant: "error",
        },
        { variant: "error" }
      );
    }
    return null;
  };
};

export const useHandleSubmit = (setEligibleElections) => {
  const { enqueueSnackbar } = useSnackbar();

  return async function handleSubmit(electionId, ranking) {
    if (electionId == null) {
      return null;
    }
    try {
      const response = await post("/api/vote/", { electionId, ranking });
      if (statusIsGood(response.status)) {
        enqueueSnackbar(
          {
            message: "Your vote has been successfully cast",
            variant: "success",
          },
          { variant: "success" }
        );
        // Remove this election from the list of eligible elections
        setEligibleElections((prevState) => {
          if (prevState == null) {
            return prevState;
          }
          const updated = { ...prevState };
          updated[electionId] = null;
          delete updated[electionId];
          return updated;
        });
      }
    } catch (e) {
      enqueueSnackbar(
        {
          message: `Failed to submit vote: ${
            e.response?.data?.detail ?? e.response?.status
          }`,
          variant: "error",
        },
        { variant: "error" }
      );
    }
    return null;
  };
};
