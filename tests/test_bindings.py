"""Test cases for the C++ bindings for ROST."""
from __future__ import annotations

import pytest

import rostpy


def test_rost_t_core_topic_modeling_api() -> None:
    """The Python API exposes the core topic-modeling operations."""
    model = rostpy.ROST_t(V=8, K=3, alpha=0.1, beta=1.0, gamma=0.01)

    model.add_observation([0], [1, 2, 3])
    model.addObservations([1], [2, 3], [], True)

    assert model.num_cells() == 2
    assert model.get_num_words() == 8
    assert model.get_refine_count() == 0
    assert model.get_word_refine_count() == 0
    assert model.get_topics_for_pose([0])
    assert model.get_poses_by_time()

    model.refine_cell(0)
    model.refine_pose([1])
    rostpy.parallel_refine(model, 1)
    rostpy.parallel_refine_tau(model, 1, 1.0, 1)

    assert model.get_refine_count() >= 3
    assert model.get_word_refine_count() >= 3
    assert len(model.estimate_cell(0)) == 3
    assert len(model.get_ml_topics_for_pose([0])) == 3
    assert len(model.get_ml_topics_and_ppx_for_pose([0])[0]) == 3
    assert len(model.get_topics_and_ppx_for_pose([0])[0]) == 3
    assert len(model.refine_ext([1, 2], 2)) == 2

    topic_model = model.get_topic_model()
    assert len(topic_model) == model.K
    assert len(topic_model[0]) == model.V
    assert len(model.get_topic_weights()) == model.K

    model.set_topic_model(topic_model)
    flat_topic_model = [count for topic in topic_model for count in topic]
    model.set_topic_model_flat(flat_topic_model, model.get_topic_weights())

    assert model.perplexity(False) > 0
    assert model.time_perplexity(0, False) > 0
    assert len(model.word_perplexity([0], True)) == 3
    assert model.topic_perplexity([0]) > 0
    assert model.cell_perplexity_topic([1, 1, 1]) > 0
    assert model.cell_perplexity_word([1, 2], [1, 1, 1]) > 0
    assert len(model.word_topic_perplexity([0])) == 3

    model.update_gamma()
    model.enable_auto_topics_size(True)
    model.shuffle_topics()
    model.add_count(1, 0, 1)
    model.relabel(1, 0, 1)
    assert model.computeMaxLikelihoodTopics([0])


@pytest.mark.parametrize(
    ("cls", "pose"),
    [
        (rostpy.ROST_xy, [0, 1, 1]),
        (rostpy.ROST_txy, [0, 1, 1]),
    ],
)
def test_spatial_models_accept_three_dimensional_poses(cls, pose) -> None:
    """Spatial model bindings accept [t, x, y] poses."""
    model = cls(V=8, K=3, alpha=0.1, beta=1.0, gamma=0.01)

    model.add_observation(pose, [1, 2, 3])

    assert model.num_cells() == 1
    assert len(model.get_topics_for_pose(pose)) == 3
