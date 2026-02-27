import math

class TrafficEnvironment:
    def __init__(self, cycle_length=60, t_yellow=3, t_allred=2):
        self.C = cycle_length 
        self.T_yellow = t_yellow 
        self.T_allred = t_allred
        self.clearance_per_phase = t_yellow + t_allred
        self.total_clearance = 2 * self.clearance_per_phase
        self.horizon = 600  # Increased to 10 minutes to see long-term failure [cite: 17]
        self.saturation_flow_rate = 0.5 # 

    def get_total_delay(self, g_ns, g_ew, vpm_rates):
        # Validate cycle equation [cite: 20]
        if abs((g_ns + g_ew + self.total_clearance) - self.C) > 0.1:
            return float('inf')

        queues = {'N': 0.0, 'S': 0.0, 'E': 0.0, 'W': 0.0}
        total_delay = 0.0
        total_vehicles = 0.0
        
        t_ns_end = g_ns
        t_ew_start = g_ns + self.clearance_per_phase
        t_ew_end = t_ew_start + g_ew

        for t in range(self.horizon):
            cycle_t = t % self.C
            is_ns_green = 0 <= cycle_t < t_ns_end
            is_ew_green = t_ew_start <= cycle_t < t_ew_end

            for d in ['N', 'S', 'E', 'W']:
                arrival_rate = vpm_rates[d] / 60.0
                queues[d] += arrival_rate
                total_vehicles += arrival_rate

                capacity = self.saturation_flow_rate if ((d in 'NS' and is_ns_green) or (d in 'EW' and is_ew_green)) else 0
                queues[d] = max(0.0, queues[d] - capacity)
                total_delay += queues[d]

        # PENALTY: Heavily penalize the leftover queue to prevent boundary sliding 
        # Squaring the queues penalizes imbalance, forcing the SA to naturally distribute green time symmetrically in oversaturated situations.
        leftover_penalty = sum(q**2 for q in queues.values()) * 100
        return (total_delay + leftover_penalty) / max(0.001, total_vehicles)