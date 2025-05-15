#!/usr/bin/env python3
"""
ATTENTION CURVE · Russia-Ukraine invasion Twitter dataset
---------------------------------------------------------
Loads tweets_clean.parquet
Builds daily tweet-volume timeline (optionally one trace per query)
Annotates key events
"""

import pandas as pd
import matplotlib.pyplot as plt

FILE = "Data/tweets_clean.parquet"   #  ← faster, clean
FIG  = "attention_curve.png"
BY_QUERY = True                      # False → single total curve

# ------------------------------------------------------------------ #
# 1 · LOAD                                                           #
# ------------------------------------------------------------------ #
print("📥  Reading", FILE)
df = pd.read_parquet("Data/tweets_clean.parquet")

# keep only war-window rows
mask = (df["date_parsed"] >= "2022-01-24") & (df["date_parsed"] <= "2022-03-06")
df = df.loc[mask].copy()
print("📊 rows in window:", len(df))


# Use the already-parsed column from the cleaner
if "date_parsed" not in df.columns:
    raise SystemExit("❌ date_parsed column missing – run the merge-clean script first")

df["date_parsed"] = pd.to_datetime(df["date_parsed"], errors="coerce")
df = df.dropna(subset=["date_parsed"])
df["date_parsed"] = df["date_parsed"].dt.tz_localize(None)   # strip TZ
df["day"] = df["date_parsed"].dt.floor("d")

print("🗓️  Date span:",
      df["date_parsed"].min().date(), "→", df["date_parsed"].max().date())

df["day"] = df["date_parsed"].dt.floor("d")
daily_tot = df.groupby("day").size()
print("\nSample daily counts:\n", daily_tot.head(10))
# ------------------------------------------------------------------ #
# 2 · DAILY COUNTS                                                   #
# ------------------------------------------------------------------ #
if BY_QUERY:
    daily = (
        df.groupby(["day", "query"])
          .size()
          .unstack(fill_value=0)
    )
else:
    daily = df.groupby("day").size().to_frame("Tweets")

# ------------------------------------------------------------------ #
# 3 · PLOT                                                           #
# ------------------------------------------------------------------ #
plt.figure(figsize=(14, 6))

if BY_QUERY:
    for col in daily.columns:
        plt.plot(daily.index, daily[col],
                 lw=2, alpha=.8, label=col.replace("_", " "))
else:
    plt.plot(daily.index, daily["Tweets"], lw=2, color="tab:blue")

plt.title("Twitter Attention Around Russia’s Invasion of Ukraine (Daily Volume)",
          fontsize=14)
plt.xlabel("Date")

# ----- choose y-label units -------
plt.ylabel("Tweets per day in Hundreds")         
#       plt.gca().set_ylim(bottom=0)
#       plt.gca().yaxis.set_major_formatter(
#           plt.FuncFormatter(lambda x, pos: f"{x/1_000:.0f}")
#       )

plt.xticks(rotation=45)

# ---- annotate key events -----------------------------------------
events = {
    "2022-02-21": "Recognises\nDNR & LNR",
    "2022-02-24": "Full-scale\ninvasion",
    "2022-02-28": "Ukraine → EU",
    "2022-03-02": "UN GA vote",
    "2022-03-05": "Global\nprotests"
}
for d, label in events.items():
    x = pd.to_datetime(d)
    plt.axvline(x, color="red", ls="--", lw=1)
    plt.text(x, plt.ylim()[1]*0.96, label,
             rotation=90, color="red",
             va="top", ha="right", fontsize=8)

plt.grid(alpha=.3)
if BY_QUERY:
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)

plt.tight_layout()
plt.savefig(FIG, dpi=300)
plt.show()
print("✅  Figure saved ➜", FIG)
