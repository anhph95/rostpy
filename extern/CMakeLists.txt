cmake_minimum_required(VERSION 3.11 FATAL_ERROR)
include(FetchContent)

# ------------------------------------------------------------------------------
# Python bindings for C++ Code
FetchContent_Declare(
  extern_pybind11

  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  )

FetchContent_GetProperties(extern_pybind11)
if(NOT extern_pybind11_POPULATED)
  FetchContent_Populate(extern_pybind11)
  add_subdirectory(
    ${extern_pybind11_SOURCE_DIR}
    ${extern_pybind11_BINARY_DIR}
    EXCLUDE_FROM_ALL)
endif()
FetchContent_MakeAvailable(extern_pybind11)

# ------------------------------------------------------------------------------
# Real-time Online Spatiotemporal Topic Modeling
FetchContent_Declare(
  extern_rost

  GIT_REPOSITORY https://gitlab.com/warplab/rost-cli.git
  SOURCE_SUBDIR librost
  )

FetchContent_GetProperties(extern_rost)
if(NOT extern_rost_POPULATED)
  FetchContent_Populate(extern_rost)
  add_subdirectory(
    ${extern_rost_SOURCE_DIR}
    ${extern_rost_BINARY_DIR}
    EXCLUDE_FROM_ALL)
endif()
FetchContent_MakeAvailable(extern_rost)
