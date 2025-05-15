import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# 0)  Merge and de‑duplicate across **all** queries
# ------------------------------------------------------------------
file_paths = [
    'Data/Russia_invade.csv',
    'Data/Russian_border_Ukraine.csv',
    'Data/Russian_troops.csv',
    'Data/StandWithUkraine.csv',
    'Data/Ukraine_border.csv',
    'Data/Ukraine_nato.csv',
    'Data/Ukraine_troops.csv',
    'Data/Ukraine_war.csv'
]

# Load and combine all datasets
df_list = []
for path in file_paths:
    if os.path.exists(path):
        df = pd.read_csv(path)
        df['hashtag_source'] = path.replace('.csv', '')  # Tag by source
        df_list.append(df)
    else:
        print(f"File not found: {path}")

all_df = pd.concat(df_list, ignore_index=True)

#  ---- DROP DUPLICATES ON TWEET ID ----
before = len(all_df)
all_df = all_df.drop_duplicates(subset="id")
print(f"🗑️  Removed {before - len(all_df):,} duplicate rows "
      f"({before}  →  {len(all_df)}).")

# Parse dates (robust)
all_df["date"] = pd.to_datetime(all_df["date"], errors="coerce", utc=True)
all_df = all_df.dropna(subset=["date"])

# ------------------------------------------------------------------
# 1)  Choose the hashtag / query you want to illustrate
# ------------------------------------------------------------------
mask = all_df["hashtags"].str.contains("StandWithUkraine", case=False, na=False)
swu_df = all_df.loc[mask]

# ------------------------------------------------------------------
# 2)  Build daily counts  (sample, lower‑bound)
# ------------------------------------------------------------------
daily = (swu_df
         .groupby(swu_df["date"].dt.floor("d"))
         .size()
         .rename("tweet_count")
         .reset_index())

# ------------------------------------------------------------------
# 3)  Plot with a plateau‑warning annotation
# ------------------------------------------------------------------
plt.figure(figsize=(13, 6))
plt.plot(daily["date"].dt.date, daily["tweet_count"], marker="o", lw=2)
plt.axhline(5_000, color="grey", ls=":", alpha=.6)
plt.text(daily["date"].iloc[0], 5_000 + 150,
         "5 000   (sample cap per day per query)",
         color="grey", fontsize=9, va="bottom")

plt.title("#StandWithUkraine — tweet sample (cap = 5 000/day/query)")
plt.xlabel("Date")
plt.ylabel("Tweets in merged, de‑duplicated sample")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True)
plt.show()
