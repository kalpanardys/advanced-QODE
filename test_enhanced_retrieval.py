"""
Unit tests for the enhanced retrieval layer modules.
"""

import unittest
import networkx as nx
import pandas as pd

from entity_loader import EntityLoader
from graph_builder import GraphBuilder
from query_processor_enhanced import EnhancedQueryProcessor


class TestEntityLoader(unittest.TestCase):
    def setUp(self):
        # Test with sample Excel file
        self.loader = EntityLoader("sample_questions.xlsm")

    def test_loader_loads_entities(self):
        entities = self.loader.get_all_entities()
        self.assertIn("pillars", entities)
        self.assertIn("roles", entities)
        self.assertIn("tools", entities)
        self.assertIn("processes", entities)

    def test_summary_is_non_zero(self):
        summary = self.loader.get_entity_summary()
        self.assertGreater(summary["total_entities"], 0)


class TestGraphBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = GraphBuilder("sample_questions.xlsm")

    def test_build_role_graph(self):
        graph = self.builder.build_role_graph()
        self.assertIsInstance(graph, nx.DiGraph)
        self.assertGreater(len(graph.nodes()), 0)

    def test_build_tool_graph(self):
        graph = self.builder.build_tool_graph()
        self.assertIsInstance(graph, nx.DiGraph)
        self.assertGreater(len(graph.nodes()), 0)

    def test_build_process_graph(self):
        graph = self.builder.build_process_graph()
        self.assertIsInstance(graph, nx.DiGraph)
        self.assertGreater(len(graph.nodes()), 0)

    def test_build_unified_graph(self):
        graph = self.builder.build_unified_graph()
        self.assertIsInstance(graph, nx.DiGraph)
        total_nodes = len(graph.nodes())
        self.assertGreater(total_nodes, 0)

    def test_graph_summary(self):
        summary = self.builder.get_graph_summary()
        self.assertIn("role_graph", summary)
        self.assertIn("tool_graph", summary)
        self.assertIn("process_graph", summary)


class TestEnhancedQueryProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = EnhancedQueryProcessor("sample_questions.xlsm")

    def test_extract_entities_with_loaded_data(self):
        result = self.processor.extract_entities("Show deployment risks")
        self.assertIn("process", result)
        self.assertIn("intent", result)
        self.assertEqual(result["intent"], "Risk Analysis")

    def test_extract_entities_returns_dict(self):
        result = self.processor.extract_entities("Test query")
        self.assertIsInstance(result, dict)
        required_keys = ["pillar", "role", "tool", "process", "intent", "query"]
        for key in required_keys:
            self.assertIn(key, result)


if __name__ == "__main__":
    unittest.main()
