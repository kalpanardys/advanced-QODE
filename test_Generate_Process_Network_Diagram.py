"""
Tests for Generate_Process_Network_Diagram.Process_Diagram.
"""

import unittest
from unittest.mock import patch

import pandas as pd
import networkx as nx

# Patch the module-level pd.read_excel call that executes on import.
with patch("pandas.read_excel", return_value=pd.DataFrame()):
    from Generate_Process_Network_Diagram import Process_Diagram

import pydot


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_process_df(rows, node_col=None):
    """
    Build a DataFrame matching the column order used by Process_Diagram
    methods that operate on final_df.

    Columns (positional):
      0   S#
      1   Yes / No
      2   Total time taken
      3   Manual time spent
      4   Predecessor 1 (incl. INIT)
      5   Predecessor 2 (optional)
      6   Predecessor 3 (optional)
      7   Predecessor 4 (optional)
      8   Predecessor 5 (optional)
      9   Criticality
      10  Team / owner role
      11  Input
      12  Output
      13  Automation tool
      14  Output type
      15  node            (added by create_network_diagram before calling helpers)
    """
    cols = [
        "S#",
        "Yes / No",
        "Total time taken",
        "Manual time spent",
        "Predecessor 1 (incl. INIT)",
        "Predecessor 2 (optional)",
        "Predecessor 3 (optional)",
        "Predecessor 4 (optional)",
        "Predecessor 5 (optional)",
        "Criticality",
        "Team / owner role",
        "Input",
        "Output",
        "Automation tool",
        "Output type",
    ]
    df = pd.DataFrame(rows, columns=cols)
    if node_col is not None:
        df["node"] = node_col
    return df


# ---------------------------------------------------------------------------
# isnan() tests
# ---------------------------------------------------------------------------

class TestIsNanProcess(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def test_actual_float_nan_is_nan(self):
        self.assertTrue(self.d.isnan(float("nan")))

    def test_integer_is_not_nan(self):
        self.assertFalse(self.d.isnan(10))

    def test_non_numeric_string_is_not_nan(self):
        self.assertFalse(self.d.isnan("hello"))


# ---------------------------------------------------------------------------
# criticality_mapping() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramCriticalityMapping(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def test_hi_lowercase_returns_3(self):
        self.assertEqual(self.d.criticality_mapping("hi"), 3)

    def test_hi_uppercase_returns_3(self):
        self.assertEqual(self.d.criticality_mapping("HI"), 3)

    def test_hi_mixed_case_returns_3(self):
        self.assertEqual(self.d.criticality_mapping("Hi"), 3)

    def test_med_lowercase_returns_2(self):
        self.assertEqual(self.d.criticality_mapping("med"), 2)

    def test_med_uppercase_returns_2(self):
        self.assertEqual(self.d.criticality_mapping("MED"), 2)

    def test_low_returns_1(self):
        self.assertEqual(self.d.criticality_mapping("low"), 1)

    def test_unknown_value_returns_1(self):
        self.assertEqual(self.d.criticality_mapping("unknown"), 1)

    def test_empty_string_returns_1(self):
        self.assertEqual(self.d.criticality_mapping(""), 1)


# ---------------------------------------------------------------------------
# node_creation() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramNodeCreation(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def test_node_creation_returns_pydot_node(self):
        node = self.d.node_creation("E1", "#ADD8E6", "filled", "box")
        self.assertIsInstance(node, pydot.Node)

    def test_node_added_to_dot_graph(self):
        before = len(self.d.dot_graph.get_nodes())
        self.d.node_creation("E2", "#FFFFFF", "filled", "ellipse")
        after = len(self.d.dot_graph.get_nodes())
        self.assertEqual(after, before + 1)

    def test_multiple_nodes_all_added(self):
        before = len(self.d.dot_graph.get_nodes())
        self.d.node_creation("E3", "#ADD8E6", "filled", "box")
        self.d.node_creation("E4", "#ADD8E6", "filled", "box")
        after = len(self.d.dot_graph.get_nodes())
        self.assertEqual(after, before + 2)


# ---------------------------------------------------------------------------
# edge_creation() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramEdgeCreation(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def test_edge_added_to_dot_graph(self):
        n1 = self.d.node_creation("E0", "#ADD8E6", "filled", "box")
        n2 = self.d.node_creation("E1", "#ADD8E6", "filled", "box")
        before = len(self.d.dot_graph.get_edges())
        self.d.edge_creation("A1\n5,2(0)\ntool", n1, n2)
        after = len(self.d.dot_graph.get_edges())
        self.assertEqual(after, before + 1)


# ---------------------------------------------------------------------------
# calculate_lead_time() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramCalculateLeadTime(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def _base_node_list(self):
        return {
            1: {"value": None, "time": 0, "node_no": "E1"},
            2: {"value": None, "time": 0, "node_no": "E2"},
        }

    def test_first_node_time_set_from_first_row(self):
        """node_list[1]["time"] must equal the first row's total-time column."""
        rows = [
            [1, "Yes", 5.0, 2.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "tool", "material"],
        ]
        df = _make_process_df(rows, node_col=[1])
        nl = self._base_node_list()
        self.d.calculate_lead_time(df, nl)
        self.assertEqual(nl[1]["time"], 5.0)

    def test_successor_time_accumulates_from_init(self):
        """A node whose pred is INIT (not node 1) gets its time = its own time + node1 time."""
        rows = [
            [1, "Yes", 3.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "tool", "material"],
            [2, "Yes", 4.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "med", "QA", "in", "out", "tool", "material"],
        ]
        df = _make_process_df(rows, node_col=[1, 2])
        nl = {
            1: {"value": None, "time": 0, "node_no": "E1"},
            2: {"value": None, "time": 0, "node_no": "E2"},
        }
        self.d.calculate_lead_time(df, nl)
        # Node 2 has pred INIT => time = 4.0 + nl[1]["time"]=3.0 => 7.0
        self.assertAlmostEqual(nl[2]["time"], 7.0)

    def test_successor_time_uses_predecessor_time(self):
        """A node with a numeric predecessor takes max(own_time + pred_time)."""
        rows = [
            [1, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "tool", "material"],
            [2, "Yes", 3.0, 1.0, 1, float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "QA", "in", "out", "tool", "material"],
        ]
        df = _make_process_df(rows, node_col=[1, 2])
        nl = {
            1: {"value": None, "time": 2.0, "node_no": "E1"},
            2: {"value": None, "time": 0.0, "node_no": "E2"},
        }
        self.d.calculate_lead_time(df, nl)
        # Node 2: time = 3.0 + nl[1]["time"]=2.0 = 5.0
        self.assertAlmostEqual(nl[2]["time"], 5.0)

    def test_nan_predecessor_not_processed(self):
        """Rows with all-NaN predecessors should leave successor time unchanged."""
        rows = [
            [1, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "tool", "material"],
        ]
        df = _make_process_df(rows, node_col=[1])
        nl = {1: {"value": None, "time": 0.0, "node_no": "E1"}}
        self.d.calculate_lead_time(df, nl)
        self.assertAlmostEqual(nl[1]["time"], 2.0)


# ---------------------------------------------------------------------------
# find_leafnodes() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramFindLeafNodes(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def test_single_linear_chain(self):
        G = nx.DiGraph()
        G.add_edges_from([("E0", "E1"), ("E1", "E2")])
        leaves = self.d.find_leafnodes(G)
        self.assertIn("E2", leaves)
        self.assertNotIn("E0", leaves)
        self.assertNotIn("E1", leaves)

    def test_branching_graph_two_leaves(self):
        G = nx.DiGraph()
        G.add_edges_from([("E0", "E1"), ("E0", "E2")])
        leaves = self.d.find_leafnodes(G)
        self.assertIn("E1", leaves)
        self.assertIn("E2", leaves)

    def test_isolated_node_not_leaf(self):
        """An isolated node has no ancestors with no incoming edges -> not a leaf."""
        G = nx.DiGraph()
        G.add_node("E0")
        leaves = self.d.find_leafnodes(G)
        self.assertNotIn("E0", leaves)

    def test_empty_graph(self):
        G = nx.DiGraph()
        leaves = self.d.find_leafnodes(G)
        self.assertEqual(leaves, [])


# ---------------------------------------------------------------------------
# new_avg_criticality() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramNewAvgCriticality(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def _build_graph(self, edges):
        """edges: list of (src, dst, time, criticality, label)."""
        for src, dst, t, crit, lbl in edges:
            self.d.Qode_graph.add_edge(src, dst, weight=[t, crit, lbl])

    def test_single_edge_path(self):
        self._build_graph([("E0", "E1", 5, 3, "A1")])
        result = self.d.new_avg_criticality(["E0", "E1"])
        self.assertAlmostEqual(result, 3.0)

    def test_two_edge_path_average(self):
        self._build_graph([
            ("E0", "E1", 3, 3, "A1"),
            ("E1", "E2", 2, 1, "A2"),
        ])
        result = self.d.new_avg_criticality(["E0", "E1", "E2"])
        self.assertAlmostEqual(result, 2.0)  # (3+1)/2

    def test_three_edge_path_average(self):
        self._build_graph([
            ("E0", "E1", 1, 3, "A1"),
            ("E1", "E2", 1, 2, "A2"),
            ("E2", "E3", 1, 1, "A3"),
        ])
        result = self.d.new_avg_criticality(["E0", "E1", "E2", "E3"])
        self.assertAlmostEqual(result, 2.0)  # (3+2+1)/3


# ---------------------------------------------------------------------------
# node_to_edge() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramNodeToEdge(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def _build_graph(self, edges):
        for src, dst, lbl in edges:
            self.d.Qode_graph.add_edge(src, dst, weight=[1, 1, lbl])

    def test_single_edge_returns_one_label(self):
        self._build_graph([("E0", "E1", "A1")])
        result = self.d.node_to_edge(["E0", "E1"])
        self.assertEqual(result, ["A1"])

    def test_two_edges_returns_two_labels(self):
        self._build_graph([("E0", "E1", "A1"), ("E1", "E2", "A2")])
        result = self.d.node_to_edge(["E0", "E1", "E2"])
        self.assertEqual(result, ["A1", "A2"])

    def test_single_node_path_returns_empty(self):
        result = self.d.node_to_edge(["E0"])
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# find_critical_paths() integration tests
# ---------------------------------------------------------------------------

class TestProcessDiagramFindCriticalPaths(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def _simple_two_node_setup(self):
        """
        Simple graph: E0 → E1
        One material leaf, one critical path.
        """
        rows = [
            [1, "Yes", 5.0, 2.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "tool", "material"],
        ]
        df = _make_process_df(rows, node_col=[1])
        node_list = {
            0: {"value": None, "time": 0, "node_no": "E0"},
            1: {"value": None, "time": 5.0, "node_no": "E1"},
        }
        self.d.Qode_graph.add_node("E0")
        self.d.Qode_graph.add_node("E1")
        self.d.Qode_graph.add_edge("E0", "E1", weight=[5.0, 3, "A1"])
        return df, node_list

    def test_critical_path_returns_list(self):
        df, nl = self._simple_two_node_setup()
        result = self.d.find_critical_paths(df, nl)
        self.assertIsInstance(result, list)

    def test_critical_path_contains_correct_edge_label(self):
        df, nl = self._simple_two_node_setup()
        result = self.d.find_critical_paths(df, nl)
        # Result is a list of edge-label lists; should contain "A1"
        all_labels = [label for path_labels in result for label in path_labels]
        self.assertIn("A1", all_labels)

    def test_output_writes_raw_file(self):
        with patch.object(self.d.dot_graph, "write_raw") as mock_write:
            self.d.output([])
            mock_write.assert_called_once_with("Diagram_Network")


# ---------------------------------------------------------------------------
# calculate_lead_time() branch-coverage tests: predecessors 2-5
# ---------------------------------------------------------------------------

class TestProcessDiagramCalculateLeadTimeMorePreds(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def _row(self, s_no, total, pred1=float("nan"), pred2=float("nan"),
             pred3=float("nan"), pred4=float("nan"), pred5=float("nan")):
        return [s_no, "Yes", total, 1.0, pred1, pred2, pred3, pred4, pred5,
                "hi", "Dev", "in", "out", "tool", "material"]

    def test_pred2_updates_time(self):
        rows = [
            self._row(1, 2.0, "INIT"),
            self._row(2, 5.0, "INIT"),
            self._row(3, 3.0, pred2=1),
        ]
        df = _make_process_df(rows, node_col=[1, 2, 3])
        nl = {
            1: {"value": None, "time": 2.0, "node_no": "E1"},
            2: {"value": None, "time": 5.0, "node_no": "E2"},
            3: {"value": None, "time": 0.0, "node_no": "E3"},
        }
        self.d.calculate_lead_time(df, nl)
        # node 3 via pred2=node1: time = 3.0 + 2.0 = 5.0
        self.assertAlmostEqual(nl[3]["time"], 5.0)

    def test_pred3_updates_time(self):
        rows = [
            self._row(1, 2.0, "INIT"),
            self._row(2, 5.0, "INIT"),
            self._row(3, 3.0, pred3=1),
        ]
        df = _make_process_df(rows, node_col=[1, 2, 3])
        nl = {
            1: {"value": None, "time": 2.0, "node_no": "E1"},
            2: {"value": None, "time": 5.0, "node_no": "E2"},
            3: {"value": None, "time": 0.0, "node_no": "E3"},
        }
        self.d.calculate_lead_time(df, nl)
        self.assertAlmostEqual(nl[3]["time"], 5.0)

    def test_pred4_updates_time(self):
        rows = [
            self._row(1, 2.0, "INIT"),
            self._row(2, 5.0, "INIT"),
            self._row(3, 3.0, pred4=1),
        ]
        df = _make_process_df(rows, node_col=[1, 2, 3])
        nl = {
            1: {"value": None, "time": 2.0, "node_no": "E1"},
            2: {"value": None, "time": 5.0, "node_no": "E2"},
            3: {"value": None, "time": 0.0, "node_no": "E3"},
        }
        self.d.calculate_lead_time(df, nl)
        self.assertAlmostEqual(nl[3]["time"], 5.0)

    def test_pred5_updates_time(self):
        rows = [
            self._row(1, 2.0, "INIT"),
            self._row(2, 5.0, "INIT"),
            self._row(3, 3.0, pred5=1),
        ]
        df = _make_process_df(rows, node_col=[1, 2, 3])
        nl = {
            1: {"value": None, "time": 2.0, "node_no": "E1"},
            2: {"value": None, "time": 5.0, "node_no": "E2"},
            3: {"value": None, "time": 0.0, "node_no": "E3"},
        }
        self.d.calculate_lead_time(df, nl)
        self.assertAlmostEqual(nl[3]["time"], 5.0)

    def test_maximum_time_wins_over_multiple_preds(self):
        """When a node has two predecessors, its accumulated time is at least
        the sum of its own time and the maximum predecessor time."""
        rows = [
            self._row(1, 2.0, "INIT"),
            self._row(2, 8.0, "INIT"),
            self._row(3, 1.0, pred1=1, pred2=2),
        ]
        df = _make_process_df(rows, node_col=[1, 2, 3])
        nl = {
            1: {"value": None, "time": 2.0, "node_no": "E1"},
            2: {"value": None, "time": 8.0, "node_no": "E2"},
            3: {"value": None, "time": 0.0, "node_no": "E3"},
        }
        self.d.calculate_lead_time(df, nl)
        # node 3 receives time from both predecessors; final value >= max(1+2, 1+8)=9
        self.assertGreaterEqual(nl[3]["time"], 9.0)


# ---------------------------------------------------------------------------
# pydot_node_creation() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramPydotNodeCreation(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def _row(self, s_no, input_val="in", output_val="out", tool="Jira"):
        return [s_no, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
                "hi", "Dev", input_val, output_val, tool, "material"]

    def test_pydot_node_creation_adds_e0_entry(self):
        rows = [self._row(1)]
        df = _make_process_df(rows, node_col=[1])
        self.d.pydot_node_creation(df)
        self.assertIn(0, self.d.node_list)

    def test_pydot_node_creation_adds_row_entries(self):
        rows = [self._row(1), self._row(2)]
        df = _make_process_df(rows, node_col=[1, 2])
        self.d.pydot_node_creation(df)
        self.assertIn(1, self.d.node_list)
        self.assertIn(2, self.d.node_list)

    def test_pydot_node_creation_values_are_pydot_nodes(self):
        rows = [self._row(1)]
        df = _make_process_df(rows, node_col=[1])
        self.d.pydot_node_creation(df)
        self.assertIsInstance(self.d.node_list[0]["value"], pydot.Node)
        self.assertIsInstance(self.d.node_list[1]["value"], pydot.Node)


# ---------------------------------------------------------------------------
# networkX_node_creation() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramNetworkXNodeCreation(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def test_networkx_node_creation_adds_e0(self):
        rows = [
            [1, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "tool", "material"]
        ]
        df = _make_process_df(rows, node_col=[1])
        self.d.networkX_node_creation(df)
        self.assertIn("E0", self.d.Qode_graph.nodes)
        self.assertIn("E1", self.d.Qode_graph.nodes)

    def test_networkx_node_creation_multiple_nodes(self):
        rows = [
            [1, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "tool", "material"],
            [2, "Yes", 3.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "QA", "in", "out", "tool", "material"],
        ]
        df = _make_process_df(rows, node_col=[1, 2])
        self.d.networkX_node_creation(df)
        self.assertIn("E1", self.d.Qode_graph.nodes)
        self.assertIn("E2", self.d.Qode_graph.nodes)


# ---------------------------------------------------------------------------
# pydot_edge_creation() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramPydotEdgeCreation(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def _build_node_list(self, ids):
        nl = {}
        for i in ids:
            n = self.d.node_creation(f"E{i}", "#ADD8E6", "filled", "box")
            nl[i] = {"value": n, "time": float(i), "node_no": f"E{i}"}
        return nl

    def test_pydot_edge_creation_adds_initial_edge(self):
        rows = [
            [1, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "Jira", "material"],
        ]
        df = _make_process_df(rows, node_col=[1])
        nl = self._build_node_list([0, 1])
        before = len(self.d.dot_graph.get_edges())
        self.d.pydot_edge_creation(df, nl)
        self.assertGreater(len(self.d.dot_graph.get_edges()), before)

    def test_pydot_edge_creation_init_predecessor(self):
        """A row with pred1=INIT and node!=1 should add an extra edge."""
        rows = [
            [1, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "Jira", "material"],
            [2, "Yes", 3.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "QA", "in", "out", "Jira", "material"],
        ]
        df = _make_process_df(rows, node_col=[1, 2])
        nl = self._build_node_list([0, 1, 2])
        before = len(self.d.dot_graph.get_edges())
        self.d.pydot_edge_creation(df, nl)
        # Should produce at least: E0->E1, E1->E2
        self.assertGreaterEqual(len(self.d.dot_graph.get_edges()), before + 2)

    def test_pydot_edge_creation_numeric_predecessor(self):
        """A row with a numeric pred1 adds an edge from pred to current."""
        rows = [
            [1, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "Jira", "material"],
            [2, "Yes", 3.0, 1.0, 1, float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "QA", "in", "out", "Jira", "material"],
        ]
        df = _make_process_df(rows, node_col=[1, 2])
        nl = self._build_node_list([0, 1, 2])
        before = len(self.d.dot_graph.get_edges())
        self.d.pydot_edge_creation(df, nl)
        self.assertGreater(len(self.d.dot_graph.get_edges()), before)


# ---------------------------------------------------------------------------
# networkX_edge_creation() tests
# ---------------------------------------------------------------------------

class TestProcessDiagramNetworkXEdgeCreation(unittest.TestCase):
    def setUp(self):
        Process_Diagram.node_list = {}
        Process_Diagram.dot_graph = pydot.Dot(graph_type="digraph")
        Process_Diagram.Qode_graph = nx.DiGraph()
        self.d = Process_Diagram()

    def test_networkx_edge_creation_init_adds_edge(self):
        rows = [
            [1, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "Jira", "material"],
        ]
        df = _make_process_df(rows, node_col=[1])
        self.d.Qode_graph.add_node("E0")
        self.d.Qode_graph.add_node("E1")
        self.d.networkX_edge_creation(df)
        self.assertIn(("E0", "E1"), self.d.Qode_graph.edges)

    def test_networkx_edge_creation_numeric_pred(self):
        rows = [
            [1, "Yes", 2.0, 1.0, "INIT", float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "Dev", "in", "out", "Jira", "material"],
            [2, "Yes", 3.0, 1.0, 1, float("nan"), float("nan"), float("nan"), float("nan"),
             "hi", "QA", "in", "out", "Jira", "material"],
        ]
        df = _make_process_df(rows, node_col=[1, 2])
        for node in ["E0", "E1", "E2"]:
            self.d.Qode_graph.add_node(node)
        self.d.networkX_edge_creation(df)
        # E1->E2 edge should exist
        self.assertIn(("E1", "E2"), self.d.Qode_graph.edges)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
