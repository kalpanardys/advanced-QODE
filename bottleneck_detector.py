"""
Bottleneck detection using centrality and path participation.
"""
from typing import Dict, Any, List
import networkx as nx


def detect_bottlenecks(graph: nx.DiGraph, paths: List[List[str]] = None, top_n: int = 10) -> Dict[str, Any]:
    """Identify potential bottlenecks in the graph.

    Returns top nodes by combined centrality and path frequency.
    """
    degree = nx.degree_centrality(graph)
    try:
        between = nx.betweenness_centrality(graph)
    except Exception:
        between = {n: 0.0 for n in graph.nodes}

    path_freq = {}
    if paths:
        for path in paths:
            for node in path:
                path_freq[node] = path_freq.get(node, 0) + 1

    scores = {}
    for node in graph.nodes:
        scores[node] = (
            degree.get(node, 0.0) * 0.4 + between.get(node, 0.0) * 0.5 + (path_freq.get(node, 0) / (len(paths) or 1)) * 0.1
        )

    ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_n]

    results = []
    for node, score in ranked:
        results.append(
            {
                "node": node,
                "score": score,
                "degree_centrality": degree.get(node, 0.0),
                "betweenness_centrality": between.get(node, 0.0),
                "path_frequency": path_freq.get(node, 0),
            }
        )

    return {"bottlenecks": results}
