# Path Planner Eval

A framework for evaluating and comparing path planning algorithms on 2D grid maps. Planners are implemented in C++20 and exposed to Python via [nanobind](https://github.com/wjakob/nanobind). A Streamlit app provides an interactive UI for selecting algorithms, tuning parameters, and visualizing planned paths side-by-side against benchmark maps with known-optimal solutions.

## Architecture

```
src/cpp/            C++20 planner implementations + nanobind bindings
src/python/eval/    Map/scenario parsers, evaluation runner
src/python/app/     Streamlit UI
data/raw/           Benchmark map archives (Moving AI .map/.scen format)
```

Each planner is a C++ function that takes a 2D grid (uint8 numpy array, 0 = free, 254 = impassable), a start/goal position, and algorithm-specific parameters. It returns a `PlanResult` with the path, cost, nodes expanded, and planning time measured inside C++.

## Algorithms

Four planners are currently registered (stubs — implementations are in progress):

| Algorithm | Parameters | Description |
|-----------|-----------|-------------|
| **A\*** | `heuristic_weight`, `connectivity` | Weighted A* graph search |
| **Dijkstra** | `connectivity` | Optimal uniform-cost search (A* with weight = 0) |
| **ARA\*** | `initial_weight`, `weight_decay`, `connectivity` | Anytime Repairing A* — iteratively tightens the heuristic weight to improve solution quality |
| **RRT** | `max_iterations`, `step_size` | Rapidly-exploring Random Tree — sampling-based planner |

## Quickstart

Requires [pixi](https://pixi.sh) (conda-based package manager).

```bash
# Install dependencies (C++ toolchain, Python, Streamlit, etc.)
pixi install

# Extract benchmark maps from bundled zip archives
pixi run setup

# Compile C++ planners into a Python extension module
pixi run build-ext

# Launch the Streamlit evaluation app
pixi run app
```

The app opens in your browser. Select a map, pick a scenario (start/goal pair), choose which algorithms to run, and click **Run Evaluation** to see planned paths overlaid on the map with a comparison table.

## Adding a New Planner

1. Create `src/cpp/planners/my_planner.hpp` and `my_planner.cpp` with a function matching the pattern:
   ```cpp
   PlanResult plan_my_planner(const Grid& grid, std::pair<int,int> start,
                               std::pair<int,int> goal, /* params */);
   ```
2. Add the `.cpp` file to `nanobind_add_module()` in `src/cpp/CMakeLists.txt`
3. Add a binding in `src/cpp/bindings.cpp` (follow the existing lambda pattern)
4. Register the planner in `_PLANNER_REGISTRY` in `src/python/eval/runner.py`
5. Add a checkbox + parameter controls in `src/python/app/app.py`

## Benchmark Maps

Maps come from the [Moving AI Lab 2D Pathfinding Benchmarks](https://movingai.com/benchmarks/grids.html), specifically the Warcraft III 512x512 set (36 maps). Each map ships with scenarios (start/goal pairs) organized by difficulty bucket, with pre-computed optimal path costs for computing optimality ratios.

Maps use the Moving AI `.map` format (text grid: `.` = passable, `@` = impassable) and `.scen` format (tab-separated scenarios with known-optimal costs).

## References

### Algorithms

- **A\* Search** — Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). "A Formal Basis for the Heuristic Determination of Minimum Cost Paths." [Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- **Dijkstra's Algorithm** — Dijkstra, E. W. (1959). "A note on two problems in connexion with graphs." [Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- **ARA\* (Anytime Repairing A\*)** — Likhachev, M., Gordon, G., & Thrun, S. (2004). "ARA*: Anytime A* with Provable Bounds on Sub-Optimality." [Wikipedia](https://en.wikipedia.org/wiki/Anytime_A*)
- **RRT (Rapidly-exploring Random Tree)** — LaValle, S. M. (1998). "Rapidly-exploring random trees: A new tool for path planning." [Wikipedia](https://en.wikipedia.org/wiki/Rapidly_exploring_random_tree)

### Benchmark Data

- Sturtevant, N. R. (2012). "Benchmarks for Grid-Based Pathfinding." *IEEE Transactions on Computational Intelligence and AI in Games*, 4(2), 144–148. [Moving AI Lab](https://movingai.com/benchmarks/grids.html)
