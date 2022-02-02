#!/usr/bin/env python
# Copyright (c) 2022, John San Soucie

from glob import glob
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "_rostpy",
        ["src/rostpy/bindings.cpp"],
    ),
]

setup(cmdclass={"build_ext": build_ext}, ext_modules=ext_modules)
