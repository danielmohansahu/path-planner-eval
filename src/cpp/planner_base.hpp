#pragma once
#include "grid.hpp"
#include "planner.hpp"
#include "planners/dijkstra.hpp"
#include <utility>

class PlannerBase {
public:
  virtual ~PlannerBase() = default;
  virtual PlanResult plan(const Grid &grid, std::pair<int, int> start,
                          std::pair<int, int> goal) = 0;
};

class DijkstraPlanner : public PlannerBase {
  int connectivity_;

public:
  explicit DijkstraPlanner(int connectivity = 8)
      : connectivity_(connectivity) {}
  PlanResult plan(const Grid &grid, std::pair<int, int> start,
                  std::pair<int, int> goal) override {
    return plan_dijkstra(grid, start, goal, connectivity_);
  }
};
