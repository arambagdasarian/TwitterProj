
"""
• totals & time span
• peak-day and pre/post means
• engagement (overall + by query)
• language mix
• hashtag & account leaders
• extra behavioural metrics (original-tweet share, media share, etc.)
"""

import pandas as pd, numpy as np, re, ast
from dateutil import parser
from pathlib import Path
from collections import Counter, defaultdict

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
INVASION_DAY = pd.Timestamp("2022-02-24", tz="UTC")   # reference split


def coerce_num(series):
    return pd.to_numeric(series, errors="coerce")

tag_re = re.compile(r"#(\w{2,})")
def tag_list(cell):
    if pd.isna(cell): return []
    s = str(cell)
    if s.startswith("[") and s.endswith("]"):
        try:
            return [t.lower() for t in ast.literal_eval(s)]
        except Exception:
            pass
    return [m.lower() for m in tag_re.findall(s)]

def parse_date(x):
    try:
        return parser.parse(str(x)).astimezone(pd.Timestamp.utcnow().tz)
    except Exception:
        return pd.NaT

# containers 
frames              = []
pair_counter        = Counter()
hashtag_counter     = Counter()
user_hour_counts    = defaultdict(lambda: defaultdict(int))  # {user: {hour:count}}
lang_counter        = Counter()

for path in CSV_PATHS:
    df = pd.read_csv(
        path,
        engine="python", quoting=3, on_bad_lines="skip"
    )

    # core fields 
    df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
    df = df.dropna(subset=["date_parsed"])
    df["day"]  = df["date_parsed"].dt.floor("d")
    df["hour"] = df["date_parsed"].dt.floor("h")

    for col in ["likeCount", "retweetCount", "replyCount", "quoteCount"]:
        if col in df.columns:
            df[col] = coerce_num(df[col])

    frames.append(df)

    # hashtag tallies 
    tags_series = df["hashtags"].dropna().map(tag_list)
    hashtag_counter.update(np.concatenate(tags_series.values))
    for tags in tags_series:
        tags = sorted(set(tags))
        if len(tags) < 2: continue
        for a, b in itertools.combinations(tags, 2):
            pair_counter[(a, b)] += 1

    # language 
    if "lang" in df.columns:
        lang_counter.update(df["lang"].dropna().str.lower())

    # hourly streak prep 
    invasion_slice = df[df["date_parsed"].dt.date == INVASION_DAY.date()]
    for _, row in invasion_slice.iterrows():
        user_hour_counts[row["user"]][row["hour"]] += 1

full = pd.concat(frames, ignore_index=True)

# 1. overall scale
total_tweets   = len(full)
unique_accounts= full["user"].nunique()
time_start, time_end = full["date_parsed"].min().date(), full["date_parsed"].max().date()
print(f"Time span: {time_start} – {time_end}  ({(time_end - time_start).days+1} days)")
print(f"Tweets: {total_tweets:,}   •   Unique accounts: {unique_accounts:,}\n")

# 2. temporal dynamics
daily_counts = full.groupby("day").size()
peak_day = daily_counts.idxmax()
print(f"Peak day: {peak_day}  →  {daily_counts.max():,} tweets")

pre  = full[full["date_parsed"] <  INVASION_DAY]
post = full[full["date_parsed"] >= INVASION_DAY]
print(f"Mean/median tweets per day  •  pre-invasion: "
      f"{pre.groupby('day').size().mean():.0f} / {pre.groupby('day').size().median():.0f}   ·   "
      f"post-invasion: {post.groupby('day').size().mean():.0f} / {post.groupby('day').size().median():.0f}\n")

# 3. engagement overall 
likes = full["likeCount"].dropna()
rts   = full["retweetCount"].dropna()
print("Overall engagement:")
print(f"  Likes   mean {likes.mean():.1f}  median {likes.median():.0f}  95-pct {likes.quantile(0.95):.0f}")
print(f"  RTs     mean {rts.mean():.1f}  median {rts.median():.0f}  95-pct {rts.quantile(0.95):.0f}\n")

# 4. engagement by query
if "query" in full.columns:
    gb = full.groupby("query")
    for q, sub in gb:
        print(f"{q:20s}  median likes {sub['likeCount'].median():.0f}  ·  median RTs {sub['retweetCount'].median():.0f}")
    print()

# 5. language mix 
total_lang = lang_counter.total()
for lang, cnt in lang_counter.most_common(8):
    print(f"Lang {lang:3s}: {cnt/total_lang:5.1%}  ({cnt:,})")
print()

# 6. top hashtags & accounts 
print("Top 5 hashtags:")
for tag, cnt in hashtag_counter.most_common(5):
    print(f"  #{tag:<15s} {cnt:,}")
print()

print("Top accounts by tweet count:")
top_users = full.groupby("user").agg(tweets=("id","size"), mean_likes=("likeCount","mean"))
for user, row in top_users.sort_values("tweets", ascending=False).head(10).iterrows():
    print(f" @{user:<20s} {row['tweets']:4d} tweets   mean likes {row['mean_likes']:.0f}")
print()

# 7. extra behavioural metrics 
orig_share = 100 * (full["retweetedTweet"].isna().mean()) if "retweetedTweet" in full.columns else np.nan
reply_share= 100 * (full["inReplyToTweetId"].notna().mean()) if "inReplyToTweetId" in full.columns else np.nan
media_share= 100 * (full["media"].notna().mean()) if "media" in full.columns else np.nan
hashtags_per_tweet = full["hashtags"].map(lambda x: len(tag_list(x))).mean()

print(f"Original-tweet share: {orig_share:.1f}%")
print(f"Replies share       : {reply_share:.1f}%")
print(f"Media share         : {media_share:.1f}%")
print(f"Avg hashtags/tweet  : {hashtags_per_tweet:.2f}\n")

most_common_pair, pair_cnt = pair_counter.most_common(1)[0]
print(f"Most common pair    : #{most_common_pair[0]} + #{most_common_pair[1]}  →  {pair_cnt:,} tweets")

# fastest-rising hashtag (#StopPutinNow as example)
stop_counts = full.explode("hashtags")["hashtags"].map(lambda x: str(x).lower()).value_counts()
stop_daily  = full[full["hashtags"].str.contains("StopPutinNow", case=False, na=False)].groupby("day").size()
if not stop_daily.empty:
    rise = stop_daily.loc[stop_daily.index>=INVASION_DAY.date()].max()
    pre_baseline = stop_daily.loc[stop_daily.index<INVASION_DAY.date()].mean()
    print(f"'#StopPutinNow' rise: {pre_baseline:.0f} → {rise} tweets/day\n")

# 95th percentile replies
replies = full["replyCount"].dropna()
print(f"95-th percentile replies: {replies.quantile(0.95):.0f}")

# longest hourly streak
longest_user = max(user_hour_counts.items(), key=lambda kv: len(kv[1])) if user_hour_counts else ("", {})
print(f"Longest hourly streak on 24 Feb: @{longest_user[0]} with {len(longest_user[1])} consecutive hours")

# hashtag diversity jump
diversity = full.groupby("day")["hashtags"].apply(lambda col: len(set(np.concatenate(col.dropna().map(tag_list).values))))
if not diversity.empty:
    d_pre  = diversity.loc[diversity.index < INVASION_DAY.date()].median()
    d_post = diversity.loc[diversity.index >= INVASION_DAY.date()].max()
    print(f"Hashtag diversity: median {d_pre:.0f} (pre)  →  {d_post:.0f} unique tags (25 Feb)")
