import { renderHook, act } from "@testing-library/react-hooks";
import { useLocalStorage } from "assets/hooks";

describe("useLocalStorage", () => {
  it("return value as undefined if not specified", () => {
    const { result } = renderHook(() => useLocalStorage("KEY"));
    expect(result.current[0]).toBeUndefined();
  });

  it("renderz initial value and updates localStorage values", () => {
    const setItemSpy = jest.spyOn(Storage.prototype, "setItem");
    const { result } = renderHook(() => useLocalStorage("KEY", "INIT_VAL"));

    let [val, setVal] = result.current;
    expect(val).toBe("INIT_VAL");

    act(() => setVal("NEW_VAL"));
    [val, setVal] = result.current;
    expect(val).toBe("NEW_VAL");

    expect(setItemSpy).toHaveBeenCalledWith("KEY", JSON.stringify("NEW_VAL"));
    expect(window.localStorage.getItem("KEY")).toBe(JSON.stringify("NEW_VAL"));

    setItemSpy.mockRestore();
  });

  it("uses previously stored value in localStorage instead of initial value parameter", () => {
    const getItemSpy = jest
      .spyOn(Storage.prototype, "getItem")
      .mockImplementation(() => JSON.stringify("PRE_EXISTING"));

    const { result } = renderHook(() => useLocalStorage("KEY", "INIT_VAL"));
    expect(getItemSpy).toHaveBeenCalledWith("KEY");

    const [value] = result.current;
    expect(value).toBe("PRE_EXISTING");
    expect(window.localStorage.getItem("KEY")).toBe(
      JSON.stringify("PRE_EXISTING")
    );

    getItemSpy.mockRestore();
  });

  it("clears and removes item from localStorage", () => {
    const getItemSpy = jest
      .spyOn(Storage.prototype, "getItem")
      .mockImplementation(() => JSON.stringify("PRE_EXISTING"));
    const removeItemSpy = jest
      .spyOn(Storage.prototype, "removeItem")
      .mockImplementation(() => undefined);

    const { result } = renderHook(() => useLocalStorage("KEY", "INIT_VAL"));

    let [value, , remove] = result.current;
    expect(value).toBe("PRE_EXISTING");
    act(() => remove());

    [value, , remove] = result.current;
    expect(value).toBeUndefined();
    expect(removeItemSpy).toHaveBeenCalledWith("KEY");

    getItemSpy.mockRestore();
    removeItemSpy.mockRestore();
  });
});
