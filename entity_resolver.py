"""
Entity resolver for mapping extracted entities to graph nodes.

Responsibilities:
- Resolve pillars, roles, tools, processes to actual graph node names
- Use rapidfuzz (via fuzzy_matcher) for fuzzy resolution
- Return matched node and confidence score
"""
from typing import Optional, Dict, Any, Iterable
import networkx as nx
from fuzzy_matcher import best_match


def resolve_entity(graph: nx.Graph, entity_type: str, entity_value: str, threshold: float = 80.0) -> Dict[str, Any]:
    """Resolve a single entity to a graph node.

    Returns: {"resolved": node_or_none, "score": float, "node_type": str or None}
    """
    if not entity_value:
        return {"resolved": None, "score": 0.0, "node_type": None}

    val = str(entity_value).strip()
    if not val:
        return {"resolved": None, "score": 0.0, "node_type": None}

    # Prefer matching nodes of the expected type when available
    candidates = []
    et = entity_type.lower() if entity_type else ""
    for n, attrs in graph.nodes(data=True):
        ntype = attrs.get("type", "").lower() if attrs else ""
        if et == "role" and ntype == "role":
            candidates.append(n)
        elif et == "tool" and ntype == "tool":
            candidates.append(n)
        elif et == "process" and ntype == "process":
            candidates.append(n)
        elif et == "pillar":
            # Pillars may not be explicit node types; consider all nodes
            candidates.append(n)

    # If no filtered candidates, fall back to all nodes
    if not candidates:
        candidates = list(graph.nodes)

    # 1. Exact case-insensitive match
    low_val = val.lower()
    for c in candidates:
        if str(c).lower() == low_val:
            node_type = graph.nodes[c].get("type") if c in graph else None
            return {"resolved": c, "score": 100.0, "node_type": node_type}

    # 2. Use fuzzy matching helper
    match = best_match(val, candidates, threshold=threshold)
    if match:
        candidate_name, score = match
        node_type = graph.nodes[candidate_name].get("type") if candidate_name in graph else None
        return {"resolved": candidate_name, "score": score, "node_type": node_type}

    # 3. substring fallback across candidates
    substr_hits = [c for c in candidates if low_val in str(c).lower() or str(c).lower() in low_val]
    if substr_hits:
        c = substr_hits[0]
        node_type = graph.nodes[c].get("type") if c in graph else None
        return {"resolved": c, "score": 85.0, "node_type": node_type}

    return {"resolved": None, "score": 0.0, "node_type": None}


def validate_graph(graph: nx.Graph, known_pillars: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Return debug info about graph construction and nodes by type.

    known_pillars: iterable of pillar names to try to match against nodes
    """
    info = {
        "total_nodes": graph.number_of_nodes(),
        "total_edges": graph.number_of_edges(),
        "pillars": [],
        "roles": [],
        "tools": [],
        "processes": [],
    }

    for n, attrs in graph.nodes(data=True):
        t = attrs.get("type") if attrs else None
        if t == "role":
            info["roles"].append(n)
        elif t == "tool":
            info["tools"].append(n)
        elif t == "process":
            info["processes"].append(n)

    if known_pillars:
        lows = {p.lower() for p in known_pillars}
        info["pillars"] = [n for n in graph.nodes if str(n).lower() in lows or any(p in str(n).lower() for p in lows)]

    return info
