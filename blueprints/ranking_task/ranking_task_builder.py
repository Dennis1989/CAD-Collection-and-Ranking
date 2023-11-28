#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprint import TaskBuilder

from distutils.dir_util import copy_tree
import os
import shutil

from typing import Optional
import subprocess

# TODO this probably does not need to be changed

class RankingTaskBuilder(TaskBuilder):
    """
    Builder for a ranking task, puts required files into
    the server directory for deployment.
    """

    BUILT_FILE = "done.built"
    BUILT_MESSAGE = "built!"

    def build_in_dir(self, build_dir: str):
        """Build the frontend if it doesn't exist, then copy into the server directory"""
        # moved the call of 'build_custom_bundle' here from init script

        self.build_custom_bundle(
            self.args.blueprint.webapp_dir,
            force_rebuild=self.args.task.force_rebuild,
            post_install_script=self.args.task.post_install_script,
        )

        target_resource_dir = os.path.join(build_dir, "static")

        # If any additional task files are required via a source_dir, copy those as well
        extra_dir_path = self.args.blueprint.get("extra_source_dir", None)
        if extra_dir_path is not None:
            extra_dir_path = os.path.expanduser(extra_dir_path)
            copy_tree(extra_dir_path, target_resource_dir)

        # Copy the built core and the given task file to the target path
        webapp_path = os.path.expanduser(self.args.blueprint.webapp_dir)
        use_bundle = os.path.join(webapp_path, "build", "bundle.js")
        target_path = os.path.join(target_resource_dir, "bundle.js")

        should_link_task_source = self.args.blueprint.get("link_task_source", False)
        if should_link_task_source:
            os.symlink(use_bundle, target_path)
        else:
            shutil.copy2(use_bundle, target_path)

        # Write a built file confirmation
        with open(os.path.join(build_dir, self.BUILT_FILE), "w+") as built_file:
            built_file.write(self.BUILT_MESSAGE)

    def build_custom_bundle(
        self,
        webapp_path,
        force_rebuild: Optional[bool] = None,
        post_install_script: Optional[str] = None,
    ):
        """Locate all of the custom files used for a custom build, create
        a prebuild directory containing all of them, then build the
        custom source.

        Check dates to only go through this build process when files have changes
        """

        """
        If doing local package development make sure to check out the below link:
        https://github.com/facebookresearch/Mephisto/issues/811
        """

        IGNORE_FOLDERS = {"node_modules", "build"}

        IGNORE_FOLDERS = {os.path.join(webapp_path, f) for f in IGNORE_FOLDERS}
        build_path = os.path.join(webapp_path, "build", "bundle.js")

        # see if we need to rebuild
        if force_rebuild is None or force_rebuild == False:
            if os.path.exists(build_path):
                created_date = os.path.getmtime(build_path)
                up_to_date = True

                for root, dirs, files in os.walk(webapp_path):
                    for igf in IGNORE_FOLDERS:
                        should_ignore = False
                        if igf in root:
                            should_ignore = True
                    if should_ignore:
                        continue
                    if not up_to_date:
                        break
                    for fname in files:
                        path = os.path.join(root, fname)
                        if os.path.getmtime(path) > created_date:
                            up_to_date = False
                            break
                if up_to_date:
                    return build_path

        # navigate and build
        return_dir = os.getcwd()
        os.chdir(webapp_path)

        packages_installed = subprocess.call(["yarn", "install"])
        if packages_installed != 0:
            raise Exception(
                "please make sure yarn is installed, otherwise view " "the above error for more info."
            )

        if post_install_script is not None and len(post_install_script) > 0:
            did_fail_script = subprocess.call(["bash", post_install_script])
            if did_fail_script != 0:
                raise Exception(
                    "Please make sure that the post_install_script mentioned in your hydra config "
                    "exists in the webapp folder for this task!\n"
                    "The script should be able to be ran with bash"
                )

        webpack_complete = subprocess.call(["yarn", "run", "dev"])
        if webpack_complete != 0:
            raise Exception(
                "Webpack appears to have failed to build your "
                "frontend. See the above error for more information."
            )

        # cleanup and return
        os.chdir(return_dir)
        return build_path