"""Fixtures for test cases."""
from __future__ import annotations

import os

try:
    from shutil import copy_tree
except ImportError:
    from shutil import copytree as copy_tree

import pytest

# from rostpy import rostpy
from rostpy import ROST_t, ROST_txy, ROST_xy


@pytest.fixture(scope="function")
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the name 'data'
    and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir = os.path.join(os.path.dirname(filename), "data")

    if os.path.isdir(test_dir):
        copy_tree(test_dir, str(tmpdir / "data"))
    return tmpdir / "data"


@pytest.fixture(params=["t", "txy", "xy"])
def rost(request):
    ROST = (
        ROST_t
        if request.param == "t"
        else ROST_xy
        if request.param == "xy"
        else ROST_txy
    )
    return ROST(
        3,
        2,
        0.1,
        1.0,
        1e-5,
    )
