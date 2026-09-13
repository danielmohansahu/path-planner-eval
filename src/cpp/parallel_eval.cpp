#include "parallel_eval.hpp"
#include <atomic>
#include <thread>

std::vector<PlanResult> parallel_evaluate(const Grid &grid,
                                          const std::vector<EvalTask> &tasks,
                                          PlannerBase &planner) {
  std::vector<PlanResult> results;

  constexpr unsigned kNumThreads = 4;
  std::atomic<size_t> next_task{0};

  auto worker = [&]() {
    while (true) {
      size_t idx = next_task.fetch_add(1, std::memory_order_relaxed);
      if (idx >= tasks.size())
        break;

      auto result = planner.plan(grid, tasks[idx].start, tasks[idx].goal);
      results.push_back(std::move(result));
    }
  };

  std::vector<std::jthread> threads;
  for (unsigned i = 0; i < kNumThreads; ++i) {
    threads.emplace_back(worker);
  }

  return results;
}
