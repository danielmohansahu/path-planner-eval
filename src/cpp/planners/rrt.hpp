#pragma once
#include "../grid.hpp"
#include "../planner.hpp"

namespace path_planner {

PlanResult plan_rrt(const Grid &grid, std::pair<int, int> start,
                    std::pair<int, int> goal, int max_iterations,
                    float step_size);

} // namespace path_planner
