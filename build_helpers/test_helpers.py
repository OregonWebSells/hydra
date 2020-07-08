import os.path
from typing import List

import pytest

from build_helpers import find, matches


@pytest.mark.parametrize(
    "path,include_files,include_dirs,excludes,scan_exclude,expected",
    [
        pytest.param("test_files", [], [], [], [], [], id="none"),
        pytest.param(
            "test_files",
            [".*"],
            [],
            [],
            [],
            [
                "a/b/file2.txt",
                "a/b/file1.txt",
                "a/b/junk.txt",
                "c/file2.txt",
                "c/file1.txt",
                "c/junk.txt",
            ],
            id="all",
        ),
        pytest.param(
            "test_files",
            [".*"],
            [],
            ["^a/.*"],
            [],
            ["c/file2.txt", "c/file1.txt", "c/junk.txt"],
            id="filter_a",
        ),
        pytest.param(
            "test_files",
            ["^a/.*"],
            [],
            [],
            [],
            ["a/b/file2.txt", "a/b/file1.txt", "a/b/junk.txt"],
            id="include_a",
        ),
        pytest.param(
            "test_files",
            ["^a/.*"],
            [],
            [".*/file1\\.txt"],
            [],
            ["a/b/file2.txt", "a/b/junk.txt"],
            id="include_a,exclude_file1",
        ),
        pytest.param(
            "test_files",
            [".*"],
            [],
            ["^.*/junk.txt$"],
            [],
            ["a/b/file2.txt", "a/b/file1.txt", "c/file2.txt", "c/file1.txt",],
            id="no_junk",
        ),
        pytest.param(
            "test_files",
            ["^.*/junk.txt"],
            [],
            [],
            [],
            ["a/b/junk.txt", "c/junk.txt"],
            id="junk_only",
        ),
        pytest.param("test_files", [".*"], [], ["^a$"], [], ["a"], id="exact_a"),
        pytest.param(
            "test_files",
            [],
            [".*bad_dir$"],
            [],
            [],
            ["a/b/bad_dir", "c/bad_dir"],
            id="bad_dirs",
        ),
    ],
)
def test_find(
    path: str,
    include_files: List[str],
    include_dirs: List[str],
    excludes: List[str],
    scan_exclude: List[str],
    expected: List[str],
):
    basedir = os.path.normpath(os.path.dirname(__file__))
    path = os.path.join(basedir, "test_files")
    ret = find(
        root=path,
        excludes=excludes,
        include_files=include_files,
        include_dirs=include_dirs,
        scan_exclude=scan_exclude,
    )
    assert ret == expected


@pytest.mark.parametrize(
    "patterns,query,expected",
    [
        (["^a/.*"], "a/", True),
        (["^a/.*"], "a\\", True),
        (["^/foo/bar/.*"], "/foo/bar/blag", True),
        (["^/foo/bar/.*"], "\\foo\\bar/blag", True),
    ],
)
def test_matches(patterns: List[str], query: str, expected: bool) -> None:
    ret = matches(patterns, query)
    assert ret == expected
