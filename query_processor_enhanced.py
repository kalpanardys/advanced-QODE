"""
Enhanced query processor using loaded entities from Excel.
"""

import re
from interfaces import QueryProcessorInterface
from entity_loader import EntityLoader
from fuzzy_matcher import best_match


class EnhancedQueryProcessor(QueryProcessorInterface):
    """Extract entities from user queries using dynamically loaded entities."""

    INTENT_KEYWORDS = {
        "Risk Analysis": ["risk", "risks", "threat", "vulnerability", "failure"],
        "Dependency Analysis": ["dependency", "dependencies", "impact", "related"],
        "Recommendations": ["recommendation", "recommendations", "best practice", "suggest"],
        "Summary": ["summary", "overview", "describe", "show", "what", "explain"],
        "Performance Review": ["performance", "latency", "throughput", "speed"],
        "Compliance Review": ["compliance", "regulatory", "policy", "audit"],
    }

    def __init__(self, file_path="sample_questions.xlsm", similarity_threshold: float = 80.0):
        self.loader = EntityLoader(file_path)
        entities = self.loader.get_all_entities()
        # Keep original-cased lists for resolution, but provide lower-case matching
        self.pillars = list(entities["pillars"])
        self.roles = list(entities["roles"])
        self.tools = list(entities["tools"])
        self.processes = list(entities["processes"])
        self.similarity_threshold = similarity_threshold

    @staticmethod
    def _normalize_text(query: str) -> str:
        """Normalize query text for matching."""
        return re.sub(r"[^a-z0-9 ]+", " ", query.lower()).strip()

    def _find_best_match(self, query: str, candidates):
        """Find the best fuzzy match for query among candidates.

        Returns the matched candidate (original casing) or None.
        """
        if not candidates:
            return None
        match = best_match(query, candidates, threshold=self.similarity_threshold)
        if match:
            return match[0]
        return None

    def _extract_intent(self, normalized_query: str):
        """Extract intent from query."""
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in normalized_query:
                    return intent
        return "Summary"

    def extract_entities(self, query: str) -> dict:
        """Extract structured entities from a user query."""
        normalized_query = self._normalize_text(query)

        # Use fuzzy matching on original candidate lists
        pillar_match = self._find_best_match(query, self.pillars)
        role_match = self._find_best_match(query, self.roles)
        tool_match = self._find_best_match(query, self.tools)
        process_match = self._find_best_match(query, self.processes)
        intent = self._extract_intent(normalized_query)

        return {
            "pillar": pillar_match,
            "role": role_match,
            "tool": tool_match,
            "process": process_match,
            "intent": intent,
            "query": query,
        }
