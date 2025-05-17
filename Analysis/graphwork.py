
import pandas as pd, ast, re, itertools, matplotlib.pyplot as plt
from collections import Counter

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

TOP_N     = 10      # chart 10 pairs
MIN_PAIR  = 3       # co-mention threshold
OUT_PNG   = "top_pairs_bar.png"

# pairs to drop  (use lowercase, no '#', order-independent)
DROP_PAIRS = {
    frozenset(("ptid", "pup")),
    frozenset(("nowar", "opl")),
    frozenset(("jinek", "opl")),
    frozenset(("jinek", "nowar")),
    frozenset(("maga", "nra")),
    frozenset(("2a",   "nra")),
    frozenset(("2a",   "maga")),
    frozenset(("bluetsunami2022", "theresistance")),
    frozenset(("bluetsunami2022", "fbr")),
    frozenset(("fjb", "letsgobrandon")),
}




tag_re    = re.compile(r"#(\w{2,})")
bad_tokens= {"none", "true", "false", "nan"}

def extract_tags(cell) -> list[str]:
    if pd.isna(cell): return []
    s = str(cell).strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            lst = ast.literal_eval(s)
            return [t.lower() for t in lst if isinstance(t, str)]
        except Exception:
            pass
    return [m.lower() for m in tag_re.findall(s)]




pair_counts = Counter()

for path in CSV_PATHS:
    for chunk in pd.read_csv(path, usecols=["hashtags"],
                             engine="python", quoting=3,
                             on_bad_lines="skip", chunksize=60_000):
        for cell in chunk["hashtags"]:
            tags = sorted({t for t in extract_tags(cell) if t not in bad_tokens})
            if len(tags) < 2: continue
            for a, b in itertools.combinations(tags, 2):
                key = frozenset((a, b))
                if key in DROP_PAIRS:      # skip unwanted combos
                    continue
                pair_counts[key] += 1




pair_counts = {p: c for p, c in pair_counts.items() if c >= MIN_PAIR}
top_pairs   = Counter(pair_counts).most_common(TOP_N)
if not top_pairs:
    raise SystemExit("No pairs left after filtering – relax thresholds.")

pairs, counts = zip(*top_pairs)
labels = [f"#{tuple(p)[0]}  +  #{tuple(p)[1]}" for p in pairs]




# plotting

plt.figure(figsize=(10, 6))
bars = plt.barh(range(len(labels)), counts, color="steelblue")
plt.yticks(range(len(labels)), labels, fontsize=9)
plt.xlabel("Tweets containing both hashtags")
plt.title(f"Top {TOP_N} co-mentioned hashtag pairs")
plt.gca().invert_yaxis()

for bar, cnt in zip(bars, counts):
    plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
             f"{cnt:,}", va="center", fontsize=8)

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300)
plt.show()
print("✅  saved clean chart →", OUT_PNG)
