#pragma once
#include "../grid.hpp"
#include "../planner.hpp"

namespace path_planner {

PlanResult plan_dijkstra(const Grid &grid, std::pair<int, int> start,
                         std::pair<int, int> goal, int connectivity);

} // namespace path_planner
