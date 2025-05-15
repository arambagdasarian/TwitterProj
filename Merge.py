#!/usr/bin/env python3
"""
MERGE & CLEAN · Russia-Ukraine hashtag datasets
-----------------------------------------------
• Reads eight CSVs (paths hard-coded below)
• Adds 'query' column (file stem)
• Drops duplicate tweet IDs
• Scrubs text columns, fixes malformed dates
• Saves tweets_clean.csv  +  tweets_clean.parquet
"""

import pandas as pd
import os, csv, re
from datetime import datetime

# ------------------------------------------------------------------
# 1 ·  HARD-CODED CSV PATHS
# ------------------------------------------------------------------
csv_paths = [
    "Data/Russia_invade.csv",
    "Data/Russian_border_Ukraine.csv",
    "Data/Russian_troops.csv",
    "Data/StandWithUkraine.csv",
    "Data/Ukraine_border.csv",
    "Data/Ukraine_nato.csv",
    "Data/Ukraine_troops.csv",
    "Data/Ukraine_war.csv"
]

for p in csv_paths:
    if not os.path.exists(p):
        raise SystemExit(f"❌  File not found: {p}")
print("📂 Files to merge:\n   " + "\n   ".join(csv_paths))

# ------------------------------------------------------------------
# 2 ·  HELPERS
# ------------------------------------------------------------------
newline_re = re.compile(r'[\r\n]+')
iso_pat   = re.compile(
    r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\+\d{2}:?\d{2})?)"
)

def scrub_text(val: str) -> str:
    """Flatten embedded newlines and change double quotes to single."""
    if isinstance(val, str):
        val = newline_re.sub(' ', val)   # make one physical line
        val = val.replace('"', "'")
    return val

def extract_iso(text: str):
    """Pull first ISO-ish timestamp out of messy wrapper."""
    m = iso_pat.search(str(text))
    return m.group(1) if m else None

# ------------------------------------------------------------------
# 3 ·  LOAD, SCRUB, CONCAT
# ------------------------------------------------------------------
chunks = []
for path in csv_paths:
    print(f"→ Reading  {path}")
    for chunk in pd.read_csv(
        path,
        engine="python",           # tolerant parser
        quoting=csv.QUOTE_NONE,    # treat " as normal char
        on_bad_lines="skip",       # drop unrecoverable rows
        chunksize=100_000          # stream in 100k rows at a time
        ):
        chunk["query"] = os.path.splitext(os.path.basename(path))[0]

            # scrub text …
        ...

        # add source label
        chunk["query"] = os.path.splitext(os.path.basename(path))[0]

        # scrub text columns
        for col in ("content", "renderedContent"):
            if col in chunk.columns:
                chunk[col] = chunk[col].map(scrub_text)

        # extract & parse date
        chunk["iso_date"] = chunk["date"].map(extract_iso)
        chunk["date_parsed"] = pd.to_datetime(
            chunk["iso_date"], errors="coerce", utc=True
        )
        chunk["date_parsed"] = chunk["date_parsed"].dt.tz_convert(None)

        chunks.append(chunk)

df = pd.concat(chunks, ignore_index=True)
print(f"🔄  Combined rows before de-dup: {len(df):,}")

# ------------------------------------------------------------------
# 4 ·  DROP DUPLICATES ON TWEET ID
# ------------------------------------------------------------------
if "id" not in df.columns:
    raise SystemExit("❌ Column 'id' missing – can't de-duplicate.")
df = df.drop_duplicates(subset="id")
print(f"🗑️   Unique tweets after de-dup : {len(df):,}")

# ------------------------------------------------------------------
# 5 ·  FINAL COLUMN ORDER (optional)
# ------------------------------------------------------------------
primary_cols = [
    "id", "date_parsed", "query", "user", "content",
    "likeCount", "retweetCount", "replyCount", "quoteCount", "hashtags"
]
# keep any extras but move them to the right
ordered_cols = primary_cols + [c for c in df.columns if c not in primary_cols]
df = df[ordered_cols]

# ------------------------------------------------------------------
# 6 ·  SAVE CLEAN FILES
# ------------------------------------------------------------------
out_csv = "tweets_clean.csv"
out_pq  = "tweets_clean.parquet"
# ---------- make all object columns true strings -----------------
obj_cols = df.select_dtypes(include="object").columns
df[obj_cols] = df[obj_cols].fillna("").astype("string")

df.to_csv(out_csv, index=False, quoting=csv.QUOTE_MINIMAL, escapechar="\\")
df.to_parquet(out_pq, index=False)

print(f"✅  Clean CSV    → {out_csv}")
print(f"✅  Clean Parquet → {out_pq}")
