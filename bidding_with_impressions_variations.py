import math
import random
from traffic_simulator import TrafficSimulator

NUM_TIME_SLOTS = 24
MIN_IMPRESSIONS = 1000
MAX_IMPRESSIONS = 5000
PEAK_START = 9
PEAK_END = 17
PEAK_AMPLITUDE = 1.2

DECAY_RATE = 0.01
ALPHA = 0.7
BETA = 0.15

# Bid adjustment parameters
MAX_BID_INCREASE = 0.2  # Maximum 20% increase in bid
MAX_BID_DECREASE = 0.3  # Maximum 30% decrease in bid
UNDERPERFORM_THRESHOLD = 0.8  # If below 80% of expected performance
BUDGET_ALERT_THRESHOLD = 0.8  # If 80% of budget is used
PERFORMANCE_WEIGHT = 0.6  # Weight for performance-based adjustment
BUDGET_WEIGHT = 0.4  # Weight for budget-based adjustment

# Class to represent an advertiser
class Advertiser:
    def __init__(self, name, bid, budget, min, reward, time_multipliers=None):
        self.name = name  # Advertiser name
        self.original_bid = bid  # Original per impression bid
        self.bid = bid  # Current per impression bid
        self.budget = budget  # Budget to spend after minimum impressions are met
        self.spent = 0  # Amount spent so far
        self.min = min  # Minimum impressions required
        self.reward = reward  # Reward for meeting minimum impressions
        self.allocated = 0  # Impressions allocated to the advertiser
        self.remaining = min  # Remaining impressions to meet the minimum
        self.max = min + (budget//bid)  # Maximum possible impressions that can be allocated
        self.expected_impressions_per_slot = min / NUM_TIME_SLOTS  # Expected impressions per time slot
        self.historical_performance = []  # Track performance across time slots
        
        # Time-dependent preferences
        self.time_multipliers = time_multipliers or {hour: 1.0 for hour in range(NUM_TIME_SLOTS)}
        
        print(f"Created Advertiser {self.name}!")
    
    def __str__(self):
        return f"Advertiser {self.name} -> Original Bid: {self.original_bid}, Current Bid: {self.bid:.2f}, Budget: {self.budget}, Spent: {self.spent:.2f}, Minimum: {self.min}, Reward: {self.reward}, Allocated: {self.allocated}, Remaining: {self.remaining}, Maximum: {self.max}"
    
    # Get effective bid for the current time slot
    def get_effective_bid(self, time_slot):
        multiplier = self.time_multipliers.get(time_slot, 1.0)
        effective_bid = self.bid * multiplier
        return effective_bid
    
    # Calculate revenue for the advertiser
    def calculate_revenue(self):
        total = self.spent
        if self.allocated >= self.min:
            total += self.reward
        return total
    
    # Update bid based on performance and budget constraints
    def adjust_bid(self, time_slot, impressions_in_slot):
        if time_slot == 0:
            return  # No adjustment in the first time slot
        
        # Calculate performance metrics
        expected_progress = (time_slot + 1) / NUM_TIME_SLOTS  # Expected portion of min impressions met
        actual_progress = (self.min - self.remaining) / self.min  # Actual portion of min impressions met
        performance_ratio = actual_progress / expected_progress if expected_progress > 0 else 1
        
        # Calculate budget metrics
        budget_ratio = self.spent / self.budget if self.budget > 0 else 1
        
        # Store performance for this time slot
        self.historical_performance.append({
            'time_slot': time_slot,
            'expected_progress': expected_progress,
            'actual_progress': actual_progress,
            'performance_ratio': performance_ratio,
            'impressions_gained': impressions_in_slot,
            'budget_ratio': budget_ratio
        })
        
        # Calculate bid adjustments
        performance_adjustment = 0
        budget_adjustment = 0
        
        # Performance-based adjustment
        if performance_ratio < UNDERPERFORM_THRESHOLD and self.remaining > 0:
            # Underperforming - increase bid
            performance_adjustment = MAX_BID_INCREASE * (1 - performance_ratio/UNDERPERFORM_THRESHOLD)
        elif performance_ratio > 1.2 and self.remaining > 0:
            # Overperforming - can decrease bid slightly
            performance_adjustment = -MAX_BID_DECREASE * 0.5 * (performance_ratio - 1.2) / 0.8
        
        # Budget-based adjustment
        remaining_time_ratio = (NUM_TIME_SLOTS - time_slot) / NUM_TIME_SLOTS
        if budget_ratio > BUDGET_ALERT_THRESHOLD * expected_progress / remaining_time_ratio:
            # Budget being consumed too fast - decrease bid
            budget_adjustment = -MAX_BID_DECREASE * (budget_ratio - BUDGET_ALERT_THRESHOLD) / (1 - BUDGET_ALERT_THRESHOLD)
        elif budget_ratio < 0.8 * expected_progress and performance_ratio < 0.9:
            # Budget being consumed too slowly and underperforming - increase bid
            budget_adjustment = MAX_BID_INCREASE * 0.5 * (1 - budget_ratio/(0.8 * expected_progress))
        
        # Combine adjustments with weights
        total_adjustment = (PERFORMANCE_WEIGHT * performance_adjustment) + (BUDGET_WEIGHT * budget_adjustment)
        
        # Apply adjustment with limits
        new_bid = self.bid * (1 + total_adjustment)
        new_bid = max(self.original_bid * 0.5, min(self.original_bid * 2, new_bid))  # Limit between 50% and 200% of original bid
        
        # Only adjust if minimum not met or within budget
        if self.remaining > 0 or self.spent < self.budget:
            old_bid = self.bid
            self.bid = new_bid
            
            # Update max impressions based on new bid
            if self.remaining <= 0:  # Already met minimum
                additional_impressions = (self.budget - self.spent) // self.bid
                self.max = self.allocated + additional_impressions
            
            print(f"{self.name}'s bid adjusted from {old_bid:.2f} to {self.bid:.2f} (perf:{performance_ratio:.2f}, budget:{budget_ratio:.2f})")
            return True
        return False

def init_advertisers():
    # Define time multipliers for each advertiser
    # Morning preference (6-12)
    morning_preference = {hour: 1.5 if 6 <= hour < 12 else 0.8 for hour in range(NUM_TIME_SLOTS)}
    # Evening preference (17-23)
    evening_preference = {hour: 1.6 if 17 <= hour < 23 else 0.7 for hour in range(NUM_TIME_SLOTS)}
    # Business hours preference (9-17)
    business_preference = {hour: 1.4 if 9 <= hour < 17 else 0.8 for hour in range(NUM_TIME_SLOTS)}
    # Night preference (22-5)
    night_preference = {hour: 1.8 if (22 <= hour < 24 or 0 <= hour < 5) else 0.6 for hour in range(NUM_TIME_SLOTS)}
    
    return {
        "A": Advertiser("A", 25, 250000, 20000, 10000, morning_preference), 
        "B": Advertiser("B", 24, 240000, 15000, 10000, evening_preference), 
        "C": Advertiser("C", 12, 125000, 10000, 5000, business_preference),  
        "D": Advertiser("D", 30, 150000, 5000, 0, night_preference) 
    }

# Sort advertisers by expected revenue of meeting minimum impressions using effective bid
def sort_advertisers(advertisers, time_slot):
    advertisers_list = list(advertisers.values())
    advertisers_list.sort(key=lambda advertiser: advertiser.min * advertiser.get_effective_bid(time_slot), reverse=True)
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
    
    if not advertisers:
        return allocation
    
    first_adv = min(decayed, advertisers[0].remaining)
    allocation.append(first_adv)
    impressions_left = estimated - first_adv + (decayed-first_adv)
    
    if len(advertisers) > 1:
        # Use effective bids for allocation
        remaining_total = sum(advertiser.remaining * advertiser.get_effective_bid(time_slot) for advertiser in advertisers[1:])
        if remaining_total > 0:
            for advertiser in advertisers[1:]:
                effective_bid = advertiser.get_effective_bid(time_slot)
                allocation.append(int(((advertiser.remaining * effective_bid)/ remaining_total) * impressions_left))
        else:
            for _ in advertisers[1:]:
                allocation.append(0)
    
    return allocation

def allocate(advertisers, index, impressions, time_slot):
    if impressions > 0 and advertisers[index].remaining > 0:
        val = min(impressions, advertisers[index].remaining)
        effective_bid = advertisers[index].get_effective_bid(time_slot)
        actual_payment = advertisers[index].bid  # Still pay the base bid
        
        advertisers[index].allocated += val
        advertisers[index].remaining -= val
        advertisers[index].spent += val * actual_payment  # Track spending at actual bid
        return_val = impressions - val
        print(f"Allocated {val} impressions (out of {impressions}) to {advertisers[index].name} at {actual_payment:.2f} per impression (effective bid: {effective_bid:.2f})")
        return return_val
    return impressions

def check_satisfaction(advertisers, remaining_advertisers, total_revenue):
    advertisers_to_remove = []
    for adv in remaining_advertisers:
        if adv.remaining <= 0:
            advertisers[adv.name] = adv
            total_revenue += adv.calculate_revenue()
            advertisers_to_remove.append(adv)
            print(f"Advertiser {adv.name} has met minimum impressions!")
    
    for adv in advertisers_to_remove:
        remaining_advertisers.remove(adv)
    
    return total_revenue

def exp_beta(random_value, beta=BETA):
    return math.exp(beta*(random_value - 1))

def gpg(advertisers, time_slot):
    valid_advertisers = [adv for adv in advertisers.values() if adv.allocated < adv.max and adv.spent + adv.bid <= adv.budget]
    if valid_advertisers:
        max_bid = float('-inf')
        selected_advertiser = None
        for advertiser in valid_advertisers:
            effective_bid = advertiser.get_effective_bid(time_slot)
            bid = effective_bid * (1-exp_beta(random.uniform(0,1)))
            if bid > max_bid:
                max_bid = bid
                selected_advertiser = advertiser
        return selected_advertiser.name, max_bid, selected_advertiser.get_effective_bid(time_slot)
    else:
        return None, 0, 0

def simulate_bidding(advertisers, num_time_slots, initial_impression_estimate, traffic):
    sim_running = True
    total_revenue = 0
    actual_impressions = traffic.get_actual_impressions(num_time_slots)
    estimated_impressions = get_estimated_impressions(actual_impressions, initial_impression_estimate)
    impressions_by_advertiser = {adv.name: 0 for adv in advertisers.values()}
    time_slot_revenue = [0] * num_time_slots

    for time_slot in range(num_time_slots):
        print(f"\n--- {time_slot} To {time_slot+1} HOURS ---")
        actual = actual_impressions[time_slot]
        estimated = estimated_impressions[time_slot]
        print(f"Actual Impressions: {actual}, Estimated Impressions: {estimated}")
        
        # Reset impression counter for this time slot
        for name in impressions_by_advertiser:
            impressions_by_advertiser[name] = 0
        
        # Adjust bids based on performance before allocation in this time slot
        if time_slot > 0:  # No adjustment in the first time slot
            print("\n--- BID ADJUSTMENTS ---")
            for adv in advertisers.values():
                adv.adjust_bid(time_slot, impressions_by_advertiser[adv.name])
        
        # Sort advertisers using effective bids for this time slot
        sorted_advertisers = sort_advertisers(advertisers, time_slot)
        remaining_advertisers = sorted_advertisers.copy()
        
        # Print time-specific preferences
        print("\n--- TIME-SPECIFIC PREFERENCES ---")
        for adv in sorted_advertisers:
            effective_bid = adv.get_effective_bid(time_slot)
            multiplier = adv.time_multipliers.get(time_slot, 1.0)
            print(f"{adv.name}: Base bid: {adv.bid:.2f}, Multiplier: {multiplier:.2f}, Effective bid: {effective_bid:.2f}")

        slot_revenue = 0
        while actual > 0 and sim_running:
            if remaining_advertisers:
                estimated_allocation = get_estimated_allocation(remaining_advertisers, estimated, time_slot)
                print(f"Estimated Allocation: {estimated_allocation}")
                
                for i in range(0, len(remaining_advertisers)):
                    if i < len(estimated_allocation) and estimated_allocation[i] > 0 and actual > 0:
                        val = min(estimated_allocation[i], actual)
                        before_actual = actual
                        return_val = allocate(remaining_advertisers, i, val, time_slot)
                        allocated_impressions = before_actual - actual + return_val
                        impressions_by_advertiser[remaining_advertisers[i].name] += allocated_impressions
                        slot_revenue += allocated_impressions * remaining_advertisers[i].bid
                        actual = actual - val + return_val

                total_revenue = check_satisfaction(advertisers, remaining_advertisers, total_revenue)
            else:
                winning_adv, winning_bid, effective_bid = gpg(advertisers, time_slot)
                if winning_adv:
                    actual -= 1
                    advertisers[winning_adv].allocated += 1
                    advertisers[winning_adv].spent += advertisers[winning_adv].bid  # Track spending at actual bid
                    impressions_by_advertiser[winning_adv] += 1
                    slot_revenue += advertisers[winning_adv].bid
                    print(f"Allocated 1 impression to {winning_adv} with perturbed bid {winning_bid:.2f} (effective: {effective_bid:.2f})", end=" | ")
                else:
                    print(f"All advertisers have reached their maximum impressions or budget!")
                    sim_running = False
        
        time_slot_revenue[time_slot] = slot_revenue
        print(f"\nSlot Revenue: {slot_revenue:.2f}")
    
    # Calculate final revenue
    total_revenue = 0
    for advertiser in advertisers.values():
        total_revenue += advertiser.calculate_revenue()
    
    return total_revenue, advertisers, time_slot_revenue

# Main function to run the simulation
def main():
    advertisers = init_advertisers()
    initial_impression_estimate = 2500
    traffic = TrafficSimulator(MIN_IMPRESSIONS, MAX_IMPRESSIONS, PEAK_START, PEAK_END, PEAK_AMPLITUDE)
    revenue, final_advertisers, time_slot_revenue = simulate_bidding(advertisers, NUM_TIME_SLOTS, initial_impression_estimate, traffic)
    
    print("\n--- SIMULATION SUMMARY ---")
    print(f"Total revenue: {revenue:.2f}")
    
    print("\n--- REVENUE BY TIME SLOT ---")
    for slot, rev in enumerate(time_slot_revenue):
        print(f"Hour {slot}: ${rev:.2f}")
    
    print("\n--- ADVERTISER PERFORMANCE ---")
    for advertiser in final_advertisers.values():
        print(advertiser)
        print(f"  - Performance Metrics:")
        print(f"    - Min Impressions Met: {'Yes' if advertiser.allocated >= advertiser.min else 'No'}")
        print(f"    - Impressions Allocated: {advertiser.allocated} / {advertiser.min} (min) / {advertiser.max} (max)")
        print(f"    - Budget Utilization: {advertiser.spent:.2f} / {advertiser.budget:.2f} ({advertiser.spent/advertiser.budget*100:.1f}%)")
        print(f"    - Final Bid: {advertiser.bid:.2f} (started at {advertiser.original_bid})")
        
        print(f"  - Time Preferences:")
        high_pref_slots = sorted([(hour, mult) for hour, mult in advertiser.time_multipliers.items() if mult > 1.0], 
                                key=lambda x: x[1], reverse=True)[:5]
        print(f"    - Highest preference hours: {', '.join([f'Hour {h} ({m:.2f}x)' for h, m in high_pref_slots])}")
        print()

if __name__ == "__main__":
    main()