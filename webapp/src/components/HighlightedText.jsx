import React from "react";
import { StepInformation } from "./util";

export function HighlightedText({oplist, tokens}) {
  if (oplist.length !== tokens.length) {
    throw new Error("Highlights and tokens are of unequal length.")
  }
  return (
    <>
    {tokens.map((token, index) => highlightEntry(token, oplist[index], index))}
    </>
  )
}

function highlightEntry(token, op, index) {
  switch(op) {
    case StepInformation.keep:
      return (
      <span key={index} className="">
        {token}{' '}
      </span>)
    case StepInformation.remove:
      return (
      <span key={index} className="text-red-500">
        {token}{' '}
      </span>)
    case StepInformation.insert:
      return (
      <span key={index} className="text-green-500">
        {token}{' '}
      </span>)
    case StepInformation.edit:
      return (
      <span key={index} className="text-yellow-500">
        {token}{' '}
      </span>)
  }

}