/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import { useMephistoLiveTask } from "mephisto-task";
import { useState } from "react";

// import our components
import { OnboardingComponent } from "./components/Onboarding.jsx";
import { LoadingScreen } from "./components/LoadingScreen.jsx";
import { RankingScreen } from "./components/RankingScreen.jsx";
import { CADScreen } from "./components/CADScreen.jsx";
import { PreviewScreen } from "./components/PreviewScreen.jsx"
import DataAndPolicy from "./components/DataAndPolicy.jsx";


/* ================= Application Components ================= */

export function MainApp() {
  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    sendLiveUpdate,
    handleSubmit,
    handleFatalError,
    isOnboarding,
    connect,
    taskConfig,
    previewHtml,
    agentId,
    destroy,
    agentStatus,
  } = useMephistoLiveTask({
    onConnectionStatusChange: (connectionStatus) => {
      console.log({ received_connection_status: connectionStatus });
    },
    onStatusUpdate: ({ status }) => {
      // Called when agentStatus updates
      console.log({ received_status_update: status });
    },
    onLiveUpdate: (liveUpdate) => {
      console.log({ received_live_update: liveUpdate });
      switch (liveUpdate.message) {
        case "set_worker_stats":
          let stats = liveUpdate.stats;
          setNumSubmittedCads(stats.num_cads);
          setNumSubmittedRankings(stats.num_rankings);
          setNumFirstPlace(stats.num_first_place);
          setHistory(stats.history)
          break;
        default:
          console.error("Can't parse received live update!");
          console.log(liveUpdate);
      }
    },
    //config, // optional overrides for connection constants
    //customConnectionHook, // (advanced usage) optional - provide your own hook for managing the under-the-hood connection mechanism to communicate with the Mephisto server. The default (useMephistoSocket) uses websockets.
  });

  // dashboard props
  const [numSubmittedCads, setNumSubmittedCads] = useState(-1);
  const [numSubmittedRankings, setNumSubmittedRankings] = useState(-1);
  const [numFirstPlace, setNumFirstPlace] = useState(-1);
  const [history, setHistory] = useState([]);

  // query dashboard
  function query_dashboard() {
    console.log("querying dashboard");
    sendLiveUpdate({
      message: "get_worker_stats",
    });
  }

  // submit feedback
  function submit_feedback(feedback) {
    // sanity check
    if(feedback === '') {
      console.error("Can't submit empty feedback!")
      return
    }

    sendLiveUpdate({
      message: "submit_feedback",
      feedback: feedback,
    })

    console.log("submitted feedback")
  }

  React.useEffect(() => {
    if (agentId) {
      console.log("connecting...");
      connect(agentId);
    }
  }, [agentId]);

  React.useEffect(() => {
    if (initialTaskData) {
      query_dashboard();
    }
  }, [initialTaskData]);

  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div className="hero-body">
          <h2 className="title is-3">{blockedExplanation}</h2>{" "}
        </div>
      </section>
    );
  }
  if (isPreview) {
    return <PreviewScreen />;
  }
  if (isLoading || !initialTaskData) {
    return <LoadingScreen />;
  }
  if (isOnboarding) {
    return <OnboardingComponent onSubmit={handleSubmit} />;
  }

  if (initialTaskData.stage == "CAD") {
    return (
      <div>
        <CADScreen
          sentence={initialTaskData.original}
          onSubmit={handleSubmit}
          numSubmittedCads={numSubmittedCads}
          numSubmittedRankings={numSubmittedRankings}
          numFirstPlace={numFirstPlace}
          history={history}
          submitFeedback={submit_feedback}
        />
      </div>
    );
  } else if (initialTaskData.stage == "RANKING") {
    return (
      <div>
        <RankingScreen
          sentences={initialTaskData.sentences}
          onSubmit={handleSubmit}
          numSubmittedCads={numSubmittedCads}
          numSubmittedRankings={numSubmittedRankings}
          numFirstPlace={numFirstPlace}
          history={history}
          submitFeedback={submit_feedback}
        />
      </div>
    );
  }

}
