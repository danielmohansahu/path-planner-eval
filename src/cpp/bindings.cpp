#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/pair.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>

#include "grid.hpp"
#include "planner.hpp"
#include "planners/a_star.hpp"
#include "planners/ara_star.hpp"
#include "planners/dijkstra.hpp"
#include "planners/rrt.hpp"

namespace nb = nanobind;
using GridArray = nb::ndarray<uint8_t, nb::ndim<2>, nb::c_contig>;

NB_MODULE(planner_core, m) {
  m.doc() = "Core C++ path planning algorithms";

  nb::class_<PlanResult>(m, "PlanResult")
      .def_ro("path", &PlanResult::path)
      .def_ro("cost", &PlanResult::cost)
      .def_ro("nodes_expanded", &PlanResult::nodes_expanded)
      .def_ro("planning_time_ms", &PlanResult::planning_time_ms)
      .def_ro("solved", &PlanResult::solved);

  m.def(
      "plan_a_star",
      [](GridArray grid_arr, std::pair<int, int> start,
         std::pair<int, int> goal, int connectivity, float heuristic_weight) {
        Grid grid(grid_arr.data(), grid_arr.shape(0), grid_arr.shape(1));
        return plan_a_star(grid, start, goal, connectivity, heuristic_weight);
      },
      nb::arg("grid"), nb::arg("start"), nb::arg("goal"),
      nb::arg("connectivity") = 8, nb::arg("heuristic_weight") = 1.0f);

  m.def(
      "plan_dijkstra",
      [](GridArray grid_arr, std::pair<int, int> start,
         std::pair<int, int> goal, int connectivity) {
        Grid grid(grid_arr.data(), grid_arr.shape(0), grid_arr.shape(1));
        return plan_dijkstra(grid, start, goal, connectivity);
      },
      nb::arg("grid"), nb::arg("start"), nb::arg("goal"),
      nb::arg("connectivity") = 8);

  m.def(
      "plan_ara_star",
      [](GridArray grid_arr, std::pair<int, int> start,
         std::pair<int, int> goal, int connectivity, float initial_weight,
         float weight_decay) {
        Grid grid(grid_arr.data(), grid_arr.shape(0), grid_arr.shape(1));
        return plan_ara_star(grid, start, goal, connectivity, initial_weight,
                             weight_decay);
      },
      nb::arg("grid"), nb::arg("start"), nb::arg("goal"),
      nb::arg("connectivity") = 8, nb::arg("initial_weight") = 3.0f,
      nb::arg("weight_decay") = 0.5f);

  m.def(
      "plan_rrt",
      [](GridArray grid_arr, std::pair<int, int> start,
         std::pair<int, int> goal, int max_iterations, float step_size) {
        Grid grid(grid_arr.data(), grid_arr.shape(0), grid_arr.shape(1));
        return plan_rrt(grid, start, goal, max_iterations, step_size);
      },
      nb::arg("grid"), nb::arg("start"), nb::arg("goal"),
      nb::arg("max_iterations") = 10000, nb::arg("step_size") = 5.0f);
}
