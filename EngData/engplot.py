#!/usr/bin/env python3
"""
plot_engagement.py
------------------
Visualises engagement metrics produced by build_engagement_tables.py

Outputs
-------
daily_likes.png
daily_retweets.png
prepost_likes_bar.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------------------------------------------------
# 1 ·  LOAD CLEAN TABLES
# ------------------------------------------------------------------
DAILY   = Path("EngData/engagement_daily.csv")     # day × query × stats
PREPOST = Path("EngData/engagement_pre_post.csv")  # pre/post × query × stats

daily   = pd.read_csv(DAILY,   parse_dates=["day"])
prepost = pd.read_csv(PREPOST)

# – choose a legend order that reads nicely –
query_order = [
    "StandWithUkraine",
    "Ukraine_war",
    "Ukraine_troops",
    "Ukraine_border",
    "Ukraine_nato",
    "Russia_invade",
    "Russian_troops",
    "Russian_border_Ukraine"
]
daily["query"]   = pd.Categorical(daily["query"], categories=query_order, ordered=True)
prepost["query"] = pd.Categorical(prepost["query"], categories=query_order, ordered=True)

# ------------------------------------------------------------------
# 2 ·  GUARANTEE NUMERIC METRICS
# ------------------------------------------------------------------
for col in daily.columns:
    if col.endswith("_mean"):
        daily[col] = pd.to_numeric(daily[col], errors="coerce")

if {"likeCount_mean", "period"}.issubset(prepost.columns):
    prepost["likeCount_mean"] = pd.to_numeric(prepost["likeCount_mean"], errors="coerce")

plt.style.use("ggplot")

# ------------------------------------------------------------------
# 3 ·  FUNCTION TO PLOT A DAILY METRIC
# ------------------------------------------------------------------
def plot_daily(metric_root: str, ylabel: str, outpng: str):
    metric = f"{metric_root}_mean"
    fig, ax = plt.subplots(figsize=(12, 6))
    any_line = False

    for q, sub in daily.groupby("query", observed=True):
        mask = sub[metric].notna()
        if mask.sum() < 2:        # fewer than 2 valid points? skip
            continue
        ax.plot(sub.loc[mask, "day"],
                sub.loc[mask, metric],
                lw=2, label=q.replace("_", " "))
        any_line = True

    if not any_line:
        print(f"⚠️  No data for {metric_root}; {outpng} skipped.")
        plt.close(fig)
        return

    ax.set_title(f"Daily mean {ylabel} per tweet")
    ax.set_xlabel("Date"); ax.set_ylabel(f"Mean {ylabel}")
    ax.legend(bbox_to_anchor=(1.02,1), loc="upper left", frameon=False)
    fig.tight_layout(); fig.savefig(outpng, dpi=300); plt.close()
    print("✅  saved", outpng)

plot_daily("likeCount",    "likes",    "daily_likes.png")
plot_daily("retweetCount", "retweets", "daily_retweets.png")

# ------------------------------------------------------------------
# 4 ·  PRE vs POST BAR CHART  (% change in mean likes)
# ------------------------------------------------------------------
if {"query", "period", "likeCount_mean"}.issubset(prepost.columns):
    pivot = (prepost
             .pivot(index="query", columns="period", values="likeCount_mean")
             .reindex(query_order))

    pivot["pct_change"] = (pivot["post"] - pivot["pre"]) / pivot["pre"] * 100
    pivot = pivot.dropna(subset=["pct_change"])

    if pivot.empty:
        print("⚠️  No finite data for pre/post likes → bar plot skipped.")
    else:
        fig, ax = plt.subplots(figsize=(9, 6))
        pivot["pct_change"].plot(kind="barh", ax=ax, color="steelblue")
        ax.set_xlabel("% change in mean likes (post 24 Feb)")
        ax.set_title("Like growth after invasion, by hashtag")
        for i, v in enumerate(pivot["pct_change"]):
            ax.text(v + 0.5, i, f"{v:.1f}%", va="center")
        fig.tight_layout(); fig.savefig("prepost_likes_bar.png", dpi=300); plt.close()
        print("✅  saved prepost_likes_bar.png")
else:
    print("⚠️  Required columns missing for pre/post bar plot.")
