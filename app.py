import streamlit as st
import pandas as pd
from traffic_engine import TrafficEnvironment
from optimizer import SimulatedAnnealing

st.set_page_config(page_title="AI Signal (Cross Section) Optimizer", layout="wide")

st.title("🚦 AI Signal (Cross Section) Optimizer")

# Sidebar
st.sidebar.header("Intersection Configuration")
cycle = st.sidebar.slider("Cycle Length (C)", 40, 120, 60)
# Total clearance for the WHOLE cycle (e.g., 6s total)
y_red_total = st.sidebar.slider("Total Cycle Clearance (Yellow + All-Red)", 4, 12, 6)

st.sidebar.header("Manual Demand (VPM)")
vpm_n = st.sidebar.slider("North", 0, 50, 12)
vpm_s = st.sidebar.slider("South", 0, 50, 13)
vpm_e = st.sidebar.slider("East", 0, 50, 15)
vpm_w = st.sidebar.slider("West", 0, 50, 29)

vpm_rates = {'N': vpm_n, 'S': vpm_s, 'E': vpm_e, 'W': vpm_w}

if st.button(" Run AI Optimization", type="primary"):
    # Pass the total clearance directly to the environment
    env = TrafficEnvironment(cycle, t_total_clearance=y_red_total)
    optimizer = SimulatedAnnealing(env, vpm_rates)
    
    with st.spinner("Executing Search Algorithm..."):
        opt_ns, opt_ew, opt_delay = optimizer.optimize()
    
    # BASELINE CALCULATION: Fixed Equal Split
    total_available_green = cycle - y_red_total
    base_ns = total_available_green // 2
    base_ew = total_available_green - base_ns
    base_delay = env.get_total_delay(base_ns, base_ew, vpm_rates)
    
    # Results Display
    st.subheader("Optimization Analysis")
    c1, c2, c3 = st.columns(3)
    c1.metric("Optimized NS Green", f"{opt_ns}s")
    c2.metric("Optimized EW Green", f"{opt_ew}s")
    
    # Calculate improvement percentage
    improvement = ((base_delay - opt_delay) / max(0.01, base_delay)) * 100
    c3.metric("Delay Reduction", f"{improvement:.1f}%")

    # Benchmarking Chart
    res_df = pd.DataFrame({
        "Scenario": ["Equal-Split Baseline", "AI Optimized (SA)"],
        "Avg Waiting Time (s)": [base_delay, opt_delay]
    })
    st.bar_chart(res_df.set_index("Scenario"))
    
    # Mathematically verify the sum
    st.info(f"Check: NS({opt_ns}) + EW({opt_ew}) + Clearance({y_red_total}) = {opt_ns + opt_ew + y_red_total}s (Cycle: {cycle}s)")
