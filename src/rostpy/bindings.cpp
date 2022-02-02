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
      .def("perplexity", static_cast<double (R::*)(bool)>(&R::perplexity))
      .def("perplexity",
           static_cast<double (R::*)(const typename R::pose_t &, bool)>(
               &R::perplexity))
      .def("time_perplexity", &R::time_perplexity)
      .def("word_perplexity", &R::word_perplexity)
      .def("topic_perplexity", &R::topic_perplexity)
      .def("cell_perplexity_topic", &R::cell_perplexity_topic)
      .def("cell_perplexity_word", &R::cell_perplexity_word)
      .def("word_topic_perplexity", &R::word_topic_perplexity)
      .def("get_topic_weights", &R::get_topic_weights)
      .def("get_topic_model", &R::get_topic_model)
      .def("get_ml_topics_for_pose", &R::get_ml_topics_for_pose)
      .def("get_ml_topics_and_ppx_for_pose", &R::get_ml_topics_and_ppx_for_pose)
      .def("get_topics_and_ppx_for_pose", &R::get_topics_and_ppx_for_pose)
      .def("get_topics_for_pose", &R::get_topics_for_pose)
      .def("add_count", &R::add_count)
      .def("relabel", &R::relabel)
      .def("shuffle_topics", &R::shuffle_topics)
      .def("add_observation",
           static_cast<void (R::*)(const typename R::pose_t &,
                                   const std::vector<int> &)>(
               &R::add_observation))
      .def("add_observation",
           static_cast<void (R::*)(
               const typename R::pose_t &, const std::vector<int>::iterator &,
               const std::vector<int>::iterator &, bool)>(&R::add_observation))
      .def("add_observation",
           static_cast<void (R::*)(
               const typename R::pose_t &, const std::vector<int>::iterator &,
               const std::vector<int>::iterator &, bool,
               const std::vector<int>::iterator &,
               const std::vector<int>::iterator &)>(&R::add_observation))
      .def("forget", &R::forget)
      .def("update_gamma", &R::update_gamma)
      .def("enable_auto_topics_size", &R::enable_auto_topics_size)
      .def("refine", &R::refine)
      .def("estimate", &R::estimate)
      .def("computeMaxLikelihoodTopics", &R::computeMaxLikelihoodTopics)
      .def("addObservations", &R::addObservations)
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
  create_rost<pose_txy, pose_neighbors_txy, pose_hash_txy, pose_equal_txy,
              ROST_txy>(m, "ROST_txy");
  m.def("parallel_refine", parallel_refine<ROST_txy>);
  create_rost<pose_xy, pose_neighbors_xy, pose_hash_xy, pose_equal_xy, ROST_xy>(
      m, "ROST_xy");
  m.def("parallel_refine", parallel_refine<ROST_xy>);
}
