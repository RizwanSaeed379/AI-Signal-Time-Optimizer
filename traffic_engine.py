import math

class TrafficEnvironment:
    def __init__(self, cycle_length=60, t_total_clearance=6):
        """
        Initializes the traffic environment for the 7th Avenue intersection.
        """
        self.C = cycle_length 
        # Total time lost to non-green lights in one full cycle
        self.total_clearance = t_total_clearance 
        # Time lost per phase transition
        self.clearance_per_phase = t_total_clearance / 2
        
        # Horizon set to 10 minutes to capture long-term queue behavior
        self.horizon = 600  
        
        # Multi-lane saturation flow rate (approx 100 VPM capacity)
        self.saturation_flow_rate = 1.67 

    def get_total_delay(self, g_ns, g_ew, vpm_rates):
        """
        Calculates the normalized delay and penalty for a given timing plan.
        """
        # 1. Validation: Ensure the timings actually fit the cycle
        if abs((g_ns + g_ew + self.total_clearance) - self.C) > 0.1:
            return float('inf')

        queues = {'N': 0.0, 'S': 0.0, 'E': 0.0, 'W': 0.0}
        total_delay = 0.0
        total_vehicles = 0.0
        
        # 2. Define exact green windows within the cycle
        # NS Green Phase
        ns_start, ns_end = 0, g_ns
        
        # EW Green Phase (Starts after NS Green + First Clearance Phase)
        ew_start = g_ns + self.clearance_per_phase
        ew_end = ew_start + g_ew

        # 3. Time-Stepped Simulation
        for t in range(self.horizon):
            cycle_t = t % self.C
            
            # Check if current second falls within the respective green windows
            is_ns_green = ns_start <= cycle_t < ns_end
            is_ew_green = ew_start <= cycle_t < ew_end

            for d in ['N', 'S', 'E', 'W']:
                # Determine arrival rate per second
                arrival_rate = vpm_rates[d] / 60.0
                queues[d] += arrival_rate
                total_vehicles += arrival_rate

                # Discharge logic: vehicles exit only during green
                if (d in 'NS' and is_ns_green) or (d in 'EW' and is_ew_green):
                    queues[d] = max(0.0, queues[d] - self.saturation_flow_rate)
                
                # Accumulate delay based on the current queue size
                total_delay += queues[d]

        # 4. Oversaturation Penalty Logic
        # Instead of penalizing the max queue blindly (which artificially forces 
        # balanced splits even for unbalanced traffic), we only penalize queues
        # that exceed their structural minimum (meaning the phase is saturated
        # and its queue is permanently growing).
        over_penalty = 0.0
        for d in ['N', 'S', 'E', 'W']:
            arrival_rate_per_sec = vpm_rates[d] / 60.0
            max_normal_queue = arrival_rate_per_sec * self.C
            if queues[d] > max_normal_queue:
                over_penalty += ((queues[d] - max_normal_queue) ** 2) * 50
        
        # Return normalized average delay + the true oversaturation penalty
        return (total_delay + over_penalty) / max(0.001, total_vehicles)
