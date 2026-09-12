#pragma once
#include "../grid.hpp"
#include "../planner.hpp"

PlanResult plan_a_star(const Grid &grid, std::pair<int, int> start,
                       std::pair<int, int> goal, int connectivity,
                       float heuristic_weight);
