"""
Response formatter module for converting retrieval output into structured sections.
"""

from interfaces import ResponseFormatterInterface


class ResponseFormatter(ResponseFormatterInterface):
    """Format retrieval results into presentation-ready sections."""

    def format(self, retrieval_result: dict) -> dict:
        source = retrieval_result.get("source")

        if source == "fallback":
            return self._format_fallback(retrieval_result)

        if source == "graph":
            return self._format_graph_response(retrieval_result)

        return {
            "summary": "No retrieval result is available.",
            "dependencies": [],
            "risks": [],
            "recommendations": [],
        }

    def _format_graph_response(self, result: dict) -> dict:
        start_entity = result.get("start_entity")
        paths = result.get("paths", [])
        related_nodes = result.get("related_nodes", [])

        summary = (
            f"Starting from '{start_entity}', the graph retrieval engine found {len(paths)} path(s) "
            f"and {len(related_nodes)} related node(s)."
        )

        dependencies = []
        for path_entry in paths:
            dependencies.append(" -> ".join(path_entry["path"]))

        if not dependencies:
            dependencies = ["No explicit dependencies were found for the selected entity."]

        risks = []
        if result.get("metadata", {}).get("path_count", 0) == 0:
            risks.append("The selected entity may be isolated or missing from the current dependency graph.")
        else:
            risks.append(
                "Review dependencies on longer multi-hop paths first, as they can indicate hidden process risk and handoff complexity."
            )

        recommendations = [
            "Validate key roles and tools attached to the entity to improve process intelligence coverage.",
            "Use multi-hop traversal to identify indirect process dependencies and potential bottlenecks.",
        ]

        return {
            "summary": summary,
            "dependencies": dependencies,
            "risks": risks,
            "recommendations": recommendations,
        }

    def _format_fallback(self, result: dict) -> dict:
        summary = result.get("summary", "No fallback summary is available.")

        return {
            "summary": summary,
            "dependencies": [
                "Fallback responses are intentionally broad to support future vector database retrieval.",
                result.get("global_context", {}).get("processes"),
            ],
            "risks": [
                "Graph lookup failed for the requested entity, so the current result is a high-level summary.",
                "Plan to connect missing entities into the knowledge graph to reduce fallback usage.",
            ],
            "recommendations": result.get("recommendations", []),
        }
