import pandas as pd
import matplotlib.pyplot as plt

# === Load CSVs ===
df_russia = pd.read_csv('Russia_invade.csv')
df_ukraine = pd.read_csv('StandWithUkraine.csv')

# === Parse tweet date column ===
df_russia['date'] = pd.to_datetime(df_russia['date'], errors='coerce')
df_ukraine['date'] = pd.to_datetime(df_ukraine['date'], errors='coerce')

# === Drop rows with missing dates ===
df_russia = df_russia.dropna(subset=['date'])
df_ukraine = df_ukraine.dropna(subset=['date'])

# === Group by day and count tweets ===
russia_tweet_volume = df_russia['date'].dt.date.value_counts().sort_index()
ukraine_tweet_volume = df_ukraine['date'].dt.date.value_counts().sort_index()

# === Plot ===
plt.figure(figsize=(14, 6))
plt.plot(russia_tweet_volume.index, russia_tweet_volume.values, label='Russia-related Tweets', marker='o')
plt.plot(ukraine_tweet_volume.index, ukraine_tweet_volume.values, label='Ukraine-related Tweets', marker='o')
plt.axvline(pd.to_datetime('2022-02-24'), color='red', linestyle='--', label='Invasion Day (Feb 24)')
plt.title('Tweet Volume Over Time (Russia vs Ukraine Keywords)')
plt.xlabel('Date')
plt.ylabel('Number of Tweets')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
