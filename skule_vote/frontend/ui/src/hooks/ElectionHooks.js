import { get } from "api/api";
import { useSnackbar } from "notistack";

export const useGetElectionSession = () => {
  const { enqueueSnackbar } = useSnackbar();

  return async function getElectionSession() {
    try {
      const response = await get("/api/electionsession/");
      if (response.status === 200) {
        return response.data[0] ?? {};
      }
    } catch (e) {
      enqueueSnackbar(
        {
          message: `Failed to fetch election session: ${e.message}`,
          variant: "error",
        },
        { variant: "error" }
      );
    }
    return null;
  };
};

export const useHandleSubmit = (electionId) => {
  const { enqueueSnackbar } = useSnackbar();

  return function handleSubmit(ranking) {
    // Get response here once API is set up
    console.log(JSON.stringify({ electionId, ranking }, null, 2));

    // Variant is repeated as a hack in order to use a custom snackbar
    enqueueSnackbar(
      { message: "Your vote has been successfully cast", variant: "success" },
      { variant: "success" }
    );
    enqueueSnackbar(
      {
        message: "Unable with vote due to Error: <error from response>.",
        variant: "error",
      },
      { variant: "error" }
    );
  };
};
