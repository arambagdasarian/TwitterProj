import pandas as pd
import ast

# Load the CSV
df = pd.read_csv("Russia_invade.csv")

# Fill NA in 'content' just in case
df['content'] = df['content'].fillna("")

# If you have these columns, great. Otherwise, create them as None
if 'inReplyToTweetId' not in df.columns:
    df['inReplyToTweetId'] = None
if 'quotedTweet' not in df.columns:
    df['quotedTweet'] = None

# Categorize tweet type
def classify_tweet(row):
    content = str(row['content'])
    if content.startswith("RT @"):
        return "retweet"
    elif pd.notna(row['inReplyToTweetId']):
        return "reply"
    elif pd.notna(row['quotedTweet']):
        return "quote"
    else:
        return "tweet"

df['tweet_type'] = df.apply(classify_tweet, axis=1)

# Count each type
tweet_counts = df['tweet_type'].value_counts()

# Print result
print("Tweet Type Breakdown:")
print(tweet_counts)

