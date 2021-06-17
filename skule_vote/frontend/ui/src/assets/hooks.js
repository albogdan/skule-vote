import { useState, useCallback } from "react";
import { useSnackbar } from "notistack";

export function useLocalStorage(key, initValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initValue;
    } catch (error) {
      return initValue;
    }
  });

  const setValue = useCallback(
    (value) => {
      try {
        setStoredValue(value);
        window.localStorage.setItem(key, JSON.stringify(value));
      } catch (error) {
        //   handle
      }
    },
    [key]
  );

  const removeKey = useCallback(() => {
    window.localStorage.removeItem(key);
    setStoredValue(undefined);
  }, [key]);

  return [storedValue, setValue, removeKey];
}

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
