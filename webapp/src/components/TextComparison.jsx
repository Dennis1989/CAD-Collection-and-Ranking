import React from "react";
import { HighlightedText } from "./HighlightedText.jsx";
import { getLevenshteinOplist } from "./util";

export function TextComparison({ sentence1, sentence2 }) {
  const tokens1 = sentence1.split(" ")
  const tokens2 = sentence2.split(" ")

  const [oplist1, oplist2] = getLevenshteinOplist(tokens1, tokens2);

  return (
    <div className="p-2">
      <table>
        <colgroup>
          <col span="1" className="w-20"></col>
          <col span="1" className=""></col>
        </colgroup>

        <tbody>
          <tr>
            <td className="border-0 p-0 font-semibold">Before:</td>
            <td className="border-0 p-0">
              <HighlightedText tokens={tokens1} oplist={oplist1} />
            </td>
          </tr>
          <tr>
            <td className="border-0 p-0 font-semibold">After:</td>
            <td className="border-0 p-0">
              <HighlightedText tokens={tokens2} oplist={oplist2} />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
