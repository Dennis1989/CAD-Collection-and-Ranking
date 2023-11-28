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
from mephisto.data_model.assignment import InitializationData
#from mephisto.abstractions.blueprints.static_from_db.static_agent_state import (
#    StaticAgentState,
#)

import os
import csv
import json
import types


import pickle
import math

from typing import ClassVar, Type, Any, Dict, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.blueprint import (
        AgentState,
        TaskRunner,
        TaskBuilder,
    )

@dataclass
class SharedRankingTaskState(
    ScreenTaskSharedState, OnboardingSharedState, GoldUnitSharedState, SharedTaskState
):
    static_task_data: Iterable[Any] = field(
        default_factory=list,
        metadata={
            "help": (
                "List or generator that returns dicts of task data. Generators can be "
                "used for tasks with lengths that aren't known at the start of a "
                "run, or are otherwise determined during the run. "
            ),
            "type": "Iterable[Dict[str, Any]]",
            "default": "[]",
        },
    )