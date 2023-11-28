
#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import TaskRunner

import os
import time
import threading
import random

from typing import ClassVar, List, Type, Any, Dict, TYPE_CHECKING
from mephisto.abstractions.blueprint import AgentState

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.assignment import InitializationData
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.agent import Agent, OnboardingAgent
    from mephisto.abstractions.blueprint import SharedTaskState
    from omegaconf import DictConfig

import mephisto.abstractions.blueprints.ranking_task.db as db
import json


class RankingTaskRunner(TaskRunner):
    """
    Task runner for a ranking task.
    """

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        super().__init__(task_run, args, shared_state)
        self.is_concurrent = False
        self.assignment_duration_in_seconds = (
            task_run.get_task_args().assignment_duration_in_seconds
        )

    def get_init_data_for_agent(self, agent: "Agent") -> Dict[str, Any]:
        """
        Return the data for an agent already assigned to a particular unit
        """
        init_state = agent.state.get_init_state()
        if init_state is not None:
            # reconnecting agent, give what we've got
            return init_state
        else:
            assignment = agent.get_unit().get_assignment()
            assignment_data = self.get_data_for_assignment(assignment)
            agent.state.set_init_state(assignment_data.shared)
            return assignment_data.shared

    # TODO: implement onboarding for ranking task
    def run_onboarding(self, agent: "OnboardingAgent"):
        """
        Static onboarding flows exactly like a regular task, waiting for
        the submit to come through
        """
        agent.await_submit(self.assignment_duration_in_seconds)

    # TODO: check this again
    def cleanup_onboarding(self, agent: "OnboardingAgent"):
        """Nothing to clean up in a static onboarding"""
        return
    def cleanup_unit(self, unit: "Unit") -> None:
        """There is currently no cleanup associated with killing an incomplete task"""
        return
    def cleanup_assignment(self, assignment: "Assignment"):
        pass
        #return super().cleanup_assignment(assignment)

    def run_assignment(self, assignment, agents: List["Agent"]) -> None:
        #while(True):
        #    for agent in agents:
        #        gotten_update = agent.get_live_update(100000)
        #        #if gotten_update != None:
        #        print(gotten_update)
        for agent in agents:
            agent.await_submit(timeout=self.assignment_duration_in_seconds)

    def get_worker_stats(self, agent):
        worker_id = agent.get_worker().db_id
        return {
            "num_cads": db.get_num_cads(worker_id),
            "num_rankings": db.get_num_rankings(worker_id),
            "num_first_place": db.get_num_first_place(worker_id),
            "history": db.get_worker_history(worker_id)
        };

    def run_unit(self, unit: "Unit", agent: "Agent") -> None:
        while (
            not agent.await_submit(timeout=None)
            and unit.db_id in self.running_units
            # and time.time() - start_time < self.assignment_duration_in_seconds
        ):
            upd = agent.get_live_update(None)
            if upd:
                message = upd.get("message")
                if (message == "get_worker_stats"):
                    response = {
                        "message": "set_worker_stats",
                        "stats": self.get_worker_stats(agent)
                    }
                    agent.observe(response)
                elif (message == "submit_feedback"):
                    worker_id = agent.get_worker().db_id
                    # get unit record
                    unit_record = db.Unit.objects(agentId=agent.get_agent_id()).first()
                    db.submit_feedback(worker_id, unit_record, upd['feedback'])
                elif (message == "set_cad"):
                    raise "Not implemented"
                elif (message == "get_permutation"):
                    raise "Not implemented"
                else:
                    raise "Can't parse live update!"
            time.sleep(0.1)
