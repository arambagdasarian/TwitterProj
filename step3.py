import pandas as pd
import matplotlib.pyplot as plt

# === Load data
df_russia = pd.read_csv('Russia_invade.csv')
df_ukraine = pd.read_csv('StandWithUkraine.csv')

# === Define tweet type
def classify_tweet(row):
    if row['content'].startswith('RT @') or row['renderedContent'].startswith('RT @'):
        return 'retweet'
    elif row['replyCount'] > 0:
        return 'reply'
    else:
        return 'original'

df_russia['tweet_type'] = df_russia.apply(classify_tweet, axis=1)
df_ukraine['tweet_type'] = df_ukraine.apply(classify_tweet, axis=1)

# === Count tweet types
russia_counts = df_russia['tweet_type'].value_counts(normalize=True) * 100
ukraine_counts = df_ukraine['tweet_type'].value_counts(normalize=True) * 100

# === Plot side-by-side
labels = ['original', 'retweet', 'reply']
russia_vals = [russia_counts.get(t, 0) for t in labels]
ukraine_vals = [ukraine_counts.get(t, 0) for t in labels]

x = range(len(labels))
width = 0.35

plt.figure(figsize=(8, 5))
plt.bar(x, russia_vals, width, label='Russia-related')
plt.bar([p + width for p in x], ukraine_vals, width, label='Ukraine-related')
plt.xticks([p + width/2 for p in x], labels)
plt.ylabel('Percentage of Tweets')
plt.title('Tweet Type Breakdown')
plt.legend()
plt.grid(True, axis='y')
plt.tight_layout()
plt.show()
