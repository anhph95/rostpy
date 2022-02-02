from __future__ import annotations

import csv
from collections import defaultdict


def load_words(
    rost,
    wordfile,
    topicfile,
    posefile,
    cell_time,
    cell_space,
    update_topic_model,
    retime,
    posedim,
):

    assert posedim in (1, 2, 3), "posedim must be between 1 and 3"
    have_topics = topicfile != ""
    have_poses = posefile != ""

    with open(wordfile) as f:
        word_lines = list(csv.reader(f))
    if have_topics:
        with open(topicfile) as f:
            topic_lines = list(csv.reader(f))
    if have_poses:
        with open(posefile) as f:
            pose_lines = list(csv.reader(f))
            pose_lines = [[float(x) for x in line] for line in pose_lines]

    assert (posedim == 1) or (
        have_poses
        and all(
            len(pose_line) == len(word_line) * (posedim - 1) + 1
            for pose_line, word_line in zip(pose_lines, word_lines)
        )
    ), "Must have synced poses"

    words_for_pose = defaultdict(list)
    topics_for_pose = defaultdict(list)
    exactposes_for_pose = defaultdict(list)
    timestamps = [float(x[0]) for x in word_lines]

    for ti, line in enumerate(word_lines):
        words = line[1:]
        t = ti if retime else timestamps[ti] / cell_time
        if posedim == 1:
            exact_poses = [(timestamps[ti],) for _ in words]
            cell_poses = [(t,) for _ in words]
        else:
            exact_poses = [
                (timestamps[ti], *[pose_lines[i * (posedim - 1) + d] for d in posedim])
                for i in range(len(words))
            ]
            cell_poses = [
                (t, *[pose_lines[i * (posedim - 1) + d] / cell_space for d in posedim])
                for i in range(len(words))
            ]
        for word, cell_pose, exact_pose in zip(words, cell_poses, exact_poses):
            words_for_pose[cell_pose].append(int(word))
            exactposes_for_pose[cell_pose].append(exact_pose)

        if have_topics:
            topics = topic_lines[ti][1:]
            assert len(topics) == len(words), "Topic and word lengths must match"
            for topic, cell_pose in zip(topics, cell_poses):
                topics_for_pose[cell_pose].append(topic)

    for pose, words in words_for_pose.items():
        rost.addObservations(
            pose,
            words,
            topics_for_pose[pose] if have_topics else [],
            update_topic_model,
        )
    return exactposes_for_pose, timestamps


def load_topic_model(rost, filename):
    with open(filename) as f:
        lines = list(csv.reader(f))
    topic_model = []
    topic_weights = []
    for line in lines:
        topic_model.extend(line)
        topic_weights.append(sum(line))
    rost.set_topic_model(topic_model, topic_weights)


def write_poses(rost, filename, wordposes):
    poses_by_time = defaultdict(list)
    for _, word_poses in wordposes.items():
        for word_pose in word_poses:
            timestamp = word_pose[0]
            poses_by_time[timestamp].append(word_pose)
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(
            [timestamp, *[y for x in poses for y in x]]
            for timestamp, poses in poses_by_time.items()
        )


def write_topics(rost, filename, wordposes, maxlikelihood):
    topics_by_time = defaultdict(list)
    for cell_pose, word_poses in wordposes.items():
        topics = (
            rost.get_ml_topics_for_pose(cell_pose)
            if maxlikelihood
            else rost.get_topics_for_pose(cell_pose)
        )
        for word_pose, topic in zip(word_poses, topics):
            timestamp = word_pose[0]
            topics_by_time[timestamp].append(topic)
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(
            [timestamp, *topics] for timestamp, topics in topics_by_time.items()
        )


def write_time_perplexity(rost, filename, timestamps, cell_time=None, recompute=True):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(
            [
                [
                    t,
                    rost.time_perplexity(
                        i if cell_time is None else t / cell_time, recompute
                    ),
                ]
                for i, t in enumerate(timestamps)
            ]
        )


def save_topic_model(rost, filename):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(rost.get_topic_model())
