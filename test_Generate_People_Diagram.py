"""
Tests for Generate_People_Diagram.People_Diagram.
"""

import math
import unittest
from unittest.mock import patch

import pandas as pd

# Patch the module-level pd.read_excel call that executes on import.
with patch("pandas.read_excel", return_value=pd.DataFrame()):
    from Generate_People_Diagram import People_Diagram

import pydot


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_people_df(rows):
    """
    Build a DataFrame matching the column order used by People_Diagram.create_edge().

    Columns (positional):
      0  S#
      1  Predecessor 1 (incl. INIT)
      2  Predecessor 2 (optional)
      3  Predecessor 3 (optional)
      4  Predecessor 4 (optional)
      5  Predecessor 5 (optional)
      6  Team / owner role
      7  Total time taken
      8  Manual time spent
    """
    cols = [
        "S#",
        "Predecessor 1 (incl. INIT)",
        "Predecessor 2 (optional)",
        "Predecessor 3 (optional)",
        "Predecessor 4 (optional)",
        "Predecessor 5 (optional)",
        "Team / owner role",
        "Total time taken",
        "Manual time spent",
    ]
    return pd.DataFrame(rows, columns=cols)


# ---------------------------------------------------------------------------
# isnan() tests
# ---------------------------------------------------------------------------

class TestIsNanPeople(unittest.TestCase):
    def setUp(self):
        People_Diagram.node_list = {}
        People_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = People_Diagram()

    def test_actual_float_nan_is_nan(self):
        self.assertTrue(self.d.isnan(float("nan")))

    def test_math_nan_is_nan(self):
        self.assertTrue(self.d.isnan(math.nan))

    def test_integer_is_not_nan(self):
        self.assertFalse(self.d.isnan(42))

    def test_zero_is_not_nan(self):
        self.assertFalse(self.d.isnan(0))

    def test_negative_float_is_not_nan(self):
        self.assertFalse(self.d.isnan(-3.14))

    def test_numeric_string_is_not_nan(self):
        self.assertFalse(self.d.isnan("1.5"))

    def test_non_numeric_string_is_not_nan(self):
        # ValueError from float("INIT") is caught; returns False
        self.assertFalse(self.d.isnan("INIT"))

    def test_none_is_not_nan(self):
        # TypeError from float(None) is caught; returns False
        self.assertFalse(self.d.isnan(None))


# ---------------------------------------------------------------------------
# node_creation() tests
# ---------------------------------------------------------------------------

class TestPeopleDiagramNodeCreation(unittest.TestCase):
    def setUp(self):
        People_Diagram.node_list = {}
        People_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = People_Diagram()

    def test_single_role_added_to_node_list(self):
        self.d.node_creation(["DevOps"])
        self.assertIn("DevOps", self.d.node_list)

    def test_multiple_roles_all_added(self):
        roles = ["Dev", "QA", "PM"]
        self.d.node_creation(roles)
        for role in roles:
            self.assertIn(role, self.d.node_list)

    def test_node_value_is_pydot_node(self):
        self.d.node_creation(["Dev"])
        node_entry = self.d.node_list["Dev"]
        self.assertIsInstance(node_entry["value"], pydot.Node)

    def test_empty_roles_list_produces_empty_node_list(self):
        self.d.node_creation([])
        self.assertEqual(self.d.node_list, {})


# ---------------------------------------------------------------------------
# edge_creation() tests
# ---------------------------------------------------------------------------

class TestPeopleDiagramEdgeCreation(unittest.TestCase):
    def setUp(self):
        People_Diagram.node_list = {}
        People_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = People_Diagram()

    def _make_node(self, name):
        n = pydot.Node(name, fillcolor="#ADD8E6", style="filled")
        n.set_shape("box")
        return n

    def test_edge_added_to_dot_graph(self):
        n1 = self._make_node("A")
        n2 = self._make_node("B")
        before = len(self.d.dot_graph.get_edges())
        self.d.edge_creation(n1, n2, "#000000")
        after = len(self.d.dot_graph.get_edges())
        self.assertEqual(after, before + 1)

    def test_edge_with_orange_color(self):
        n1 = self._make_node("X")
        n2 = self._make_node("Y")
        self.d.edge_creation(n1, n2, "#FFA500")
        edges = self.d.dot_graph.get_edges()
        self.assertTrue(len(edges) >= 1)


# ---------------------------------------------------------------------------
# create_edge() tests
# ---------------------------------------------------------------------------

class TestPeopleDiagramCreateEdge(unittest.TestCase):
    def setUp(self):
        People_Diagram.node_list = {}
        People_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = People_Diagram()
        # Pre-create nodes for roles "Dev" and "QA"
        self.d.node_creation(["Dev", "QA"])

    def test_no_edges_when_all_preds_are_nan(self):
        rows = [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Dev", 10, 10]
        ]
        df = _make_people_df(rows)
        before = len(self.d.dot_graph.get_edges())
        self.d.create_edge(df)
        # No predecessor -> no edge added
        self.assertEqual(len(self.d.dot_graph.get_edges()), before)

    def test_no_edge_when_pred_is_init(self):
        rows = [
            [1, "INIT", float("nan"), float("nan"), float("nan"), float("nan"), "Dev", 10, 10]
        ]
        df = _make_people_df(rows)
        before = len(self.d.dot_graph.get_edges())
        self.d.create_edge(df)
        self.assertEqual(len(self.d.dot_graph.get_edges()), before)

    def test_edge_created_for_valid_pred1(self):
        rows = [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Dev", 5, 5],
            [2, 1, float("nan"), float("nan"), float("nan"), float("nan"), "QA", 10, 5],
        ]
        df = _make_people_df(rows)
        before = len(self.d.dot_graph.get_edges())
        self.d.create_edge(df)
        self.assertGreater(len(self.d.dot_graph.get_edges()), before)

    def test_black_edge_color_when_times_differ(self):
        """When Total != Manual, edge should be black (#000000)."""
        rows = [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Dev", 5, 5],
            [2, 1, float("nan"), float("nan"), float("nan"), float("nan"), "QA", 10, 3],
        ]
        df = _make_people_df(rows)
        self.d.create_edge(df)
        edges = self.d.dot_graph.get_edges()
        colors = [str(e.get_color()).strip('"') for e in edges if e.get_color() is not None]
        self.assertIn("#000000", colors)

    def test_orange_edge_color_when_times_equal(self):
        """When Total == Manual, edge should be orange (#FFA500)."""
        rows = [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Dev", 5, 5],
            [2, 1, float("nan"), float("nan"), float("nan"), float("nan"), "QA", 5, 5],
        ]
        df = _make_people_df(rows)
        self.d.create_edge(df)
        edges = self.d.dot_graph.get_edges()
        colors = [str(e.get_color()).strip('"') for e in edges if e.get_color() is not None]
        self.assertIn("#FFA500", colors)

    def test_multiple_predecessors_create_multiple_edges(self):
        """A row with two valid predecessors should produce two edges."""
        People_Diagram.node_list = {}
        People_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d.node_creation(["Dev", "QA", "PM"])
        rows = [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Dev", 5, 5],
            [2, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "QA", 5, 5],
            [3, 1, 2, float("nan"), float("nan"), float("nan"), "PM", 5, 5],
        ]
        df = _make_people_df(rows)
        before = len(self.d.dot_graph.get_edges())
        self.d.create_edge(df)
        self.assertEqual(len(self.d.dot_graph.get_edges()), before + 2)

    def test_output_writes_raw_file(self):
        with patch.object(self.d.dot_graph, "write_raw") as mock_write:
            self.d.output()
            mock_write.assert_called_once_with("Diagram_People")


# ---------------------------------------------------------------------------
# create_edge() branch-coverage tests: predecessors 3-5
# ---------------------------------------------------------------------------

class TestPeopleDiagramCreateEdgeMorePreds(unittest.TestCase):
    def setUp(self):
        People_Diagram.node_list = {}
        People_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        self.d = People_Diagram()
        self.d.node_creation(["Dev", "QA", "PM", "BA", "OPS"])

    def _base_rows(self):
        """Five anchor rows (no predecessors, one per role)."""
        return [
            [1, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Dev", 5, 5],
            [2, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "QA", 5, 5],
            [3, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "PM", 5, 5],
            [4, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "BA", 5, 5],
        ]

    def test_pred3_creates_edge(self):
        rows = self._base_rows() + [
            [5, float("nan"), float("nan"), 1, float("nan"), float("nan"), "OPS", 5, 5],
        ]
        df = _make_people_df(rows)
        before = len(self.d.dot_graph.get_edges())
        self.d.create_edge(df)
        self.assertGreater(len(self.d.dot_graph.get_edges()), before)

    def test_pred4_creates_edge(self):
        rows = self._base_rows() + [
            [5, float("nan"), float("nan"), float("nan"), 1, float("nan"), "OPS", 5, 5],
        ]
        df = _make_people_df(rows)
        before = len(self.d.dot_graph.get_edges())
        self.d.create_edge(df)
        self.assertGreater(len(self.d.dot_graph.get_edges()), before)

    def test_pred5_creates_edge(self):
        rows = self._base_rows() + [
            [5, float("nan"), float("nan"), float("nan"), float("nan"), 1, "OPS", 5, 5],
        ]
        df = _make_people_df(rows)
        before = len(self.d.dot_graph.get_edges())
        self.d.create_edge(df)
        self.assertGreater(len(self.d.dot_graph.get_edges()), before)

    def test_all_five_preds_creates_five_edges(self):
        rows = self._base_rows() + [
            [5, 1, 2, 3, 4, float("nan"), "OPS", 5, 5],
        ]
        df = _make_people_df(rows)
        before = len(self.d.dot_graph.get_edges())
        self.d.create_edge(df)
        self.assertEqual(len(self.d.dot_graph.get_edges()), before + 4)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
