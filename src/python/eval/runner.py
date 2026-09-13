"""Evaluation runner: runs a planner against a scenario."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import planner_core

from .scenarios import Scenario

_PLANNER_REGISTRY: dict[str, dict] = {
    "A*": {
        "func": "plan_a_star",
        "params": {"connectivity": 8, "heuristic_weight": 1.0},
    },
    "Dijkstra": {
        "func": "plan_dijkstra",
        "params": {"connectivity": 8},
    },
    "ARA*": {
        "func": "plan_ara_star",
        "params": {"connectivity": 8, "initial_weight": 3.0, "weight_decay": 0.5},
    },
    "RRT": {
        "func": "plan_rrt",
        "params": {"max_iterations": 10000, "step_size": 5.0},
    },
}


@dataclass
class EvalResult:
    """Result of running one planner on one scenario."""

    algorithm: str
    scenario_name: str
    path: list[tuple[int, int]]
    cost: float
    nodes_expanded: int
    planning_time_ms: float
    solved: bool
    optimal_cost: float
    optimality_ratio: float


def run_single_evaluation(
    algorithm: str,
    scenario: Scenario,
    params: dict | None = None,
) -> EvalResult:
    """Run a single planner on a single scenario."""
    entry = _PLANNER_REGISTRY[algorithm]
    func = getattr(planner_core, entry["func"])

    merged = {**entry["params"], **(params or {})}
    result = func(scenario.grid, scenario.start, scenario.goal, **merged)

    if result.solved and scenario.optimal_cost > 0:
        optimality_ratio = result.cost / scenario.optimal_cost
    else:
        optimality_ratio = float("inf")

    return EvalResult(
        algorithm=algorithm,
        scenario_name=scenario.name,
        path=list(result.path),
        cost=result.cost,
        nodes_expanded=result.nodes_expanded,
        planning_time_ms=result.planning_time_ms,
        solved=result.solved,
        optimal_cost=scenario.optimal_cost,
        optimality_ratio=optimality_ratio,
    )


def run_evaluation_parallel(
    scenarios: list[Scenario],
    planner_params: dict[str, dict] | None = None,
) -> pd.DataFrame:
    """Run Dijkstra evaluation in parallel using C++ thread pool."""
    params = planner_params or {}
    dijkstra_params = params.get("Dijkstra", {})
    connectivity = dijkstra_params.get("connectivity", 8)

    task_list = [(s.start, s.goal) for s in scenarios]
    grid = scenarios[0].grid

    results = planner_core.parallel_plan_dijkstra(grid, task_list, connectivity)

    rows = []
    for scenario, result in zip(scenarios, results):
        if result.solved and scenario.optimal_cost > 0:
            optimality_ratio = result.cost / scenario.optimal_cost
        else:
            optimality_ratio = float("inf")

        rows.append(
            {
                "algorithm": "Dijkstra",
                "scenario_name": scenario.name,
                "map_name": scenario.map_name,
                "cost": result.cost,
                "nodes_expanded": result.nodes_expanded,
                "planning_time_ms": result.planning_time_ms,
                "solved": result.solved,
                "optimal_cost": scenario.optimal_cost,
                "optimality_ratio": optimality_ratio,
            }
        )

    return pd.DataFrame(rows)
