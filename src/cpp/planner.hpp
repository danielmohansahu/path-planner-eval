#pragma once
#include <utility>
#include <vector>

struct PlanResult {
  std::vector<std::pair<int, int>> path;
  double cost = 0.0;
  int nodes_expanded = 0;
  double planning_time_ms = 0.0;
  bool solved = false;
};
