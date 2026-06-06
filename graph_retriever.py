"""
Graph retriever module for multi-hop traversal of dependency graphs.
"""

import networkx as nx
from interfaces import GraphRetrieverInterface
from fuzzy_matcher import best_match
from graph_reasoner import rank_paths, generate_reasoning
import networkx as nx


class GraphRetriever(GraphRetrieverInterface):
    """Retrieve related entities from a NetworkX graph."""

    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def _get_neighbors(self, node):
        if isinstance(self.graph, nx.DiGraph):
            neighbors = set(self.graph.predecessors(node)) | set(self.graph.successors(node))
        else:
            neighbors = set(self.graph.neighbors(node))
        return neighbors

    def _get_node_metadata(self, node):
        return dict(self.graph.nodes[node]) if node in self.graph else {}

    def _get_edge_metadata(self, source, target):
        data = self.graph.get_edge_data(source, target)
        return data if data is not None else {}

    def _build_path_payload(self, path):
        edge_metadata = [self._get_edge_metadata(path[i], path[i + 1]) for i in range(len(path) - 1)]
        return {
            "path": path,
            "path_length": len(path) - 1,
            "node_metadata": [self._get_node_metadata(node) for node in path],
            "edge_metadata": edge_metadata,
        }

    def traverse(self, start_entity: str, depth: int = 2) -> dict:
        """Traverse the graph from a starting entity up to a maximum depth."""
        result = {
            "source": "graph",
            "start_entity": start_entity,
            "depth": depth,
            "paths": [],
            "related_nodes": [],
            "metadata": {},
        }

        if start_entity not in self.graph:
            result["metadata"] = {
                "available_nodes": len(self.graph),
                "reason": "start_entity_not_found",
            }
            return result

        visited = {start_entity}
        queue = [(start_entity, [start_entity], 0)]
        collected = set()
        paths = []

        while queue:
            current_node, path, hops = queue.pop(0)
            if hops >= depth:
                continue

            for neighbor in self._get_neighbors(current_node):
                if neighbor in path:
                    continue

                next_path = path + [neighbor]
                paths.append(self._build_path_payload(next_path))
                collected.add(neighbor)
                queue.append((neighbor, next_path, hops + 1))

        result["paths"] = paths
        result["related_nodes"] = sorted(collected)
        result["metadata"] = {
            "node_count": len(result["related_nodes"]),
            "path_count": len(result["paths"]),
        }
        return result

    def resolve_pillar(self, pillar: str, threshold: float = 80.0):
        """Resolve a pillar string to candidate graph nodes using fuzzy matching on node names."""
        if not pillar:
            return []

        candidates = list(self.graph.nodes)
        match = best_match(pillar, candidates, threshold=threshold)
        if match:
            return [match[0]]

        # fallback: substring match
        lowered = pillar.lower()
        hits = [n for n in candidates if lowered in str(n).lower()]
        return hits

    def get_top_paths(self, start_entity: str = None, pillar: str = None, depth: int = 4, top_paths: int = 5, similarity_threshold: float = 80.0) -> dict:
        """Return ranked top dependency paths starting from an entity or a resolved pillar."""
        if pillar and not start_entity:
            resolved = self.resolve_pillar(pillar, threshold=similarity_threshold)
            if resolved:
                start_entity = resolved[0]

        result = {
            "source": "graph",
            "start_entity": start_entity,
            "depth": depth,
            "paths": [],
            "related_nodes": [],
            "metadata": {},
        }

        if not start_entity or start_entity not in self.graph:
            result["metadata"] = {"reason": "start_entity_not_found"}
            return result

        # Collect simple paths up to cutoff depth
        all_paths = []
        try:
            for target in self.graph.nodes:
                if target == start_entity:
                    continue
                for path in nx.all_simple_paths(self.graph, source=start_entity, target=target, cutoff=depth):
                    all_paths.append(path)
        except Exception:
            all_paths = []

        ranked = rank_paths(self.graph, all_paths, top_n=top_paths)

        result["paths"] = ranked
        related = set()
        for r in ranked:
            related.update(r.get("path", []))
        result["related_nodes"] = sorted(related)
        result["metadata"] = {"node_count": len(result["related_nodes"]), "path_count": len(all_paths)}
        result["reasoning"] = generate_reasoning(self.graph, start_entity, ranked)

        return result
