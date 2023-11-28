import React from 'react'
import { useState, useEffect } from 'react';

export function useMephistoLiveTask(props) {
  const [blockedReason, setBlockedReason] = useState(null);
  const [blockedExplanation, setBlockedExplanation] = useState("");
  const [isPreview, setIsPreview] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [initialTaskData, setInitialTaskData] = useState({
    stage: "CAD",
    original: "Test sentence"
  });
  const [isOnboarding, setIsOnboarding] = useState(true);
  const [taskConfig, setTaskConfig] = useState({});
  const [previewHtml, setPreviewHtml] = useState("");
  const [agentId, setAgentId] = useState("<agent id>");
  const [agentStatus, setAgentStatus] = useState("connected");

  function sendLiveUpdate(update) {
    console.log({"live update": update})

    if(update.message == 'get_worker_stats') {
      const worker_history = [
        {
          "finished_time": "Mon 28 Aug 2023, 05:22PM",
          "stage": "RANKING",
          "output_ranking": ["First sentence.", "Second sentence."]
        },
        {
          "finished_time": "Mon 28 Aug 2023, 05:22PM",
          "stage": "CAD",
          "num_first_place": 2,
          "original": "This is a very sexist sentence.",
          "cad": "This is not a very sexist text."
        }
      ]
      const worker_stats = {
        "num_cads": 1,
        "num_rankings": 1,
        "num_first_place": 1,
        "history": worker_history
      }
      const response = {
          "message": "set_worker_stats",
          "stats": worker_stats
      }
      props.onLiveUpdate(response)
    }
  }

  function handleSubmit(data) {
    console.log({"handle submit": data})
    if (isOnboarding) {
      setIsOnboarding(false)
    } else {
      alert(data)
    }
  }

  function handleFatalError(error) {
    console.log({"fatal error": error})
  }

  function connect(agentId) {
    console.log("connect")
  }

  function destroy() {
    console.log("destroy ???")
  }

  return {
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
  }
}
