#include "dijkstra.hpp"
#include <chrono>
#include <map>

PlanResult plan_dijkstra(const Grid &grid, std::pair<int, int> start,
                         std::pair<int, int> goal, int connectivity) {
  PlanResult result;
  auto t0 = std::chrono::system_clock::now();

  std::map<std::pair<int, int>, double> dist;
  std::map<std::pair<int, int>, std::pair<int, int>> parent;

  std::priority_queue<std::pair<double, std::pair<int, int>>,
                      std::vector<std::pair<double, std::pair<int, int>>>,
                      std::greater<>>
      pq;

  dist[start] = 0.0;
  pq.push({0.0, start});

  while (!pq.empty()) {
    auto [d, u] = pq.top();
    pq.pop();

    result.nodes_expanded++;

    if (u == goal) {
      result.solved = true;
      std::vector<std::pair<int, int>> path;
      auto cur = goal;
      while (cur != start) {
        path.push_back(cur);
        cur = parent[cur];
      }
      path.push_back(start);
      std::reverse(path.begin(), path.end());
      result.path = std::move(path);
      break;
    }

    if (d > dist[u])
      continue;

    for (auto [nr, nc] : grid.neighbors(u.first, u.second, connectivity)) {
      std::pair<int, int> v = {nr, nc};
      double edge_cost = 1.0;
      double new_dist = d + edge_cost;

      if (dist.find(v) == dist.end() || new_dist < dist[v]) {
        dist[v] = new_dist;
        parent[v] = u;
        pq.push({new_dist, v});
      }
    }
  }

  auto t1 = std::chrono::system_clock::now();
  result.planning_time_ms =
      std::chrono::duration<double, std::milli>(t1 - t0).count();

  if (result.solved) {
    result.cost = dist[goal];
  }

  return result;
}
