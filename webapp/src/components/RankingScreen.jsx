/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, { useState, useEffect } from "react";
import Tippy from "@tippyjs/react";
import "tippy.js/dist/tippy.css";
import Dashboard from "./DBoardBody.jsx";
import Navbar from "./Navbar.jsx";
import { getInfrequentTokens } from "./util.js";
// drag and drop dependencies
import { DndContext, closestCenter } from "@dnd-kit/core";
import Footer from "./footer.jsx";

import {
  arrayMove,
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";

// custom components
import { SortableItem } from "./SortableItem.jsx";

export function RankingScreen({
  sentences,
  onSubmit,
  numSubmittedCads,
  numSubmittedRankings,
  numFirstPlace,
  history,
  submitFeedback,
}) {
  // nums = [0,1,...n] where n = len(sentences)
  let nums = [...sentences.keys()];
  // increment every element by one
  // this is necessary because sortable lists don't seem to work with 'id' or 'key' 0
  nums = nums.map((num) => num + 1);
  const [permutation, setPermutation] = useState(nums);
  const [showDashApp, setShowDashApp] = useState(false);
  const [showRankingApp, setShowRankingApp] = useState(true);
  const [showUserSubmission, setShowUserSubmission] = useState(false);

  const handleSubmit = () => {
    setShowRankingApp(false);
    setShowDashApp(true);
    setShowUserSubmission(true);
  };
  const handleConfirmSubmit = () => {
    // decrement every element in permutation again before passing it to the backend
    setShowUserSubmission(false);
    onSubmit({
      sentences: sentences,
      permutation: permutation.map((idx) => idx - 1),
    });
  };
  const handlebackButton = () => {
    setShowDashApp(false);
    setShowRankingApp(true);
  };
  const infrequentTokens = getInfrequentTokens(sentences);

  return (
    <div className="bg-slate-200">
      <Navbar title="Unsexify Ranking Task" />

      {showRankingApp && (
        <DndContext
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <h2 class="font-san font-bold text-center p-4">
            Rank the following sentences from most to least sexist
          </h2>
          <div className="w-100 px-20 items-center justify-center">
            <div className="label">Most Sexist</div>
            <SortableContext
              items={permutation}
              strategy={verticalListSortingStrategy}
            >
              {/* watch out! our permutation array is 1-indexed while the sentences array is 0-indexed */}
              {permutation.map((index) => (
                <SortableItem
                  id={index}
                  key={index}
                  sentence={sentences[index - 1]}
                  infrequentTokens={infrequentTokens}
                  style={{ backgroundColor: "#FFD580" }}
                />
              ))}

              <div className="label">Least Sexist</div>
            </SortableContext>

            <div className="p-2 flex justify-center">
              <button
                className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full"
                onClick={(e) => handleSubmit()}
              >
                Save the task
              </button>
            </div>
          </div>
        </DndContext>
      )}

      {showDashApp && (
        <Dashboard
          numSubmittedCads={numSubmittedCads}
          numSubmittedRankings={numSubmittedRankings}
          numFirstPlace={numFirstPlace}
          history={history}
          currentSubmission={{
            stage: "RANKING",
            permutation: permutation,
            sentences: sentences,
          }}
          onSubmit={handleConfirmSubmit}
          onBack={handlebackButton}
        />
      )}
      <div>
        <Footer
          submitFeedback={submitFeedback}
        />
      </div>
    </div>
  );

  function handleDragEnd(event) {
    console.log("Drag");
    const { active, over } = event;
    console.log("Active:" + active.id);
    console.log("Over :" + over.id);
    if (active.id !== over.id) {
      setPermutation((items) => {
        const activeIndex = items.indexOf(active.id);
        const overIndex = items.indexOf(over.id);
        console.log(arrayMove(items, activeIndex, overIndex));
        return arrayMove(items, activeIndex, overIndex);
      });
    }
  }
}
