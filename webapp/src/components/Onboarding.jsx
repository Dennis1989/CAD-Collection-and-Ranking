/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, { useState, useEffect } from "react";
import Navbar from "./Navbar.jsx";
import { DndContext, closestCenter } from "@dnd-kit/core";
import Tippy from "@tippyjs/react";
import "tippy.js/dist/tippy.css";
import CADInstructions from "./CADinstruction.jsx";
import RankingInstructions from "./RankingInstruction.jsx";
import { levenshteinDistance, getInfrequentTokens } from "./util.js";
import { DemographicsQuestionnaire } from "./DemographicsQuestionnaire/DemographicsQuestionnaire.jsx";

import Footer from "./footer.jsx";

import {
  arrayMove,
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";

import { SortableItem } from "./SortableItem.jsx";

function OnboardingComponent({ onSubmit , submitFeedback}) {
  // For cad onboarding

  const [showInstructionCAD, setShowInstructionCAD] = useState(true);
  const [showCADApp, setCADApp] = useState(false);
  const [sentence, setSentences] = useState(
    "Women are less intelligent than men.",
  );
  const [textInput, setTextInput] = useState("");
  const [wordChanges, setWordChanges] = useState(
    levenshteinDistance(sentence, ""),
  );
  const [showHintCad, setShowHintCad] = useState(false);
  const toggleHintCAD = () => {
    setShowHintCad(!showHintCad);
  };

  // to calculate the changegs made in inputtext and the given sentences
  const handleInputChange = (e) => {
    const userInput = e.target.value;
    setTextInput(userInput);

    const changes = levenshteinDistance(sentence, userInput);
    setWordChanges(changes);
  };

  // to hide the instruction

  const handleOkaycadButtonClick = () => {
    setShowInstructionCAD(false);
    setCADApp(true);
  };

  const handlebackcadButtonClick = () => {
    setShowInstructionCAD(true);
    setCADApp(false);
  };

  //copy the sentence to text field
  const handleCopy = () => {
    setWordChanges(0);
    setTextInput(sentence);
  };

  const handleSubmit = () => {
    if (wordChanges > 0 && textInput.length > 0) {
      setShowInstruction(true);
      setCADApp(false);
    }
  };

  // *****till here cad onboarding****

  // *****Ranking onboarding*******

  const [showInstruction, setShowInstruction] = useState(false);
  const [showRankingApp, setShowRankingApp] = useState(false);
  const [showHint, setShowHint] = useState(false);

  const [ranking, setRanking] = useState([
    "Flies are less intelligent than dogs.",
    "Women are less tall.",
    "Women are less intelligent than men.",
    "Women are as intelligent as men.",
  ]);

  function check_ranking() {
    let most_sexist_sentence = "Women are less intelligent than men.";
    return ranking[0] === most_sexist_sentence;
  }

  const infrequentTokens = getInfrequentTokens(ranking);

  const sentencesWithHighlights = ranking.map((sentence, index) => (
    <div key={index}>
      <div>{sentence}</div>
    </div>
  ));

  const toggleHintPopup = () => {
    setShowHint(!showHint);
  };

  const handleOkayButtonClick = () => {
    setShowInstruction(false);
    setShowRankingApp(true);
  };
  const handlebackrankButtonClick = () => {
    setShowInstruction(true);
    setShowRankingApp(false);
  };
  const handleSoftSubmit = () => {
    //onSubmit({ success: check_ranking() });
    setShowRankingApp(false);
    setShowDemographicsQuestionnaire(true);
  };
  const handlegobackcadButtonClick = () => {
    setShowInstruction(false);
    setCADApp(true);
  };

  function handleDragEnd(event) {
    console.log("Drag");
    const { active, over } = event;
    console.log("Active:" + active.id);
    console.log("Over :" + over.id);

    if (active.id !== over.id) {
      setRanking((items) => {
        const activeIndex = items.indexOf(active.id);
        const overIndex = items.indexOf(over.id);
        console.log(arrayMove(items, activeIndex, overIndex));
        return arrayMove(items, activeIndex, overIndex);
      });
    }
  }

  // Demographics state
  const [showDemographicsQuestionnaire, setShowDemographicsQuestionnaire] =
    useState(false);

  const [gender, setGender] = useState("");
  const [age, setAge] = useState(-1);
  const [occupation, setOccupation] = useState("");
  const [education, setEducation] = useState("");
  const [birthCountry, setBirthCountry] = useState("");
  const [youthCountry, setYouthCountry] = useState("");
  const [currentCountry, setCurrentCountry] = useState("");
  const [ethnicity, setEthnicity] = useState("");
  const [religion, setReligion] = useState("");
  const [politicalAffiliation, setPoliticalAffiliation] = useState("");
  const [englishFluency, setEnglishFluency] = useState("");
  const [sexismFaced, setSexismFaced] = useState("");

  function handleDemographicsSubmit(e) {
    const demographics = {
      gender: gender,
      age: age,
      occupation: occupation,
      education: education,
      birthCountry: birthCountry,
      youthCountry: youthCountry,
      currentCountry: currentCountry,
      ethnicity: ethnicity,
      religion: religion,
      politicalAffiliation: politicalAffiliation,
      englishFluency: englishFluency,
      sexismFaced: sexismFaced,
    };

    onSubmit({
      success: check_ranking(),
      demographics: demographics,
    });
  }

  function handleDemographicsBack(e) {
    setShowDemographicsQuestionnaire(false);
    setShowRankingApp(true);
  }

  // ******Ranking onboarding****

  return (
    <div className="h-screen bg-slate-200 overflow-auto">
      <Navbar title="Onboarding" />

      {showInstructionCAD && (
        <CADInstructions onclick={handleOkaycadButtonClick} />
      )}
      {showCADApp && (
        <div className="text-center p-4">
          <h2 className="font-san font-bold text-center p-4">
            This is an exemplary Unsexify Modification task. Please modify this
            sentence to be non-sexist.
          </h2>
          <div className="frame flex items-center justify-center">
            <div className="font-san font-bold text-center p-4">{sentence}</div>
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
                if (
                  e.key === "Enter" &&
                  wordChanges > 0 &&
                  textInput.length > 0
                ) {
                  //onSubmit({ sentence: sentence, CAD: textInput });
                  handleSubmit();
                }
              }}
            />
          </div>
          <div>
            <p className="text-1xl font-semibold p-2">
              {" "}
              Number of word changes: {wordChanges}
            </p>
            <span
              className="hint-text p-2 flex justify-center hover:underline text-center p-3 cursor-pointer text-cyan-500 mb-1"
              onClick={toggleHintPopup}
            >
              Need a hint?
            </span>
          </div>
          {showHint && (
            <div className="items-center flex justify-center mb-3">
              <div className="w-2/3 p-4 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600">
                <div className="hint-dialogue">
                  <div className="hint-content">
                    You can change the sentence "Women are less intelligent than
                    men" to "Women are as intelligent as men."
                  </div>
                </div>
              </div>
            </div>
          )}
          <button
            className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full mr-2"
            onClick={handlebackcadButtonClick}
          >
            Go back to instruction page
          </button>
          <Tippy content="Click here to save the data" placement="bottom">
            <button
              className={`py-2 px-4 rounded-full mr-2 ${
                wordChanges === 0 || textInput.length === 0
                  ? "bg-gray-400 font-san font-bold text-gray-700 cursor-not-allowed"
                  : "bg-cyan-800 font-san font-bold hover:bg-cyan-500 text-white"
              }`}
              onClick={handleSubmit}
              disabled={wordChanges === 0 || textInput.length === 0}
            >
              Click here to Save
            </button>
          </Tippy>

          <div></div>
        </div>
      )}

      {showInstruction && (
        <RankingInstructions
          onBackclick={handlegobackcadButtonClick}
          onContinueclick={handleOkayButtonClick}
        />
      )}
      {showRankingApp && (
        <DndContext
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          {/* The rest of the ranking app */}
          <h2 className="font-san font-bold text-center p-4">
            This is an exemplary ranking task. Please rank from most to least
            sexist:
          </h2>
          <div className="w-100 px-20 items-center justify-center text-black">
            <div className="label pb-3">Most sexist</div>

            <SortableContext
              items={ranking}
              strategy={verticalListSortingStrategy}
            >
              {ranking.map((sentence) => (
                <SortableItem
                  key={sentence}
                  id={sentence}
                  sentence={sentence}
                  infrequentTokens={infrequentTokens}
                />
              ))}
            </SortableContext>

            <div className="label">Least Sexist</div>
          </div>
          <span
            className="hint-text p-2 flex justify-center hover:underline text-center p-3 cursor-pointer text-cyan-500"
            onClick={toggleHintPopup}
          >
            Need a hint?
          </span>
          {showHint && (
            <div className="items-center flex justify-center mb-3">
              <div className="w-1/3 p-3 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600">
                The original sentence:
                <div className="text-center p-2 text-bold italic">
                  "Women are less intelligent than men."
                </div>
                is definitely the most sexist one. It should be at the top.
              </div>
            </div>
          )}
          <div className="p-2 flex justify-center">
            <button
              className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full mr-2"
              onClick={handlebackrankButtonClick}
            >
              Go back to instruction
            </button>
            <Tippy content="Click here to save the data" placement="bottom">
              <button
                className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full mr-2"
                onClick={handleSoftSubmit}
              >
                Click here to Save
              </button>
            </Tippy>
          </div>
        </DndContext>
      )}

      {showDemographicsQuestionnaire && (
        <DemographicsQuestionnaire
          gender={gender}
          setGender={setGender}
          age={age}
          setAge={setAge}
          occupation={occupation}
          setOccupation={setOccupation}
          education={education}
          setEducation={setEducation}
          birthCountry={birthCountry}
          setBirthCountry={setBirthCountry}
          youthCountry={youthCountry}
          setYouthCountry={setYouthCountry}
          currentCountry={currentCountry}
          setCurrentCountry={setCurrentCountry}
          ethnicity={ethnicity}
          setEthnicity={setEthnicity}
          religion={religion}
          setReligion={setReligion}
          politicalAffiliation={politicalAffiliation}
          setPoliticalAffiliation={setPoliticalAffiliation}
          englishFluency={englishFluency}
          setEnglishFluency={setEnglishFluency}
          sexismFaced={sexismFaced}
          setSexismFaced={setSexismFaced}
          handleSubmit={handleDemographicsSubmit}
          handleBack={handleDemographicsBack}
        />
      )}
      <Footer
          submitFeedback={submitFeedback}
      />
    </div>
  );
}

export { OnboardingComponent };
