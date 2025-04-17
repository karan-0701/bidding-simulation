import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)

# Number of entries to generate
num_entries = 10000

# Generate data
data = {
    'AdvertiserId': list(range(1, num_entries + 1)),
    'Minimum_Impressions': np.random.randint(500, 10001, num_entries),
    'Budget': np.random.randint(10000, 25001, num_entries),
    'Bid': np.random.randint(1, 101, num_entries),
    'Reward': np.random.randint(10000, 25001, num_entries),
    'Performance': np.round(np.clip(np.random.normal(0.6, 0.15, num_entries), 0, 1), 2)
}

# Scale up the edge cases proportionally (10x)
# Edge case 1: Minimum bids (0.1)
min_bid_indices = random.sample(range(num_entries), 200)
for idx in min_bid_indices:
    data['Bid'][idx] = 1

# Edge case 2: Maximum bids (2.0)
max_bid_indices = random.sample(range(num_entries), 200)
for idx in max_bid_indices:
    data['Bid'][idx] = 100

# Edge case 3: Minimum impressions (exactly 1000)
min_imp_indices = random.sample(range(num_entries), 300)
for idx in min_imp_indices:
    data['Minimum_Impressions'][idx] = 500

# Edge case 4: Maximum impressions (exactly 5000)
max_imp_indices = random.sample(range(num_entries), 300)
for idx in max_imp_indices:
    data['Minimum_Impressions'][idx] = 10000

# Edge case 5: Minimum budget (exactly 100.0)
min_budget_indices = random.sample(range(num_entries), 250)
for idx in min_budget_indices:
    data['Budget'][idx] = 10000

# Edge case 6: Maximum budget (exactly 500.0)
max_budget_indices = random.sample(range(num_entries), 250)
for idx in max_budget_indices:
    data['Budget'][idx] = 25000

# Edge case 7: Extreme performance values (0.0 and 1.0)
min_perf_indices = random.sample(range(num_entries), 150)
for idx in min_perf_indices:
    data['Performance'][idx] = 0.0

max_perf_indices = random.sample(range(num_entries), 150)
for idx in max_perf_indices:
    data['Performance'][idx] = 1.0

# Edge case 8: Minimum reward (exactly 10000)
min_reward_indices = random.sample(range(num_entries), 200)
for idx in min_reward_indices:
    data['Reward'][idx] = 10000

# Edge case 9: Maximum reward (exactly 25000)
max_reward_indices = random.sample(range(num_entries), 200)
for idx in max_reward_indices:
    data['Reward'][idx] = 25000

# Additional variations to increase variability
# Add some high-variance clusters
for i in range(5):
    cluster_size = random.randint(50, 150)
    cluster_start = random.randint(0, num_entries - cluster_size)
    cluster_end = cluster_start + cluster_size
    
    # Create a cluster with specific characteristics
    cluster_bid = round(random.uniform(1.0, 1.8), 2)  # Ensure minimum bid is at least 1.0
    cluster_impression_base = random.randint(1500, 4500)
    cluster_budget_base = random.randint(150, 450)
    
    for j in range(cluster_start, cluster_end):
        variation = random.uniform(0.8, 1.2)  # 20% variation
        bid_value = round(cluster_bid * variation, 2)
        data['Bid'][j] = max(1, bid_value)  # Clamp bid value to a minimum of 1
        data['Minimum_Impressions'][j] = int(cluster_impression_base * variation)
        data['Budget'][j] = round(cluster_budget_base * variation, 1)

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('advertiser_data_10k.csv', index=False)

# Print the first few rows to verify
print(df.head(10))

# Count edge cases
print(f"\nEntries with minimum bid (1): {len(df[df['Bid'] == 1])}")
print(f"Entries with maximum bid (100): {len(df[df['Bid'] == 100])}")
print(f"Entries with minimum impressions (500): {len(df[df['Minimum_Impressions'] == 500])}")
print(f"Entries with maximum impressions (10000): {len(df[df['Minimum_Impressions'] == 10000])}")
print(f"Entries with minimum performance (0.0): {len(df[df['Performance'] == 0.0])}")
print(f"Entries with maximum performance (1.0): {len(df[df['Performance'] == 1.0])}")
print(f"Entries with minimum budget (10000): {len(df[df['Budget'] == 10000])}")
print(f"Entries with maximum budget (25000): {len(df[df['Budget'] == 25000])}")
print(f"Entries with minimum reward (10000): {len(df[df['Reward'] == 10000])}")
print(f"Entries with maximum reward (25000): {len(df[df['Reward'] == 25000])}")

# Verify that all bid values are at least 1
if (df['Bid'] < 1).any():
    print("There are still invalid bid values.")
else:
    print("All bid values are valid (no values below 1).")

# Print basic statistics
print("\nBasic Statistics:")
print(df.describe())