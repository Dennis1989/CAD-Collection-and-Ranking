#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import time
import datetime
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from mephisto.abstractions.blueprint import AgentState
import os.path
import threading

if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.packet import Packet

from mephisto.utils.logger_core import get_logger

from mongoengine import *
from mephisto.abstractions.blueprints.ranking_task.db import *

import mephisto.data_model

logger = get_logger(name=__name__)

DATA_FILE = "agent_data.json"

from mephisto.abstractions.blueprints.ranking_task.game_stage import GameStage
import mephisto.abstractions.blueprints.ranking_task.ranking_utils as ru

class RankingAgentState(AgentState):
    """
    Agent state for static tasks.
    """

    def _get_empty_state(self) -> Dict[str, Optional[Dict[str, Any]]]:
        return {
            "inputs": None,
            "outputs": None,
        }

    def _set_init_state(self, data: Any):
        """Set the initial state for this agent"""
        is_screening = data.get('is_screening', False)
        is_onboarding = data.get('is_onboarding', False)

        if not is_screening and not is_onboarding:
            # get our mongo_id that was handed through generator
            mongo_id = data['mongo_id']

            # create unit_record
            worker_id = self.agent.get_worker().db_id
            agent_id = self.agent.get_agent_id()

            unit_id = self.agent.unit_id
            register_new_unit(mongo_id, worker_id, agent_id, unit_id)

            # don't pass mongo_id to client
            cleaned_data = data.copy()
            cleaned_data.pop('mongo_id')

            self.state["inputs"] = cleaned_data
        elif is_screening and not is_onboarding:
            cleaned_data = data.copy()
            # can't remove this right now because we need this flag to prevent saving in _update_submit
            # cleaned_data.pop('is_screening')
            self.state["inputs"] = cleaned_data
        elif not is_screening and is_onboarding:
            cleaned_data = data.copy()
            # see screening
            # cleaned_data.pop('is_onboarding')
            self.state["inputs"] = cleaned_data
        else:
            raise "Unit is onboarding and screening at the same time!"

    def get_init_state(self) -> Optional[Dict[str, Any]]:

        """
        Return the initial state for this agent,
        None if no such state exists
        """
        if self.state["inputs"] is None:
            return None
        return self.state["inputs"].copy()

    def _load_data(self) -> None:
        """Load data for this agent from disk"""
        data_dir = self.agent.get_data_dir()
        data_path = os.path.join(data_dir, DATA_FILE)
        if self.agent.db.key_exists(data_path):
            self.state = self.agent.db.read_dict(data_path)
            # Old compatibility with saved times
            if "times" in self.state:
                assert isinstance(self.state["times"], dict)
                self.metadata.task_start = self.state["times"]["task_start"]
                self.metadata.task_end = self.state["times"]["task_end"]
        else:
            self.state = self._get_empty_state()

    def get_data(self) -> Dict[str, Any]:
        """Return dict of this agent's state"""
        return self.state.copy()

    def _save_data(self) -> None:
        """Save static agent data to disk"""
        data_dir = self.agent.get_data_dir()
        out_filename = os.path.join(data_dir, DATA_FILE)
        self.agent.db.write_dict(out_filename, self.state)
        logger.info(f"SAVED_DATA_TO_DISC at {out_filename}")


    def update_data(self, live_update: Dict[str, Any]) -> None:
        """
        Process the incoming data packet, and handle updating the state
        """
        # TODO: update data on pseudo submit
        pass

    def _update_submit(self, submission_data: Dict[str, Any]) -> None:
        """Move the submitted output to the local dict and write submission to our DB."""
        logger.info("Unit submitted")
        # check if reconciling
        is_reconcile = False
        if submission_data.get("MEPHISTO_MTURK_RECONCILED", False)== True:
            logger.warning("Mephisto tries to reconcile!")
            is_reconcile = True

        assert isinstance(submission_data, dict), (
            "Ranking task must get dict results. Ensure you are passing an object to "
            f"your frontend task's `handleSubmit` method. Got {submission_data}"
        )

        # move submitted output to local dict
        self.state["outputs"] = submission_data

        # if screening or onboarding unit => don't save data
        is_screening = self.state["inputs"].get('is_screening', False)
        is_onboarding = self.state["inputs"].get('is_onboarding', False)
        if is_screening:
            return

        if is_onboarding:
            submit_worker_demographics(self.agent.worker_id, self.state['outputs']['demographics'])

        # get records
        unit_record = Unit.objects(agentId=self.agent.get_agent_id()).first()

        # save ranking unit data
        if isinstance(unit_record, RankingUnit):
            permutation = self.state['outputs']['permutation']

            # if reconcile we have to manually parse permutation
            if is_reconcile:
                elems = permutation.split(',')
                permutation = [int(el) for el in elems]

            assignment_record = RankingAssignment.objects(units__contains=unit_record).first()
            permutated_cads = [assignment_record.cads[i] for i in permutation]
            # check if output already exists. this can happen when reconciling.
            # & check if current ranking and previously saved coincide
            if unit_record.outputRanking and unit_record.outputRanking.cads == permutated_cads:
                print("Got additional submission of already saved data. Discarding.")
            else:
                # it might be that due to weird late submissions or something we get more rankings than requested.
                # in that case we don't want to pay out bonuses again.
                # thus check before and after submitting ranking if 'ranking round' is finished and only pay out
                # bonuses if changed.
                all_rankings_present_before = ranking_done(assignment_record.original)
                submit_permutation(self.agent.get_agent_id(), permutation)
                all_rankings_present_after = ranking_done(assignment_record.original)
                if all_rankings_present_after != all_rankings_present_before:
                    # get mephisto database
                    mephisto_db = self.agent.get_task_run().db

                    args = self.agent.get_live_run().task_run.args.blueprint
                    # auto pay bonus
                    if args.auto_pay_bonus:
                        def give_delayed_boni():
                            logger.info(f"Detected that ranking for cad {assignment_record.original.id} finished. Sleeping now:")
                            time.sleep(100)
                            logger.info(f"Starting bonuses for original {assignment_record.original.id}")
                            give_cad_bonuses(assignment_record.original, mephisto_db, args.bonus_cad)
                            give_ranking_bonuses(assignment_record.original, mephisto_db, args.bonus_ranking)
                            logger.info(f"Finished bonuses for original {assignment_record.original.id}")
                        pay_thread = threading.Thread(target=give_delayed_boni)
                        pay_thread.start()

        # save cad unit data
        elif isinstance(unit_record, CADUnit):
            if 'cad' in self.state['outputs']:
                cad = self.state['outputs']['cad']
                # check if output for this unit already exists. see above
                if unit_record.outputCad and unit_record.outputCad.cad == cad:
                    print("Got additional submission of already saved data. Discarding.")
                else:
                    # save submitted cad in db
                    submit_cad(self.agent.get_agent_id(), cad)
            elif 'explanation' in self.state['outputs']:
                explanation = self.state['outputs']['explanation']
                if unit_record.outputExplanation and unit_record.outputExplanation.explanation == explanation:
                    print("Got additional submission of already saved data. Discarding.")
                else:
                    submit_skip_explanation(self.agent.get_agent_id(), explanation)

def give_cad_bonuses(original, mephisto_db, total_bonus_per_original):
    """
    Given an original, grant the bonuses to workers for good cads.

    @param Mongo DB object of original
    @param Mephisto database to query for workers etc.
    """
    # get all ranking units for this original
    ranking_units = [u for ass in RankingAssignment.objects(original=original) for u in ass.units]
    # get all rankings
    rankings = [u.outputRanking.cads for u in ranking_units]
    # aggregate all rankings
    aggregate_ranking = ru.aggregate_rankings(rankings)
    best_cads = aggregate_ranking[-1]

    if len(best_cads) > 0:
        bonus_per_cad = total_bonus_per_original / len(best_cads)
    for cad in best_cads:
        # determine all units that submitted this cad
        units = CADUnit.objects(outputCad=cad)
        # bonus the workers
        if len(units) > 0:
            bonus_per_worker = bonus_per_cad / len(units)
        for u in units:
            # get the mephisto data structures
            worker = mephisto.data_model.worker.Worker(mephisto_db, u.workerId)
            mephisto_unit = mephisto.data_model.unit.Unit(mephisto_db, u.unitId)

            # check in the db if we already paid the bonus for this unit
            # set if not
            db_query_res = Unit._get_collection().update_one({"_id": u.id, "paidBonus": False}, {"$set": {"paidBonus": True}})
            if db_query_res.modified_count != 1:
                # something went wrong
                logger.error(f"Wanted to pay bonus for unit {u.id} (MongoDB ID), however it was already flagged as paid!")
                continue

            bonus_message = "\n".join([
                "Thanks for participating in the NotOneBitSexist project!",
                "",
                f'Your sentence: "{u.outputCad.cad}"',
                f"Was ranked among the least sexist by other workers!",
                "Keep up the good work!",
                "",
            ])
            logger.info(f"Computed a bonus: {bonus_per_worker}$ to worker {u.workerId} for CADUnit {u.unitId}")

            try:
                worker.bonus_worker(bonus_per_worker, bonus_message, mephisto_unit)
                logger.info(f"Paid a bonus: {bonus_per_worker}$ to worker {u.workerId} for CADUnit {u.unitId}")
            except Exception as e:
                logger.info(f"Failed to pay bonus: {bonus_per_worker}$ to worker {u.workerId} for CADUnit {u.unitId}")

# TODO: does it make sense to integrate this with the give_cad_bonusees method?
def give_ranking_bonuses(original, mephisto_db, total_bonus_per_original):
    """
    Given an original, grant the bonuses to workers for ranking closest to the aggregate ranking.

    @param MongoDB object of original.
    @param Mephisto database to query for workers etc.
    """
    # get all ranking units for this original
    ranking_units = [u for ass in RankingAssignment.objects(original=original) for u in ass.units]
    # get all rankings
    rankings = [u.outputRanking.cads for u in ranking_units]
    # aggregate all rankings
    aggregate_ranking = ru.aggregate_rankings(rankings)
    best_rankings = ru.get_most_agreeable_rankings(rankings)

    # get all ranking records with the current best ranking
    best_ranking_records = [record for ranking in best_rankings for record in Ranking.objects(cads=ranking)]

    # NOTE: we assume that there are no preexisting ranking units.
    # now get all RankingUnits which output is one of the best_ranking records
    units = list(RankingUnit.objects(outputRanking__in=best_ranking_records))

    if len(units) > 0:
        bonus_per_worker = total_bonus_per_original / len(units)
    for u in units:
        # get the mephisto data structures
        worker = mephisto.data_model.worker.Worker(mephisto_db, u.workerId)
        mephisto_unit = mephisto.data_model.unit.Unit(mephisto_db, u.unitId)

        # check in the db if we already paid the bonus for this unit
        # set if not
        db_query_res = Unit._get_collection().update_one({"_id": u.id, "paidBonus": False}, {"$set": {"paidBonus": True}})
        if db_query_res.modified_count != 1:
            # something went wrong
            logger.error(f"Wanted to pay bonus for unit {u.id} (MongoDB ID), however it was already flagged as paid!")
            continue

        ranking_string = "\n".join([f"{idx+1}. {cad.cad}" for idx, cad in enumerate(u.outputRanking.cads)])

        bonus_message = "\n".join([
            "Thanks for participating in the NotOneBitSexist project!",
            "",
            "Your ranking: (from most to least sexist)",
            ranking_string,
            "",
            "Was closest to the average ranking!",
            "This means that you were best in estimating what other people find sexist.",
            "Keep up the good work!",
            "",
        ])
        logger.info(f"Computed Bonus: {bonus_per_worker}$ to worker {u.workerId} for RankingUnit {u.unitId}")

        try:
            worker.bonus_worker(bonus_per_worker, bonus_message, mephisto_unit)
            logger.info(f"Paid a bonus: {bonus_per_worker}$ to worker {u.workerId} for RankingUnit {u.unitId}")
        except Exception as e:
            logger.info(f"Failed to pay bonus: {bonus_per_worker} for worker {u.workerId} for RankingUnit {u.unitId}")
            print(e)
