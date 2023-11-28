/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import { useState, useEffect } from "react";

import Tippy from "@tippyjs/react";
import "tippy.js/dist/tippy.css";
import Dashboard from "./DBoardBody.jsx";
import { levenshteinDistance } from "./util.js";
import Navbar from "./Navbar.jsx";
import { SkipCadExplanationPopup } from "./SkipCadExplanationPopup.jsx";
import Footer from "./footer.jsx";

export function CADScreen({
  sentence,
  onSubmit,
  numSubmittedCads,
  numSubmittedRankings,
  numFirstPlace,
  history,
  submitFeedback,
}) {
  const [textInput, setTextInput] = useState("");
  const [wordChanges, setWordChanges] = useState(0);
  const [validInput, setValidInput] = useState(false);

  const [showCADApp, setCADApp] = useState(true);
  const [showDashApp, setShowDashApp] = useState(false);
  const [showUserSubmission, setShowUserSubmission] = useState(false);

  const handleCopy = () => {
    setWordChanges(0);
    setTextInput(sentence);
  };

  const handleInputChange = (e) => {
    const userInput = e.target.value;
    setTextInput(userInput);

    const changes = levenshteinDistance(sentence, userInput);
    setWordChanges(changes);

    const isValid = userInput.length > 0 && changes > 0;
    setValidInput(isValid);
  };
  const handleSubmit = () => {
    setCADApp(false);
    setShowDashApp(true);
    setShowUserSubmission(true);
  };
  const handleConfirmSubmit = () => {
    setShowUserSubmission(false);
    onSubmit({ sentence: sentence, cad: textInput });
  };
  const handlebackButton = () => {
    setShowDashApp(false);
    setCADApp(true);
  };

  // state for skip cad functionality
  const [showSkipCadExplanationPopup, setShowSkipCadExplanationPopup] =
    useState(false);
  const [explanation, setExplanation] = useState("");

  // handlers for buttons on popup
  function handleSubmitSkipCadExplanation() {
    onSubmit({ sentence: sentence, explanation: explanation });
  }
  function handleBackSkipCadExplanation() {
    setShowSkipCadExplanationPopup(false);
  }

  // handlers for button on cad interface
  function handleSkipCad() {
    setShowSkipCadExplanationPopup(true);
  }

  return (
    <div className="bg-slate-200">
      <Navbar title="Unisexify Modification Task" />

      {showCADApp && (
        <>
          {showSkipCadExplanationPopup && (
            <SkipCadExplanationPopup
              explanation={explanation}
              setExplanation={setExplanation}
              onSubmit={handleSubmitSkipCadExplanation}
              onBack={handleBackSkipCadExplanation}
            />
          )}

          <div className="text-center p-4">
            <div className="frame flex items-center justify-center">
              <div className="font-san text-center p-4">{sentence}</div>
              <div className="p-3">
                <Tippy
                  content="Click here to copy the example sentence into the text box"
                  placement="bottom"
                >
                  <button
                    className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full"
                    onClick={handleCopy}
                  >
                    Copy below
                  </button>
                </Tippy>
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="text"
                placeholder="Unsexify the given sentence"
                value={textInput}
                onChange={handleInputChange}
                className="h-10 mb-6 text-gray-900 border-gray-300 rounded-lg w-100 pl-10 pr-20"
                style={{ margin: "0 0.5rem" }}
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    handleSubmit();
                  }
                }}
                onPaste={(e) => {
                  e.preventDefault();
                }}
              />
            </div>
            <div>
              <p className="text-1xl font-semibold p-2">
                {" "}
                Number of word changes: {wordChanges}
              </p>
            </div>

            <button
              className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full mb-2 md:mb-0 md:mr-2"
              onClick={handleSkipCad}
            >
              Not sexist
            </button>

            <Tippy content="Click here to save the data" placement="bottom">
              <>
                {validInput && (
                  <button
                    className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full"
                    onClick={handleSubmit}
                  >
                    Save the task
                  </button>
                )}
                {!validInput && (
                  <button class="bg-gray-400 rounded-full py-2 px-4 font-san font-bold text-gray-700 cursor-not-allowed">
                    Save the Task
                  </button>
                )}
              </>
            </Tippy>
          </div>
        </>
      )}

      {showDashApp && (
        <Dashboard
          numSubmittedCads={numSubmittedCads}
          numSubmittedRankings={numSubmittedRankings}
          numFirstPlace={numFirstPlace}
          history={history}
          currentSubmission={{
            stage: "CAD",
            original: sentence,
            cad: textInput,
          }}
          onSubmit={handleConfirmSubmit}
          onBack={handlebackButton}
        />
      )}
      <Footer
          submitFeedback={submitFeedback}
      />
    </div>
  );
}
