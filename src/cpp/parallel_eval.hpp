#pragma once
#include "grid.hpp"
#include "planner.hpp"
#include "planner_base.hpp"
#include <utility>
#include <vector>

struct EvalTask {
  std::pair<int, int> start;
  std::pair<int, int> goal;
};

std::vector<PlanResult> parallel_evaluate(const Grid &grid,
                                          const std::vector<EvalTask> &tasks,
                                          PlannerBase &planner);
