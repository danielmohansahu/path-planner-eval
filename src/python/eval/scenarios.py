"""Moving AI Lab .scen file parser and Scenario dataclass."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .maps import load_map

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DATA_DIR = _PROJECT_ROOT / "data" / "maps"

_BENCHMARK_SETS = {
    "bg": ("bgmaps-map.zip", "bgmaps-scen.zip"),
    "sc1": ("sc1-map.zip", "sc1-scen.zip"),
    "wc3": ("wc3maps512-map.zip", "wc3maps512-scen.zip"),
}


@dataclass
class Scenario:
    """A single planning scenario from a Moving AI .scen file."""

    name: str
    map_path: Path
    map_name: str
    grid: np.ndarray
    start: tuple[int, int]  # (row, col)
    goal: tuple[int, int]  # (row, col)
    optimal_cost: float


def _ensure_extracted() -> None:
    """Extract benchmark zips if data/maps/ subdirectories are missing."""
    for subdir, (map_zip, scen_zip) in _BENCHMARK_SETS.items():
        dest = _DATA_DIR / subdir
        if dest.exists() and any(dest.glob("*.map")):
            continue
        dest.mkdir(parents=True, exist_ok=True)
        for zf_name in (map_zip, scen_zip):
            zf_path = _PROJECT_ROOT / zf_name
            if zf_path.exists():
                with zipfile.ZipFile(zf_path) as zf:
                    zf.extractall(dest)


def load_scenarios(scen_path: Path) -> list[Scenario]:
    """Parse a Moving AI .scen file into Scenario objects.

    Coordinate convention: .scen uses (x=col, y=row).
    We convert to (row, col) for numpy indexing.
    """
    scen_path = Path(scen_path)
    map_dir = scen_path.parent
    scenarios: list[Scenario] = []
    grid_cache: dict[str, np.ndarray] = {}

    with open(scen_path) as f:
        f.readline()  # "version 1"

        for i, line in enumerate(f):
            parts = line.strip().split()
            if len(parts) < 9:
                continue

            map_file = parts[1]
            start_x, start_y = int(parts[4]), int(parts[5])
            goal_x, goal_y = int(parts[6]), int(parts[7])
            optimal_cost = float(parts[8])

            map_name = Path(map_file).stem
            map_path = map_dir / map_file

            if map_name not in grid_cache:
                grid_cache[map_name] = load_map(map_path)

            scenarios.append(
                Scenario(
                    name=f"{map_name}-{i}",
                    map_path=map_path,
                    map_name=map_name,
                    grid=grid_cache[map_name],
                    start=(start_y, start_x),
                    goal=(goal_y, goal_x),
                    optimal_cost=optimal_cost,
                )
            )

    return scenarios


def get_bundled_scenarios() -> dict[str, list[Scenario]]:
    """Load all bundled benchmark scenarios, organized by map name.

    Auto-extracts zip files on first call if maps are missing.
    Returns dict mapping "set/map_name" -> list[Scenario].
    """
    _ensure_extracted()
    result: dict[str, list[Scenario]] = {}

    for subdir in sorted(_BENCHMARK_SETS.keys()):
        set_dir = _DATA_DIR / subdir
        if not set_dir.exists():
            continue
        for scen_file in sorted(set_dir.glob("*.scen")):
            scenarios = load_scenarios(scen_file)
            if scenarios:
                key = f"{subdir}/{scenarios[0].map_name}"
                result[key] = scenarios

    return result
