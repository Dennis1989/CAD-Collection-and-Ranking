import React, { useState } from "react";

import { TextComparison } from "./TextComparison.jsx";
import { ContentWarning } from "./ContentWarning.jsx";

function CADInstructions({ onclick }) {
  const [isExplanationVisible, setIsExplanationVisible] = useState(false);

  const toggleExplanation = () => {
    setIsExplanationVisible(!isExplanationVisible);
  };

  return (
    <div className=" flex justify-center">
      <div className="text-center p-5 flex flex-col content-center w-full md:w-[70%] gap-4">
        <ContentWarning />
        <div className="flex items-center justify-center">
          <div className="p-4 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600 w-full">
            <div className="font-san font-bold text-lg text-rose-500">
              Read the instructions carefully. Your onboarding performance will
              be assessed, and failure to pay attention may result in exclusion
              from the task.
            </div>
            <div className="bg-cyan-50 rounded-t-2xl p-3">
              <div className="font-san font-bold text-lg">
                Instructions for the Unsexify Modification Task:
              </div>
            </div>
            <div className="flex items-center justify-center p-2">
              Your goal is to transform a sexist sentence into a non-sexist one,
              changing it as little as possible.
            </div>

            <div className="w-full flex justify-center pt-4 pb-2">
              <div className="bg-green-400 text-white font-bold rounded-2xl px-4 py-2 w-fit">
                <span className="pr-2">$</span>
                <span className="ml-2">Bonuses</span>
              </div>
            </div>

            <p>
              Your modifications (and those made by others) will later be
              assessed by participants, who will rank them from the most sexist
              to the least sexist. For every original sentence, the worker who
              submitted the least sexist sentence will be rewarded with a bonus.
              If multiple workers submit the same sentence or there is a tie the
              bonus will be split.
            </p>
            <p>
              Try to make the{" "}
              <span className="font-extrabold italic">best modifications</span> and go for{" "}
              <span className="font-extrabold italic">unique sentences</span> to increase
              you chances of getting a bonus.{" "}
            </p>

            <div className="w-full flex justify-center pt-4 pb-2">
            <div className="bg-red-500 text-white font-bold rounded-2xl px-4 py-2 flex w-fit">
              <svg
                class="h-6 w-6 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="white"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
                />
              </svg>
              <div className="ml-2">Caution</div>
            </div>
            </div>

                <span className="font-extrabold italic">Avoid utilizing ChatGPT</span> or
                any of its variation. If you are discovered using it, you will
                be prohibited from participating in the assignment.

                <p className="mb-4 mt-3 italic">
              It is not advisable to use a mobile device for this task, as some of the features or options may be limited or restricted.
            </p>
          </div>
        </div>

        <div className="p-2 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600 w-full">
          <div className="flex items-center justify-center text-center font-bold p-2 text-lg">
            Please keep in mind that there is no single solution! Every sentence
            can be modified in multiple ways. Here are some examples of possible
            modifications:
          </div>

          <div className="flex items-center justify-center text-center">
            <TextComparison
              sentence1="Women are less intelligent than men."
              sentence2="Women are as intelligent as men."
            />
          </div>
          <div className="flex items-center justify-center text-center">
            <TextComparison
              sentence1="Women are less intelligent than men."
              sentence2="Women are less tall."
            />
          </div>
          <div className="flex items-center justify-center text-center">
            <TextComparison
              sentence1="Women are less intelligent than men."
              sentence2="Flies are less intelligent than dogs."
            />
          </div>
          <span
            className="hint-text p-2 flex justify-center hover:underline text-center p-3 cursor-pointer text-cyan-500"
            onClick={toggleExplanation}
          >
            Click here for explanation
          </span>

          {isExplanationVisible && (
            <>
              <div>
                The original statement, "
                <strong>
                  <em>Women are less intelligent than men</em>
                </strong>
                ," spreads a harmful stereotype suggesting women are naturally
                less intelligent than men. The revised statements don't contain
                this stereotype.
              </div>
              <div className="block font-bold mt-3 text-rose-500">
                Please note that this is just an example, and the generated
                statements may be subjective.
              </div>
            </>
          )}
        </div>

        <div className="p-2 flex justify-center">
          <button
            className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full"
            onClick={onclick}
          >
            Let's try it out
          </button>
        </div>
      </div>
    </div>
  );
}

export default CADInstructions;
