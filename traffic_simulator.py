import math
import numpy as np
import matplotlib.pyplot as plt

class TrafficSimulator:
    def __init__(self, min_impressions=1000, max_impressions=5000, peak_start=9, peak_end=17, peak_amplitude=1.2):
        self.min_impressions = min_impressions
        self.max_impressions = max_impressions
        self.peak_start = peak_start
        self.peak_end = peak_end
        self.peak_amplitude = peak_amplitude

    def get_actual_impressions(self, time_slots):
        base_impressions = np.random.uniform(self.min_impressions, self.max_impressions, time_slots)
        for t in range(time_slots):
            if t >= self.peak_start and t <= self.peak_end:
                base_impressions[t] *= self.peak_amplitude 

        noise = np.random.normal(0, 200, time_slots)
        simulated_impressions = base_impressions + noise
        simulated_impressions = np.clip(simulated_impressions, self.min_impressions, self.max_impressions)
        simulated_impressions = simulated_impressions.astype(int)
        return simulated_impressions