import { useState, useCallback } from "react";
import { get } from "api/api";
import { useSnackbar } from "notistack";

export const statusIsGood = (code) => {
  return code >= 200 && code < 300;
};

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

export const useGetEligibility = () => {
  const { enqueueSnackbar } = useSnackbar();

  return async function getEligibility() {
    try {
      const response = await get("/api/votereligible");
      if (statusIsGood(response.status)) {
        if (response.data.voter_eligible) {
          enqueueSnackbar(
            {
              message: "You are an eligible student",
              variant: "success",
            },
            { variant: "success" }
          );
        } else {
          enqueueSnackbar(
            {
              message: "You are not an eligible student",
              variant: "warning",
            },
            { variant: "warning" }
          );
        }
      }
    } catch (e) {
      enqueueSnackbar(
        {
          message: `Failed to get voter eligibility: ${
            e.response?.data?.detail ?? e.message ?? e.response?.status
          }`,
          variant: "error",
        },
        { variant: "error" }
      );
    }
    return null;
  };
};
