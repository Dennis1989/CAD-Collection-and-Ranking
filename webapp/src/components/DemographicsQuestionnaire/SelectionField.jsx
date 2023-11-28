import React, { useState } from "react";

export function SelectionField({
  label,
  options,
  initialSelection,
  customInputOption,
  placeholder,
  userInput,
  setUserInput,
}) {

  const [curSelection, setCurSelection] = useState((initialSelection !== undefined) ? initialSelection : "")
  const [customInput, setCustomInput] = useState("")

  function onSelectionChange(e) {
    let selection = e.target.value;
    setCurSelection(selection);

    if (customInputOption !== undefined && selection === customInputOption) {
      // set user input if switching back to custom option
      setUserInput(customInput);
    } else {
      setUserInput(selection);
    }
  }

  function onCustomInputChange(e) {
    let newInput = e.target.value
    setCustomInput(newInput)

    if (customInputOption !== undefined && curSelection === customInputOption) {
      // set user input if switching back to custom option
      setUserInput(newInput);
    }
  }

  return (
    <>
      <label
        className="block text-gray-700 text-sm font-bold mb-2"
        htmlFor="selection"
      >
        {label}
      </label>
      <select
        className="block appearance-none shadow w-full bg-white border border-gray-200 text-gray-700 py-2 px-3 pr-8 mb-2 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
        id="selection"
        onChange={onSelectionChange}
      >
        {initialSelection === undefined && <option value="" hidden></option>}
        {initialSelection !== undefined && (
          <option key={-1} value={initialSelection}>{initialSelection}</option>
        )}

        {options.map((option, index) => (
          <option key={index} value={option}>{option}</option>
        ))}

        {customInputOption !== undefined && (
          <option key={-2} value={customInputOption}>{customInputOption}</option>
        )}
      </select>


      {customInputOption !== undefined && curSelection === customInputOption && (
        <input
          className="w-full shadow appearance-none border rounded w-1/2 mb-2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="customInput"
          type="text"
          placeholder={placeholder}
          onChange={onCustomInputChange}
          value={customInput}
        />
      )}
    </>
  );
}
