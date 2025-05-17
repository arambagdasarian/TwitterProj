#!/usr/bin/env python3
"""
simple_stats.py
---------------
Reads the eight raw CSVs, prints / saves a one-table summary.

Outputs
-------
simple_summary.tsv   – per-file row + combined totals
"""

import pandas as pd, numpy as np
from pathlib import Path

CSV_PATHS = [
    "Data/Russia_invade.csv",
    "Data/Russian_border_Ukraine.csv",
    "Data/Russian_troops.csv",
    "Data/StandWithUkraine.csv",
    "Data/Ukraine_border.csv",
    "Data/Ukraine_nato.csv",
    "Data/Ukraine_troops.csv",
    "Data/Ukraine_war.csv",
]

ENG_COLS = ["likeCount", "retweetCount"]
DATE_COL = "date"

rows = []

for p in CSV_PATHS:
    name = Path(p).stem
    try:
        df = pd.read_csv(
            p,
            engine="python",   # tolerant
            quoting=3,
            on_bad_lines="skip"
        )
    except Exception as e:
        print(f"⚠️  {name}: could not read – {e}")
        continue

    # numeric coercion
    for col in ENG_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # date parse (ignore problematic TZ strings)
    if DATE_COL in df.columns:
        df["date_parsed"] = pd.to_datetime(df[DATE_COL], errors="coerce", utc=True)
        df = df.dropna(subset=["date_parsed"])
    else:
        df["date_parsed"] = pd.NaT

    if df.empty:
        print(f"⚠️  {name}: no valid rows after cleaning.")
        continue

    row = {
        "file"        : name,
        "tweets"      : len(df),
        "unique_users": df["user"].nunique() if "user" in df.columns else np.nan,
        "first_date"  : df["date_parsed"].min().date(),
        "last_date"   : df["date_parsed"].max().date(),
        "mean_likes"  : df["likeCount"].mean(skipna=True) if "likeCount" in df.columns else np.nan,
        "median_likes": df["likeCount"].median(skipna=True) if "likeCount" in df.columns else np.nan,
        "mean_rts"    : df["retweetCount"].mean(skipna=True) if "retweetCount" in df.columns else np.nan,
        "median_rts"  : df["retweetCount"].median(skipna=True) if "retweetCount" in df.columns else np.nan,
    }
    rows.append(row)
    print(row)

# ---------- combined row ------------------------------------------
if rows:
    full = pd.concat([pd.read_csv(p, engine="python", quoting=3, on_bad_lines="skip")
                      for p, r in zip(CSV_PATHS, rows)], ignore_index=True)

    for col in ENG_COLS:
        if col in full.columns:
            full[col] = pd.to_numeric(full[col], errors="coerce")

    full["date_parsed"] = pd.to_datetime(full[DATE_COL], errors="coerce", utc=True)

    combined = {
        "file"        : "ALL",
        "tweets"      : len(full),
        "unique_users": full["user"].nunique() if "user" in full.columns else np.nan,
        "first_date"  : full["date_parsed"].min().date(),
        "last_date"   : full["date_parsed"].max().date(),
        "mean_likes"  : full["likeCount"].mean(skipna=True) if "likeCount" in full.columns else np.nan,
        "median_likes": full["likeCount"].median(skipna=True) if "likeCount" in full.columns else np.nan,
        "mean_rts"    : full["retweetCount"].mean(skipna=True) if "retweetCount" in full.columns else np.nan,
        "median_rts"  : full["retweetCount"].median(skipna=True) if "retweetCount" in full.columns else np.nan,
    }
    rows.append(combined)
    print("\nCombined:", combined)

# ---------- save ---------------------------------------------------
pd.DataFrame(rows).to_csv("simple_summary.tsv", sep="\t", index=False)
print("\n✅  Summary saved → simple_summary.tsv")

