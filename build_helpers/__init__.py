# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
# type: ignore
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


class BuildPyCommand(build_py.build_py):
    """Custom build command."""

    def run(self):
        if not self.dry_run:
            self.run_command("antlr")
        build_py.build_py.run(self)


class Develop(develop.develop):
    """Custom build command."""

    def run(self):
        if not self.dry_run:
            self.run_command("antlr")
        develop.develop.run(self)


class SDistCommand(sdist.sdist):
    """Custom build command."""

    def run(self):
        if not self.dry_run:
            self.run_command("antlr")
        sdist.run(self)


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
            ".egg-info",
            ".pytest_cache",
            "build",
            "dist",
            "__pycache__",
            ".pyc",
        ]
        deletion_list = CleanCommand.find(
            ".", includes=delete_patterns, excludes=["\\.nox/.*"]
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
        try:
            """
            This is a nasty hack to work around setuptools inability to handle copying files from the parent dir.
            When we build we copy the parent grammar and bin directories here.
            And we use them.
            In addition, when we create the source dist (sdist) tox is using, we add those same into it -
            because this is what the tox build is getting access to.
            finally, this code need to work both in the tox mode where bin and grammar are in
            the source tree and in normal mode when they are not, so it copies them here only if
            they are not already here and finally deletes them.
            """
            copied_bin = False
            copied_grammar = False
            if exists("bin"):
                dir_util.copy_tree("bin", "bin")
                copied_bin = True
            if exists("../grammar"):
                dir_util.copy_tree("../grammar", "grammar")
                copied_grammar = True

            pyver = 3
            for grammar in [
                "hydra/grammar/Override.g4",
            ]:
                command = [
                    sys.executable,
                    join(root_dir, "bin/antlr4"),
                    f"-Dlanguage=Python{pyver}",
                    "-o",
                    join(project_root, "hydra/grammar/gen/"),
                    "-Xexact-output-dir",
                    "-visitor",
                    join(project_root, grammar),
                ]
                self.announce(
                    f"Generating parser for Python {pyver}: {command}",
                    level=distutils.log.INFO,
                )
                subprocess.check_call(command)
        finally:
            if copied_bin:
                shutil.rmtree("bin", ignore_errors=True)
            if copied_grammar:
                shutil.rmtree("grammar", ignore_errors=True)
