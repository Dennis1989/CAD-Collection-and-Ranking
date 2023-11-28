#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
)
from mephisto.data_model.unit import Unit
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import task_script, build_custom_bundle

from mephisto.abstractions.blueprints.ranking_task.ranking_shared_task_state import SharedRankingTaskState
import mephisto.abstractions.blueprints.ranking_task.db as mongo_db

from rich import print
from omegaconf import DictConfig


from mongoengine import *

from mephisto.abstractions.blueprints.ranking_task.game_stage import GameStage

def my_screening_unit_generator():
    while True:
        yield {
            "sentences": [
                "Sexist sentence.",
                "Non-sexist sentence.",
                "Very sexist sentence.",
                ],
            "stage": GameStage.RANKING,
            "is_screening": True
        }

def validate_screening_unit(unit: Unit):
    agent = unit.get_assigned_agent()
    if agent is not None:
        data = agent.state.get_data()
        print(data)
        if (
            data["outputs"] is not None
            and "permutation" in data["outputs"]
            and data["outputs"]["permutation"] == [2,0,1]
        ):
            # user correctly sorted the sentences
            return True
    return False

onboarding_task_data = {
    "sentences": [
        "Sexist sentence.",
        "Non-sexist sentence.",
        "Very sexist sentence.",
        ],
    "stage": GameStage.RANKING,
    "is_onboarding": True
}

# TODO change this
def handle_onboarding(onboarding_data):
    if onboarding_data["outputs"]["success"] == True:
        return True
    return False

def worker_can_do_unit(worker: "Worker", unit: "Unit") -> bool:
    worker_id = worker.db_id
    assignment_mongo_id = unit.get_assignment_data().shared['mongo_id']
    assignment_record = mongo_db.Assignment.objects(id=assignment_mongo_id).first()

    # check if worker already did ranking for same original
    if isinstance(assignment_record, mongo_db.RankingAssignment):
        # get sentence id of original
        original_sentence_external_id = assignment_record.original.externalId

        # get other sentence objects with same id
        other_sentence_instances = mongo_db.Sentence.objects(externalId=original_sentence_external_id)

        # now only take their ids
        other_ids = [s.id for s in other_sentence_instances]

        # query database for all other ranking assignments for this original
        other_assignments = mongo_db.RankingAssignment.objects(original__in=other_ids)
        for rk in other_assignments:
            for u in rk.units:
                # check if worker did this unit
                if worker_id == u.workerId:
                    return False

    # NOTE: this is a bit duplicate to the one above. but this could make sense once we add
    #       game assignments.
    # check if worker already did cad for same original
    if isinstance(assignment_record, mongo_db.CADAssignment):
        # get sentence id of original
        original_sentence_external_id = assignment_record.original.externalId

        # get other sentence objects with same id
        other_sentence_instances = mongo_db.Sentence.objects(externalId=original_sentence_external_id)

        # now only take their ids
        other_ids = [s.id for s in other_sentence_instances]
        # query database for all other cad assignments for this original
        other_cad_assignments = mongo_db.CADAssignment.objects(original__in=other_ids)
        for rk in other_cad_assignments:
            for u in rk.units:
                # check if worker did this unit
                if worker_id == u.workerId:
                    return False

    return True

@task_script(default_config_file="debug_basic.yaml")
def main(operator: Operator, cfg: DictConfig) -> None:
    # connect to mongo db
    db_username = cfg.mephisto.blueprint["db_username"]
    db_password = cfg.mephisto.blueprint["db_password"]
    db_location = cfg.mephisto.blueprint["db_location"]

    DATABBASE_URL = f"mongodb://{db_username}:{db_password}@{db_location}"
    connect(host=DATABBASE_URL)

    is_using_screening_units = cfg.mephisto.blueprint["use_screening_task"]

    shared_state = SharedRankingTaskState(
        onboarding_data=onboarding_task_data,
        validate_onboarding=handle_onboarding,
        worker_can_do_unit=worker_can_do_unit,
    )

    if is_using_screening_units:
        """
        When using screening units there has to be a
        few more properties set on shared_state
        """
        shared_state.on_unit_submitted = ScreenTaskRequired.create_validation_function(
            cfg.mephisto,
            validate_screening_unit,
        )
        shared_state.screening_data_factory = my_screening_unit_generator()
        shared_state.qualifications += ScreenTaskRequired.get_mixin_qualifications(
            cfg.mephisto, shared_state
        )

    #task_dir = cfg.task_dir

    #build_custom_bundle(
    #    task_dir,
    #    force_rebuild=cfg.mephisto.task.force_rebuild,
    #    post_install_script=cfg.mephisto.task.post_install_script,
    #)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
