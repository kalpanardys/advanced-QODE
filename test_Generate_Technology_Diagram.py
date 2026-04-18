"""
Tests for Generate_Technology_Diagram.Technology_Diagram.
"""

import unittest
from unittest.mock import patch

import pandas as pd

# Patch the module-level pd.read_excel call that executes on import.
with patch("pandas.read_excel", return_value=pd.DataFrame()):
    from Generate_Technology_Diagram import Technology_Diagram

import pydot


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_tech_df(rows):
    """
    Build a DataFrame matching the column order used by Technology_Diagram.create_edge().

    Columns (positional):
      0  S#
      1  Predecessor 1 (incl. INIT)
      2  Predecessor 2 (optional)
      3  Predecessor 3 (optional)
      4  Predecessor 4 (optional)
      5  Predecessor 5 (optional)
      6  Automation tool
    """
    cols = [
        "S#",
        "Predecessor 1 (incl. INIT)",
        "Predecessor 2 (optional)",
        "Predecessor 3 (optional)",
        "Predecessor 4 (optional)",
        "Predecessor 5 (optional)",
        "Automation tool",
    ]
    return pd.DataFrame(rows, columns=cols)


# ---------------------------------------------------------------------------
# isnan() tests
# ---------------------------------------------------------------------------

class TestIsNanTech(unittest.TestCase):
    def setUp(self):
        Technology_Diagram.node_list = {}
        Technology_Diagram.edge_list = []
        Technology_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = Technology_Diagram()

    def test_actual_float_nan_is_nan(self):
        self.assertTrue(self.d.isnan(float("nan")))

    def test_string_number_is_not_nan(self):
        self.assertFalse(self.d.isnan("3"))

    def test_non_numeric_string_is_not_nan(self):
        self.assertFalse(self.d.isnan("tool"))


# ---------------------------------------------------------------------------
# node_creation() tests
# ---------------------------------------------------------------------------

class TestTechnologyDiagramNodeCreation(unittest.TestCase):
    def setUp(self):
        Technology_Diagram.node_list = {}
        Technology_Diagram.edge_list = []
        Technology_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = Technology_Diagram()

    def test_single_tool_added_to_node_list(self):
        self.d.node_creation(["Jira"])
        self.assertIn("Jira", self.d.node_list)

    def test_multiple_tools_all_added(self):
        tools = ["Jira", "Jenkins", "Confluence"]
        self.d.node_creation(tools)
        for tool in tools:
            self.assertIn(tool, self.d.node_list)

    def test_node_value_is_pydot_node(self):
        self.d.node_creation(["Jira"])
        self.assertIsInstance(self.d.node_list["Jira"]["value"], pydot.Node)

    def test_empty_tools_list_produces_empty_node_list(self):
        self.d.node_creation([])
        self.assertEqual(self.d.node_list, {})

    def test_nodes_added_to_dot_graph(self):
        before = len(self.d.dot_graph.get_nodes())
        self.d.node_creation(["ToolA", "ToolB"])
        after = len(self.d.dot_graph.get_nodes())
        self.assertEqual(after, before + 2)


# ---------------------------------------------------------------------------
# check_edge_present() tests
# ---------------------------------------------------------------------------

class TestTechnologyDiagramCheckEdgePresent(unittest.TestCase):
    def setUp(self):
        Technology_Diagram.node_list = {}
        Technology_Diagram.edge_list = []
        Technology_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = Technology_Diagram()

    def _make_pydot_node(self, name):
        n = pydot.Node(name, fillcolor="#ADD8E6", style="filled")
        return n

    def test_new_edge_added_to_edge_list(self):
        n1 = self._make_pydot_node("A")
        n2 = self._make_pydot_node("B")
        self.d.check_edge_present("A1", n1, n2)
        self.assertEqual(len(self.d.edge_list), 1)
        self.assertEqual(self.d.edge_list[0]["label"], "A1")

    def test_duplicate_edge_label_appended_not_duplicated(self):
        n1 = self._make_pydot_node("A")
        n2 = self._make_pydot_node("B")
        self.d.check_edge_present("A1", n1, n2)
        self.d.check_edge_present("A2", n1, n2)
        # Same head/tail -> should still be one entry with concatenated label
        self.assertEqual(len(self.d.edge_list), 1)
        self.assertIn("A2", self.d.edge_list[0]["label"])

    def test_different_direction_creates_new_entry(self):
        n1 = self._make_pydot_node("A")
        n2 = self._make_pydot_node("B")
        self.d.check_edge_present("A1", n1, n2)
        # Reversed direction: head=n2, tail=n1
        self.d.check_edge_present("A2", n2, n1)
        self.assertEqual(len(self.d.edge_list), 2)

    def test_different_tail_creates_new_entry(self):
        n1 = self._make_pydot_node("A")
        n2 = self._make_pydot_node("B")
        n3 = self._make_pydot_node("C")
        self.d.check_edge_present("A1", n1, n2)
        self.d.check_edge_present("A2", n1, n3)
        self.assertEqual(len(self.d.edge_list), 2)


# ---------------------------------------------------------------------------
# edge_creation() tests
# ---------------------------------------------------------------------------

class TestTechnologyDiagramEdgeCreation(unittest.TestCase):
    def setUp(self):
        Technology_Diagram.node_list = {}
        Technology_Diagram.edge_list = []
        Technology_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = Technology_Diagram()

    def test_edge_added_to_dot_graph(self):
        n1 = pydot.Node("ToolA")
        n2 = pydot.Node("ToolB")
        before = len(self.d.dot_graph.get_edges())
        self.d.edge_creation("A1", n1, n2)
        after = len(self.d.dot_graph.get_edges())
        self.assertEqual(after, before + 1)


# ---------------------------------------------------------------------------
# create_edge() tests
# ---------------------------------------------------------------------------

class TestTechnologyDiagramCreateEdge(unittest.TestCase):
    def setUp(self):
        Technology_Diagram.node_list = {}
        Technology_Diagram.edge_list = []
        Technology_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = Technology_Diagram()
        self.d.node_creation(["Jira", "Jenkins"])

    def test_no_edges_when_all_preds_nan(self):
        rows = [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Jira"]
        ]
        df = _make_tech_df(rows)
        self.d.create_edge(df)
        self.assertEqual(len(self.d.edge_list), 0)

    def test_no_edge_when_pred_is_init(self):
        rows = [
            [1, "INIT", float("nan"), float("nan"), float("nan"), float("nan"), "Jira"]
        ]
        df = _make_tech_df(rows)
        self.d.create_edge(df)
        self.assertEqual(len(self.d.edge_list), 0)

    def test_edge_created_for_valid_pred1(self):
        rows = [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Jira"],
            [2, 1, float("nan"), float("nan"), float("nan"), float("nan"), "Jenkins"],
        ]
        df = _make_tech_df(rows)
        self.d.create_edge(df)
        self.assertEqual(len(self.d.edge_list), 1)

    def test_edge_label_contains_activity_number(self):
        rows = [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Jira"],
            [2, 1, float("nan"), float("nan"), float("nan"), float("nan"), "Jenkins"],
        ]
        df = _make_tech_df(rows)
        self.d.create_edge(df)
        self.assertIn("A1", self.d.edge_list[0]["label"])

    def test_multiple_predecessors_two_separate_edges_or_merged(self):
        Technology_Diagram.node_list = {}
        Technology_Diagram.edge_list = []
        Technology_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d.node_creation(["Jira", "Jenkins", "Confluence"])
        rows = [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Jira"],
            [2, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Jenkins"],
            [3, 1, 2, float("nan"), float("nan"), float("nan"), "Confluence"],
        ]
        df = _make_tech_df(rows)
        self.d.create_edge(df)
        # Two distinct source tools -> two edge-list entries
        self.assertEqual(len(self.d.edge_list), 2)

    def test_output_writes_raw_file(self):
        with patch.object(self.d.dot_graph, "write_raw") as mock_write:
            self.d.output()
            mock_write.assert_called_once_with("Diagram_Technology")


# ---------------------------------------------------------------------------
# create_edge() branch-coverage tests: predecessors 3-5
# ---------------------------------------------------------------------------

class TestTechnologyDiagramCreateEdgeMorePreds(unittest.TestCase):
    def setUp(self):
        Technology_Diagram.node_list = {}
        Technology_Diagram.edge_list = []
        Technology_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = Technology_Diagram()
        self.d.node_creation(["Jira", "Jenkins", "Confluence", "GitLab", "Sonar"])

    def _anchor_rows(self):
        return [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Jira"],
            [2, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Jenkins"],
            [3, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Confluence"],
            [4, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "GitLab"],
        ]

    def test_pred3_creates_entry(self):
        rows = self._anchor_rows() + [
            [5, float("nan"), float("nan"), 1, float("nan"), float("nan"), "Sonar"],
        ]
        df = _make_tech_df(rows)
        self.d.create_edge(df)
        self.assertEqual(len(self.d.edge_list), 1)

    def test_pred4_creates_entry(self):
        rows = self._anchor_rows() + [
            [5, float("nan"), float("nan"), float("nan"), 1, float("nan"), "Sonar"],
        ]
        df = _make_tech_df(rows)
        self.d.create_edge(df)
        self.assertEqual(len(self.d.edge_list), 1)

    def test_pred5_creates_entry(self):
        rows = self._anchor_rows() + [
            [5, float("nan"), float("nan"), float("nan"), float("nan"), 1, "Sonar"],
        ]
        df = _make_tech_df(rows)
        self.d.create_edge(df)
        self.assertEqual(len(self.d.edge_list), 1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
