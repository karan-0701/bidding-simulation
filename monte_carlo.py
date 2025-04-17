import pandas as pd
import numpy as np
import math
import random
import time
import copy
from traffic_simulator import TrafficSimulator
from tqdm import tqdm

#default simulation hyperparameters
NUM_TIME_SLOTS = 24
MIN_IMPRESSIONS = 1000
MAX_IMPRESSIONS = 5000
PEAK_START = 9
PEAK_END = 17
PEAK_AMPLITUDE = 1.2
DECAY_RATE = 0.01
ALPHA = 0.7
BETA = 0.15
NUM_SIMULATIONS = 500
MIN_ADV = 10
MAX_ADV = 50

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
        #print(f"Created Advertiser {self.name}")
    
    # def __str__(self):
    #     return f"Advertiser {self.name} -> Bid: {self.bid}, Budget: {self.budget}, Minimum: {self.min}, Reward: {self.reward}, Allocated: {self.allocated}, Remaining: {self.remaining}, Maximum: {self.max}"
    
    def __str__(self):
        return f"Advertiser {self.name} ->  {self.bid}, Minimum: {self.min}, Reward: {self.reward}, Allocated: {self.allocated}, Remaining: {self.remaining}"
    
    # Calculate revenue for the advertiser
    def calculate_revenue(self):
        total = self.bid * self.allocated
        if self.allocated >= self.min:
            total += self.reward
        return total

#class to simulate the bidding process
class BiddingSimulator:
    def __init__(self, min_impressions=MIN_IMPRESSIONS, max_impressions=MAX_IMPRESSIONS, 
                    peak_start=PEAK_START, peak_end=PEAK_END, peak_amplitude=PEAK_AMPLITUDE,
                    decay_rate=DECAY_RATE, alpha=ALPHA, beta=BETA):
        self.min_impressions = min_impressions
        self.max_impressions = max_impressions
        self.peak_start = peak_start
        self.peak_end = peak_end
        self.peak_amplitude = peak_amplitude
        self.decay_rate = decay_rate
        self.alpha = alpha
        self.beta = beta
        self.traffic = TrafficSimulator(min_impressions, max_impressions, peak_start, peak_end, peak_amplitude)
        self.run_gpg = True
        
    def init_advertisers(self):
        return {
            "A": Advertiser("A", 25, 250, 20000, 100), 
            "B": Advertiser("B", 24, 240, 15000, 100), 
            "C": Advertiser("C", 12, 125, 10000, 50),  
            "D": Advertiser("D", 30, 150, 5000, 0) 
        }

    # Sort advertisers by expected revenue of meeting minimum impressions
    def sort_advertisers(self, advertisers):
        advertisers_list = list(advertisers.values())
        advertisers_list.sort(key=lambda advertiser: advertiser.min * advertiser.bid, reverse=True)
        return advertisers_list

    # Estimate impressions for the current time slot
    def get_estimated_impressions(self, actual_impressions, initial_estimate, alpha=ALPHA):
        estimated = [initial_estimate]
        for i in range(1, len(actual_impressions)):
            estimated.append(int(alpha * actual_impressions[i-1] + (1 - alpha) * estimated[i-1]))
        return estimated

    # Calculate the decay probability for the current time slot
    def decay_probability(self, time_slot, decay_rate=DECAY_RATE):
        return math.exp(-decay_rate * time_slot)

    def get_estimated_allocation(self, advertisers, estimated, time_slot):
        allocation = []
        decayed = int(estimated * self.decay_probability(time_slot))
        first_adv = min(decayed, advertisers[0].remaining)
        allocation.append(first_adv)
        impressions_left = estimated - first_adv + (decayed-first_adv)
        remaining_total = sum(advertiser.remaining * advertiser.bid for advertiser in advertisers[1:])
        for advertiser in advertisers[1:]:
            allocation.append(int(((advertiser.remaining * advertiser.bid)/ remaining_total) * impressions_left))
        return allocation

    def allocate(self, advertisers, index, impressions):
        if(impressions>0 and advertisers[index].remaining > 0):
            val = min(impressions, advertisers[index].remaining)
            advertisers[index].allocated += val
            advertisers[index].remaining -= val
            return_val = impressions - val
            #print(f"Allocated {val} impressions (out of {impressions}) to {advertisers[index].name}")
            return return_val
        return 0

    def check_satisfaction(self, advertisers, remaining_advertisers):
        for adv in remaining_advertisers[:]:
            if adv.remaining <= 0:
                advertisers[adv.name] = adv
                remaining_advertisers.remove(adv)
                #print(f"Advertiser {adv.name} has met minimum impressions!")

    def exp_beta(self, random_value, beta=BETA):
        return math.exp(beta*(random_value - 1))

    def gpg(self, advertisers):
        valid_advertisers = [adv for adv in advertisers.values() if adv.allocated < adv.max]
        if valid_advertisers:
            max_bid = float('-inf')
            selected_advertiser = None
            for advertiser in valid_advertisers:
                bid = advertiser.bid * (1-self.exp_beta(random.uniform(0,1)))
                if bid > max_bid:
                    max_bid = bid
                    selected_advertiser = advertiser
            return selected_advertiser.name, max_bid
        else:
            return None, 0

    def simulate_bidding(self, advertisers, num_time_slots, initial_impression_estimate):
        sim_running = True
        sorted_advertisers = self.sort_advertisers(advertisers)
        remaining_advertisers = sorted_advertisers.copy()
        total_revenue = 0
        actual_impressions = self.traffic.get_actual_impressions(num_time_slots)
        estimated_impressions = self.get_estimated_impressions(actual_impressions, initial_impression_estimate)

        for time_slot in range(num_time_slots):
            #print(f"\n--- {time_slot} To {time_slot+1} HOURS ---")
            actual = actual_impressions[time_slot]
            estimated = estimated_impressions[time_slot]
            #print(f"Actual Impressions: {actual}, Estimated Impressions: {estimated}")
            if remaining_advertisers:
                estimated_allocation = self.get_estimated_allocation(remaining_advertisers, estimated, time_slot)
                #print(f"Estimated Allocation: {estimated_allocation}")

            while actual>0 and sim_running:
                if remaining_advertisers:
                    for i in range(0, len(remaining_advertisers)):
                        if(estimated_allocation[i] > 0 and actual > 0):
                            val = min(estimated_allocation[i], actual)
                            return_val = self.allocate(remaining_advertisers, i, val)
                            actual = actual - val + return_val
                    self.check_satisfaction(advertisers, remaining_advertisers)
                elif self.run_gpg:
                    winning_adv, winning_bid = self.gpg(advertisers)
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
        
    def run_simulation(self, num_time_slots=NUM_TIME_SLOTS, initial_impression_estimate=2500, custom_advertisers=None, run_gpg=True, decay_rate=DECAY_RATE):
        advertisers = custom_advertisers if custom_advertisers else self.init_advertisers()
        self.decay_rate = decay_rate
        self.run_gpg = run_gpg
        revenue = self.simulate_bidding(advertisers, num_time_slots, initial_impression_estimate)
        #print(f"Total revenue: {revenue}")
        # for advertiser in advertisers.values():
        #     print(advertiser)
        return revenue, advertisers


#class to run the Monte Carlo simulation
class MonteCarloSimulation:
    def __init__(self):
        self.bidding_simulator = BiddingSimulator()
    
    def run_monte_carlo(self, num_simulations=10000, min_adv=100, max_adv=500):
        # Load the advertiser dataset
        advertiser_data = pd.read_csv('advertiser_data_10k.csv')
        
        # Monte Carlo simulation parameters
        decay_factor_range = np.arange(0, 1.01, 0.01)
        results = []

        # Run Monte Carlo simulation
        for i in tqdm(range(num_simulations), desc="Running simulations"):
            #print(f"\n---MONTE CARLO SIMULATION #{i+1}---")
            # Set a unique seed based on the simulation iteration to ensure different samples
            random.seed(time.time() + i)
            sampled_advertisers = advertiser_data.sample(random.randint(min_adv,max_adv))
            # Convert sampled advertisers to Advertiser objects
            converted_advertisers = {}
            for idx, row in sampled_advertisers.iterrows():
                name = row['AdvertiserId']
                bid = row['Bid']
                budget = row['Budget']
                min_impressions = row['Minimum_Impressions']
                reward = row['Reward']
                
                converted_advertisers[name] = Advertiser(
                    name=name,
                    bid=bid,
                    budget=budget,
                    min=min_impressions,
                    reward=reward
                )

            best_decay_factor = 0
            max_reward = -float('inf')
            indiv_results = {}
            
            # Test different decay factors
            for decay_factor in decay_factor_range:
                #print(f"\nDecay Factor: {decay_factor}")
                advertisers_copy = copy.deepcopy(converted_advertisers)
                reward, simulated_advertisers = self.bidding_simulator.run_simulation(custom_advertisers=advertisers_copy, run_gpg=False, decay_rate=decay_factor)
                del advertisers_copy
                del simulated_advertisers
                if reward > max_reward:
                    max_reward = reward
                    best_decay_factor = decay_factor
                indiv_results[decay_factor] = reward
            
            # Save the result for this simulation
            results.append({
                'advertiser_ids': sampled_advertisers['AdvertiserId'].tolist(),
                'best_decay_factor': best_decay_factor,
                'max_reward': max_reward,
                'decay_factor_results': indiv_results,
            })
            
            # del converted_advertisers
            # del sampled_advertisers
            # del indiv_results
            


        # Save results to a file
        output_file = 'monte_carlo_results.csv'
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_file, index=False)
        
        print(f"\nMonte Carlo simulation completed. Results saved to {output_file}.")
        return results_df

def main():
    simulator = MonteCarloSimulation()
    results = simulator.run_monte_carlo(num_simulations=NUM_SIMULATIONS, min_adv=MIN_ADV, max_adv=MAX_ADV)
    #Perform additional analysis on results
    print(f"Average max reward: {results['max_reward'].mean()}")
    print(f"Average optimal decay factor: {results['best_decay_factor'].mean()}")


if __name__ == "__main__":
    main()