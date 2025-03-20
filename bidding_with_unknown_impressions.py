import math
from traffic_simulator import *
from optimal_gpg import *

NUM_TIME_SLOTS = 24

class Advertiser:
    def __init__(self, name, click_rate, budget, min_impressions, reward):
        self.name = name
        self.click_rate = click_rate
        self.budget = budget
        self.min_impressions = min_impressions
        self.reward = reward
    
    def __str__(self):
        return f"Advertiser(Name: {self.name}, Budget: {self.budget}, Minimum Impressions: {self.min_impressions})"

def initialize_advertisers():
    return [
        Advertiser("A", 25, 250, 20000, 100), 
        Advertiser("B", 24, 240, 15000, 100), 
        Advertiser("C", 12, 125, 10000, 50),  
        Advertiser("D", 30, 150, 5000, 0) 
    ]

def sort_advertisers_by_min_impressions(advertisers):
    return sorted(advertisers, key=lambda advertiser: advertiser.min_impressions, reverse=True)

def estimate_impressions(current_impressions, previous_estimate, alpha=0.7):
    return alpha * current_impressions + (1 - alpha) * previous_estimate

def calculate_decay_probability(time_slot, decay_rate=0.01):
    return math.exp(-decay_rate * time_slot)

def allocate_impressions_to_advertiser(advertiser, slot_estimate, time_slot):
    allocated_impressions = slot_estimate * calculate_decay_probability(time_slot)
    advertiser.min_impressions -= allocated_impressions
    return allocated_impressions

def allocate_remaining_impressions(advertisers, slot_estimate, time_slot):
    remaining_impressions_sum = sum(adv.min_impressions for adv in advertisers[1:])
    for advertiser in advertisers[1:]:
        allocated_impressions = (advertiser.min_impressions / remaining_impressions_sum) * slot_estimate
        advertiser.min_impressions -= allocated_impressions

def remove_satisfied_advertisers(advertisers):
    return [adv for adv in advertisers if adv.min_impressions > 0]

def simulate_bidding(advertisers, num_time_slots, initial_impression_estimate):
    total_reward = 0
    estimated_impressions = []
    actual_impressions = TrafficSimulator().get_actual_impressions(num_time_slots)
    advertisers_greedy = advertisers
    # Store original minimum impressions for each advertiser
    original_min_impressions = {adv.name: adv.min_impressions for adv in advertisers}

    for time_slot in range(num_time_slots):
        print(f"\n--- Time Slot {time_slot} ---")

        if time_slot == 0:
            slot_estimate = int(initial_impression_estimate)
        else:
            slot_estimate = int(estimate_impressions(actual_impressions[time_slot - 1], estimated_impressions[time_slot - 1]))

        estimated_impressions.append(slot_estimate)
        print(f"Estimated Impressions: {slot_estimate}")

        if advertisers:
            print(f"{advertisers[0].name}'s initial min impressions: {int(advertisers[0].min_impressions)}")
            allocated_impressions_first = int(allocate_impressions_to_advertiser(advertisers[0], slot_estimate, time_slot))

            print(f"Allocated {allocated_impressions_first} impressions to {advertisers[0].name}")
            extra_allocations = 0
            if advertisers[0].min_impressions < 0:
                extra_allocations = abs(int(advertisers[0].min_impressions))
                advertisers[0].min_impressions = 0
                
                advertiser_name = advertisers[0].name
                advertiser_reward = advertisers[0].click_rate * original_min_impressions[advertiser_name] + advertisers[0].reward
                total_reward += advertiser_reward
                print(f"Reward calculation for {advertiser_name}: {advertisers[0].click_rate} * {original_min_impressions[advertiser_name]} + {advertisers[0].reward} = {advertiser_reward}")
                print(f"Total reward is now: {total_reward}")
                
            print(f"{advertisers[0].name}'s remaining min impressions: {int(advertisers[0].min_impressions)}")

            remaining_impressions = slot_estimate - allocated_impressions_first + extra_allocations
            print(f"Remaining Impressions after {advertisers[0].name}: {remaining_impressions}")

            first_advertiser_satisfied = advertisers[0].min_impressions <= 0
            
            remaining_advertisers = advertisers[1:]
            
            if first_advertiser_satisfied:
                print(f"{advertisers[0].name} has been satisfied and removed from the list.")
                advertisers.pop(0)

            if remaining_advertisers and remaining_impressions > 0:
                print(f"Processing remaining advertisers: {[adv.name for adv in remaining_advertisers]}")
                remaining_impressions_sum = sum(int(adv.min_impressions) for adv in remaining_advertisers)
                
                if remaining_impressions_sum > 0:  
                    for advertiser in remaining_advertisers:
                        allocated_impressions_remaining = int((advertiser.min_impressions / remaining_impressions_sum) * remaining_impressions)
                        advertiser.min_impressions -= allocated_impressions_remaining
                        print(f"Allocated {allocated_impressions_remaining} impressions to {advertiser.name}")
                        print(f"{advertiser.name}'s remaining min impressions: {int(advertiser.min_impressions)}")
                        
                        if advertiser.min_impressions <= 0:
                            advertiser_name = advertiser.name
                            advertiser_reward = advertiser.click_rate * original_min_impressions[advertiser_name] + advertiser.reward
                            total_reward += advertiser_reward
                            print(f"Reward calculation for {advertiser_name}: {advertiser.click_rate} * {original_min_impressions[advertiser_name]} + {advertiser.reward} = {advertiser_reward}")
                            print(f"Total reward is now: {total_reward}")
            
            advertisers = [adv for adv in advertisers if adv.min_impressions > 0]
            print(f"Remaining advertisers after satisfaction check: {[adv.name for adv in advertisers]}")
        # else:
        #     for i in range(slot_estimate):
        #         optimal_gpg(advertisers_greedy)

    return total_reward

def main():
    advertisers = initialize_advertisers()
    sorted_advertisers = sort_advertisers_by_min_impressions(advertisers)
    initial_impression_estimate = 2500
    
    reward  = simulate_bidding(sorted_advertisers, NUM_TIME_SLOTS, initial_impression_estimate)
    print(reward)

if __name__ == "__main__":
    main()