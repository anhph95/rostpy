#!/usr/bin/env python
# Copyright (c) 2022, John San Soucie

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

# Convert distutils Windows platform specifiers to CMake -A arguments


# A CMakeExtension needs a sourcedir instead of a file list.
# The name must be the _single_ output extension from the CMake build.
# If you need multiple extensions, see scikit-build.
class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        # required for auto-detection & inclusion of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
        ]
        # Adding CMake arguments set as environment variable
        # (needed e.g. to build for ARM OSx on conda-forge)
        if "CMAKE_ARGS" in os.environ:
            cmake_args += [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]

        rost_build_temp = str(Path(self.build_temp) / "rost")
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        if not os.path.exists(rost_build_temp):
            os.makedirs(rost_build_temp)

        subprocess.check_call(
            ["cmake", str(Path(ext.sourcedir) / "extern/librost")] + cmake_args,
            cwd=rost_build_temp,
        )
        subprocess.check_call(
            [
                "make",
            ],
            cwd=rost_build_temp,
        )
        subprocess.check_call(
            ["make", "install"],
            cwd=rost_build_temp,
        )
        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp
        )
        subprocess.check_call(
            [
                "make",
            ],
            cwd=self.build_temp,
        )
        subprocess.check_call(
            ["make", "install"],
            cwd=self.build_temp,
        )


setup(
    ext_modules=[CMakeExtension("rostpy")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
    use_scm_version={"write_to": "src/rostpy/_version.py"},
    setup_requires=["setuptools_scm"],
)
