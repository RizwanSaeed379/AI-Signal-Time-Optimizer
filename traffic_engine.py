import math

class TrafficEnvironment:
    def __init__(self, cycle_length=60, t_total_clearance=6):
        # Full signal cycle time (seconds)
        self.cycle_time = cycle_length
        
        # Total yellow + all-red time in one full cycle
        self.total_clearance_time = t_total_clearance
        
        # Clearance time between two phases
        self.clearance_per_phase = t_total_clearance / 2
        
        # Simulation runs for 10 minutes (in seconds)
        self.simulation_duration = 600
        
        # Maximum number of cars that can leave per second during green
        self.rate_of_outgoing_cars = 1.67  

    def get_total_delay(self, green_ns, green_ew, cars_per_minute):
        
        # Make sure timings actually fit inside one cycle
        if abs((green_ns + green_ew + self.total_clearance_time) - self.cycle_time) > 0.1:
            return float('inf')

        waiting_cars = {'N': 0.0, 'S': 0.0, 'E': 0.0, 'W': 0.0}
        total_wait_time = 0.0
        total_cars_arrived = 0.0

        # Green windows
        ns_green_start, ns_green_end = 0, green_ns

        ew_green_start = green_ns + self.clearance_per_phase
        ew_green_end = ew_green_start + green_ew

        # Second-by-second simulation
        for current_second in range(self.simulation_duration):
            position_in_cycle = current_second % self.cycle_time

            ns_is_green = ns_green_start <= position_in_cycle < ns_green_end
            ew_is_green = ew_green_start <= position_in_cycle < ew_green_end

            for direction in ['N', 'S', 'E', 'W']:

                # Cars arriving this second
                cars_arriving_per_second = cars_per_minute[direction] / 60.0
                waiting_cars[direction] += cars_arriving_per_second
                total_cars_arrived += cars_arriving_per_second

                # Cars leaving only during green
                if (direction in 'NS' and ns_is_green) or (direction in 'EW' and ew_is_green):
                    waiting_cars[direction] = max(
                        0.0,
                        waiting_cars[direction] - self.rate_of_outgoing_cars
                    )

                # Add current queue to total delay
                total_wait_time += waiting_cars[direction]

        # Oversaturation penalty
        penalty = 0.0
        for direction in ['N', 'S', 'E', 'W']:
            arrival_rate_sec = cars_per_minute[direction] / 60.0
            max_normal_queue = arrival_rate_sec * self.cycle_time

            if waiting_cars[direction] > max_normal_queue:
                penalty += ((waiting_cars[direction] - max_normal_queue) ** 2) * 50

        # Normalized delay
        return (total_wait_time + penalty) / max(0.001, total_cars_arrived)
