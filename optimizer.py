import random
import math

class SimulatedAnnealing:
    def __init__(self, env, vpm_rates):
        self.env = env
        self.vpm_rates = vpm_rates

    def optimize(self, initial_temp=100.0, cooling_rate=0.99, iterations=1200):
        total_green = self.env.C - self.env.total_clearance
        
        # Start at the logical center (27/27) 
        current_g_ns = total_green // 2
        current_delay = self.env.get_total_delay(current_g_ns, total_green - current_g_ns, self.vpm_rates)
        
        best_g_ns, best_delay = current_g_ns, current_delay
        temp = initial_temp

        for _ in range(iterations):
            move = random.choice([-1, 1])
            # Set g_min to 15 to stay away from the 10s boundary error [cite: 17]
            next_ns = max(15, min(current_g_ns + move, total_green - 15))
            next_delay = self.env.get_total_delay(next_ns, total_green - next_ns, self.vpm_rates)
            
            delta = next_delay - current_delay

            # Metropolis Criterion 
            if delta < 0 or (temp > 0 and random.random() < math.exp(-delta / temp)):
                current_g_ns, current_delay = next_ns, next_delay
                if current_delay < best_delay:
                    best_g_ns, best_delay = current_g_ns, current_delay
            
            temp *= cooling_rate
            
        return int(best_g_ns), int(total_green - best_g_ns), best_delay

class HillClimbing:
    def __init__(self, env, vpm_rates):
        self.env = env
        self.vpm_rates = vpm_rates

    def optimize(self, max_iterations=50):
        total_green = self.env.C - self.env.total_clearance
        
        # Start at the logical center
        current_g_ns = total_green // 2
        current_delay = self.env.get_total_delay(current_g_ns, total_green - current_g_ns, self.vpm_rates)
        
        for _ in range(max_iterations):
            improved = False
            # Check neighbors: move left or right
            for move in [-1, 1]:
                next_ns = current_g_ns + move
                # Ensure it stays within bounds
                if 15 <= next_ns <= total_green - 15:
                    next_delay = self.env.get_total_delay(next_ns, total_green - next_ns, self.vpm_rates)
                    if next_delay < current_delay:
                        current_delay = next_delay
                        current_g_ns = next_ns
                        improved = True
                        break # Took the first improving step
            
            if not improved:
                break # Local optimum reached
                
        return int(current_g_ns), int(total_green - current_g_ns), current_delay