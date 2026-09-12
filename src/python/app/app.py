"""Path Planning Evaluation — Streamlit Application."""

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import streamlit as st

from eval import (
    compare_algorithms,
    get_bundled_scenarios,
    run_evaluation,
    run_single_evaluation,
)

st.set_page_config(page_title="Path Planner Eval", layout="wide")
st.title("Path Planning Evaluation")

# ── Map colormap ──────────────────────────────────────────────────
_CMAP = mcolors.ListedColormap(["white", "khaki", "black"])
_NORM = mcolors.BoundaryNorm([0, 1, 200, 255], _CMAP.N)


# ── Load scenarios ────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading benchmark maps...")
def _load_scenarios():
    return get_bundled_scenarios()


all_scenarios = _load_scenarios()

# ── Sidebar ───────────────────────────────────────────────────────
st.sidebar.header("Configuration")

map_names = sorted(all_scenarios.keys())
selected_map = st.sidebar.selectbox("Map", map_names)

map_scenarios = all_scenarios[selected_map]
max_scenarios = st.sidebar.slider(
    "Scenarios to evaluate",
    min_value=1,
    max_value=min(50, len(map_scenarios)),
    value=min(10, len(map_scenarios)),
)
scenarios = map_scenarios[:max_scenarios]

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

num_runs = st.sidebar.slider("Runs per scenario", 1, 10, 1)

run_button = st.sidebar.button(
    "Run Evaluation",
    type="primary",
    disabled=len(selected_planners) == 0,
)

# ── Map Preview ───────────────────────────────────────────────────
st.subheader(f"Map: {selected_map}")

first_scenario = scenarios[0]
grid = first_scenario.grid

fig_map, ax_map = plt.subplots(figsize=(8, 8))
ax_map.imshow(grid, cmap=_CMAP, norm=_NORM, interpolation="nearest")
ax_map.plot(
    first_scenario.start[1], first_scenario.start[0], "go", markersize=8, label="Start"
)
ax_map.plot(
    first_scenario.goal[1], first_scenario.goal[0], "r*", markersize=10, label="Goal"
)
ax_map.legend(loc="upper right")
ax_map.set_title(f"{selected_map} ({grid.shape[1]}x{grid.shape[0]})")
ax_map.set_xlabel("col")
ax_map.set_ylabel("row")
st.pyplot(fig_map)
plt.close(fig_map)

# ── Evaluation ────────────────────────────────────────────────────
if run_button:
    with st.spinner("Running evaluation..."):
        df = run_evaluation(
            planners=selected_planners,
            scenarios=scenarios,
            planner_params=planner_params,
            num_runs=num_runs,
        )

    st.subheader("Algorithm Comparison")
    comparison = compare_algorithms(df)
    st.dataframe(comparison, use_container_width=True)

    st.subheader("Detailed Results")
    display_cols = [
        "algorithm",
        "scenario_name",
        "solved",
        "cost",
        "planning_time_ms",
        "nodes_expanded",
        "optimal_cost",
        "optimality_ratio",
    ]
    st.dataframe(
        df[display_cols].round(4),
        use_container_width=True,
        height=300,
    )

    # ── Path Visualization (first scenario) ───────────────────
    st.subheader("Path Visualization (Scenario 1)")
    colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"]

    fig_path, ax_path = plt.subplots(figsize=(8, 8))
    ax_path.imshow(grid, cmap=_CMAP, norm=_NORM, interpolation="nearest")

    for i, algo in enumerate(selected_planners):
        result = run_single_evaluation(
            algo, first_scenario, planner_params.get(algo, {})
        )
        if result.solved and result.path:
            rows = [p[0] for p in result.path]
            cols = [p[1] for p in result.path]
            ax_path.plot(
                cols,
                rows,
                color=colors[i % len(colors)],
                linewidth=2,
                alpha=0.7,
                label=f"{algo} (cost={result.cost:.1f})",
            )

    ax_path.plot(first_scenario.start[1], first_scenario.start[0], "go", markersize=10)
    ax_path.plot(first_scenario.goal[1], first_scenario.goal[0], "r*", markersize=12)
    ax_path.legend(loc="upper right")
    ax_path.set_title("Planned Paths")
    st.pyplot(fig_path)
    plt.close(fig_path)

    # ── Comparison Charts ─────────────────────────────────────
    st.subheader("Metric Comparison")
    metrics = [
        ("mean_time_ms", "Planning Time (ms)"),
        ("mean_cost", "Path Cost"),
        ("mean_nodes_expanded", "Nodes Expanded"),
    ]
    chart_cols = st.columns(len(metrics))
    for col_widget, (metric, title) in zip(chart_cols, metrics):
        with col_widget:
            fig_bar, ax_bar = plt.subplots(figsize=(4, 3))
            comparison[metric].plot(kind="bar", ax=ax_bar, color="steelblue")
            ax_bar.set_title(title)
            ax_bar.set_ylabel(metric)
            ax_bar.tick_params(axis="x", rotation=45)
            fig_bar.tight_layout()
            st.pyplot(fig_bar)
            plt.close(fig_bar)
