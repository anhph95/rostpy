cmake_minimum_required(VERSION 3.15)
project(rostpy VERSION 0.2.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17 CACHE STRING "C++ version selection")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(pybind11 REQUIRED)

pybind11_add_module(_rostpy src/rostpy/bindings.cpp)
target_include_directories(_rostpy PRIVATE extern/librost/librost/include)
