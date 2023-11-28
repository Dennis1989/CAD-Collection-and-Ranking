#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit

db = None


def format_for_printing_data(data):
    global db
    # Custom tasks can define methods for how to display their data in a relevant way
    worker_name = Worker.get(db, data["worker_id"]).worker_name
    contents = data["data"]
    duration = data["task_end"] - data["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    inputs = contents["inputs"]
    outputs = contents["outputs"]
    # Case 1: CAD was submitted
    if inputs['stage'] == "CAD" and 'cad' in outputs:
        inputs_string = (
            f"Original: {inputs['original']}"
        )
        output_string = (
            f"CAD:      {outputs['cad']}"
        )

    # Case 2: CAD was rejected and explanation provided
    elif inputs['stage'] == "CAD" and 'explanation' in outputs:
        inputs_string = (
            f"Original: {inputs['original']}"
        )
        output_string = (
            f"Worker rejected the input as not sexist and provided the following explanation:\n{outputs['explanation']}"
        )
    # Case 3: Ranking was submitted
    elif inputs['stage'] == "RANKING":
        inputs_string = "Input sentences:\n"
        inputs_string += "\n".join([f"{num}. {sentence}" for (num, sentence) in enumerate(inputs['sentences'])])

        output_string = f"Permutation: {outputs['permutation']}"
    else:
        raise Exception("Unknown unit type")

    return f"-------------------\n{metadata_string}\n{inputs_string}\n{output_string}"


def main():
    global db
    db = LocalMephistoDB()
    run_examine_or_review(db, format_for_printing_data)


if __name__ == "__main__":
    main()
