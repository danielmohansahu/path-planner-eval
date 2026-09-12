"""Path Planning Evaluation — Streamlit Application."""

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from eval import get_bundled_scenarios, run_single_evaluation

st.set_page_config(page_title="Path Planner Eval", layout="wide")
st.title("Path Planning Evaluation")

_CMAP = mcolors.ListedColormap(["white", "khaki", "black"])
_NORM = mcolors.BoundaryNorm([0, 1, 200, 255], _CMAP.N)
_PATH_COLORS = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"]


@st.cache_data(show_spinner="Loading benchmark maps...")
def _load_scenarios():
    return get_bundled_scenarios()


all_scenarios = _load_scenarios()

# ── Sidebar ───────────────────────────────────────────────────────
st.sidebar.header("Configuration")

map_names = sorted(all_scenarios.keys())
selected_map = st.sidebar.selectbox("Map", map_names)
map_scenarios = all_scenarios[selected_map]

# Scenario picker — default to mid-range difficulty
scenario_labels = []
for s in map_scenarios:
    dist = ((s.start[0] - s.goal[0]) ** 2 + (s.start[1] - s.goal[1]) ** 2) ** 0.5
    scenario_labels.append(f"{s.name}  (dist={dist:.0f}, optimal={s.optimal_cost:.1f})")

optimal_costs = [s.optimal_cost for s in map_scenarios]
default_idx = int(
    np.argmin([abs(c - float(np.median(optimal_costs))) for c in optimal_costs])
)

viz_idx = st.sidebar.selectbox(
    "Scenario",
    range(len(map_scenarios)),
    index=default_idx,
    format_func=lambda i: scenario_labels[i],
)
scenario = map_scenarios[viz_idx]

st.sidebar.subheader("Algorithms")

selected_planners: list[str] = []
planner_params: dict[str, dict] = {}

use_a_star = st.sidebar.checkbox("A*", value=True)
if use_a_star:
    selected_planners.append("A*")
    with st.sidebar.expander("A* Parameters"):
        hw = st.slider("Heuristic weight", 0.5, 5.0, 1.0, 0.1, key="astar_hw")
        conn = st.selectbox("Connectivity", [4, 8], index=1, key="astar_conn")
        planner_params["A*"] = {"heuristic_weight": hw, "connectivity": conn}

use_dijkstra = st.sidebar.checkbox("Dijkstra", value=True)
if use_dijkstra:
    selected_planners.append("Dijkstra")
    with st.sidebar.expander("Dijkstra Parameters"):
        conn = st.selectbox("Connectivity", [4, 8], index=1, key="dij_conn")
        planner_params["Dijkstra"] = {"connectivity": conn}

use_ara_star = st.sidebar.checkbox("ARA*", value=False)
if use_ara_star:
    selected_planners.append("ARA*")
    with st.sidebar.expander("ARA* Parameters"):
        iw = st.slider("Initial weight", 1.0, 10.0, 3.0, 0.5, key="ara_iw")
        wd = st.slider("Weight decay", 0.1, 1.0, 0.5, 0.1, key="ara_wd")
        conn = st.selectbox("Connectivity", [4, 8], index=1, key="ara_conn")
        planner_params["ARA*"] = {
            "initial_weight": iw,
            "weight_decay": wd,
            "connectivity": conn,
        }

use_rrt = st.sidebar.checkbox("RRT", value=False)
if use_rrt:
    selected_planners.append("RRT")
    with st.sidebar.expander("RRT Parameters"):
        mi = st.slider("Max iterations", 1000, 50000, 10000, 1000, key="rrt_mi")
        ss = st.slider("Step size", 1.0, 20.0, 5.0, 0.5, key="rrt_ss")
        planner_params["RRT"] = {"max_iterations": mi, "step_size": ss}

run_button = st.sidebar.button(
    "Run Evaluation",
    type="primary",
    disabled=len(selected_planners) == 0,
)

# ── Map Preview ───────────────────────────────────────────────────
st.subheader(f"Map: {selected_map}")

grid = scenario.grid
fig_map, ax_map = plt.subplots(figsize=(8, 8))
ax_map.imshow(grid, cmap=_CMAP, norm=_NORM, interpolation="nearest")
ax_map.plot(scenario.start[1], scenario.start[0], "go", markersize=8, label="Start")
ax_map.plot(scenario.goal[1], scenario.goal[0], "r*", markersize=10, label="Goal")
ax_map.legend(loc="upper right")
ax_map.set_title(f"{selected_map} ({grid.shape[1]}×{grid.shape[0]})")
ax_map.set_xticks([])
ax_map.set_yticks([])
st.pyplot(fig_map)
plt.close(fig_map)

# ── Evaluation ────────────────────────────────────────────────────
if run_button:
    results = []
    with st.spinner("Running evaluation..."):
        for algo in selected_planners:
            results.append(
                run_single_evaluation(algo, scenario, planner_params.get(algo, {}))
            )

    # ── Path Visualization ────────────────────────────────────
    st.subheader(f"Paths: {scenario.name}")
    fig_path, ax_path = plt.subplots(figsize=(8, 8))
    ax_path.imshow(grid, cmap=_CMAP, norm=_NORM, interpolation="nearest")

    for i, r in enumerate(results):
        if r.solved and r.path:
            rows = [p[0] for p in r.path]
            cols = [p[1] for p in r.path]
            ax_path.plot(
                cols,
                rows,
                color=_PATH_COLORS[i % len(_PATH_COLORS)],
                linewidth=2,
                alpha=0.7,
                label=f"{r.algorithm} (cost={r.cost:.1f})",
            )

    ax_path.plot(scenario.start[1], scenario.start[0], "go", markersize=10)
    ax_path.plot(scenario.goal[1], scenario.goal[0], "r*", markersize=12)
    ax_path.legend(loc="upper right")
    ax_path.set_title(f"Planned Paths — {scenario.name}")
    ax_path.set_xticks([])
    ax_path.set_yticks([])
    st.pyplot(fig_path)
    plt.close(fig_path)

    # ── Results Table ─────────────────────────────────────────
    st.subheader("Results")
    st.dataframe(
        [
            {
                "Algorithm": r.algorithm,
                "Solved": r.solved,
                "Cost": round(r.cost, 2),
                "Time (ms)": round(r.planning_time_ms, 3),
                "Nodes Expanded": r.nodes_expanded,
                "Optimal Cost": round(r.optimal_cost, 2),
                "Optimality Ratio": round(r.optimality_ratio, 4)
                if r.optimality_ratio != float("inf")
                else "—",
            }
            for r in results
        ],
        use_container_width=True,
        hide_index=True,
    )
