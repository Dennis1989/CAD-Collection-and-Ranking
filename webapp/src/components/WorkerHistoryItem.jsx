import React, { useEffect, useState } from "react";
import Tippy from "@tippyjs/react";
import "tippy.js/dist/tippy.css";
import { getLevenshteinOplist } from "./util";
import { HighlightedText } from "./HighlightedText.jsx";

export function WorkerHistoryItem({ item }) {
  const [expanded, setExpanded] = useState(false);

  const handleToggleExpand = () => {
    setExpanded(!expanded);
  };

  useEffect(() => {
    setExpanded(false);
  }, [item]);

  if (item.stage === "RANKING") {
    return (
      <>
        <tr>
          <td className="border-left"></td>
          <td className="p-2 font-semibold">Ranked Sentences</td>
          <td className="border p-2">{item.finished_time}</td>
          <td className="border p-2">
            <button
              className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full w-full"
              onClick={handleToggleExpand}
            >
              {expanded ? "Hide" : "Expand"}
            </button>
          </td>
        </tr>
        {expanded && (
          <tr>
            <td></td>
            <td className="p-2" colSpan="3">
              <ol className="list-decimal pl-4">
                {item.output_ranking.map((ranking, index) => (
                  <li key={index} className="py-1">
                    {ranking}
                  </li>
                ))}
              </ol>
            </td>
          </tr>
        )}
      </>
    );
  } else {
    const tokens1 = item.original.split(" ");
    const tokens2 = item.cad.split(" ");

    const [oplist1, oplist2] = getLevenshteinOplist(tokens1, tokens2);
    return (
      <>
        <tr>
          <td className="border-left">
            {item.num_first_place > 0 && (
              <Tippy
                content="Number of times this sentence was ranked first by someone else"
                placement="bottom"
              >
                <div>⭐ {item.num_first_place}</div>
              </Tippy>
            )}
          </td>
          <td className=" p-2 font-semibold">Generated Sentence</td>
          <td className="border p-2">{item.finished_time}</td>
          <td className="border p-2">
            <button
              className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full w-full"
              onClick={handleToggleExpand}
            >
              {expanded ? "Hide" : "Expand"}
            </button>
          </td>
        </tr>
        {expanded && (
          <tr>
            <td></td>
            <td className="p-2" colSpan="3">
              <table>
                <colgroup>
                  <col span="1" className="w-32"></col>
                  <col span="1" className=""></col>
                </colgroup>

                <tbody>
                  <tr>
                    <td className="border-0 p-0 font-semibold">Original:</td>
                    <td className="border-0 p-0">
                      <HighlightedText tokens={tokens1} oplist={oplist1} />
                    </td>
                  </tr>
                  <tr>
                    <td className="border-0 p-0 font-semibold">
                      Your Sentence:
                    </td>
                    <td className="border-0 p-0">
                      <HighlightedText tokens={tokens2} oplist={oplist2} />
                    </td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        )}
      </>
    );
  }
}
