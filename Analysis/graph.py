#!/usr/bin/env python3
"""
CLEAN HASHTAG CO-OCCURRENCE NETWORK
-----------------------------------
* Reads eight CSVs (hard-coded paths)
* Uses only the **hashtags** column (safe reader)
* Keeps tweets with **≥2 hashtags**
* Counts co-occurrence  → edge weight
* Drops edges with weight < MIN_EDGE (default 3)
* Saves:
      hashtag_edges.csv    (edge list)
      hashtag_graph.gml    (for Gephi / Cytoscape)
      hashtag_graph.png    (spring preview, coloured by Louvain community)
"""

import pandas as pd, ast, re, itertools, networkx as nx
import matplotlib.pyplot as plt
import community as community_louvain          # pip install python-louvain
from collections import Counter
from pathlib import Path

# -------------------------------------------------- CONFIG ----------
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
MIN_EDGE  = 3          # keep only edges seen ≥3 times
TOP_PREVIEW = 150      # top-degree nodes to draw in PNG
# --------------------------------------------------------------------

comma_split = re.compile(r"[;, ]+")
strip_hash  = re.compile(r"^#")

def parse_hashtags(cell: str) -> list[str]:
    """Return list of cleaned hashtags from CSV cell."""
    if pd.isna(cell):                # missing field
        return []
    s = str(cell).strip()

    # literal list?
    if s.startswith("[") and s.endswith("]"):
        try:
            tags = ast.literal_eval(s)
            return [strip_hash.sub("", t).lower() for t in tags if t]
        except Exception:
            pass

    # raw tweet or CSV list
    tokens = comma_split.split(s)
    return [strip_hash.sub("", t).lower() for t in tokens if t.startswith("#") or t]

edge_ctr = Counter()
node_ctr = Counter()

for path in csv_paths:
    print("→", path)
    for chunk in pd.read_csv(path,
                             usecols=["hashtags"],
                             engine="python",
                             quoting=3,
                             on_bad_lines="skip",
                             chunksize=80_000):

        for tags in chunk["hashtags"]:
            tags = parse_hashtags(tags)
            if len(tags) < 2:
                continue
            tags = sorted(set(tags))
            node_ctr.update(tags)
            for a, b in itertools.combinations(tags, 2):
                edge_ctr[(a, b)] += 1

print(f"Unique hashtags: {len(node_ctr):,}")
print(f"All raw edges : {len(edge_ctr):,}")

# --------------- build graph with threshold ------------------------
G = nx.Graph()
for tag, freq in node_ctr.items():
    G.add_node(tag, freq=freq)

for (a, b), w in edge_ctr.items():
    if w >= MIN_EDGE:
        G.add_edge(a, b, weight=w)

print(f"Edges ≥{MIN_EDGE}: {G.number_of_edges():,}")
print(f"Nodes retained:  {G.number_of_nodes():,}")

if G.number_of_edges() == 0:
    raise SystemExit("No edges passed the MIN_EDGE threshold – lower MIN_EDGE.")

# --------------- save edge list + graph ----------------------------
pd.DataFrame(
    ((u, v, d["weight"]) for u, v, d in G.edges(data=True)),
    columns=["source", "target", "weight"]
).to_csv("hashtag_edges.csv", index=False)

nx.write_gml(G, "hashtag_graph.gml")
print("✅  Files written:  hashtag_edges.csv,  hashtag_graph.gml")

# --------------- Louvain communities for colouring -----------------
partition = community_louvain.best_partition(G, weight="weight")
nx.set_node_attributes(G, partition, "community")

# --------------- quick PNG preview ---------------------------------
top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:TOP_PREVIEW]
H = G.subgraph([n for n, _ in top_nodes]).copy()

# spring-layout weighted by edge weight
pos = nx.spring_layout(H, k=0.6, weight="weight", seed=42)

# colour by community
colors = [partition[n] for n in H.nodes()]

plt.figure(figsize=(10, 10))
nx.draw_networkx_edges(H, pos, width=[H[u][v]["weight"]*0.3 for u, v in H.edges()], alpha=0.4)
nx.draw_networkx_nodes(H, pos,
                       node_size=[H.degree(n)*5 for n in H.nodes()],
                       node_color=colors, cmap="tab20")
nx.draw_networkx_labels(H, pos, font_size=7, font_family="sans-serif")
plt.axis("off"); plt.tight_layout()
plt.savefig("hashtag_graph.png", dpi=300)
plt.show()

print("✅  Preview PNG  → hashtag_graph.png")
