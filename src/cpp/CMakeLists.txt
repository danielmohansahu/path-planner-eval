cmake_minimum_required(VERSION 3.26)
project(PlannerEval LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python 3.11 EXACT COMPONENTS Interpreter Development.Module REQUIRED)
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(
    planner_core 
    bindings.cpp 
)

# Output the compiled library next to the FastAPI app, relative to this CMakeLists location
set_target_properties(planner_core PROPERTIES 
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../python/server
)
