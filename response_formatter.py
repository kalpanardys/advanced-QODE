"""
Response formatter module for converting retrieval output into structured sections.
"""

from unittest import result

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
            f"{start_entity} is a critical entity. "
            f"Failure of {start_entity} may impact {len(related_nodes)} connected entities across the delivery lifecycle."
         )

         impacted_entities = set()

         for path_entry in paths:
          path = path_entry.get("path", [])
          for node in path[1:]:
            impacted_entities.add(node)

         impacted_entities = sorted(list(impacted_entities))

         if len(impacted_entities) >= 8:
           risk_level = "HIGH"
         elif len(impacted_entities) >= 4:
          risk_level = "MEDIUM"
         else:
          risk_level = "LOW"

         risks = [
           f"Business Risk Level: {risk_level}",
           f"Failure of '{start_entity}' may impact downstream tools, roles, and processes."
         ]

         recommendations = [
          "Review critical dependencies regularly.",
          "Implement monitoring and alerting for key entities.",
           "Validate upstream and downstream process relationships."
         ]

         return {
           "summary": summary,
           "impacted_entities": impacted_entities,
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
