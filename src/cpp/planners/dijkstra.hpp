#pragma once
#include "../grid.hpp"
#include "../planner.hpp"

PlanResult plan_dijkstra(const Grid &grid, Coord start, Coord goal,
                         int connectivity);
