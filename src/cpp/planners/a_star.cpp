#include "a_star.hpp"

using namespace path_planner;

PlanResult plan_a_star(const Grid &grid, std::pair<int, int> start,
                       std::pair<int, int> goal, int connectivity,
                       float heuristic_weight) {
  PlanResult result;
  result.solved = false;
  return result;
}
