import math
import random

class Advertiser:
    def __init__(self, name, click_rate, budget, min_impressions, reward):
        self.name = name
        self.click_rate = click_rate
        self.budget = budget
        self.min_impressions = min_impressions
        self.reward = reward
    
    def __str__(self):
        return f"Advertiser(Name: {self.name}, Budget: {self.budget}, Minimum Impressions: {self.min_impressions})"

advertisers = [
    Advertiser("A", 25, 250, 5, 100),
    Advertiser("B", 24, 240, 5, 100),
    Advertiser("C", 12, 125, 5, 50),
    Advertiser("D", 30, 150, 0, 0)
]

def exp_beta(random_value, beta=0.22):
    return math.exp(beta*(random_value-1))

adv_with_contraints = [adv for adv in advertisers if adv.min_impressions > 0]

while True:
    if all(advertiser.min_impressions == 0 or advertiser.budget < advertiser.click_rate for advertiser in adv_with_contraints):
        print("All priority bids done!!")
        print("\n \n")
        break
    
    max_bid = float('-inf')
    selected_advertiser = None
    
    for advertiser in adv_with_contraints:
        bid = (1 - exp_beta(random.uniform(0,1)))*advertiser.click_rate
        print(f"Advertiser {advertiser.name} bids {advertiser.click_rate:.4f}")
        if bid > max_bid:
            max_bid = bid
            selected_advertiser = advertiser
    
    if selected_advertiser:
        print(f"Selected Advertiser: {selected_advertiser.name}, Bid: {selected_advertiser.click_rate:.4f}")
        selected_advertiser.budget -= selected_advertiser.click_rate
        selected_advertiser.min_impressions -= 1
        print(f"{selected_advertiser.name} Remaining Impressions: {selected_advertiser.min_impressions}, Budget: {selected_advertiser.budget:.2f}")
    
    adv_with_contraints = [adv for adv in advertisers if adv.min_impressions > 0]

adv_without_contraints = [adv for adv in advertisers if adv.min_impressions == 0]

if not adv_without_contraints:
    print("No advertisers left without constraints.")
else:
    while True:
        if all(advertiser.budget < advertiser.click_rate for advertiser in adv_without_contraints):
            print("All bids are zero, stopping the loop")
            break
        
        max_bid = float('-inf')
        selected_advertiser = None
        
        for advertiser in adv_without_contraints:
            bid = (1 - exp_beta(random.uniform(0,1)))*advertiser.click_rate
            print(f"Advertiser {advertiser.name} bids {advertiser.click_rate:.4f}")
            if bid > max_bid:
                max_bid = bid
                selected_advertiser = advertiser
        
        if selected_advertiser:
            print(f"Selected Advertiser: {selected_advertiser.name}, Bid: {selected_advertiser.click_rate:.4f}")
            selected_advertiser.budget -= selected_advertiser.click_rate
            print(f"{selected_advertiser.name} Remaining Budget: {selected_advertiser.budget:.2f}")
        
        if selected_advertiser.budget <= 0:
            adv_without_contraints.remove(selected_advertiser)

def optimal_gpg(advertisers):
        while True:
            if all(advertiser.budget < advertiser.click_rate for advertiser in advertisers):
                print("All bids are zero, stopping the loop")
                break
            
            max_bid = float('-inf')
            selected_advertiser = None
            
            for advertiser in advertisers:
                bid = (1 - exp_beta(random.uniform(0,1)))*advertiser.click_rate
                # print(f"Advertiser {advertiser.name} bids {advertiser.click_rate:.4f}")
                if bid > max_bid:
                    max_bid = bid
                    selected_advertiser = advertiser
            
            if selected_advertiser:
                print(f"Selected Advertiser: {selected_advertiser.name}, Bid: {selected_advertiser.click_rate:.4f}")
                selected_advertiser.budget -= selected_advertiser.click_rate
                print(f"{selected_advertiser.name} Remaining Budget: {selected_advertiser.budget:.2f}")
            
            if selected_advertiser.budget <= 0:
               advertisers.remove(selected_advertiser)
        