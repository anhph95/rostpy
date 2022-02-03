"""Command-line interface."""
from __future__ import annotations

import logging
import os

import click
from _rostpy import ROST_t, ROST_txy, ROST_xy, parallel_refine

from .utils import (
    load_topic_model,
    load_words,
    save_topic_model,
    write_poses,
    write_time_perplexity,
    write_topics,
)

logger = logging.getLogger(__name__)
THREADS = os.cpu_count()


class ROSTCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.extend(
            reversed(
                [
                    click.Option(
                        (
                            "-i",
                            "--in-words",
                        ),
                        default="/dev/stdin",
                        help="word frequency count file. Each line is a document/cell, with integer representation of words",
                    ),
                    click.Option(
                        ("--in-words-delim",),
                        default=",",
                        help="delimiter used to separate words",
                    ),
                    click.Option(
                        ("--out-topics",),
                        default="topics.csv",
                        help="output topics file",
                    ),
                    click.Option(
                        ("--out-topics-ml",),
                        default="topics.maxlikelihood.csv",
                        help="output maximum likelihood topics file",
                    ),
                    click.Option(
                        ("--out-topicmodel",),
                        default="topicmodel.csv",
                        help="output topic model file",
                    ),
                    click.Option(
                        ("--in-topicmodel",), default="", help="input topic model file"
                    ),
                    click.Option(
                        ("--in-topics",), default="", help="initial topic labels"
                    ),
                    click.Option(("--logfile",), default="topics.log", help="log file"),
                    click.Option(
                        ("--ppx-rate",),
                        default=10,
                        type=click.IntRange(min=1),
                        help="number of iterations between perplexity reports",
                    ),
                    click.Option(
                        ("--ppx-out",),
                        default="perplexity.csv",
                        help="perplexity score for each timestep",
                    ),
                    click.Option(
                        (
                            "-V",
                            "--vocabsize",
                        ),
                        required=True,
                        type=click.IntRange(min=1),
                        help="vocabulary size",
                    ),
                    click.Option(
                        (
                            "-K",
                            "--ntopics",
                        ),
                        default=100,
                        type=click.IntRange(min=1),
                        help="topic size",
                    ),
                    click.Option(
                        (
                            "-n",
                            "--iter",
                        ),
                        default=100,
                        type=click.IntRange(min=1),
                        help="number of iterations",
                    ),
                    click.Option(
                        (
                            "-a",
                            "--alpha",
                        ),
                        default=0.1,
                        type=click.FloatRange(min=0.0),
                        help="controls the sparsity of theta; lower alpha means the model will prefer to characterize documents by few topics",
                    ),
                    click.Option(
                        (
                            "-b",
                            "--beta",
                        ),
                        default=1.0,
                        type=click.FloatRange(min=0.0),
                        help="controls the sparsity of phi; lower beta means the model will prefer to characterize topics by few words.",
                    ),
                    click.Option(
                        ("--threads",),
                        default=4,
                        type=click.IntRange(min=1, max=THREADS, clamp=True),
                        help="number of threads to use",
                    ),
                    click.Option(
                        ("--g-time",),
                        default=1,
                        type=click.IntRange(min=1),
                        help="depth of the temporal neighborhood (in number of cells)",
                    ),
                    click.Option(
                        ("--g-space",),
                        default=1,
                        type=click.IntRange(min=1),
                        help="depth of the spatial neighborhood (in number of cells)",
                    ),
                    click.Option(
                        ("--g-sigma",),
                        default=0.5,
                        type=click.FloatRange(min=0.0, max=1.0),
                        help="rate of decay of the neighborhood topic distribution",
                    ),
                    click.Option(
                        ("--cell-time",),
                        default=1,
                        type=click.IntRange(min=1),
                        help="cell width in time dimension",
                    ),
                    click.Option(
                        ("--cell-space",),
                        default=32,
                        type=click.IntRange(min=1),
                        help="cell width in spatial dimensions",
                    ),
                    click.Option(
                        ("--in-topicmask",),
                        default="",
                        help="mask file for topics; format is k lines of 0 or 1, where 0=> do not use the topic",
                    ),
                    click.Option(
                        ("--add-to-topicmodel",),
                        default=True,
                        help="add the given initial topic labels to topic model; only applicable whne a topic model and topics are provided",
                    ),
                    click.Option(
                        ("--out-intermediate-topics",),
                        default=False,
                        help="output intermediate topics",
                    ),
                    click.Option(
                        ("--in-position",), default="", help="word position CSV file"
                    ),
                    click.Option(
                        ("--out-position",),
                        default="topics.position.csv",
                        help="position data for topics",
                    ),
                    click.Option(
                        ("--topicmodel-update",),
                        default=True,
                        help="update global topic model with each iteration",
                    ),
                    click.Option(
                        ("--retime/--no-retime",),
                        default=True,
                        help="if this option is given, then timestamp from the words is ignored, and a sequntial time is given to each timestep",
                    ),
                    click.Option(
                        ("--grow-topics-size/--no-grow-topics-size",),
                        default=False,
                        help="grow # topics using Chineese Restaurant Process (CRP)",
                    ),
                    click.Option(
                        ("--gamma",),
                        default=1e-5,
                        type=click.FloatRange(min=0.0),
                        help="used to control topic growth rate using CRP",
                    ),
                ]
            )
        )


@click.group()
@click.version_option("0.1.0")
def cli() -> None:
    """ROST Python Bindings."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%y-%m-%d %H:%M:%S",
    )


@cli.command(cls=ROSTCommand)
@click.pass_context
def topics_refine_t(*args, **kwargs):
    """Topic modeling of data with 1 dimensional structure"""
    topics_refine(dim="t", **kwargs)


@cli.command(cls=ROSTCommand)
def topics_refine_xy(*args, **kwargs):
    """Topic modeling of data with 2 dimensional spatial structure (stationary in time)"""
    topics_refine(dim="xy", **kwargs)


@cli.command(cls=ROSTCommand)
def topics_refine_txy(*args, **kwargs):
    """Topic modeling of data with 2 dimensional spatial structure (nonstationary in time)"""
    topics_refine(dim="txy", **kwargs)


def topics_refine(*args, **opt):
    assert opt["dim"] in ("t", "xy", "txy"), (
        "dim must be 't', 'xy', or 'txy'; you provided '%s'" % opt["dim"]
    )
    # nd = len(opt["dim"]) != 1
    # pose = (
    #     [opt["g_time"]] if not nd else [opt["g_time"], opt["g_space"], opt["g_space"]]
    # )

    if opt["dim"] == "t":
        ROST = ROST_t
        posedim = 1
    elif opt["dim"] == "xy":
        ROST = ROST_xy
        posedim = 3
    else:
        assert opt["dim"] == "txy", (
            "dim must be 't', 'xy', or 'txy'; you gave %s" % opt["dim"]
        )
        ROST = ROST_txy
        posedim = 3

    # cell_space = opt["cell_space"]
    cell_time = opt["cell_time"]
    rost = ROST(
        V=opt["vocabsize"],
        K=opt["ntopics"],
        alpha=opt["alpha"],
        beta=opt["beta"],
        gamma=opt["gamma"],
    )
    g_sigma = opt["g_sigma"]
    rost.g_sigma = g_sigma

    logger.info("words = %s", opt["in_words"])
    logger.info("init_topics = %s", opt["in_topics"])
    logger.info("word position = %s", opt["in_position"])
    logger.info("alpha = %3.5f", opt["alpha"])
    logger.info("beta = %3.5f", opt["beta"])
    logger.info("gamma = %3.5f", opt["gamma"])
    logger.info("grow_topics_size = %s", opt["grow_topics_size"])
    logger.info("g_space (neighborhood spatial extent in #cells) = %d", opt["g_space"])
    logger.info("g_time (neighborhood temporal extent in #cells)= %d", opt["g_time"])
    logger.info("cell_space (spatial width of a cell) = %d", opt["cell_space"])
    logger.info("cell_time (temporal width of a cell) = %d", opt["cell_time"])
    logger.info("K = %d", opt["ntopics"])
    logger.info("V = %d", opt["vocabsize"])
    logger.info("iterations = %d", opt["iter"])

    if opt["grow_topics_size"]:
        logger.info("CRP_Topics=True")
        rost.enable_auto_topics_size()

    rost.update_global_model = opt["topicmodel_update"]
    logger.info("topicmodel_update = %s", rost.update_global_model)
    add_to_topic_model = (opt["in_topicmodel"] == "") or opt["add_to_topicmodel"]
    if opt["in_topicmodel"] != "":
        load_topic_model(rost, opt["in_topicmodel"])

    wordposes, timestamps = load_words(
        rost,
        opt["in_words"],
        opt["in_topics"],
        opt["in_position"],
        opt["cell_time"],
        opt["cell_space"],
        add_to_topic_model,
        opt["retime"],
        posedim,
    )

    logger.info("Writing position file: %s", opt["out_position"])
    write_poses(rost, opt["out_position"], wordposes)

    for i in range(opt["iter"]):
        logger.debug("iter: %d", i)
        parallel_refine(rost, opt["threads"])
        if (opt["ppx_rate"] > 0) and (
            (i % opt["ppx_rate"] == 0) or (i == opt["iter"] - 1)
        ):
            logger.info("Computing perplexity...")
            ppx = rost.perplexity(True)
            logger.info("iteration %d perplexity=%3.5f", i, ppx)
            if opt["out_intermediate_topics"]:
                logger.warning("intermediate topic output not implemented")
    logger.info("Writing topics to: %s", opt["out_topics"])
    write_topics(rost, opt["out_topics"], wordposes, False)
    logger.info("Writing perplexity for each time step to: %s", opt["ppx_out"])
    write_time_perplexity(
        rost,
        opt["ppx_out"],
        timestamps,
        cell_time=None if opt["retime"] else cell_time,
        recompute=True,
    )
    if opt["out_topicmodel"] != "":
        logger.info("Writing topic model to: %s", opt["out_topicmodel"])
        save_topic_model(rost, opt["out_topicmodel"])


if __name__ == "__main__":
    cli(prog_name="rostpy")  # pragma: no cover
