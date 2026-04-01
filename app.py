import streamlit as st
import pandas as pd
from traffic_engine import TrafficEnvironment
from optimizer import SimulatedAnnealing

st.set_page_config(page_title="AI Signal (Cross Section) Optimizer", layout="wide")

st.title("🚦 AI Signal (Cross Section) Optimizer")

# Sidebar controls
st.sidebar.header("Intersection Settings")

cycle_time = st.sidebar.slider("Cycle Length (seconds)", 40, 120, 60)

total_clearance_time = st.sidebar.slider(
    "Total Clearance (Yellow + All-Red)",
    4, 12, 6
)

st.sidebar.header("Traffic Demand (Cars Per Minute)")

north_rate = st.sidebar.slider("North", 0, 50, 12)
south_rate = st.sidebar.slider("South", 0, 50, 13)
east_rate = st.sidebar.slider("East", 0, 50, 15)
west_rate = st.sidebar.slider("West", 0, 50, 29)

cars_per_minute = {
    'N': north_rate,
    'S': south_rate,
    'E': east_rate,
    'W': west_rate
}

if st.button("Run AI Optimization", type="primary"):

    environment = TrafficEnvironment(cycle_time, t_total_clearance=total_clearance_time)
    optimizer = SimulatedAnnealing(environment, cars_per_minute)

    with st.spinner("Running optimization algorithm..."):
        optimized_ns, optimized_ew, optimized_delay = optimizer.optimize()

    # Baseline: equal split
    total_green_time = cycle_time - total_clearance_time
    baseline_ns = total_green_time // 2
    baseline_ew = total_green_time - baseline_ns

    baseline_delay = environment.get_total_delay(
        baseline_ns,
        baseline_ew,
        cars_per_minute
    )

    st.subheader("Optimization Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("Optimized NS Green", f"{optimized_ns}s")
    col2.metric("Optimized EW Green", f"{optimized_ew}s")

    improvement_percent = (
        (baseline_delay - optimized_delay) /
        max(0.01, baseline_delay)
    ) * 100

    if improvement_percent >= 10.0:
        st.success(f"Success Threshold Met: {improvement_percent:.1f}% Reduction")
    else:
        st.warning(f"Marginal Improvement: {improvement_percent:.1f}% Reduction (Below 10% Goal)")
    col3.metric("Delay Reduction", f"{improvement_percent:.1f}%")

    # Comparison chart
    results_table = pd.DataFrame({
        "Scenario": ["Equal Split", "AI Optimized"],
        "Average Waiting Time (seconds)": [baseline_delay, optimized_delay]
    })

    st.bar_chart(results_table.set_index("Scenario"))

    st.info(
        f"Check: NS({optimized_ns}) + EW({optimized_ew}) + "
        f"Clearance({total_clearance_time}) = "
        f"{optimized_ns + optimized_ew + total_clearance_time}s "
        f"(Cycle: {cycle_time}s)"
    )
