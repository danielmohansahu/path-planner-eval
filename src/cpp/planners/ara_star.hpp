#pragma once
#include "../grid.hpp"
#include "../planner.hpp"

PlanResult plan_ara_star(const Grid &grid, Coord start, Coord goal,
                         int connectivity, float initial_weight,
                         float weight_decay);
