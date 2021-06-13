import { useState, useCallback } from "react";
import axios from "axios";
import { get } from "api/api";

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

export async function getElectionSession() {
  try {
    const response = await get("/api/electionsession/");
    if (response.status === 200) {
      return response.data[0] ?? {};
    }
  } catch {
    // handle a flash error here
    // Have to merge snackbar PR
  }
  return null;
}
