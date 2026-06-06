"""
Graph reasoning utilities: path ranking, top critical paths, and narrative generation.
"""
from typing import List, Dict, Any
import networkx as nx
from bottleneck_detector import detect_bottlenecks


def score_path(graph: nx.DiGraph, path: List[str], centrality: Dict[str, float]) -> float:
    """Score path by length, centrality and number of impacted nodes."""
    length_score = len(path)
    central_score = sum(centrality.get(n, 0.0) for n in path) / max(len(path), 1)
    impacted_count = len(path) - 1
    # Weighted combination
    return length_score * 0.4 + central_score * 5.0 + impacted_count * 0.6


def rank_paths(graph: nx.DiGraph, paths: List[List[str]], top_n: int = 5) -> List[Dict[str, Any]]:
    """Rank and return top_n paths with scores and metadata."""
    try:
        centrality = nx.betweenness_centrality(graph)
    except Exception:
        centrality = {n: 0.0 for n in graph.nodes}

    scored = []
    for p in paths:
        s = score_path(graph, p, centrality)
        scored.append((s, p))

    scored.sort(key=lambda x: -x[0])
    results = []
    for score, path in scored[:top_n]:
        results.append({"path": path, "score": score})
    return results


def generate_reasoning(graph: nx.DiGraph, start_node: str, top_paths: List[Dict[str, Any]]) -> str:
    """Generate a short reasoning paragraph based on metrics and top paths."""
    nodes_in_paths = set()
    for entry in top_paths:
        nodes_in_paths.update(entry["path"] if isinstance(entry, dict) else entry)

    bottlenecks = detect_bottlenecks(graph, [p["path"] if isinstance(p, dict) else p for p in top_paths], top_n=5)

    top_nodes = [b["node"] for b in bottlenecks["bottlenecks"][:3]]

    reasoning = (
        f"Starting from '{start_node}', the engine identified {len(top_paths)} critical dependency path(s). "
        f"Nodes that frequently appear across these paths include: {', '.join(sorted(nodes_in_paths))}. "
    )
    if top_nodes:
        reasoning += f"Potential bottlenecks detected: {', '.join(top_nodes)}. "

    reasoning += (
        "These metrics indicate which upstream services or roles are critical and warrant further resilience or redundancy reviews."
    )

    return reasoning
