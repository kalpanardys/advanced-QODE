"""
Fallback retriever module for global summary retrieval and future vector store support.
"""

from interfaces import FallbackRetrieverInterface


class FallbackRetriever(FallbackRetrieverInterface):
    """Provide fallback content when graph retrieval has no direct matches."""

    DEFAULT_SUMMARIES = {
        "pillars": (
            "Pillars are the strategic dimensions that guide process intelligence: governance, risk, security, cost, and reliability. "
            "A strong retrieval layer should link user intent to these foundational areas."
        ),
        "roles": (
            "Roles define people and teams responsible for outcomes across the process lifecycle. "
            "Understanding role interactions helps uncover accountability, handoffs, and bottlenecks."
        ),
        "tools": (
            "Tools are the platforms and automation engines that execute process work. "
            "Tool relationships expose integration points and technical dependencies."
        ),
        "processes": (
            "Processes represent the workflow stages and transitions that form the enterprise value stream. "
            "Capturing process relationships enables reliable analysis and decision support."
        ),
        "default": (
            "When a direct graph match is unavailable, the system provides a global process intelligence overview. "
            "This summary is designed to keep the user moving forward while future vector retrieval is integrated."
        ),
    }

    def __init__(self, global_summaries=None):
        self.global_summaries = global_summaries or self.DEFAULT_SUMMARIES

    def get_fallback(self, query: str, missing_entities=None) -> dict:
        """Return a structured fallback summary for unmatched queries."""
        missing_entities = missing_entities or []
        topics = [entity.title() for entity in missing_entities if entity]

        if topics:
            summary = (
                f"No direct match was found for {', '.join(topics)}. "
                "The platform is returning higher-level process intelligence context."
            )
        else:
            summary = self.global_summaries["default"]

        return {
            "source": "fallback",
            "reason": "no_graph_match",
            "query": query,
            "missing_entities": missing_entities,
            "summary": summary,
            "global_context": {
                "pillars": self.global_summaries["pillars"],
                "roles": self.global_summaries["roles"],
                "tools": self.global_summaries["tools"],
                "processes": self.global_summaries["processes"],
            },
            "recommendations": [
                "Review process definitions and role assignments to improve entity coverage.",
                "Map tools, roles, and processes into a shared knowledge graph for better future retrieval.",
                "Define fallback summaries for common enterprise process questions while vector search is deployed.",
            ],
        }

    def query_vector_store(self, query: str) -> dict:
        """Placeholder method for future vector database integration."""
        raise NotImplementedError("Vector store integration is not configured yet.")
