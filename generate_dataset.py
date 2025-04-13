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
    'Minimum_Impressions': np.random.randint(1000, 5001, num_entries),
    'Budget': np.round(np.random.uniform(100.0, 500.0, num_entries), 1),
    'Bid': np.round(np.random.uniform(0.1, 2.0, num_entries), 2),
    'Reward': [],
    'Performance': np.round(np.clip(np.random.normal(0.6, 0.15, num_entries), 0, 1), 2)
}

# Calculate Reward based on logic: Minimum_Impressions × reward_per_impression
for i in range(num_entries):
    reward_per_impression = round(random.uniform(0.05, 0.30), 2)
    reward = round(data['Minimum_Impressions'][i] * reward_per_impression, 1)
    data['Reward'].append(reward)

# Scale up the edge cases proportionally (10x)
# Edge case 1: Minimum bids (0.1)
min_bid_indices = random.sample(range(num_entries), 200)
for idx in min_bid_indices:
    data['Bid'][idx] = 0.1

# Edge case 2: Maximum bids (2.0)
max_bid_indices = random.sample(range(num_entries), 200)
for idx in max_bid_indices:
    data['Bid'][idx] = 2.0

# Edge case 3: Minimum impressions (exactly 1000)
min_imp_indices = random.sample(range(num_entries), 300)
for idx in min_imp_indices:
    data['Minimum_Impressions'][idx] = 1000

# Edge case 4: Maximum impressions (exactly 5000)
max_imp_indices = random.sample(range(num_entries), 300)
for idx in max_imp_indices:
    data['Minimum_Impressions'][idx] = 5000

# Edge case 5: Minimum budget (exactly 100.0)
min_budget_indices = random.sample(range(num_entries), 250)
for idx in min_budget_indices:
    data['Budget'][idx] = 100.0

# Edge case 6: Maximum budget (exactly 500.0)
max_budget_indices = random.sample(range(num_entries), 250)
for idx in max_budget_indices:
    data['Budget'][idx] = 500.0

# Edge case 7: Extreme performance values (0.0 and 1.0)
min_perf_indices = random.sample(range(num_entries), 150)
for idx in min_perf_indices:
    data['Performance'][idx] = 0.0

max_perf_indices = random.sample(range(num_entries), 150)
for idx in max_perf_indices:
    data['Performance'][idx] = 1.0

# Edge case 8: Minimum reward_per_impression (exactly 0.05)
min_reward_indices = random.sample(range(num_entries), 200)
for idx in min_reward_indices:
    reward_per_impression = 0.05
    data['Reward'][idx] = round(data['Minimum_Impressions'][idx] * reward_per_impression, 1)

# Edge case 9: Maximum reward_per_impression (exactly 0.30)
max_reward_indices = random.sample(range(num_entries), 200)
for idx in max_reward_indices:
    reward_per_impression = 0.30
    data['Reward'][idx] = round(data['Minimum_Impressions'][idx] * reward_per_impression, 1)

# Additional variations to increase variability
# Add some high-variance clusters
for i in range(5):
    cluster_size = random.randint(50, 150)
    cluster_start = random.randint(0, num_entries - cluster_size)
    cluster_end = cluster_start + cluster_size
    
    # Create a cluster with specific characteristics
    cluster_bid = round(random.uniform(0.3, 1.8), 2)
    cluster_impression_base = random.randint(1500, 4500)
    cluster_budget_base = random.randint(150, 450)
    
    for j in range(cluster_start, cluster_end):
        variation = random.uniform(0.8, 1.2)  # 20% variation
        data['Bid'][j] = round(cluster_bid * variation, 2)
        data['Minimum_Impressions'][j] = int(cluster_impression_base * variation)
        data['Budget'][j] = round(cluster_budget_base * variation, 1)

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('advertiser_data_10k.csv', index=False)

# Print the first few rows to verify
print(df.head(10))

# Count edge cases
print(f"\nEntries with minimum bid (0.1): {len(df[df['Bid'] == 0.1])}")
print(f"Entries with maximum bid (2.0): {len(df[df['Bid'] == 2.0])}")
print(f"Entries with minimum impressions (1000): {len(df[df['Minimum_Impressions'] == 1000])}")
print(f"Entries with maximum impressions (5000): {len(df[df['Minimum_Impressions'] == 5000])}")
print(f"Entries with minimum performance (0.0): {len(df[df['Performance'] == 0.0])}")
print(f"Entries with maximum performance (1.0): {len(df[df['Performance'] == 1.0])}")
print(f"Entries with minimum budget (100.0): {len(df[df['Budget'] == 100.0])}")
print(f"Entries with maximum budget (500.0): {len(df[df['Budget'] == 500.0])}")

# Print basic statistics
print("\nBasic Statistics:")
print(df.describe())