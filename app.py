import streamlit as st
import pandas as pd
from traffic_engine import TrafficEnvironment
from optimizer import SimulatedAnnealing

st.set_page_config(page_title="7th Avenue AI Signal Optimizer", layout="wide")

st.title(" AI Signal Optimizer")
st.markdown("Optimization of time-varying traffic demand using Simulated Annealing.")

# Sidebar: Input Configuration Layer
st.sidebar.header("Intersection Configuration")
cycle = st.sidebar.slider("Cycle Length (C)", 40, 120, 60)
y_red = st.sidebar.slider("Yellow + All-Red Clearance (Per Phase)", 3, 8, 5)

st.sidebar.header("Manual Demand (VPM)")
vpm_n = st.sidebar.slider("North Arrival Rate", 0, 50, 15)
vpm_s = st.sidebar.slider("South Arrival Rate", 0, 50, 15)
vpm_e = st.sidebar.slider("East Arrival Rate", 0, 50, 25)
vpm_w = st.sidebar.slider("West Arrival Rate", 0, 50, 25)

vpm_rates = {'N': vpm_n, 'S': vpm_s, 'E': vpm_e, 'W': vpm_w}

if st.button(" Run AI Optimization", type="primary"):
    # Initialize Object-Oriented environment 
    env = TrafficEnvironment(cycle, t_yellow=y_red-2, t_allred=2)
    from optimizer import SimulatedAnnealing, HillClimbing
    optimizer = SimulatedAnnealing(env, vpm_rates)
    baseline_opt = HillClimbing(env, vpm_rates)
    
    # Run Simulated Annealing (Informed Search)
    with st.spinner("Executing Search Algorithm..."):
        opt_ns, opt_ew, opt_delay = optimizer.optimize()
    
    # Baseline comparison (Hill-Climbing)
    base_ns, base_ew, base_delay = baseline_opt.optimize()
    
    # Results Presentation
    st.subheader("Optimization Analysis")
    c1, c2, c3 = st.columns(3)
    c1.metric("Optimized NS Green", f"{opt_ns}s")
    c2.metric("Optimized EW Green", f"{opt_ew}s")
    
    # Calculate improvement percentage
    improvement = ((base_delay - opt_delay) / max(0.01, base_delay)) * 100
    c3.metric("Delay Reduction", f"{improvement:.1f}%")

    # Bar Chart for Performance Benchmarking
    res_df = pd.DataFrame({
        "Scenario": ["Hill-Climbing Baseline", "AI Optimized (SA)"],
        "Avg Waiting Time (s)": [base_delay, opt_delay]
    })
    st.bar_chart(res_df.set_index("Scenario"))
    
    # Residual Queue Visualization (To debug 50 VPM saturation)
    st.subheader("Final Queue Lengths (Vehicles Left)")
    final_queues = {'N': 0.0, 'S': 0.0, 'E': 0.0, 'W': 0.0}
    # Simulate one final run to capture the residual states
    for t in range(env.horizon):
        cycle_t = t % cycle
        for d in ['N', 'S', 'E', 'W']:
            final_queues[d] += vpm_rates[d] / 60.0
            is_green = (d in 'NS' and 0 <= cycle_t < opt_ns) or \
                       (d in 'EW' and (opt_ns + env.clearance_per_phase) <= cycle_t < env.C)
            cap = 0.5 if is_green else 0
            final_queues[d] = max(0, final_queues[d] - cap)
            
    st.bar_chart(pd.DataFrame(list(final_queues.items()), columns=['Dir', 'Vehicles']).set_index('Dir'))

    if improvement >= 20:
        st.success("Target Objective Achieved: >20% reduction.")