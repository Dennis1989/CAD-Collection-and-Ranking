import React from "react";
import { getInfrequentTokens } from "./util.js";

function RankingInstructions({ onBackclick, onContinueclick }) {
  const exampleranking = [
    "Women are less intelligent than men.",
    "Flies are less intelligent than dogs.",
    "Women are less tall.",
    "Women are as intelligent as men.",
  ];

  const infrequentTokens = getInfrequentTokens(exampleranking);

  const colorToken = (token) => {
    const lowerCaseToken = token.toLowerCase(); // Convert token to lowercase
    if (infrequentTokens.includes(lowerCaseToken)) {
      // Color infrequent tokens
      return <span className="font-extrabold">{token}</span>;
    } else {
      // Regular tokens
      return token;
    }
  };
  return (
    <div className="frame-3 flex flex-col gap-4 p-4">
      <div className="text-center">
        <div className="flex items-center justify-center">
          <div className="w:1/4 md:w-1/2 sm:w-3/4 p-4 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600">
            <div className="font-san font-bold text-lg text-rose-500">
              Read the instructions carefully. Your onboarding performance will
              be assessed, and failure to pay attention may result in exclusion
              from the task.
            </div>

            <div className="bg-cyan-50 rounded-t-2xl p-3">
              <h2 className="font-san font-bold text-lg">
                Instructions for Ranking task
              </h2>

              <div className="flex items-center justify-center p-3">
                <i className="fa fa-list-ol fa-4x" aria-hidden="true"></i>
              </div>
            </div>
            <div className="p-3 text-sm md:text-base lg:text-lg">
              Sort sentences from most sexist at the top to least sexist at the
              bottom.{" "}
            </div>

            <div className="w-full flex justify-center pt-4 pb-2">
              <div className="bg-green-400 text-white font-bold rounded-2xl px-4 py-2 w-fit">
                <span className="pr-2">$</span>
                <span className="ml-2">Bonuses</span>
              </div>
            </div>
            <div>
              A bonus will be awarded if your rankings closely resemble the
              rankings given by other participants for these statements.
              Therefore, be{" "}
              <span className="font-extrabold italic">honest</span> when assessing others.
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center gap-5 sm:flex-row">
        <div className="flex-1 p-3 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600 sm:flex-initial w-full sm:w-auto">
          <div className="flex items-center justify-center p-3 rounded-2xl">
            <h3 className="font-san font-bold flex items-center justify-center text-sm md:text-base lg:text-lg">
              Step 1
            </h3>{" "}
          </div>
          <div className="flex items-center justify-center p-3">
            <i className="fa fa-solid fa-bars fa-4x fa-xl"></i>
            <i class="fa fa-check" style={{ color: "green" }}></i>
          </div>
          <div className="flex items-center justify-center text-center p-3 text-sm md:text-base lg:text-lg">
            Identify the most sexist sentences from the given list of sentences.
          </div>
        </div>
        <div className="flex-1 p-3 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600 sm:flex-initial w-full sm:w-auto">
          <div className="flex items-center justify-center p-3 rounded-2xl">
            <h3 className="font-san font-bold flex items-center justify-center text-sm md:text-base lg:text-lg">
              Step 2
            </h3>{" "}
          </div>
          <div className="flex items-center justify-center p-3">
            <i className="fa fa-solid fa-bars fa-4x fa-xl"></i>
            <i class="fa fa-sort" style={{ color: "red" }}></i>
          </div>
          <div className="flex items-center justify-center text-center p-3 text-sm md:text-base lg:text-lg">
            Drag and move the most sexist sentence to the top of the list.
          </div>
        </div>
        <div className="flex-1 p-3 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600 sm:flex-initial w-full sm:w-auto">
          <div className="flex items-center justify-center p-3 rounded-2xl">
            <h3 className="font-san font-bold flex items-center justify-center text-sm md:text-base lg:text-lg">
              Step 3
            </h3>{" "}
          </div>
          <div className="flex items-baseline justify-center p-3">
            <i className="fa fa-list-ol fa-4x" aria-hidden="true"></i>
          </div>
          <div className="flex items-center justify-center p-3 text-center text-sm md:text-base lg:text-lg">
            Repeat the process until all sentences are sorted from most to least
            sexist.
          </div>
        </div>
      </div>

      <div className="flex items-center justify-center">
        <div className="w:1/4 md:w-1/2 sm:w-3/4 p-2 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600 p-4">
          <h2 className="text-center text-lg font-bold">
            A ranking you might generate:
          </h2>
          <div className="flex justify-center mt-2 text-left">
            <div className="flex flex-row">
              <ol className="list-decimal pl-8">
                {exampleranking.map((sentence, index) => (
                  <li key={index}>
                    {
                      /* Split sentence into tokens, apply coloring, and join them back */
                      sentence.split(/\s+/).map((token, i) => (
                        <React.Fragment key={i}>
                          {colorToken(token)}
                          {i < sentence.split(/\s+/).length - 1 ? " " : ""}
                        </React.Fragment>
                      ))
                    }
                  </li>
                ))}
              </ol>

              {/* labels */}
              <div className="pl-2 flex flex-col justify-between italic font-light">
                <p className="font-thin">most sexist</p>
                <p className="font-thin">least sexist</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="p-3 flex justify-center">
        <button
          className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full mr-2"
          onClick={onBackclick}
        >
          Go back to generation
        </button>
        <button
          className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full"
          onClick={onContinueclick}
        >
          Okay I understood
        </button>
      </div>
    </div>
  );
}
export default RankingInstructions;
