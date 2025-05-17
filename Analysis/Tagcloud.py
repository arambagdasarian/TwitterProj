#!/usr/bin/env python3
"""
WORD CLOUD  ·  Russia–Ukraine tweets
------------------------------------
• Reads tweets_clean.parquet
• Strips URLs, mentions, hashtags, punctuation
• Removes English stop-words + a few Twitter-specific tokens
• Generates tweets_wordcloud.png
"""

import pandas as pd, re, string
from pathlib import Path
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

FILE = Path("Data/tweets_clean.parquet")   # change if needed
OUT  = Path("tweets_wordcloud.png")

# ------------------------------------------------------------------
# 1 · LOAD TWEET TEXT
# ------------------------------------------------------------------
df = pd.read_parquet(FILE)
if "content" not in df.columns:
    raise SystemExit("❌  'content' column missing.")
texts = df["content"].dropna().astype(str)

# ------------------------------------------------------------------
# 2 · BASIC CLEANING
# ------------------------------------------------------------------
url_re     = re.compile(r"https?://\S+")
mention_re = re.compile(r"@\w+")
hashtag_re = re.compile(r"#\w+")
punct_tbl  = str.maketrans("", "", string.punctuation)

def clean(text):
    text = url_re.sub(" ", text)
    text = mention_re.sub(" ", text)
    text = hashtag_re.sub(" ", text)
    text = text.translate(punct_tbl)
    return text.lower()

cleaned_texts = texts.map(clean)

# Remove non-alphabetic and short words (e.g. "u", "i", "a")
def filter_tokens(text):
    words = text.split()
    return " ".join([word for word in words if word.isalpha() and len(word) > 2])

filtered_texts = cleaned_texts.map(filter_tokens)

# ------------------------------------------------------------------
# 3 · STOPWORDS
# ------------------------------------------------------------------
extra_stops = {
    "rt", "amp", "https", "co", "ukraine", "russia", "war", "troops",
    "standwithukraine", "invasion", "people", "one", "get", "say"
}
stops = STOPWORDS.union(extra_stops)

# ------------------------------------------------------------------
# 4 · BUILD WORD CLOUD
# ------------------------------------------------------------------
wc = WordCloud(
    width=1600,
    height=900,
    background_color="white",
    stopwords=stops,
    max_words=300,
    collocations=False
).generate(" ".join(filtered_texts))

plt.figure(figsize=(16, 9))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.tight_layout()
plt.savefig(OUT, dpi=300)
plt.show()

print("✅  Word cloud saved →", OUT)
