#pragma once
#include "../grid.hpp"
#include "../planner.hpp"

PlanResult plan_a_star(const Grid &grid, Coord start, Coord goal,
                       int connectivity, float heuristic_weight);
