import math
import numpy as np
import matplotlib.pyplot as plt

min_impressions = 1000
max_impressions = 5000
time_slots = 24

peak_start = 9
peak_end = 17
peak_amplitude = 1.2
base_impressions = np.random.uniform(min_impressions, max_impressions, time_slots)

def get_actual_impressions():
    for t in range(time_slots):
        if t >= peak_start and t <= peak_end:
            base_impressions[t] *= peak_amplitude 

    noise = np.random.normal(0, 200, time_slots)
    simulated_impressions = base_impressions + noise
    simulated_impressions = np.clip(simulated_impressions, min_impressions, max_impressions)
    
    return simulated_impressions