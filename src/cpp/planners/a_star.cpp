#include "a_star.hpp"
#include <chrono>
#include <cmath>
#include <map>
#include <queue>
#include <vector>

namespace {

double heuristic(std::pair<int, int> a, std::pair<int, int> b) {
  double dr = a.first - b.first;
  double dc = a.second - b.second;
  return std::sqrt(dr * dr + dc * dc);
}

} // namespace

PlanResult plan_a_star(const Grid &grid, std::pair<int, int> start,
                       std::pair<int, int> goal, int connectivity,
                       float heuristic_weight) {
  PlanResult result;
  auto t0 = std::chrono::steady_clock::now();

  std::map<std::pair<int, int>, double> g_score;
  std::map<std::pair<int, int>, std::pair<int, int>> parent;

  using PQEntry = std::pair<double, std::pair<int, int>>;
  std::priority_queue<PQEntry, std::vector<PQEntry>, std::greater<>> open;

  g_score[start] = 0.0;
  double h = heuristic_weight * heuristic(start, goal);
  open.push({h, start});

  while (!open.empty()) {
    auto [f, current] = open.top();
    open.pop();

    if (current == goal) {
      result.solved = true;
      break;
    }

    if (f >
        g_score[current] + heuristic_weight * heuristic(current, goal) + 1e-9)
      continue;

    result.nodes_expanded++;

    for (auto [nr, nc] :
         grid.neighbors(current.first, current.second, connectivity)) {
      std::pair<int, int> neighbor = {nr, nc};

      bool is_diagonal = (nr != current.first && nc != current.second);
      double edge_cost = is_diagonal ? std::sqrt(2.0) : 1.0;
      double tentative_g = g_score[current] + edge_cost;

      if (tentative_g < g_score[neighbor]) {
        g_score[neighbor] = tentative_g;
        parent[neighbor] = current;
        double f_new =
            tentative_g + heuristic_weight * heuristic(neighbor, goal);
        open.push({f_new, neighbor});
      }
    }
  }

  auto t1 = std::chrono::steady_clock::now();
  result.planning_time_ms =
      std::chrono::duration<double, std::milli>(t1 - t0).count();

  if (result.solved) {
    std::vector<std::pair<int, int>> path;
    auto cur = goal;
    while (cur != start) {
      path.push_back(cur);
      cur = parent.at(cur);
    }
    path.push_back(start);
    std::reverse(path.begin(), path.end());
    result.path = std::move(path);
    result.cost = g_score[goal];
  }

  return result;
}
