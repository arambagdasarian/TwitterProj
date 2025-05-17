
import pandas as pd, re, string
from pathlib import Path
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

FILE = Path("Data/tweets_clean.parquet")   
OUT  = Path("tweets_wordcloud.png")

df = pd.read_parquet(FILE)
if "content" not in df.columns:
    raise SystemExit("❌  'content' column missing.")
texts = df["content"].dropna().astype(str)


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

def filter_tokens(text):
    words = text.split()
    return " ".join([word for word in words if word.isalpha() and len(word) > 2])

filtered_texts = cleaned_texts.map(filter_tokens)

extra_stops = {
    "rt", "amp", "https", "co", "ukraine", "russia", "war", "troops",
    "standwithukraine", "invasion", "people", "one", "get", "say"
}
stops = STOPWORDS.union(extra_stops)


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
