import networkx as nx
import numpy as np
import json
import random
import glob
import community
import colorsys


np.random.seed(42)
random.seed(42)

similarity_matrix = np.load("./similarity_matrix.npy")

similarity_matrix = np.array(similarity_matrix)
list_of_graphs = glob.glob("/Users/arjuns/Downloads/fyp/scraping/new/graphs/*/*.graphml")
list_of_graphs = [graph.split("/")[-1].split(".")[0] for graph in list_of_graphs]


thresholds = [
    0.00125125, 0.0042042, 0.00586587, 0.00705706, 0.00888889,
    0.00026026, 0.00387387, 0.00511512, 0.00653654, 0.00821822,
    0.00992993
]

def get_community_color(community_id):
    # Same HSL logic, but convert to RGB then hex
    hue = ((community_id * 137.508) % 360) / 360  # normalize hue between 0 and 1
    r, g, b = colorsys.hls_to_rgb(hue, 0.5, 0.9)  # h, l, s
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

for threshold in thresholds:
    G = nx.Graph()
    G.add_nodes_from(list_of_graphs)

    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            if similarity_matrix[i][j] > threshold:
                G.add_edge(list_of_graphs[i], list_of_graphs[j], weight=similarity_matrix[i][j])

    if len(G.edges) == 0:
        print(f"[!] Skipping threshold {threshold} — no edges.")
        continue

    partition = community.best_partition(G, random_state=42)
    pos = nx.spring_layout(G, seed=42)

    data = {
        "threshold": threshold,
        "nodes": [
            {
                "id": node,
                "label": node,
                "community": partition[node],
                "x": pos[node][0],
                "y": pos[node][1],
                "color": get_community_color(partition.get(node, 0))
            }
            for node in G.nodes()
        ],
        "edges": [
            {
                "source": u,
                "target": v,
                "weight": d["weight"]
            }
            for u, v, d in G.edges(data=True)
        ]
    }

    fname = f"graphs_output/graph_{str(threshold).replace('.', '_')}.json"
    with open(fname, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[✓] Saved: {fname} — Nodes: {len(G.nodes())}, Edges: {len(G.edges())}, Communities: {len(set(partition.values()))}")
