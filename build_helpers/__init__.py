# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
# type: ignore
import errno

import codecs
import distutils.cmd
import distutils.log
import os
import re
import shutil
import subprocess
from distutils import cmd
from os.path import abspath, basename, dirname, exists, isdir, join, realpath, normpath
from typing import Any, List, Optional

from setuptools.command import build_py, sdist, develop


def find_version(*file_paths):
    with codecs.open(os.path.join(*file_paths), "r") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def matches(patterns: List[str], string: str) -> bool:
    string = string.replace("\\", "/")
    for pattern in patterns:
        if re.match(pattern, string):
            return True
    return False


def find_(
    root: str,
    rbase: str,
    include_files,
    include_dirs: List[str],
    excludes: List[str],
    scan_exclude: List[str],
):
    files = []
    scan_root = os.path.join(root, rbase)
    with os.scandir(scan_root) as it:
        for entry in it:
            path = os.path.join(rbase, entry.name)
            if matches(scan_exclude, path):
                continue

            if entry.is_dir():
                if matches(include_dirs, path):
                    if not matches(excludes, path):
                        files.append(path)
                else:
                    ret = find_(
                        root=root,
                        rbase=path,
                        include_files=include_files,
                        include_dirs=include_dirs,
                        excludes=excludes,
                        scan_exclude=scan_exclude,
                    )
                    files.extend(ret)
            else:
                if matches(include_files, path) and not matches(excludes, path):
                    files.append(path)

    return files


def find(
    root: str,
    include_files: List[str],
    include_dirs: List[str],
    excludes: List[str],
    scan_exclude: Optional[List[str]] = None,
):
    if scan_exclude is None:
        scan_exclude = []
    return find_(
        root=root,
        rbase="",
        include_files=include_files,
        include_dirs=include_dirs,
        excludes=excludes,
        scan_exclude=scan_exclude,
    )


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

    def run(self):
        files = find(
            ".",
            include_files=["^hydra/grammar/gen/.*"],
            include_dirs=[
                "\\.egg-info$",
                "^.pytest_cache$",
                ".*/__pycache__$",
                ".*/multirun$",
                ".*/outputs$",
                "^build$",
                "^dist$",
            ],
            scan_exclude=["^.git$", "^.nox/.*$", "^website/.*$"],
            excludes=[".*\\.gitignore$"],
        )

        if self.dry_run:
            print("Would clean up the following files and dirs")
            print("\n".join(files))
        else:
            for f in files:
                if exists(f):
                    if isdir(f):
                        shutil.rmtree(f, ignore_errors=True)
                    else:
                        os.unlink(f)


def run_antlr(self):
    try:
        self.announce("Generating parsers with antlr4", level=distutils.log.FATAL)
        self.run_command("antlr")
    except OSError as e:
        if e.errno == errno.ENOENT:
            msg = f"| Unable to generate parsers: {e} |"
            msg = "=" * len(msg) + "\n" + msg + "\n" + "=" * len(msg)
            self.announce(f"{msg}", level=distutils.log.FATAL)
            exit(1)
        else:
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
