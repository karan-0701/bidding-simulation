import math
import random
from traffic_simulator import TrafficSimulator

NUM_TIME_SLOTS = 24
MIN_IMPRESSIONS = 250
MAX_IMPRESSIONS = 750
PEAK_START = 9
PEAK_END = 17
PEAK_AMPLITUDE = 1.2

DECAY_RATE = 0.1
ALPHA = 0.7
BETA = 0.15

# Class to represent an advertiser
class Advertiser:
    def __init__(self, name, bid, budget, min, reward):
        self.name = name # Advertiser name
        self.bid = bid # Per impression bid
        self.budget = budget # Budget to spend after minimum impressions are met
        self.min = min # Minimum impressions required
        self.reward = reward # Reward for meeting minimum impressions
        self.allocated = 0 # Impressions allocated to the advertiser
        self.remaining = min # Remaining impressions to meet the minimum
        self.max = min + (budget//bid) # Maximum possible impressions that can be allocated
        print(f"Created Advertiser {self.name}!")
    
    def __str__(self):
        return f"Advertiser {self.name} -> Bid: {self.bid}, Budget: {self.budget}, Minimum: {self.min}, Reward: {self.reward}, Allocated: {self.allocated}, Remaining: {self.remaining}, Maximum: {self.max}"
    
    # Calculate revenue for the advertiser
    def calculate_revenue(self):
        total = 0
        if self.allocated >= self.min:
            total += (self.bid * self.allocated) + self.reward
        return total

def init_advertisers():
    return {
        "A": Advertiser("A", 25, 250, 10000, 100), 
        "B": Advertiser("B", 24, 240, 2000, 100), 
        "C": Advertiser("C", 12, 125, 2000, 50),  
        "D": Advertiser("D", 30, 150, 2000, 0) 
    }

# Sort advertisers by expected revenue of meeting minimum impressions
def sort_advertisers(advertisers):
    advertisers_list = list(advertisers.values())
    advertisers_list.sort(key=lambda advertiser: advertiser.min * advertiser.bid, reverse=True)
    return advertisers_list

# Estimate impressions for the current time slot
def get_estimated_impressions(actual_impressions, initial_estimate, alpha=ALPHA):
    estimated = [initial_estimate]
    for i in range(1, len(actual_impressions)):
        estimated.append(int(alpha * actual_impressions[i-1] + (1 - alpha) * estimated[i-1]))
    return estimated

# Calculate the decay probability for the current time slot
def decay_probability(time_slot, decay_rate=DECAY_RATE):
    return math.exp(-decay_rate * time_slot)

def get_estimated_allocation(advertisers, estimated, time_slot):
    allocation = []
    decayed = int(estimated * decay_probability(time_slot))
    if decayed <= 0:
        decayed = 1
    first_adv = min(decayed, advertisers[0].remaining)
    allocation.append(first_adv)
    impressions_left = estimated - first_adv + (decayed-first_adv)
    remaining_total = sum(advertiser.remaining * advertiser.bid for advertiser in advertisers[1:])
    for advertiser in advertisers[1:]:
        allocation.append(int(((advertiser.remaining * advertiser.bid)/ remaining_total) * impressions_left))
    return allocation

def allocate(advertisers, index, impressions):
    if(impressions>0 and advertisers[index].remaining > 0):
        val = min(impressions, advertisers[index].remaining)
        advertisers[index].allocated += val
        advertisers[index].remaining -= val
        return_val = impressions - val
        #print(f"Allocated {val} impressions (out of {impressions}) to {advertisers[index].name}")
        return return_val
    return 0

def check_satisfaction(advertisers, remaining_advertisers):
    for adv in remaining_advertisers.copy():
        if adv.remaining <= 0:
            advertisers[adv.name] = adv
            remaining_advertisers.remove(adv)
            print(f"Advertiser {adv.name} has met minimum impressions!")

def exp_beta(random_value, beta=BETA):
    return math.exp(beta*(random_value - 1))

def gpg(advertisers):
    valid_advertisers = [adv for adv in advertisers.values() if adv.allocated < adv.max]
    if valid_advertisers:
        max_bid = float('-inf')
        selected_advertiser = None
        for advertiser in valid_advertisers:
            bid = advertiser.bid * (1-exp_beta(random.uniform(0,1)))
            if bid > max_bid:
                max_bid = bid
                selected_advertiser = advertiser
        return selected_advertiser.name, max_bid
    else:
        return None, 0

def simulate_bidding(advertisers, num_time_slots, initial_impression_estimate, traffic, run_gpg=True):
    sim_running = True
    sorted_advertisers = sort_advertisers(advertisers)
    remaining_advertisers = sorted_advertisers.copy()
    total_revenue = 0
    actual_impressions = traffic.get_actual_impressions(num_time_slots)
    estimated_impressions = get_estimated_impressions(actual_impressions, initial_impression_estimate)

    for time_slot in range(num_time_slots):
        print(f"\n--- {time_slot} To {time_slot+1} HOURS ---")
        actual = actual_impressions[time_slot]
        estimated = estimated_impressions[time_slot]
        print(f"Actual Impressions: {actual}, Estimated Impressions: {estimated}")
        if remaining_advertisers:
            estimated_allocation = get_estimated_allocation(remaining_advertisers, estimated, time_slot)
            print(f"Estimated Allocation: {estimated_allocation}")

        while actual>0 and sim_running:
            if remaining_advertisers:
                for i in range(0, len(remaining_advertisers)):
                    if(estimated_allocation[i] > 0 and actual > 0):
                        val = min(estimated_allocation[i], actual)
                        return_val = allocate(remaining_advertisers, i, val)
                        actual = actual - val + return_val
                check_satisfaction(advertisers, remaining_advertisers)
            elif run_gpg:
                winning_adv, winning_bid = gpg(advertisers)
                if winning_adv:
                    actual -= 1
                    advertisers[winning_adv].allocated += 1
                    print(f"Allocated 1 impression to {winning_adv} with perturbated bid {winning_bid:.2f}", end=" | ")
                else:
                    print(f"All advertisers have reached their maximum impressions!")
                    sim_running = False
            else:
                # print(f"GPG disabled!")
                sim_running = False
            
    for advertiser in advertisers.values():
        total_revenue += advertiser.calculate_revenue()
    return total_revenue

'''
note to self
-add similar logic of remaining advertisers in the greedy algorithm based on budget
'''

# Main function to run the simulation
def main():
    advertisers = init_advertisers()
    initial_impression_estimate = 2500
    traffic = TrafficSimulator(MIN_IMPRESSIONS, MAX_IMPRESSIONS, PEAK_START, PEAK_END, PEAK_AMPLITUDE)
    revenue = simulate_bidding(advertisers, NUM_TIME_SLOTS, initial_impression_estimate, traffic, False)
    print("\n--- SIMULATION SUMMARY ---")
    print(f"Total revenue: {revenue}")
    for advertiser in advertisers.values():
        print(advertiser)

if __name__ == "__main__":
    main()