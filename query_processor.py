"""
Query processor module for entity extraction from user queries.
"""

import re
from interfaces import QueryProcessorInterface


class QueryProcessor(QueryProcessorInterface):
    """Extract entities and intent from user queries."""

    DEFAULT_PILLARS = [
        "governance",
        "security",
        "compliance",
        "reliability",
        "performance",
        "cost",
        "quality",
        "delivery",
        "risk",
    ]

    DEFAULT_ROLES = [
        "devops",
        "developer",
        "security",
        "qa",
        "qa engineer",
        "engineer",
        "project manager",
        "product owner",
        "architect",
        "operations",
        "business analyst",
        "devops team",
    ]

    DEFAULT_TOOLS = [
        "jenkins",
        "jira",
        "git",
        "github",
        "gitlab",
        "docker",
        "kubernetes",
        "ansible",
        "terraform",
        "aws",
        "azure",
        "slack",
        "confluence",
    ]

    DEFAULT_PROCESSES = [
        "deployment",
        "build",
        "release",
        "integration",
        "testing",
        "verification",
        "validation",
        "incident management",
        "change management",
        "onboarding",
        "audit",
        "security review",
    ]

    INTENT_KEYWORDS = {
        "risk analysis": ["risk", "risks", "threat", "vulnerability", "failure"],
        "Dependency Analysis": ["dependency", "dependencies", "impact"],
        "Recommendations": ["recommendation", "recommendations", "best practice", "suggest"],
        "Summary": ["summary", "overview", "describe", "show", "what", "explain"],
        "Performance Review": ["performance", "latency", "throughput"],
        "Compliance Review": ["compliance", "regulatory", "policy"],
    }

    def __init__(self, pillars=None, roles=None, tools=None, processes=None):
        self.pillars = [p.lower() for p in (pillars or self.DEFAULT_PILLARS)]
        self.roles = [r.lower() for r in (roles or self.DEFAULT_ROLES)]
        self.tools = [t.lower() for t in (tools or self.DEFAULT_TOOLS)]
        self.processes = [p.lower() for p in (processes or self.DEFAULT_PROCESSES)]

    @staticmethod
    def _normalize_text(query: str) -> str:
        return re.sub(r"[^a-z0-9 ]+", " ", query.lower()).strip()

    @staticmethod
    def _choose_best_match(normalized_query: str, matches):
        if not matches:
            return None

        positions = []
        for candidate in matches:
            token = candidate.lower()
            match = re.search(re.escape(token), normalized_query)
            if match:
                positions.append((match.start(), -len(token), candidate))

        if not positions:
            return None

        return sorted(positions)[0][2]

    def _extract_from_dictionary(self, normalized_query: str, candidates):
        matches = [candidate for candidate in candidates if candidate.lower() in normalized_query]
        return self._choose_best_match(normalized_query, matches)

    def _extract_intent(self, normalized_query: str):
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in normalized_query:
                    return intent.title() if intent.islower() else intent
        return "Summary"

    def extract_entities(self, query: str) -> dict:
        """Return structured entities extracted from a user query."""
        normalized_query = self._normalize_text(query)

        pillar = self._extract_from_dictionary(normalized_query, self.pillars)
        role = self._extract_from_dictionary(normalized_query, self.roles)
        tool = self._extract_from_dictionary(normalized_query, self.tools)
        process = self._extract_from_dictionary(normalized_query, self.processes)
        intent = self._extract_intent(normalized_query)

        return {
            "pillar": pillar.title() if pillar else None,
            "role": role.title() if role else None,
            "tool": tool.title() if tool else None,
            "process": process.title() if process else None,
            "intent": intent,
            "query": query,
        }
