"""
Unit tests for the retrieval layer modules.
"""

import unittest
import networkx as nx

from query_processor import QueryProcessor
from graph_retriever import GraphRetriever
from fallback_retriever import FallbackRetriever
from response_formatter import ResponseFormatter


class TestQueryProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = QueryProcessor()

    def test_extract_entities_role_process_intent(self):
        result = self.processor.extract_entities("Show DevOps deployment risks")
        self.assertEqual(result["role"], "Devops")
        self.assertEqual(result["process"], "Deployment")
        self.assertEqual(result["intent"], "Risk Analysis")

    def test_extract_entities_tool_and_pillar(self):
        result = self.processor.extract_entities("Analyze GitHub security compliance")
        self.assertEqual(result["tool"], "Github")
        self.assertEqual(result["pillar"], "Security")
        self.assertEqual(result["intent"], "Compliance Review")

    def test_extract_entities_when_no_match(self):
        result = self.processor.extract_entities("What is the holistic state?")
        self.assertIsNone(result["pillar"])
        self.assertIsNone(result["role"])
        self.assertEqual(result["intent"], "Summary")


class TestGraphRetriever(unittest.TestCase):
    def setUp(self):
        self.graph = nx.DiGraph()
        self.graph.add_node("Deployment", type="process")
        self.graph.add_node("Jenkins", type="tool")
        self.graph.add_node("DevOps Team", type="role")
        self.graph.add_node("Security Review", type="process")
        self.graph.add_edge("Deployment", "Jenkins", label="uses")
        self.graph.add_edge("Jenkins", "DevOps Team", label="owned_by")
        self.graph.add_edge("DevOps Team", "Security Review", label="reviews")
        self.retriever = GraphRetriever(self.graph)

    def test_traverse_returns_expected_path(self):
        result = self.retriever.traverse("Deployment", depth=3)
        expected_path = ["Deployment", "Jenkins", "DevOps Team", "Security Review"]
        self.assertTrue(any(entry["path"] == expected_path for entry in result["paths"]))
        self.assertEqual(result["metadata"]["path_count"], 3)
        self.assertEqual(result["start_entity"], "Deployment")

    def test_traverse_with_missing_entity_returns_empty_paths(self):
        result = self.retriever.traverse("Unknown Entity", depth=2)
        self.assertEqual(result["paths"], [])
        self.assertEqual(result["metadata"]["reason"], "start_entity_not_found")


class TestFallbackRetriever(unittest.TestCase):
    def setUp(self):
        self.fallback = FallbackRetriever()

    def test_get_fallback_returns_global_summary(self):
        result = self.fallback.get_fallback("Explain unknown process")
        self.assertEqual(result["source"], "fallback")
        self.assertIn("global_context", result)
        self.assertTrue(result["recommendations"])

    def test_get_fallback_includes_missing_entities(self):
        result = self.fallback.get_fallback("Explain unknown process", missing_entities=["deployment"])
        self.assertIn("Deployment", result["summary"])
        self.assertEqual(result["missing_entities"], ["deployment"])


class TestResponseFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = ResponseFormatter()

    def test_format_graph_response(self):
        graph_result = {
            "source": "graph",
            "start_entity": "Deployment",
            "paths": [{"path": ["Deployment", "Jenkins"], "path_length": 1}],
            "related_nodes": ["Jenkins"],
            "metadata": {"path_count": 1},
        }
        response = self.formatter.format(graph_result)
        self.assertIn("summary", response)
        self.assertIn("Deployment -> Jenkins", response["dependencies"])
        self.assertTrue(response["risks"])
        self.assertTrue(response["recommendations"])

    def test_format_fallback_response(self):
        fallback_result = {
            "source": "fallback",
            "summary": "No graph match found.",
            "global_context": {"processes": "Process overview."},
            "recommendations": ["Review data coverage."],
        }
        response = self.formatter.format(fallback_result)
        self.assertEqual(response["summary"], "No graph match found.")
        self.assertIn("Process overview.", response["dependencies"])
        self.assertTrue(response["recommendations"])


if __name__ == "__main__":
    unittest.main()
