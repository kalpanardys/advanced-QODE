"""
Tests for diagram builders.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import pydot
import networkx as nx

from diagram_generator import PeopleDiagramBuilder, TechnologyDiagramBuilder, ProcessNetworkDiagramBuilder, DotExporter
from utils import criticality_mapping, find_leaf_nodes, get_avg_criticality, node_to_edge


class TestDotExporter(unittest.TestCase):
    def test_write_raw_calls_dot_graph_write_raw(self):
        exporter = DotExporter()
        mock_dot = MagicMock()
        exporter.write_raw(mock_dot, "test.dot")
        mock_dot.write_raw.assert_called_once_with("test.dot")


class TestPeopleDiagramBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = PeopleDiagramBuilder()

    @patch('diagram_generator.load_qode_data')
    def test_load_data_calls_load_qode_data(self, mock_load):
        mock_df = pd.DataFrame()
        mock_load.return_value = mock_df
        result = self.builder.load_data("test.xlsx")
        mock_load.assert_called_once_with("test.xlsx")
        pd.testing.assert_frame_equal(result, mock_df)

    def test_build_graph_creates_nodes_and_edges(self):
        # Create test data
        data = {
            "S#": [1, 2],
            "Predecessor 1 (incl. INIT)": [float("nan"), 1],
            "Predecessor 2 (optional)": [float("nan"), float("nan")],
            "Predecessor 3 (optional)": [float("nan"), float("nan")],
            "Predecessor 4 (optional)": [float("nan"), float("nan")],
            "Predecessor 5 (optional)": [float("nan"), float("nan")],
            "Team / owner role": ["Dev", "QA"],
            "Total time taken": [10, 5],
            "Manual time spent": [10, 2]
        }
        df = pd.DataFrame(data)
        
        result = self.builder.build_graph(df)
        
        # Check that nodes were created
        self.assertIn("Dev", self.builder.node_list)
        self.assertIn("QA", self.builder.node_list)
        
        # Check that edges were created (QA should have edge from Dev)
        edges = result.get_edges()
        self.assertTrue(len(edges) > 0)

    def test_write_output_uses_dot_exporter(self):
        mock_dot = MagicMock()
        with patch('diagram_generator.DotExporter') as mock_exporter_class:
            mock_exporter = MagicMock()
            mock_exporter_class.return_value = mock_exporter
            
            self.builder.write_output(mock_dot, "test.dot")
            
            mock_exporter.write_raw.assert_called_once_with(mock_dot, "test.dot")


class TestTechnologyDiagramBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = TechnologyDiagramBuilder()

    def test_build_graph_creates_nodes_and_consolidated_edges(self):
        # Create test data
        data = {
            "S#": [1, 2],
            "Predecessor 1 (incl. INIT)": [float("nan"), 1],
            "Predecessor 2 (optional)": [float("nan"), float("nan")],
            "Predecessor 3 (optional)": [float("nan"), float("nan")],
            "Predecessor 4 (optional)": [float("nan"), float("nan")],
            "Predecessor 5 (optional)": [float("nan"), float("nan")],
            "Automation tool": ["Jira", "Jenkins"]
        }
        df = pd.DataFrame(data)
        
        result = self.builder.build_graph(df)
        
        # Check that nodes were created
        self.assertIn("Jira", self.builder.node_list)
        self.assertIn("Jenkins", self.builder.node_list)
        
        # Check that edges were created
        edges = result.get_edges()
        self.assertTrue(len(edges) > 0)


class TestProcessNetworkDiagramBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = ProcessNetworkDiagramBuilder()

    def test_criticality_mapping_hi(self):
        self.assertEqual(criticality_mapping("hi"), 3)

    def test_criticality_mapping_med(self):
        self.assertEqual(criticality_mapping("med"), 2)

    def test_criticality_mapping_low(self):
        self.assertEqual(criticality_mapping("low"), 1)

    def test_criticality_mapping_default(self):
        self.assertEqual(criticality_mapping("unknown"), 1)

    def test_find_leaf_nodes_simple(self):
        G = nx.DiGraph()
        G.add_edges_from([("E0", "E1"), ("E1", "E2")])
        leaves = find_leaf_nodes(G)
        self.assertIn("E2", leaves)
        self.assertNotIn("E0", leaves)
        self.assertNotIn("E1", leaves)

    def test_find_leaf_nodes_branching(self):
        G = nx.DiGraph()
        G.add_edges_from([("E0", "E1"), ("E0", "E2")])
        leaves = find_leaf_nodes(G)
        self.assertIn("E1", leaves)
        self.assertIn("E2", leaves)

    def test_get_avg_criticality_single_edge(self):
        G = nx.DiGraph()
        G.add_edge("E0", "E1", weight=[5, 3, "A1"])
        result = get_avg_criticality(G, ["E0", "E1"])
        self.assertEqual(result, 3.0)

    def test_get_avg_criticality_two_edges(self):
        G = nx.DiGraph()
        G.add_edge("E0", "E1", weight=[3, 3, "A1"])
        G.add_edge("E1", "E2", weight=[2, 1, "A2"])
        result = get_avg_criticality(G, ["E0", "E1", "E2"])
        self.assertEqual(result, 2.0)  # (3 + 1) / 2

    def test_node_to_edge_single(self):
        G = nx.DiGraph()
        G.add_edge("E0", "E1", weight=[1, 1, "A1"])
        result = node_to_edge(G, ["E0", "E1"])
        self.assertEqual(result, ["A1"])

    def test_node_to_edge_multiple(self):
        G = nx.DiGraph()
        G.add_edge("E0", "E1", weight=[1, 1, "A1"])
        G.add_edge("E1", "E2", weight=[1, 1, "A2"])
        result = node_to_edge(G, ["E0", "E1", "E2"])
        self.assertEqual(result, ["A1", "A2"])

    def test_create_pydot_nodes_creates_e0_and_process_nodes(self):
        data = {
            "S#": [1, 2],
            "Total time taken": [5, 3],
            "Manual time spent": [2, 1],
            "Predecessor 1 (incl. INIT)": [float("nan"), 1],
            "Predecessor 2 (optional)": [float("nan"), float("nan")],
            "Predecessor 3 (optional)": [float("nan"), float("nan")],
            "Predecessor 4 (optional)": [float("nan"), float("nan")],
            "Predecessor 5 (optional)": [float("nan"), float("nan")],
            "Criticality": ["hi", "med"],
            "Team / owner role": ["Dev", "QA"],
            "Input": ["Req", "Code"],
            "Output": ["Design", "Test"],
            "Automation tool": ["Jira", "Jenkins"],
            "Output type": ["material", "material"],
            "node": [1, 2]
        }
        df = pd.DataFrame(data)
        
        self.builder._create_pydot_nodes(df)
        
        self.assertIn(0, self.builder.node_list)  # E0 node
        self.assertIn(1, self.builder.node_list)  # First row
        self.assertIn(2, self.builder.node_list)  # Second row

    def test_calculate_lead_times(self):
        data = {
            "S#": [1, 2],
            "Total time taken": [5, 3],
            "Manual time spent": [2, 1],
            "Predecessor 1 (incl. INIT)": [float("nan"), 1],
            "Predecessor 2 (optional)": [float("nan"), float("nan")],
            "Predecessor 3 (optional)": [float("nan"), float("nan")],
            "Predecessor 4 (optional)": [float("nan"), float("nan")],
            "Predecessor 5 (optional)": [float("nan"), float("nan")],
            "Criticality": ["hi", "med"],
            "Team / owner role": ["Dev", "QA"],
            "Input": ["Req", "Code"],
            "Output": ["Design", "Test"],
            "Automation tool": ["Jira", "Jenkins"],
            "Output type": ["material", "material"],
            "node": [1, 2]
        }
        df = pd.DataFrame(data)
        
        self.builder._create_pydot_nodes(df)
        self.builder._calculate_lead_times(df)
        
        # E1 time should be 5 (first row's total time)
        self.assertEqual(self.builder.node_list[1]["time"], 5.0)
        # E2 time should be 5 + 3 = 8 (pred E1's time + E2's time)
        self.assertEqual(self.builder.node_list[2]["time"], 8.0)

    def test_build_graph_creates_complete_network(self):
        data = {
            "S#": [1, 2],
            "Yes / No": ["Yes", "Yes"],
            "Total time taken": [5, 3],
            "Manual time spent": [2, 1],
            "Predecessor 1 (incl. INIT)": [float("nan"), 1],
            "Predecessor 2 (optional)": [float("nan"), float("nan")],
            "Predecessor 3 (optional)": [float("nan"), float("nan")],
            "Predecessor 4 (optional)": [float("nan"), float("nan")],
            "Predecessor 5 (optional)": [float("nan"), float("nan")],
            "Criticality": ["hi", "med"],
            "Team / owner role": ["Dev", "QA"],
            "Input": ["Req", "Code"],
            "Output": ["Design", "Test"],
            "Automation tool": ["Jira", "Jenkins"],
            "Output type": ["material", "material"]
        }
        df = pd.DataFrame(data)
        
        result = self.builder.build_graph(df)
        
        # Check that the graph was created
        self.assertIsNotNone(result)
        # Check that pydot nodes were created
        nodes = result.get_nodes()
        self.assertTrue(len(nodes) > 0)
        # Check that edges were created
        edges = result.get_edges()
        self.assertTrue(len(edges) > 0)
        # Check that networkx graph was created
        self.assertTrue(len(self.builder.qode_graph.nodes) > 0)


if __name__ == "__main__":
    unittest.main()