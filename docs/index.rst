
Welcome to documentation!
=========================


Introduction
------------

This GitHub repository is a maintenance fork of the original GitLab
``rostpy`` repository. The fork exists so the Python packaging, installation
workflow, and compatibility updates can be maintained here.

The C++ ``librost`` headers are still provided by the upstream GitLab
``rost-cli`` repository through a Git submodule:

.. code-block:: text

   extern/librost -> https://gitlab.com/warplab/rost-cli.git

Install from GitHub with pip
----------------------------

Install directly from the GitHub fork with a Git URL:

.. code-block:: bash

   python -m pip install "git+https://github.com/anhph95/rostpy.git"

Activate your virtual environment before running the install command.

Clone for development
---------------------

For local development, clone with submodules so the ``librost`` headers are
available before building:

.. code-block:: bash

   git clone --recurse-submodules https://github.com/anhph95/rostpy.git

If the repository was already cloned without submodules, initialize the
submodule before building:

.. code-block:: bash

   git submodule update --init --recursive

The build expects the ``librost`` headers at:

.. code-block:: text

   extern/librost/librost/include

GitHub source archives do not include submodule contents. For that reason,
prefer the Git URL installation form above instead of downloading a ``.zip``
archive.

Core Python API
---------------

The package exposes three ROST topic-model classes:

``ROST_t``
   One-dimensional temporal model. Poses are written as ``[t]``.

``ROST_xy``
   Spatial model. Poses are written as ``[t, x, y]``; time is ignored when
   hashing cells.

``ROST_txy``
   Spatiotemporal model. Poses are written as ``[t, x, y]``.

The module-level refinement functions are:

``parallel_refine(model, nt)``
   Refine all current cells using ``nt`` worker threads.

``parallel_refine_tau(model, nt, tau, iter)``
   Refine ``iter`` sampled cells using a beta-distributed cell preference.
   Larger ``tau`` values preferentially sample later cell IDs.

Callable model methods
----------------------

Model setup and state:

``K``
   Number of configured topics.

``active_K``
   Number of active topics when automatic topic growth is enabled.

``V``
   Vocabulary size.

``alpha``, ``beta``, ``gamma``, ``betaV``
   Topic-model hyperparameters.

``g_sigma``
   Spatial/temporal neighborhood decay factor.

``update_global_model``
   Boolean controlling whether refinement updates the global topic-word model.

Observation methods:

``add_observation(pose, words, update_model=True)``
   Add word observations at a pose.

``add_observation(pose, words, topics, update_model=True)``
   Add word observations with explicit initial topic labels.

``addObservations(pose, words, topics=[], update_model=True)``
   Compatibility spelling for adding observations.

``forget(cell_id=-1)``
   Forget one cell. If no cell ID is supplied, ``librost`` chooses one.

Refinement and estimation:

``refine_cell(cell_id, blocking=True)``
   Refine one cell by numeric cell ID.

``refine_pose(pose, blocking=True)``
   Refine one cell by pose.

``estimate_cell(cell_id, update_ppx=False)``
   Estimate maximum-likelihood topics for one cell by cell ID.

``refine_ext(words, n_iter=10, nZg=[])``
   Sample topics for a list of words without adding those words to the model.

``computeMaxLikelihoodTopics(pose)``
   Compatibility spelling for maximum-likelihood topic estimation by pose.

Topic/model inspection:

``get_topics_for_pose(pose)``
   Return current topic labels for a pose.

``get_topics_and_ppx_for_pose(pose)``
   Return current topic labels and perplexity for a pose.

``get_ml_topics_for_pose(pose, update_ppx=False)``
   Return maximum-likelihood topic labels for a pose.

``get_ml_topics_and_ppx_for_pose(pose)``
   Return maximum-likelihood topic labels and perplexity for a pose.

``get_topic_model()``
   Return the topic-word count matrix as a ``K x V`` nested list.

``set_topic_model(topic_model)``
   Replace the topic-word count matrix with a ``K x V`` nested list.

``set_topic_model_flat(topic_model, topic_weights)``
   Compatibility interface for the older flattened topic model format.

``get_topic_weights()``
   Return total word counts per topic.

Perplexity and diagnostics:

``perplexity(recompute=False)``
   Return whole-model perplexity.

``perplexity(pose, recompute=False)``
   Return perplexity for one pose.

``time_perplexity(t, recompute=False)``
   Return perplexity for one time step.

``word_perplexity(pose, recompute=False)``
   Return per-word perplexities for one pose.

``topic_perplexity(pose)``
   Return topic-label perplexity for one pose.

``cell_perplexity_topic(nZ)``
   Return topic perplexity for a topic-count vector.

``cell_perplexity_word(words, nZ)``
   Return word perplexity for words under a topic-count vector.

``word_topic_perplexity(pose)``
   Return per-word topic perplexity for one pose.

Counters and indexing:

``num_cells()``
   Return the number of cells in the model.

``get_num_words()``
   Return the configured vocabulary size.

``get_refine_count()``
   Return the number of cell refinements completed.

``get_word_refine_count()``
   Return the number of word refinements completed.

``get_poses_by_time()``
   Return the internal mapping from time to poses.

Low-level count controls:

``add_count(w, z, c=1)``
   Add ``c`` counts for word ``w`` in topic ``z``.

``relabel(w, z_old, z_new)``
   Move one word count from one topic to another.

``shuffle_topics()``
   Randomly shuffle topic labels in the current cells.

``update_gamma()``
   Update topic-growth weights.

``enable_auto_topics_size(v=True)``
   Enable or disable automatic topic growth.

Example usage
-------------

.. code-block:: python

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
   print(topics_with_ppx)
   print(topic_weights)
   print(overall_ppx)

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :caption: Contents
   :glob:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
