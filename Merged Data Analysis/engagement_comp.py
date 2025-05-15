#!/usr/bin/env python3
"""
ENGAGEMENT COMPARISON  ·  Russia–Ukraine Twitter dataset
--------------------------------------------------------
• Loads tweets_clean.parquet
• Keeps 2022-01-24 → 2022-03-06
• Computes mean / median / 95-th-pct likes, RTs, replies, quotes
  per [day, query]
• Saves  engagement_daily.csv  (+ pre/post table)
"""

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
FILE   = Path("Data/tweets_clean.parquet")
OUTCSV = Path("engagement_daily.csv")
START, END = "2022-01-24", "2022-03-06"
INVASION   = "2022-02-24"

print("📥  Reading", FILE)
df = pd.read_parquet(FILE)

# ------------------------------------------------------------------
# 1 ·  WINDOW FILTER
# ------------------------------------------------------------------
df = df.loc[(df["date_parsed"] >= START) & (df["date_parsed"] <= END)].copy()
df["date_parsed"] = pd.to_datetime(df["date_parsed"]).dt.tz_localize(None)
df["day"] = df["date_parsed"].dt.floor("d")
print(f"🗓️  Rows in window: {len(df):,}")

# ------------------------------------------------------------------
# 2 ·  ENSURE NUMERIC ENGAGEMENT COLUMNS  ← *** NEW ***
# ------------------------------------------------------------------
eng_cols = ["likeCount", "retweetCount", "replyCount", "quoteCount"]
for col in eng_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")   # strings → NaN → float

# optional: drop rows where *all* engagement fields are NaN
df = df.dropna(subset=eng_cols, how="all")

# ------------------------------------------------------------------
# 3 ·  AGGREGATE
# ------------------------------------------------------------------
def pct95(x): return x.quantile(0.95)

agg_map = {c: ["mean", "median", pct95] for c in eng_cols}

daily = (
    df.groupby(["day", "query"], observed=True)
      .agg(agg_map)
      .reset_index()
)

daily.columns = (
    ["day", "query"] + [f"{m}_{s}" for m, s in daily.columns[2:]]
)
print("✅  Aggregated rows:", len(daily))
daily.to_csv(OUTCSV, index=False)
print("💾  Saved →", OUTCSV)

# ------------------------------------------------------------------
# 4 ·  PRE / POST-INVASION SUMMARY  (optional)
# ------------------------------------------------------------------
summary = (
    df.assign(period = df["day"] < INVASION)      # True = pre
      .groupby(["period", "query"])
      .agg(agg_map)
      .reset_index()
)
summary["period"] = summary["period"].map({True: "pre", False: "post"})
summary.columns = (
    ["period", "query"] + [f"{m}_{s}" for m, s in summary.columns[2:]]
)
summary.to_csv("engagement_pre_post.csv", index=False)
print("💾  Saved → engagement_pre_post.csv")
