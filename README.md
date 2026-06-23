# rostpy

[![Documentation Status][rtd-badge]][rtd-link]
[![Code style: black][black-badge]][black-link]

[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]


## Installation from GitHub

`rostpy` keeps the C++ `librost` headers as a Git submodule. The Python
package is maintained in this repository, while the submodule points to the
upstream `rost-cli` repository on GitLab:

```text
extern/librost -> https://gitlab.com/warplab/rost-cli.git
```

Install directly from a Git URL so pip can clone the repository and initialize
the submodule before building the extension:

```bash
/usr/bin/python3 -m pip install "git+https://github.com/<you>/rostpy.git"
```

For a manual clone, include submodules:

```bash
git clone --recurse-submodules https://github.com/<you>/rostpy.git
```

If the repository was already cloned without submodules, initialize them before
building:

```bash
git submodule update --init --recursive
```

The build expects the `librost` headers at:

```text
extern/librost/librost/include
```

GitHub source archives do not include submodule contents, so prefer the Git URL
install form above instead of downloading a `.zip` archive.




[black-badge]:              https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]:               https://github.com/psf/black
[pypi-link]:                https://pypi.org/project/rostpy/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/rostpy
[pypi-version]:             https://badge.fury.io/py/rostpy.svg
[rtd-badge]:                https://readthedocs.org/projects/rostpy/badge/?version=latest
[rtd-link]:                 https://rostpy.readthedocs.io/en/latest/?badge=latest
