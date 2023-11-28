
#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass, field
from omegaconf import MISSING
from mephisto.abstractions.blueprints.ranking_task.ranking_task_builder import RankingTaskBuilder
from mephisto.abstractions.blueprints.ranking_task.ranking_task_runner import RankingTaskRunner
from mephisto.abstractions.blueprints.ranking_task.ranking_agent_state import RankingAgentState
from mephisto.abstractions.blueprints.ranking_task.ranking_shared_task_state import SharedRankingTaskState

from mephisto.operations.registry import register_mephisto_abstraction

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

import os

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
    )
    from omegaconf import DictConfig

BLUEPRINT_TYPE_RANKING = "ranking_task"
logger = get_logger(name=__name__)

@dataclass
class RankingBlueprintArgs(
    ScreenTaskRequiredArgs, OnboardingRequiredArgs, UseGoldUnitArgs, BlueprintArgs
):
    """
    RankingBlueprint: Tasks launched from ranking blueprints need
    a prebuilt javascript bundle containing the task. We suggest building
    with our provided useMephistoTask hook.
    """

    _blueprint_type: str = BLUEPRINT_TYPE_RANKING
    _group: str = field(
        default="RankingBlueprint",
        metadata={
            "help": """
                Tasks launched from static blueprints need
                a prebuilt javascript bundle containing the task. We suggest building
                with our provided useMephistoTask hook.
            """
        },
    )
    webapp_dir: str = field(
        default=MISSING,
        metadata={
            "help": """
                Path to react project for frontend. Frontend should be buildable
                in this dir with `npm run dev` and resulting bundle.js should be
                located in ./build.
            """,
            "required": True,
        },
    )
    link_task_source: bool = field(
        default=False,
        metadata={
            "help": """
                Symlinks the task_source file in your development folder to the
                one used for the server. Useful for local development so you can run
                a watch-based build for your task_source, allowing the UI code to
                update without having to restart the server each time.
            """,
            "required": False,
        },
    )
    extra_source_dir: str = field(
        default=MISSING,
        metadata={
            "help": (
                "Optional path to sources that the HTML may "
                "refer to (such as images/video/css/scripts)"
            )
        },
    )
    units_per_assignment: int = field(
        default=1, metadata={"help": "How many workers you want to do each assignment"}
    )
    # added parameters
    # initial population of db
    data_pickle: str = field(
        default=MISSING, metadata={"help": "Path to json file containing a dict which keys are the sentences and values are lists of cads for the sentence."}
    )
    initial_populate_from_pickle: bool = field(
        default=False, metadata={"help": "Populate MongoDB with initial data from pickle file.", "required": False}
    )
    data_json: str = field(
        default=MISSING, metadata={"help": "Path to json file containing a dict which keys are the sentences and values are lists of cads for the sentence."}
    )
    initial_populate_from_json: bool = field(
        default=False, metadata={"help": "Populate MongoDB with initial data from pickle file.", "required": False}
    )

    initial_populate_count: int = field(
        default=-1, metadata={"help": """Max number of sentences to add in initial populate. If <0 populate add all sentences."""}
    )
    initial_population_preexisting_cads_limit: int = field(
        default=-1, metadata={"help": "Max number of preexisting cads to add to the database. If <0 populate with all cads."}
    )
    initial_drop_db: bool = field(
        default=False, metadata={"Help": "Drops old database before starting task. Only use this for debugging purposes!!!"}
    )
    # task related
    cads_per_original: int = field(
        default=4, metadata={"help": """Desired number of cads per original.
                             For every sentence where this is greater than the number of cads in the initial data,
                             we will create the appropriate number of assignments.
                             """}
    )
    sentences_per_ranking: int = field(
        default=4, metadata={"help": "Lower bound on how many entries a ranking assignment should have."}
    )
    rankings_per_original: int = field(
        default=2, metadata={"help": "How many ranking assignments should be created per original."}
    )
    db_username: str = field(
        default=MISSING, metadata={"help": "Username of the Mongo DB to use for our task data.", "required":True}
    )
    db_password: str = field(
        default=MISSING, metadata={"help": "Password of Mongo DB to use for our task data.", "required":True}
    )
    db_location: str = field(
        default=MISSING, metadata={"help": "Hostname and Port of Mongo DB.", "required":True}
    )
    auto_pay_bonus: bool = field(
        default=False, metadata={"help": "If bonuses for good performance should be automatically be paid out."}
    )
    bonus_ranking: float = field(
        default=MISSING, metadata={"help": "Bonus amount to be paid out to the best ranking regarding one original."}
    )
    bonus_cad: float = field(
        default=MISSING, metadata={"help": "Bonus amount to be paid out to the best cad for one original."}
    )