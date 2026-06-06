"""
Impact analysis utilities for dependency graphs.
"""
from typing import List, Dict, Any
import networkx as nx


def analyze_impact(graph: nx.DiGraph, start_node: str, max_depth: int = 4, top_paths: int = 5) -> Dict[str, Any]:
    """Compute impacted nodes and categorize them by impact level.

    Returns a dict with paths, node frequencies and impact categories.
    """
    # Collect simple paths from start_node to other nodes up to max_depth
    paths = []
    try:
        for target in graph.nodes:
            if target == start_node:
                continue
            # limit path length
            for path in nx.all_simple_paths(graph, source=start_node, target=target, cutoff=max_depth):
                paths.append(path)
    except Exception:
        paths = []

    # Count node frequencies across paths
    freq = {}
    for path in paths:
        for node in path[1:]:
            freq[node] = freq.get(node, 0) + 1

    total_paths = len(paths) or 1

    impact = {"high": [], "medium": [], "low": []}
    for node, count in sorted(freq.items(), key=lambda x: -x[1]):
        pct = count / total_paths
        if pct >= 0.5:
            impact["high"].append((node, count))
        elif pct >= 0.25:
            impact["medium"].append((node, count))
        else:
            impact["low"].append((node, count))

    # Return top N unique paths (by length desc then frequency)
    ranked_paths = sorted(paths, key=lambda p: (-len(p), p))[:top_paths]

    return {
        "start_node": start_node,
        "total_paths": len(paths),
        "paths": ranked_paths,
        "frequencies": freq,
        "impact": impact,
    }
