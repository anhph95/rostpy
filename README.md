# rostpy

`rostpy` provides Python bindings for ROST topic modeling.

This repository is a maintenance fork of the original GitLab `rostpy`
repository. It is hosted on GitHub so the Python package can be maintained and
modernized here, while preserving the upstream `librost` dependency.

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

GitHub source archives do not include submodule contents, so prefer the Git URL
install form instead of downloading a `.zip` archive.

## Topic modeling abundance data

The main intended workflow is topic modeling ecological abundance data, such as
IFCB taxon carbon, concentration, or count tables.

In this framing:

- each taxon is a vocabulary word;
- each sample is a document/cell;
- each latent topic is an ecological community;
- each sample is represented by a mixture of latent communities.

ROST expects discrete word IDs. If the input is an abundance table, first scale
the abundances to deterministic integer counts. This preserves absolute
abundance differences among samples, unlike fixed-depth relative tokenization,
which changes the model target to relative composition only.

```python
import numpy as np
import pandas as pd
import rostpy

# Example abundance table.
# Rows are samples, columns are taxa, and values are abundance-like
# measurements such as carbon biomass, cell concentration, or counts.
abundance = pd.DataFrame(
    {
        "Chaetoceros": [25000, 5000, 0],
        "Lauderia": [10000, 30000, 5000],
        "Pseudo-nitzschia": [0, 15000, 45000],
    },
    index=["sample_001", "sample_002", "sample_003"],
)

# Expected shape:
# abundance.shape == (3, 3)
# Three samples by three taxa.

# Store taxon names before converting the table to integer word counts.
# These names are useful later when interpreting the learned topic-word matrix.
taxa = abundance.columns

# Choose a deterministic scaling factor.
# ROST needs integer counts, but raw abundance values may be too large to
# repeat directly as word tokens. Scaling compresses the counts while keeping
# absolute abundance structure.
scale = 10000

# Convert abundance to integer counts.
# Use round() instead of astype(int) directly so values are not always floored
# toward zero. Flooring can systematically remove near-threshold taxa.
counts = abundance.div(scale).round().astype(int)

# Expected output:
# counts
#                   Chaetoceros  Lauderia  Pseudo-nitzschia
# sample_001                  2         1                 0
# sample_002                  0         3                 2
# sample_003                  0         0                 4

# Optional quality checks.
# token_counts is the number of ROST word tokens that each sample will
# contribute to the model.
token_counts = counts.sum(axis=1)

# Expected output:
# token_counts
# sample_001    3
# sample_002    5
# sample_003    4
#
# If many rows are zero, reduce the scale or use a dominance-compressing
# transform such as sqrt(abundance) before scaling.
print(token_counts.describe())
print("empty samples:", int((token_counts == 0).sum()))
print("nonzero taxa:", int((counts.sum(axis=0) > 0).sum()), "of", counts.shape[1])

# Create a temporal ROST model.
# V is the vocabulary size: one word ID per taxon.
# K is the number of latent communities/topics.
# alpha controls topic smoothing within samples.
# beta controls taxon smoothing within topics.
# gamma controls automatic topic growth if enable_auto_topics_size(True) is used.
model = rostpy.ROST_t(
    V=len(taxa),
    K=2,
    alpha=0.5,
    beta=0.5,
    gamma=0.1,
)

# g_sigma controls neighborhood decay between cells.
# For ROST_t, neighboring cells are neighboring time indices.
model.g_sigma = 0.5

# Add each sample to the model.
# ROST_t uses one-dimensional poses: [t].
# Each taxon ID is repeated according to its scaled integer count.
sample_ids = counts.index.to_list()
pose_to_sample = {}

for t, sample_id in enumerate(sample_ids):
    row = counts.loc[sample_id]

    # Build the observation as repeated integer word IDs.
    # Example:
    # counts [2, 1, 0] becomes obs [0, 0, 1].
    obs = []
    for taxon_id, count in enumerate(row):
        obs.extend([taxon_id] * int(count))

    # Skip empty samples because they do not contribute words to the model.
    if not obs:
        continue

    # Add this sample as one ROST cell at temporal pose [t].
    model.add_observation([t], obs)
    pose_to_sample[t] = sample_id

# Expected output:
# model.num_cells() == number of non-empty samples
# model.get_num_words() == number of taxa
print("cells:", model.num_cells())
print("vocabulary size:", model.get_num_words())

# Refine the latent topic assignments.
# parallel_refine(model, nt) refines all current cells with nt worker threads.
# Repeating this call performs multiple refinement epochs.
for epoch in range(100):
    rostpy.parallel_refine(model, nt=1)

# Expected output:
# get_refine_count() increases by roughly model.num_cells() per epoch.
# get_word_refine_count() increases by the number of word tokens refined.
print("refined cells:", model.get_refine_count())
print("refined words:", model.get_word_refine_count())

# Convert per-word topic labels into per-sample community counts.
community_counts = {
    f"community_{k + 1}": [0 for _ in sample_ids]
    for k in range(model.K)
}

for t, sample_id in enumerate(sample_ids):
    if t not in pose_to_sample:
        continue

    # get_ml_topics_for_pose returns maximum-likelihood topic labels for the
    # words observed at this pose. These labels are useful for final summaries
    # because they are less noisy than a single stored Gibbs sample.
    topics = model.get_ml_topics_for_pose([t])

    # Expected output:
    # topics is a list of integer topic IDs, one per word token in the sample.
    # Example: [0, 0, 1]
    for topic in topics:
        community_counts[f"community_{topic + 1}"][t] += 1

# Convert community counts to a table indexed by original sample IDs.
community_count_df = pd.DataFrame(community_counts, index=sample_ids)

# Normalize within each sample to estimate community mixture probabilities.
community_prob_df = community_count_df.div(
    community_count_df.sum(axis=1),
    axis=0,
).fillna(0)

# Expected shape:
# community_prob_df.shape == (number_of_samples, K)
print(community_prob_df)

# Extract the learned topic-word count matrix.
# Rows are communities/topics and columns are taxa.
topic_word_counts = model.get_topic_model()

topic_word_df = pd.DataFrame(
    topic_word_counts,
    columns=taxa,
    index=[f"community_{k + 1}" for k in range(model.K)],
)

# Normalize within each community to get taxon probabilities.
topic_word_prob_df = topic_word_df.div(topic_word_df.sum(axis=1), axis=0).fillna(0)

# Expected shape:
# topic_word_prob_df.shape == (K, number_of_taxa)
print(topic_word_prob_df)

# Whole-model perplexity is a diagnostic of model fit.
# Lower values generally indicate that the model predicts the observed words
# better, but interpretability and ecological plausibility still matter.
print("perplexity:", model.perplexity())
```

## Model choices

`rostpy` exposes three model classes. They use the same topic-modeling methods,
but differ in how they interpret the cell pose.

Use `ROST_t` when samples are ordered only by time. The pose has one value:
`[t]`.

```python
model = rostpy.ROST_t(V=len(taxa), K=2, alpha=0.5, beta=0.5, gamma=0.1)
model.add_observation([t], obs)
```

Use `ROST_txy` when samples have time and spatial coordinates. The pose has
three values: `[time_bin, x_bin, y_bin]`. This is the best choice when nearby
samples in time and space should influence each other.

```python
model = rostpy.ROST_txy(V=len(taxa), K=2, alpha=0.5, beta=0.5, gamma=0.1)
model.add_observation([time_bin, x_bin, y_bin], obs)
```

Use `ROST_xy` when spatial location matters but time should be ignored when
matching cells. The pose is still `[time_bin, x_bin, y_bin]`, but the model
hashes cells by the spatial dimensions.

```python
model = rostpy.ROST_xy(V=len(taxa), K=2, alpha=0.5, beta=0.5, gamma=0.1)
model.add_observation([time_bin, x_bin, y_bin], obs)
```

Constructor options:

- `V`: vocabulary size. For abundance tables, this is the number of taxa.
- `K`: number of latent topics or communities. Larger `K` allows more
  communities, but can make results harder to interpret.
- `alpha`: smoothing for topic mixtures inside each cell/sample. Larger values
  allow samples to mix more evenly across topics; smaller values encourage each
  sample to use fewer topics.
- `beta`: smoothing for taxon/word distributions inside each topic. Larger
  values make topics broader; smaller values make topics concentrate on fewer
  taxa.
- `gamma`: topic-growth parameter used when `enable_auto_topics_size(True)` is
  enabled. It is not the neighborhood smoothing parameter.

Important model attributes:

- `model.K`: configured number of topics.
- `model.active_K`: number of active topics when automatic topic growth is
  enabled.
- `model.V`: vocabulary size.
- `model.g_sigma`: neighborhood decay. Smaller values reduce the influence of
  neighboring cells faster.
- `model.update_global_model`: whether refinement updates the global topic-word
  count matrix.

## Core callable API

Module-level functions:

- `parallel_refine(model, nt)`: refine all current cells using `nt` worker
  threads. Repeating this call performs multiple refinement epochs.
- `parallel_refine_tau(model, nt, tau, iter)`: refine `iter` sampled cells using
  `nt` worker threads. The `tau` parameter biases which cell IDs are selected;
  larger values favor later cells.

Model classes:

- `ROST_t`: temporal model with poses shaped like `[t]`.
- `ROST_xy`: spatial model with poses shaped like `[t, x, y]`, but time is
  ignored for cell matching.
- `ROST_txy`: spatiotemporal model with poses shaped like `[t, x, y]`.

Observation methods:

- `add_observation(pose, words, update_model=True)`: add one sample/cell to the
  model. `pose` is the time/spatial coordinate, and `words` is a list of integer
  taxon IDs.
- `add_observation(pose, words, topics, update_model=True)`: add one sample with
  explicit initial topic labels. `topics` must have the same length as `words`.
- `addObservations(pose, words, topics=[], update_model=True)`: compatibility
  spelling for `add_observation`.
- `forget(cell_id=-1)`: remove one cell from the model. If `cell_id` is not
  supplied, `librost` chooses a cell internally.

Refinement and estimation methods:

- `refine_cell(cell_id, blocking=True)`: run one Gibbs-style refinement update
  for a cell by numeric cell ID.
- `refine_pose(pose, blocking=True)`: run one refinement update for a cell by
  pose, such as `[t]` or `[time_bin, x_bin, y_bin]`.
- `estimate_cell(cell_id, update_ppx=False)`: return maximum-likelihood topic
  labels for one cell without replacing the stored labels.
- `refine_ext(words, n_iter=10, nZg=[])`: sample topic labels for a temporary
  list of words without adding those words to the model. This is useful for
  asking how an external sample would be labeled.

Topic label methods:

- `get_topics_for_pose(pose)`: return the current stored topic labels for the
  words at a pose. These are the current sampled labels.
- `get_ml_topics_for_pose(pose, update_ppx=False)`: return
  maximum-likelihood topic labels for the words at a pose. This is usually a
  cleaner choice for final summaries.
- `get_topics_and_ppx_for_pose(pose)`: return current sampled topic labels and
  the current perplexity value for a pose.
- `get_ml_topics_and_ppx_for_pose(pose)`: return maximum-likelihood topic labels
  and perplexity for a pose.

Topic model methods:

- `get_topic_model()`: return the learned topic-word count matrix as a nested
  list shaped `K x V`, where rows are topics and columns are taxa/words.
- `set_topic_model(topic_model)`: replace the topic-word count matrix with a
  nested `K x V` list.
- `set_topic_model_flat(topic_model, topic_weights)`: older compatibility
  method that accepts a flattened topic-word matrix and topic weights.
- `get_topic_weights()`: return total word counts assigned to each topic.

Perplexity and diagnostics:

- `perplexity(recompute=False)`: return whole-model perplexity. Lower values
  usually mean the model predicts the observed words better.
- `perplexity(pose, recompute=False)`: return perplexity for one pose.
- `time_perplexity(t, recompute=False)`: return perplexity for one time step.
- `word_perplexity(pose, recompute=False)`: return per-word perplexity values
  for a pose.
- `topic_perplexity(pose)`: return how surprising the topic distribution is at a
  pose under the global topic weights.
- `cell_perplexity_topic(nZ)`: return topic perplexity for a topic-count vector,
  where `nZ[k]` is the count assigned to topic `k`.
- `cell_perplexity_word(words, nZ)`: return word perplexity for a list of words
  under a topic-count vector.
- `word_topic_perplexity(pose)`: return per-word topic perplexity at a pose.

Counters and indexing:

- `num_cells()`: return the number of cells/samples currently in the model.
- `get_num_words()`: return the vocabulary size `V`.
- `get_refine_count()`: return the number of cell refinements completed.
- `get_word_refine_count()`: return the number of word-token refinements
  completed.
- `get_poses_by_time()`: return a dictionary mapping time bins to poses.

Lower-level controls:

- `add_count(w, z, c=1)`: manually add `c` counts for word/taxon `w` in topic
  `z`.
- `relabel(w, z_old, z_new)`: manually move one word count from topic `z_old` to
  topic `z_new`.
- `shuffle_topics()`: randomly shuffle topic labels in existing cells.
- `update_gamma()`: update the internal topic-growth weights.
- `enable_auto_topics_size(enabled=True)`: enable or disable automatic topic
  growth controlled by `gamma`.
