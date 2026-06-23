//
// Created by sansoucie on 12/6/21.
//

#include <array>
#include <iterator>
#include <vector>

#include "rost/io.hpp"
#include "rost/refinery.hpp"
#include "rost/rost.hpp"
#include "rost/rost_types.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace py::literals;

typedef std::vector<int> pose_t;
typedef neighbors<pose_t> neighbors_t;

template <
    typename PoseT, typename PoseNeighborsT, typename PoseHashT,
    typename PoseEqualsT,
    typename R = warp::ROST<PoseT, PoseNeighborsT, PoseHashT, PoseEqualsT>>
void create_rost(py::module_ m, const char *name) {
  py::class_<R>(m, name, py::module_local())
      .def(py::init(
               [](size_t V, size_t K, double alpha, double beta, double gamma) {
                 return new R(V, K, alpha, beta, PoseNeighborsT(1), PoseHashT(),
                              gamma);
               }),
           "V"_a, "K"_a, "alpha"_a, "beta"_a, "gamma"_a)
      .def_readonly("alpha", &R::alpha)
      .def_readonly("beta", &R::beta)
      .def_readonly("gamma", &R::gamma)
      .def_readonly("betaV", &R::betaV)
      .def_readonly("V", &R::V)
      .def("perplexity", static_cast<double (R::*)(bool)>(&R::perplexity),
           "recompute"_a = false)
      .def("perplexity",
           static_cast<double (R::*)(const typename R::pose_t &, bool)>(
               &R::perplexity),
           "pose"_a, "recompute"_a = false)
      .def("time_perplexity", &R::time_perplexity, "t"_a,
           "recompute"_a = false)
      .def("word_perplexity", &R::word_perplexity, "pose"_a,
           "recompute"_a = false)
      .def("topic_perplexity", &R::topic_perplexity)
      .def("cell_perplexity_topic", &R::cell_perplexity_topic)
      .def("cell_perplexity_word", &R::cell_perplexity_word)
      .def("word_topic_perplexity", &R::word_topic_perplexity)
      .def("get_topic_weights", &R::get_topic_weights)
      .def("get_topic_model", &R::get_topic_model)
      .def("get_ml_topics_for_pose", &R::get_ml_topics_for_pose, "pose"_a,
           "update_ppx"_a = false)
      .def("get_ml_topics_and_ppx_for_pose", &R::get_ml_topics_and_ppx_for_pose)
      .def("get_topics_and_ppx_for_pose", &R::get_topics_and_ppx_for_pose)
      .def("get_topics_for_pose", &R::get_topics_for_pose)
      .def("get_poses_by_time",
           [](const R &self) {
             std::map<typename R::pose_dim_t,
                      std::vector<typename R::pose_t>>
                 poses_by_time;
             for (const auto &entry : self.get_poses_by_time()) {
               poses_by_time[entry.first] = {
                   entry.second.begin(), entry.second.end()};
             }
             return poses_by_time;
           })
      .def("get_refine_count", &R::get_refine_count)
      .def("get_word_refine_count", &R::get_word_refine_count)
      .def("get_num_words", &R::get_num_words)
      .def("num_cells", &R::num_cells)
      .def("add_count", &R::add_count)
      .def("relabel", &R::relabel)
      .def("shuffle_topics", &R::shuffle_topics)
      .def("add_observation",
           [](R &self, const typename R::pose_t &pose,
              const std::vector<int> &words, bool update_model) {
             self.add_observation(pose, words.begin(), words.end(),
                                  update_model);
           },
           "pose"_a, "words"_a, "update_model"_a = true)
      .def("add_observation",
           [](R &self, const typename R::pose_t &pose,
              const std::vector<int> &words, const std::vector<int> &topics,
              bool update_model) {
             self.add_observation(pose, words.begin(), words.end(),
                                  update_model, topics.begin(), topics.end());
           },
           "pose"_a, "words"_a, "topics"_a, "update_model"_a = true)
      .def("forget", &R::forget, "cell_id"_a = -1)
      .def("update_gamma", &R::update_gamma)
      .def("enable_auto_topics_size", &R::enable_auto_topics_size,
           "enabled"_a = true)
      .def("refine_cell",
           [](R &self, size_t cid, bool blocking) {
             auto readToken = self.get_read_token();
             self.refine(*self.get_cell(cid), blocking);
           },
           "cell_id"_a, "blocking"_a = true)
      .def("refine_pose",
           [](R &self, const typename R::pose_t &pose, bool blocking) {
             auto cell_it = self.cell_lookup.find(pose);
             if (cell_it == self.cell_lookup.end()) {
               throw py::key_error("pose not found");
             }
             auto readToken = self.get_read_token();
             self.refine(*self.get_cell(cell_it->second), blocking);
           },
           "pose"_a, "blocking"_a = true)
      .def("estimate_cell",
           [](R &self, size_t cid, bool update_ppx) {
             return self.estimate(*self.get_cell(cid), update_ppx);
           },
           "cell_id"_a, "update_ppx"_a = false)
      .def("refine_ext", &R::refine_ext, "words"_a, "n_iter"_a = 10,
           "nZg"_a = std::vector<int>())
      .def("computeMaxLikelihoodTopics", &R::computeMaxLikelihoodTopics)
      .def("addObservations",
           [](R &self, const typename R::pose_t &pose,
              const std::vector<int> &words, const std::vector<int> &topics,
              bool update_model) {
             self.addObservations(pose, words, topics, update_model);
           },
           "pose"_a, "words"_a, "topics"_a = std::vector<int>(),
           "update_model"_a = true)
      .def("set_topic_model_flat",
           static_cast<void (R::*)(const std::vector<int> &,
                                   const std::vector<int> &)>(
               &R::set_topic_model),
           "topic_model"_a, "topic_weights"_a)
      .def("set_topic_model",
           [](R &self, const std::vector<std::vector<int>> &topic_model) {
             auto writeToken = self.get_write_token();
             self.set_topic_model(*writeToken, topic_model);
           },
           "topic_model"_a)
      .def_readwrite("g_sigma", &R::g_sigma)
      .def_readwrite("update_global_model", &R::update_global_model)
      .def_property_readonly("K", &R::get_num_topics)
      .def_property_readonly("active_K", &R::get_active_topics);
}

PYBIND11_MODULE(_rostpy, m) {
  using namespace std;
  using namespace warp;

  typedef array<int, 1> pose_t;
  typedef neighbors<pose_t> pose_neighbors_t;
  typedef hash_container<pose_t> pose_hash_t;
  typedef pose_equal<pose_t> pose_equal_t;
  typedef ROST<pose_t, pose_neighbors_t, pose_hash_t, pose_equal_t> ROST_t;

  typedef array<int, 3> pose_txy;
  typedef neighbors<pose_txy> pose_neighbors_txy;
  typedef hash_container<pose_txy> pose_hash_txy;
  typedef pose_equal<pose_txy> pose_equal_txy;
  typedef ROST<pose_txy, pose_neighbors_txy, pose_hash_txy, pose_equal_txy>
      ROST_txy;

  typedef array<int, 3> pose_xy;
  typedef neighbors<pose_xy> pose_neighbors_xy;
  typedef hash_pose_ignoretime<pose_xy> pose_hash_xy;
  typedef pose_equal<pose_xy> pose_equal_xy;
  typedef ROST<pose_xy, pose_neighbors_xy, pose_hash_xy, pose_equal_xy> ROST_xy;

  create_rost<pose_t, pose_neighbors_t, pose_hash_t, pose_equal_t, ROST_t>(
      m, "ROST_t");
  m.def("parallel_refine", parallel_refine<ROST_t>);
  m.def("parallel_refine_tau", parallel_refine_tau<ROST_t>);
  create_rost<pose_txy, pose_neighbors_txy, pose_hash_txy, pose_equal_txy,
              ROST_txy>(m, "ROST_txy");
  m.def("parallel_refine", parallel_refine<ROST_txy>);
  m.def("parallel_refine_tau", parallel_refine_tau<ROST_txy>);
  create_rost<pose_xy, pose_neighbors_xy, pose_hash_xy, pose_equal_xy, ROST_xy>(
      m, "ROST_xy");
  m.def("parallel_refine", parallel_refine<ROST_xy>);
  m.def("parallel_refine_tau", parallel_refine_tau<ROST_xy>);
}
