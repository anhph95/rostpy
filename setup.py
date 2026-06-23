#!/usr/bin/env python
# Copyright (c) 2022, John San Soucie
from __future__ import annotations

from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

LIBROST_INCLUDE = Path("extern/librost/librost/include")

if not LIBROST_INCLUDE.is_dir():
    raise RuntimeError(
        "Missing librost headers at extern/librost/librost/include. "
        "Initialize the Git submodule with "
        "`git submodule update --init --recursive`, or install rostpy from a "
        "Git URL so pip can initialize submodules before building."
    )

setup(
    ext_modules=[
        Pybind11Extension(
            "_rostpy",
            ["src/rostpy/bindings.cpp"],
            include_dirs=[str(LIBROST_INCLUDE)],
            cxx_std=17,
        )
    ],
    cmdclass={"build_ext": build_ext},
)
