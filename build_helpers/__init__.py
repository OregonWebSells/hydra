# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
# type: ignore
import errno

import codecs
import distutils.cmd
import distutils.log
import os
import re
import setuptools
import shutil
import subprocess
import sys
from distutils import cmd, dir_util
from os.path import abspath, basename, dirname, exists, isdir, join
from typing import Any, List

from setuptools.command import build_py, sdist, develop


def find_version(*file_paths):
    with codecs.open(os.path.join(*file_paths), "r") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def run_antlr(self):
    try:
        self.announce("Generating parsers with antlr4", level=distutils.log.FATAL)
        self.run_command("antlr")
    except OSError as e:
        if e.errno == errno.ENOENT:
            msg = f"| Unable to generate parsers, is java installed? {e} |"
            msg = "=" * len(msg) + "\n" + msg + "\n" + "=" * len(msg)
            self.announce(f"{msg}", level=distutils.log.FATAL)
            exit(1)
        else:
            # Something else went wrong while trying to run `wget`
            raise


class BuildPyCommand(build_py.build_py):
    def run(self):
        if not self.dry_run:
            run_antlr(self)
        build_py.build_py.run(self)


class Develop(develop.develop):
    def run(self):
        if not self.dry_run:
            run_antlr(self)
        develop.develop.run(self)


class SDistCommand(sdist.sdist):
    def run(self):
        if not self.dry_run:
            run_antlr(self)
        sdist.sdist.run(self)


class CleanCommand(cmd.Command):
    """
    Our custom command to clean out junk files.
    """

    description = "Cleans out junk files we don't want in the repo"
    user_options: List[Any] = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def find(root, includes, excludes=[]):
        res = []
        for parent, dirs, files in os.walk(root):
            for f in dirs + files:
                add = list()
                for include in includes:
                    if re.findall(include, f):
                        add.append(join(parent, f))
                res.extend(add)
        final_list = []
        # Exclude things that matches an exclude pattern
        for ex in excludes:
            for file in res:
                if not re.findall(ex, file):
                    final_list.append(file)
        return final_list

    def run(self):
        delete_patterns = [
            ".eggs",
            "hydra/grammar/gen",
            ".egg-info",
            ".pytest_cache",
            "build/",
            "dist",
            "__pycache__",
            ".pyc",
        ]
        deletion_list = CleanCommand.find(
            ".", includes=delete_patterns, excludes=["\\.nox/.*", ".gitignore"]
        )

        for f in deletion_list:
            if exists(f):
                if isdir(f):
                    shutil.rmtree(f, ignore_errors=True)
                else:
                    os.unlink(f)


class ANTLRCommand(distutils.cmd.Command):
    """Generate parsers using ANTLR."""

    description = "Run ANTLR"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        root_dir = abspath(dirname(__file__))
        project_root = abspath(dirname(basename(__file__)))
        for grammar in [
            "hydra/grammar/Override.g4",
        ]:
            command = [
                "java",
                "-jar",
                join(root_dir, "bin/antlr-4.8-complete.jar"),
                f"-Dlanguage=Python3",
                "-o",
                join(project_root, "hydra/grammar/gen/"),
                "-Xexact-output-dir",
                "-visitor",
                join(project_root, grammar),
            ]

            self.announce(
                f"Generating parser for Python3: {command}", level=distutils.log.INFO,
            )

            subprocess.check_call(command)
