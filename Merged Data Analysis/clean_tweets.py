import pandas as pd
import csv
import re

RAW  = "Data/tweets_merged_dedup.csv"
CLEAN_CSV = "tweets_clean.csv"
CLEAN_PQ  = "tweets_clean.parquet"

# -------- helper to scrub newlines inside text columns ----------
newline_re = re.compile(r'[\r\n]+')

def scrub_text(val):
    if isinstance(val, str):
        val = newline_re.sub(' ', val)     # flatten \r\n to space
        val = val.replace('"', "'")        # replace bare quotes
    return val

# -------- 1 · read in tolerant streaming mode -------------------
chunks = []
for chunk in pd.read_csv(
        RAW,
        engine="python",
        quoting=csv.QUOTE_NONE,
        on_bad_lines="skip",
        chunksize=100_000):

    
    # scrub text columns on the fly  ------------------------------
    text_cols = ["content", "renderedContent"]
    for col in text_cols:
        if col in chunk.columns:
            chunk[col] = chunk[col].map(scrub_text)
    
    chunks.append(chunk)

df = pd.concat(chunks, ignore_index=True)
print("✅  Loaded & scrubbed:", len(df), "rows")

# -------- 2 · save clean CSV ------------------------------------
df.to_csv(
    CLEAN_CSV,
    index=False,
    quoting=csv.QUOTE_MINIMAL,
    escapechar="\\"
)
print("💾  Wrote clean CSV →", CLEAN_CSV)

# -------- 3 · optional Parquet ----------------------------------
df.to_parquet(CLEAN_PQ, index=False)
print("💾  Wrote Parquet     →", CLEAN_PQ)
