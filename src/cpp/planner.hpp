#pragma once
#include <vector>

#include "coord.hpp"

struct PlanResult {
  std::vector<Coord> path;
  double cost = 0.0;
  int nodes_expanded = 0;
  double planning_time_ms = 0.0;
  bool solved = false;
};
