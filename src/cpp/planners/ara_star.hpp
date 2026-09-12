#pragma once
#include "../grid.hpp"
#include "../planner.hpp"

namespace path_planner {

PlanResult plan_ara_star(const Grid &grid, std::pair<int, int> start,
                         std::pair<int, int> goal, int connectivity,
                         float initial_weight, float weight_decay);

} // namespace path_planner
