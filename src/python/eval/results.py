"""Result analysis and export utilities."""

from pathlib import Path

import numpy as np
import pandas as pd


def compare_algorithms(df: pd.DataFrame) -> pd.DataFrame:
    """Create a pivot table comparing algorithms across metrics."""
    return (
        df.groupby("algorithm")
        .agg(
            mean_cost=("cost", "mean"),
            mean_time_ms=("planning_time_ms", "mean"),
            mean_nodes_expanded=("nodes_expanded", "mean"),
            mean_optimality_ratio=(
                "optimality_ratio",
                lambda x: x.replace([np.inf, -np.inf], np.nan).mean(),
            ),
            solve_rate=("solved", "mean"),
            total_scenarios=("scenario_name", "nunique"),
        )
        .round(4)
    )


def export_results(df: pd.DataFrame, path: Path, fmt: str = "csv") -> None:
    """Export results DataFrame to CSV or JSON."""
    path = Path(path)
    if fmt == "csv":
        df.to_csv(path, index=True)
    elif fmt == "json":
        df.to_json(path, orient="records", indent=2)
    else:
        raise ValueError(f"Unsupported format: {fmt!r}")
