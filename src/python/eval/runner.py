"""Evaluation runner: runs planners against scenarios and collects results."""

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

AVAILABLE_PLANNERS = list(_PLANNER_REGISTRY.keys())


@dataclass
class EvalResult:
    """Result of running one planner on one scenario."""

    algorithm: str
    scenario_name: str
    map_name: str
    path: list[tuple[int, int]]
    cost: float
    nodes_expanded: int
    planning_time_ms: float
    solved: bool
    optimal_cost: float
    optimality_ratio: float


def _run_single(
    algorithm: str,
    scenario: Scenario,
    params: dict,
) -> EvalResult:
    entry = _PLANNER_REGISTRY[algorithm]
    func = getattr(planner_core, entry["func"])

    merged = {**entry["params"], **params}
    result = func(scenario.grid, scenario.start, scenario.goal, **merged)

    if result.solved and scenario.optimal_cost > 0:
        optimality_ratio = result.cost / scenario.optimal_cost
    else:
        optimality_ratio = float("inf")

    return EvalResult(
        algorithm=algorithm,
        scenario_name=scenario.name,
        map_name=scenario.map_name,
        path=list(result.path),
        cost=result.cost,
        nodes_expanded=result.nodes_expanded,
        planning_time_ms=result.planning_time_ms,
        solved=result.solved,
        optimal_cost=scenario.optimal_cost,
        optimality_ratio=optimality_ratio,
    )


def run_single_evaluation(
    algorithm: str,
    scenario: Scenario,
    params: dict | None = None,
) -> EvalResult:
    """Run a single planner on a single scenario. Returns full EvalResult with path."""
    return _run_single(algorithm, scenario, params or {})


def run_evaluation(
    planners: list[str],
    scenarios: list[Scenario],
    planner_params: dict[str, dict] | None = None,
    num_runs: int = 1,
) -> pd.DataFrame:
    """Run selected planners against scenarios and return results as DataFrame."""
    if planner_params is None:
        planner_params = {}

    rows = []
    for algo in planners:
        params = planner_params.get(algo, {})
        for scenario in scenarios:
            for run_idx in range(num_runs):
                result = _run_single(algo, scenario, params)
                rows.append(
                    {
                        "algorithm": result.algorithm,
                        "scenario_name": result.scenario_name,
                        "map_name": result.map_name,
                        "cost": result.cost,
                        "nodes_expanded": result.nodes_expanded,
                        "planning_time_ms": result.planning_time_ms,
                        "solved": result.solved,
                        "optimal_cost": result.optimal_cost,
                        "optimality_ratio": result.optimality_ratio,
                        "run_index": run_idx,
                    }
                )

    return pd.DataFrame(rows)
