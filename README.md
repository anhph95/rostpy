# rostpy

[![Documentation Status][rtd-badge]][rtd-link]
[![Code style: black][black-badge]][black-link]

[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]


## Installation from GitHub

This repository is a maintenance fork of the original GitLab `rostpy`
repository. It is hosted on GitHub so the Python package can be maintained and
modernized here, while preserving the upstream `librost` dependency.

`rostpy` keeps the C++ `librost` headers as a Git submodule. The Python package
is maintained in this GitHub fork, while the submodule points to the upstream
`rost-cli` repository on GitLab:

```text
extern/librost -> https://gitlab.com/warplab/rost-cli.git
```

Install directly from a Git URL so pip can clone the repository and initialize
the submodule before building the extension. Activate your virtual environment
first, then install with:

```bash
python -m pip install "git+https://github.com/anhph95/rostpy.git"
```

For a manual clone, include submodules:

```bash
git clone --recurse-submodules https://github.com/anhph95/rostpy.git
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

## Core Python API

The package exposes three ROST topic-model classes:

- `ROST_t`: one-dimensional temporal poses, written as `[t]`
- `ROST_xy`: spatial poses, written as `[t, x, y]`; time is ignored when hashing
  cells
- `ROST_txy`: spatiotemporal poses, written as `[t, x, y]`

The module also exposes:

- `parallel_refine(model, nt)`
- `parallel_refine_tau(model, nt, tau, iter)`

Each model exposes these callable methods and properties:

- model setup/state: `K`, `active_K`, `V`, `alpha`, `beta`, `gamma`, `betaV`,
  `g_sigma`, `update_global_model`
- observations: `add_observation`, `addObservations`, `forget`
- refinement and estimation: `refine_cell`, `refine_pose`, `estimate_cell`,
  `refine_ext`, `computeMaxLikelihoodTopics`
- topics and model state: `get_topics_for_pose`, `get_topics_and_ppx_for_pose`,
  `get_ml_topics_for_pose`, `get_ml_topics_and_ppx_for_pose`,
  `get_topic_model`, `set_topic_model`, `set_topic_model_flat`,
  `get_topic_weights`
- diagnostics: `perplexity`, `time_perplexity`, `word_perplexity`,
  `topic_perplexity`, `cell_perplexity_topic`, `cell_perplexity_word`,
  `word_topic_perplexity`
- counters and indexing: `num_cells`, `get_num_words`, `get_refine_count`,
  `get_word_refine_count`, `get_poses_by_time`
- low-level count controls: `add_count`, `relabel`, `shuffle_topics`,
  `update_gamma`, `enable_auto_topics_size`

## Example usage

```python
import rostpy

# Create a temporal model.
model = rostpy.ROST_t(V=100, K=5, alpha=0.1, beta=1.0, gamma=0.01)

# Add two cells of word observations. ROST_t poses use [t].
model.add_observation([0], [3, 10, 42, 42])
model.add_observation([1], [2, 3, 3, 20])

# Refine one cell, then refine all cells in parallel with one worker.
model.refine_pose([0])
rostpy.parallel_refine(model, nt=1)

# Estimate maximum-likelihood topic labels for a pose.
topics = model.get_ml_topics_for_pose([0])
topics_with_ppx = model.get_ml_topics_and_ppx_for_pose([0])

# Inspect model state.
topic_word_counts = model.get_topic_model()
topic_weights = model.get_topic_weights()
overall_ppx = model.perplexity(False)

# Replace the topic model with a K x V matrix.
model.set_topic_model(topic_word_counts)

print(topics)
print(topic_weights)
print(overall_ppx)
```




[black-badge]:              https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]:               https://github.com/psf/black
[pypi-link]:                https://pypi.org/project/rostpy/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/rostpy
[pypi-version]:             https://badge.fury.io/py/rostpy.svg
[rtd-badge]:                https://readthedocs.org/projects/rostpy/badge/?version=latest
[rtd-link]:                 https://rostpy.readthedocs.io/en/latest/?badge=latest
