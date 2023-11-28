#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass, field
from omegaconf import MISSING
from mephisto.abstractions.blueprint import (
    Blueprint,
    BlueprintArgs,
    SharedTaskState,
)
from mephisto.abstractions.blueprints.mixins.onboarding_required import (
    OnboardingRequired,
    OnboardingSharedState,
    OnboardingRequiredArgs,
)
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig
from mephisto.abstractions.blueprints.mixins.screen_task_required import (
    ScreenTaskRequired,
    ScreenTaskRequiredArgs,
    ScreenTaskSharedState,
)
from mephisto.abstractions.blueprints.mixins.use_gold_unit import (
    UseGoldUnit,
    UseGoldUnitArgs,
    GoldUnitSharedState,
)
from mephisto.abstractions.blueprints.ranking_task.ranking_task_builder import RankingTaskBuilder
from mephisto.abstractions.blueprints.ranking_task.ranking_task_runner import RankingTaskRunner
from mephisto.abstractions.blueprints.ranking_task.ranking_agent_state import RankingAgentState
from mephisto.abstractions.blueprints.ranking_task.ranking_shared_task_state import SharedRankingTaskState
from mephisto.abstractions.blueprints.ranking_task.ranking_args import RankingBlueprintArgs

from mephisto.operations.registry import register_mephisto_abstraction
from mephisto.data_model.assignment import InitializationData

from mongoengine import *
from mongoengine.connection import get_connection, get_db

import os
from typing import ClassVar, Type, Any, Dict, Iterable, TYPE_CHECKING
import os
import csv
import json
import types
import time

from queue import Queue
from threading import Thread

import pickle
import math

from mephisto.abstractions.blueprints.ranking_task.db import *
import mephisto.abstractions.blueprints.ranking_task.db as db
from mephisto.abstractions.blueprints.ranking_task.game_stage import GameStage

from typing import ClassVar, Type, TYPE_CHECKING
from mephisto.abstractions.blueprint import (
    SharedTaskState,
)
from mephisto.utils.logger_core import (
    get_logger,
)

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import (
        TaskBuilder,
        TaskRunner,
        AgentState
    )
    from omegaconf import DictConfig

BLUEPRINT_TYPE_RANKING = "ranking_task"
logger = get_logger(name=__name__)

# TODO maybe make this extend Blueprint directly
@register_mephisto_abstraction()
class RankingBlueprint(ScreenTaskRequired, OnboardingRequired, UseGoldUnit, Blueprint):
    """Blueprint for a ranking task"""

    TaskBuilderClass: ClassVar[Type["TaskBuilder"]] = RankingTaskBuilder
    ArgsClass = RankingBlueprintArgs
    TaskRunnerClass: ClassVar[Type["TaskRunner"]] = RankingTaskRunner
    TaskRunnerClass = RankingTaskRunner
    AgentStateClass: ClassVar[Type["AgentState"]] = RankingAgentState
    OnboardingAgentStateClass: ClassVar[Type["AgentState"]] = RankingAgentState
    BLUEPRINT_TYPE = BLUEPRINT_TYPE_RANKING

    SharedStateClass = SharedRankingTaskState

    def __init__(
        self,
        task_run: "TaskRun",
        args: "DictConfig",
        shared_state: "SharedRankingTaskState",
    ):
        assert isinstance(
            shared_state, SharedRankingTaskState
        ), "Cannot initialize with a non-static state"
        super().__init__(task_run, args, shared_state)

        if args.blueprint.get('initial_drop_db', False):
            print("Dropping database!!")
            db.clear_db()

        if args.blueprint.get('initial_populate_from_pickle', False):
            pickle_file = os.path.expanduser(args.blueprint.get('data_pickle'))

            # can't fail because we have dafaults
            num_sentences = args.blueprint.get('initial_populate_count')
            num_cads = args.blueprint.get('initial_population_preexisting_cads_limit')

            sentences_num_string = str(num_sentences) if num_sentences>=0 else "all"
            cad_num_string = str(num_cads) if num_cads>=0 else "all"
            print(f"Initializing database with {sentences_num_string} sentences from {pickle_file}.\nAdd at most {cad_num_string} cads per sentence.")

            pickle_off = open(pickle_file,"rb")
            sentences_list = list(pickle.load(pickle_off))
            db.populate_db(sentences_list, num_sentences, num_cads)

        if args.blueprint.get('initial_populate_from_json', False):
            raise Exception("Init with json is not up to date")
            json_file = os.path.expanduser(args.blueprint.get('data_json'))
            num_sentences = args.blueprint.get('initial_populate_count')

            print(f"Initializing database with {num_sentences} sentences from {json_file}.")

            json_off = open(json_file,"rb")
            sentences_dict = dict(json.load(json_off))
            db.populate_db(sentences_dict, num_sentences)

    @classmethod
    def assert_task_args(
        cls, args: "DictConfig", shared_state: "SharedRankingTaskState"
    ) -> None:
        """Ensure that static requirements are fulfilled, and source file exists"""
        assert isinstance(
            shared_state, SharedRankingTaskState
        ), "Cannot assert args on a non-static state"
        super().assert_task_args(args, shared_state)

        # validate that input data exists
        blue_args = args.blueprint
        if blue_args.get("data_pickle", None) is not None and blue_args.get("initial_populate_from_pickle", False):
            pickle_file = os.path.expanduser(blue_args.data_pickle)
            assert os.path.exists(
                pickle_file
            ), f"Provided pickle file {pickle_file} doesn't exist"
        elif blue_args.get("data_json", None) is not None and blue_args.get("initial_populate_from_json", False):
            json_file = os.path.expanduser(blue_args.data_json)
            assert os.path.exists(
                json_file
            ), f"Provided json file {json_file} doesn't exist"
        elif shared_state.static_task_data is not None:
            if isinstance(shared_state.static_task_data, types.GeneratorType):
                # TODO(#97) can we check something about this?
                # Some discussion here: https://stackoverflow.com/questions/661603/how-do-i-know-if-a-generator-is-empty-from-the-start
                pass
            else:
                assert (
                    len([x for x in shared_state.static_task_data]) > 0
                ), "Length of data dict provided was 0"

        # check that only one method is used for initialisation
        assert not (blue_args.get("initial_populate_from_json", False) and blue_args.get("initial_populate_from_pickle")), "Only expect to initialize from either json or pickle."

        # check if webapp dir exists
        found_webapp_dir = args.blueprint.webapp_dir
        assert (
            found_webapp_dir is not None
        ), "Must provide a path to the React webapp for this task."
        found_webapp_path = os.path.expanduser(found_webapp_dir)
        assert os.path.exists(
            found_webapp_path
        ), f"Provided webapp_dir {found_webapp_path} does not exist."
        # check if webapp dir contains build folder
        found_build_path = os.path.join(found_webapp_dir, 'build')
        assert os.path.exists(found_build_path), f"Provided webapp_dir {found_webapp_dir} does not contain /build dir."

        link_task_source = args.blueprint.link_task_source
        current_architect = args.architect._architect_type
        allowed_architects = ["local"]
        assert link_task_source == False or (
            link_task_source == True and current_architect in allowed_architects
        ), f"`link_task_source={link_task_source}` is not compatible with architect type: {args.architect._architect_type}. Please check your task configuration."

        if link_task_source == False and current_architect in allowed_architects:
            logger.info(
                "If you want your server to update on reload whenever you make changes to your webapp, then make sure to set \n\nlink_task_source: [blue]true[/blue]\n\nin your task's hydra configuration and run \n\n[purple]cd[/purple] webapp [red]&&[/red] [green]npm[/green] run dev:watch\n\nin a separate terminal window. For more information check out:\nhttps://mephisto.ai/docs/guides/tutorials/custom_react/#12-launching-the-task\n",
                extra={"markup": True},
            )

        if args.blueprint.auto_pay_bonus:
            assert 'bonus_ranking' in args.blueprint, "Bonus amount for ranking missing"
            assert 'bonus_cad' in args.blueprint, "Bonus amount for cad missing"

    def get_initialization_data(self) -> Iterable["InitializationData"]:
        """
        Return the InitializationData retrieved from the specified stream
        """
        # load task data
        blue_args = self.args.blueprint
        # this shouldn't fail because we have default values
        cads_per_original = blue_args.get("cads_per_original")
        sentences_per_ranking = blue_args.get("sentences_per_ranking")
        rankings_per_original = blue_args.get("rankings_per_original")

        # we use a queue to collect assignments across threads.
        # we use False as a sentinal element
        assignment_queue = Queue()

        def check_ranking_assignments(assignment_queue):
            """
            This method uses the database create_ranking_assignments method to
            * query the database for new ranking assignments
            * create entries in the database for these assignments
            it then pushes InitialisationData objects to the assignment queue to be handed off to mephisto.

            This method returns a tuple (failed, added) where
            * failed iff query was aborted
            * added iff there were new assignments added to the queue
            """
            failed = False
            added = False

            ranking_assignments = None
            try:
                ranking_assignments = db.create_ranking_assignments(sentences_per_ranking, rankings_per_original)
            except Exception as e:
                failed = True

            if ranking_assignments is not None and len(ranking_assignments) > 0:
                added = True
                for assignment in ranking_assignments:
                    sentences = [cad.cad for cad in CAD.objects(id__in=assignment['cads'])]
                    num_units = assignment['reqNumRankings']
                    assignment_data = {
                        "sentences": sentences,
                        "stage": GameStage.RANKING,
                        # pass mongo id through to agent initialisation
                        "mongo_id": str(assignment['_id'])
                        }
                    assignment_queue.put(InitializationData(
                        shared=assignment_data,
                        unit_data=[{}] * num_units,
                    ))

            return (failed, added)

        def check_cad_assignments(assignment_queue):
            """
            This method uses the database create_cad_assignments method to
            * query the database for new cad assignments
            * create entries in the database for these assignments
            it then pushes InitialisationData objects to the assignment queue to be handed off to mephisto.

            This method returns a tuple (failed, added) where
            * failed iff query was aborted
            * added iff there were new assignments added to the queue
            """
            failed = False
            added = False

            cad_assignments = None
            try:
                cad_assignments = db.create_cad_assignments(cads_per_original)
            except Exception as e:
                failed = True

            if cad_assignments is not None and len(cad_assignments) > 0:
                added = True
                for assignment in cad_assignments:
                    num_units = assignment['reqNumCads']
                    assignment_data = {
                        "original": Sentence.objects(id=assignment['original']).first().sentence,
                        "stage": GameStage.CAD,
                        # pass mongo id through to agent initialisation
                        "mongo_id": str(assignment['_id'])
                        }
                    assignment_queue.put(InitializationData(
                        shared=assignment_data,
                        unit_data=[{}] * num_units,
                    ))

            return (failed, added)

        # wrap a boolean so that we can pass it by reference to the threads
        class DoneFlag:
            def __init__(self):
                self.done=False

        cad_done_flag = DoneFlag()
        ranking_done_flag = DoneFlag()


        def poll_assignments(assignment_queue, cad_done_flag, ranking_done_flag):
            while(not cad_done_flag.done):
                check_cad_assignments(assignment_queue)
                check_ranking_assignments(assignment_queue)
                # update done_flag
                # TODO: maybe do this not here
                cad_done_flag.done = db.all_requested_cads_generated()
                time.sleep(5)

            logger.info("All cad assignments generated. Only polling for ranking assignments now")

            while(not ranking_done_flag.done):
                (failed, added) = check_ranking_assignments(assignment_queue)
                if not failed and not added:
                    # in this case all cads are already generated and we succesfully
                    # queried the database for more ranking assignments and got none.
                    # Now we know that there also cannot be any more ranking assignment.
                    ranking_done_flag.done = True
                time.sleep(10)

            # terminate the queue here
            logger.info("Terminating assignment queue!")
            assignment_queue.put(False)

        poll_assignments_thread = Thread(target=poll_assignments, args=(assignment_queue,cad_done_flag, ranking_done_flag, ))
        poll_assignments_thread.start()

        def watch_mongo(assignment_queue, cad_done_flag):
            client = get_connection()
            change_stream = client.test.watch()
            for change in change_stream:
                check_ranking_assignments(assignment_queue)
                # this is triggered after every db change.
                # so on the last db change that makes the
                # done turn true we can end the for loop
                cad_done_flag.done = db.all_requested_cads_generated()
                if cad_done_flag.done:
                    logger.info("End mongo change watcher")
                    return

        watch_mongo_thread = Thread(target=watch_mongo, args = (assignment_queue, cad_done_flag ))
        watch_mongo_thread.start()

        def fetch_new_assignments() -> Iterable["InitializationData"]:
            # wrap list iterator as generator. This is neccessary for mephisto to operate properly
            counter = 0
            for m in iter(assignment_queue.get, False):
                counter += 1
                logger.info(f"Yielded assignment #{counter}")
                yield m

            logger.info("Generator done!")

        return fetch_new_assignments()
