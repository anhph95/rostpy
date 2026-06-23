# rostpy

`rostpy` provides Python bindings for ROST topic modeling.

This repository is a maintenance fork of the original GitLab `rostpy`
repository. It is hosted on GitHub so the Python package can be maintained and
modernized here while preserving the upstream `librost` dependency.

`librost` is still provided by the upstream GitLab `rost-cli` repository through
a Git submodule:

```text
extern/librost -> https://gitlab.com/warplab/rost-cli.git
```

## Installation

Activate your Python environment first, then install from this GitHub fork:

```bash
python -m pip install "git+https://github.com/anhph95/rostpy.git"
```

For local development, clone with submodules:

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

GitHub source archives do not include submodule contents, so prefer Git-based
installation instead of downloading a `.zip` archive.

## Example notebook

The worked example lives in:

```text
examples/rost_repeated_runs_statistics.ipynb
```

It demonstrates a generic abundance-table workflow:

- deterministic abundance-to-count scaling;
- fitting a ROST model;
- repeating stochastic runs;
- computing model statistics;
- selecting the best run;
- inspecting sample-topic and topic-word probabilities.

The README intentionally stays focused on package functionality. The notebook
contains the executable example.

## Data model

ROST expects each observation to be a list of integer word IDs. For abundance
tables, a common workflow is:

```text
abundance table
-> deterministic integer counts
-> repeated word IDs
-> ROST observations
```

In this framing:

- each column is a word, feature, or taxon;
- each row is a sample or cell;
- each latent topic is a recurring community or pattern;
- each sample is represented by a mixture of topics.

## Model classes

`rostpy` exposes three model classes. They use the same topic-modeling methods
but differ in how they interpret cell poses.

- `ROST_t`: temporal model. Poses are `[t]`.
- `ROST_txy`: spatiotemporal model. Poses are `[time_bin, x_bin, y_bin]`.
- `ROST_xy`: spatial model. Poses are `[time_bin, x_bin, y_bin]`, but time is
  ignored when matching cells.

Constructor options:

- `V`: vocabulary size, usually the number of words/features/taxa.
- `K`: number of topics.
- `alpha`: smoothing for topic mixtures within samples.
- `beta`: smoothing for word distributions within topics.
- `gamma`: topic-growth parameter used when `enable_auto_topics_size(True)` is
  enabled.

Important attributes:

- `model.K`: configured topic count.
- `model.active_K`: active topic count when automatic topic growth is enabled.
- `model.V`: vocabulary size.
- `model.g_sigma`: neighborhood decay between cells.
- `model.update_global_model`: whether refinement updates the global topic-word
  model.

## Core functions

Module-level refinement:

- `parallel_refine(model, nt)`: refine all current cells using `nt` worker
  threads.
- `parallel_refine_tau(model, nt, tau, iter)`: refine sampled cells using a
  beta-distributed cell preference.

Observation methods:

- `add_observation(pose, words, update_model=True)`: add one observation.
- `add_observation(pose, words, topics, update_model=True)`: add one observation
  with initial topic labels.
- `addObservations(pose, words, topics=[], update_model=True)`: compatibility
  spelling for adding observations.
- `forget(cell_id=-1)`: remove one cell.

Refinement and estimation:

- `refine_cell(cell_id, blocking=True)`: refine one cell by internal cell ID.
- `refine_pose(pose, blocking=True)`: refine one cell by pose.
- `estimate_cell(cell_id, update_ppx=False)`: estimate maximum-likelihood topics
  for one cell.
- `refine_ext(words, n_iter=10, nZg=[])`: sample topics for external words
  without adding them to the model.

Topic labels and model state:

- `get_topics_for_pose(pose)`: return current sampled topic labels.
- `get_ml_topics_for_pose(pose, update_ppx=False)`: return maximum-likelihood
  topic labels.
- `get_topics_and_ppx_for_pose(pose)`: return current labels and perplexity.
- `get_ml_topics_and_ppx_for_pose(pose)`: return maximum-likelihood labels and
  perplexity.
- `get_topic_model()`: return the `K x V` topic-word count matrix.
- `set_topic_model(topic_model)`: set the topic-word matrix from a nested
  `K x V` list.
- `set_topic_model_flat(topic_model, topic_weights)`: compatibility interface
  for a flattened topic-word matrix.
- `get_topic_weights()`: return total word counts assigned to each topic.

Diagnostics:

- `perplexity(recompute=False)`: whole-model perplexity.
- `perplexity(pose, recompute=False)`: pose-level perplexity.
- `time_perplexity(t, recompute=False)`: time-step perplexity.
- `word_perplexity(pose, recompute=False)`: per-word perplexity values.
- `topic_perplexity(pose)`: topic-label perplexity for a pose.
- `cell_perplexity_topic(nZ)`: topic perplexity for a topic-count vector.
- `cell_perplexity_word(words, nZ)`: word perplexity under a topic-count vector.
- `word_topic_perplexity(pose)`: per-word topic perplexity.

Counters and indexing:

- `num_cells()`: number of cells currently in the model.
- `get_num_words()`: vocabulary size.
- `get_refine_count()`: number of cell refinements completed.
- `get_word_refine_count()`: number of word-token refinements completed.
- `get_poses_by_time()`: dictionary mapping time bins to poses.

Lower-level controls:

- `add_count(w, z, c=1)`: manually add counts for word `w` in topic `z`.
- `relabel(w, z_old, z_new)`: manually move a word count between topics.
- `shuffle_topics()`: randomly shuffle topic labels in existing cells.
- `update_gamma()`: update internal topic-growth weights.
- `enable_auto_topics_size(enabled=True)`: enable or disable automatic topic
  growth.

## Reproducibility note

ROST refinement is stochastic. Parallel refinement can also vary because thread
scheduling changes update order. For analysis, repeated runs are often more
useful than trying to force one parallel run to be exactly reproducible.

The example notebook demonstrates this repeated-run workflow.
