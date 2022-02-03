#!/usr/bin/env python
# Copyright (c) 2022, John San Soucie
from __future__ import annotations

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

setup(
    ext_modules=[
        Pybind11Extension(
            "_rostpy",
            ["src/rostpy/bindings.cpp"],
            include_dirs=["extern/librost/include"],
        )
    ],
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    use_scm_version={"write_to": "src/rostpy/_version.py"},
    setup_requires=["setuptools_scm"],
)
