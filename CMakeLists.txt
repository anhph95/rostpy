cmake_minimum_required(VERSION 2.8.12)
cmake_policy(SET CMP0048 NEW)
project(rostpy VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 14 CACHE STRING "C++ version selection")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)
set(CXX_STANDARD 14)
set(CXX_STANDARD_REQUIRED ON)
set(CXX_EXTENSIONS ON)

find_package(pybind11 REQUIRED)

include_directories(extern/librost/include)
pybind11_add_module(_rostpy src/rostpy/bindings.cpp)
