cmake_minimum_required(VERSION 3.26)
project(PlannerEval LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python 3.11 COMPONENTS Interpreter Development.Module REQUIRED)

execute_process(
    COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
    OUTPUT_VARIABLE nanobind_ROOT
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
list(APPEND CMAKE_PREFIX_PATH "${nanobind_ROOT}")
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(
    planner_core
    bindings.cpp
    planners/a_star.cpp
    planners/dijkstra.cpp
    planners/ara_star.cpp
    planners/rrt.cpp
    parallel_eval.cpp
)

set_target_properties(planner_core PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../python/eval
)
