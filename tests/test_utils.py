"""Test cases for the utils module."""
# from __future__ import annotations

from __future__ import annotations

# import itertools
# import os
# import pytest

# from rostpy import utils

# def dictlist_to_listdicts(dictlist):
#     keys, values = zip(*dictlist.items())
#     return [dict(zip(keys, v)) for v in itertools.product(*values)]


# def pytest_generate_tests(metafunc):
#     # called once per each test function
#     funcarglist = metafunc.cls.params[metafunc.function.__name__]
#     argnames = sorted(funcarglist[0])
#     metafunc.parametrize(
#         argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
#     )


# class TestLoadWords:

#     params = {
#         "test_load_words_returns_exactposes_for_pose": dictlist_to_listdicts(
#             {
#                 "topicfile": ["", "topics.txt"],
#                 "update_topic_model": [True, False],
#                 "retime": [True, False],
#                 "posedim": [1, 3],
#             }
#         )
#     }

#     def test_load_words_returns_exactposes_for_pose(
#         self, datadir, rost, topicfile, update_topic_model, retime, posedim
#     ):
#         """It exits with a status code of zero."""
#         wordfile = os.path.join(datadir, "words.txt")
#         topicfile = os.path.join(datadir, topicfile) if topicfile != "" else topicfile
#         posefile = os.path.join(datadir, "poses.txt")
#         cell_time = 1.0
#         cell_space = 1.0
#         exactposes_for_pose, timestamps = utils.load_words(
#             rost,
#             wordfile,
#             topicfile,
#             posefile,
#             cell_time,
#             cell_space,
#             update_topic_model,
#             retime,
#             posedim,
#         )
#         print(exactposes_for_pose)
#         # assert exactposes_for_pose == {
#         #     1.0: tuple(
#         #         float(x)
#         #         for x in [1, 0, 0, 0, 1, 0, 2, 1, 0, 1, 1, 1, 2, 2, 0, 2, 1, 2, 2]
#         #     ),
#         #     2.0: tuple(
#         #         float(x)
#         #         for x in [2, 0, 0, 0, 1, 0, 2, 1, 0, 1, 1, 1, 2, 2, 0, 2, 1, 2, 2]
#         #     ),
#         # }
#         assert timestamps == [1.0, 2.0]
