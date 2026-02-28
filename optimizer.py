import random
import math

class SimulatedAnnealing:
    def __init__(self, environment, cars_per_minute):
        self.environment = environment
        self.cars_per_minute = cars_per_minute

    def optimize(self, starting_temperature=100.0, cooling_rate=0.99, iterations=2000):

        total_green_time = self.environment.cycle_time - self.environment.total_clearance_time

        # Start from equal split
        current_ns_green = total_green_time // 2
        current_delay = self.environment.get_total_delay(
            current_ns_green,
            total_green_time - current_ns_green,
            self.cars_per_minute
        )

        best_ns_green = current_ns_green
        best_delay = current_delay
        temperature = starting_temperature

        for _ in range(iterations):

            step = random.choice([-1, 1])

            # Keep minimum green of 15 seconds
            next_ns_green = max(
                15,
                min(current_ns_green + step, total_green_time - 15)
            )

            next_delay = self.environment.get_total_delay(
                next_ns_green,
                total_green_time - next_ns_green,
                self.cars_per_minute
            )

            change_in_delay = next_delay - current_delay

            # Accept better solutions or probabilistically accept worse ones
            if change_in_delay < 0 or (
                temperature > 0 and random.random() < math.exp(-change_in_delay / temperature)
            ):
                current_ns_green = next_ns_green
                current_delay = next_delay

                if current_delay < best_delay:
                    best_ns_green = current_ns_green
                    best_delay = current_delay

            temperature *= cooling_rate

        return int(best_ns_green), int(total_green_time - best_ns_green), best_delay


class HillClimbing:
    def __init__(self, environment, cars_per_minute):
        self.environment = environment
        self.cars_per_minute = cars_per_minute

    def optimize(self, max_iterations=50):

        total_green_time = self.environment.cycle_time - self.environment.total_clearance_time

        current_ns_green = total_green_time // 2
        current_delay = self.environment.get_total_delay(
            current_ns_green,
            total_green_time - current_ns_green,
            self.cars_per_minute
        )

        for _ in range(max_iterations):
            improvement_found = False

            for step in [-1, 1]:
                next_ns_green = current_ns_green + step

                if 15 <= next_ns_green <= total_green_time - 15:

                    next_delay = self.environment.get_total_delay(
                        next_ns_green,
                        total_green_time - next_ns_green,
                        self.cars_per_minute
                    )

                    if next_delay < current_delay:
                        current_ns_green = next_ns_green
                        current_delay = next_delay
                        improvement_found = True
                        break  # take first improvement

            if not improvement_found:
                break  # local optimum reached

        return int(current_ns_green), int(total_green_time - current_ns_green), current_delay
