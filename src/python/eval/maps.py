"""Moving AI Lab .map file parser."""

from pathlib import Path

import numpy as np

_CHAR_TO_COST: dict[str, int] = {
    ".": 0,
    "G": 0,
    "S": 127,
    "@": 254,
    "O": 254,
    "T": 254,
    "W": 254,
}


def load_map(path: Path) -> np.ndarray:
    """Parse a Moving AI .map file into a uint8 numpy grid.

    Returns array of shape (height, width) with values:
    0 = free, 127 = swamp, 254 = impassable.
    """
    with open(path) as f:
        f.readline()  # "type octile"
        height = int(f.readline().strip().split()[1])
        width = int(f.readline().strip().split()[1])
        f.readline()  # "map"

        grid = np.full((height, width), 254, dtype=np.uint8)
        for r in range(height):
            row_chars = f.readline().rstrip("\n")
            for c, ch in enumerate(row_chars[:width]):
                grid[r, c] = _CHAR_TO_COST.get(ch, 254)

    return grid
