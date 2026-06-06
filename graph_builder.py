"""
Graph builder module - constructs dependency graphs from Excel data.
Builds NetworkX graphs representing role, tool, and process relationships.
"""

import networkx as nx
import pandas as pd
from utils import load_qode_data, get_predecessors, get_predecessor_role
from entity_loader import EntityLoader
import re


class GraphBuilder:
    """Build dependency graphs from QODE Excel data."""

    def __init__(self, file_path="sample_questions.xlsm"):
        self.file_path = file_path
        self.df = None
        self.role_graph = None
        self.tool_graph = None
        self.process_graph = None
        self.pillar_graph = None
        self._load_data()

    def _load_data(self):
        """Load data from Excel file."""
        try:
            self.df = load_qode_data(self.file_path)
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def build_role_graph(self):
        """Build a graph of role dependencies."""
        self.role_graph = nx.DiGraph()

        if self.df is None or "Team / owner role" not in self.df.columns:
            return self.role_graph

        # Add nodes
        roles = self.df["Team / owner role"].unique()
        for role in roles:
            if pd.notna(role):
                self.role_graph.add_node(str(role), type="role")

        # Add edges based on process predecessors
        for idx, row in self.df.iterrows():
            current_role = row.get("Team / owner role")
            if pd.isna(current_role):
                continue

            current_role = str(current_role)
            preds = get_predecessors(row)

            for pred in preds:
                try:
                    pred_role = get_predecessor_role(self.df, pred, "Team / owner role")
                    pred_role = str(pred_role)
                    if pred_role in self.role_graph and current_role in self.role_graph:
                        self.role_graph.add_edge(
                            pred_role, current_role, label=f"Process flow", weight=1
                        )
                except Exception:
                    pass

        return self.role_graph

    def build_tool_graph(self):
        """Build a graph of tool dependencies."""
        self.tool_graph = nx.DiGraph()

        if self.df is None or "Automation tool" not in self.df.columns:
            return self.tool_graph

        # Add nodes
        tools = self.df["Automation tool"].unique()
        for tool in tools:
            if pd.notna(tool):
                self.tool_graph.add_node(str(tool), type="tool")

        # Add edges based on process predecessors
        for idx, row in self.df.iterrows():
            current_tool = row.get("Automation tool")
            if pd.isna(current_tool):
                continue

            current_tool = str(current_tool)
            preds = get_predecessors(row)

            for pred in preds:
                try:
                    pred_tool = get_predecessor_role(self.df, pred, "Automation tool")
                    pred_tool = str(pred_tool)
                    if pred_tool in self.tool_graph and current_tool in self.tool_graph:
                        self.tool_graph.add_edge(
                            pred_tool, current_tool, label="Integration", weight=1
                        )
                except Exception:
                    pass

        return self.tool_graph

    def build_process_graph(self):
        """Build a graph of process dependencies."""
        self.process_graph = nx.DiGraph()

        if self.df is None or ("Input" not in self.df.columns and "Output" not in self.df.columns):
            return self.process_graph

        # Create process nodes from Input and Output
        processes = set()
        if "Input" in self.df.columns:
            processes.update(self.df["Input"].dropna().unique())
        if "Output" in self.df.columns:
            processes.update(self.df["Output"].dropna().unique())

        for process in processes:
            if pd.notna(process):
                self.process_graph.add_node(str(process), type="process")

        # Add edges: Input -> Output for each row
        for idx, row in self.df.iterrows():
            input_proc = row.get("Input")
            output_proc = row.get("Output")

            if pd.notna(input_proc) and pd.notna(output_proc):
                input_proc = str(input_proc)
                output_proc = str(output_proc)
                if input_proc in self.process_graph and output_proc in self.process_graph:
                    self.process_graph.add_edge(input_proc, output_proc, label="Flow", weight=1)

        return self.process_graph

    def build_pillar_graph(self):
        """Build a graph of pillars and their relationships to processes, roles and tools."""
        self.pillar_graph = nx.DiGraph()

        # Load pillars from EntityLoader (which reads the same Excel file)
        try:
            loader = EntityLoader(self.file_path)
            pillars = list(loader.get_all_entities().get("pillars", []))
        except Exception:
            pillars = ["Governance", "Security", "Compliance", "Reliability", "Performance", "Cost", "Quality", "Delivery", "Risk"]

        # Add pillar nodes
        for p in pillars:
            if pd.notna(p):
                self.pillar_graph.add_node(str(p), type="pillar")

        if self.df is None:
            return self.pillar_graph

        # Determine pillar mentions per row by scanning textual columns and looking for pillar initials in numeric columns (e.g., GxW)
        text_columns = [c for c in self.df.columns if self.df[c].dtype == object]
        numeric_columns = [c for c in self.df.columns if pd.api.types.is_numeric_dtype(self.df[c])]

        for idx, row in self.df.iterrows():
            # collect candidate pillars for the row
            matched = set()
            # text search
            for c in text_columns:
                try:
                    val = row.get(c)
                    if pd.isna(val):
                        continue
                    sval = str(val).lower()
                    for p in pillars:
                        if p and p.lower() in sval:
                            matched.add(p)
                except Exception:
                    continue

            # numeric heuristic: look for columns like 'GxW' which suggests Governance
            for nc in numeric_columns:
                if re.match(r"^[A-Z]xW", str(nc)) or "GxW" in str(nc):
                    # map initial letter to pillar if possible
                    initial = str(nc)[0].upper()
                    for p in pillars:
                        if p and p[0].upper() == initial:
                            # if value is non-zero, map
                            try:
                                v = row.get(nc)
                                if pd.notna(v) and float(v) != 0:
                                    matched.add(p)
                            except Exception:
                                pass

            # if nothing matched, attempt to match by tool, role, process names
            role = row.get("Team / owner role")
            tool = row.get("Automation tool")
            output = row.get("Output")
            input_p = row.get("Input")
            candidates = [role, tool, output, input_p]
            for cand in candidates:
                if pd.isna(cand):
                    continue
                s = str(cand).lower()
                for p in pillars:
                    if p and p.lower() in s:
                        matched.add(p)

            # create edges from pillar to role/tool/process for each matched pillar
            for p in matched:
                # connect to role
                if pd.notna(role):
                    r = str(role)
                    if r not in self.pillar_graph:
                        self.pillar_graph.add_node(r, type="role")
                    self.pillar_graph.add_edge(p, r, label="related_role")
                # connect to tool
                if pd.notna(tool):
                    t = str(tool)
                    if t not in self.pillar_graph:
                        self.pillar_graph.add_node(t, type="tool")
                    self.pillar_graph.add_edge(p, t, label="related_tool")
                # connect to process (use output if available else input)
                proc = None
                if pd.notna(output):
                    proc = str(output)
                elif pd.notna(input_p):
                    proc = str(input_p)
                if proc:
                    if proc not in self.pillar_graph:
                        self.pillar_graph.add_node(proc, type="process")
                    self.pillar_graph.add_edge(p, proc, label="related_process")

        return self.pillar_graph

    def build_unified_graph(self):
        """Build a unified graph combining roles, tools, and processes."""
        unified = nx.DiGraph()

        # Ensure all component graphs are built
        if self.role_graph is None:
            self.build_role_graph()
        if self.tool_graph is None:
            self.build_tool_graph()
        if self.process_graph is None:
            self.build_process_graph()

        # Add all nodes and edges from component graphs
        for graph, component_type in [
            (self.role_graph, "role"),
            (self.tool_graph, "tool"),
            (self.process_graph, "process"),
            (self.pillar_graph, "pillar"),
        ]:
            if graph:
                for node, attrs in graph.nodes(data=True):
                    unified.add_node(node, **attrs)
                for src, tgt, attrs in graph.edges(data=True):
                    unified.add_edge(src, tgt, **attrs)

        # Add cross-component edges (role uses tool, role performs process)
        if self.df is not None:
            for idx, row in self.df.iterrows():
                role = row.get("Team / owner role")
                tool = row.get("Automation tool")
                output = row.get("Output")

                if pd.notna(role) and pd.notna(tool):
                    role, tool = str(role), str(tool)
                    if role in unified and tool in unified:
                        unified.add_edge(role, tool, label="uses", weight=1)

                if pd.notna(role) and pd.notna(output):
                    role, output = str(role), str(output)
                    if role in unified and output in unified:
                        unified.add_edge(role, output, label="produces", weight=1)

        return unified

    def get_graph_summary(self):
        """Return summary statistics of all graphs."""
        self.build_role_graph()
        self.build_tool_graph()
        self.build_process_graph()
        self.build_pillar_graph()

        return {
            "role_graph": {
                "nodes": len(self.role_graph.nodes()) if self.role_graph else 0,
                "edges": len(self.role_graph.edges()) if self.role_graph else 0,
            },
            "tool_graph": {
                "nodes": len(self.tool_graph.nodes()) if self.tool_graph else 0,
                "edges": len(self.tool_graph.edges()) if self.tool_graph else 0,
            },
            "process_graph": {
                "nodes": len(self.process_graph.nodes()) if self.process_graph else 0,
                "edges": len(self.process_graph.edges()) if self.process_graph else 0,
            },
            "pillar_graph": {
                "nodes": len(self.pillar_graph.nodes()) if self.pillar_graph else 0,
                "edges": len(self.pillar_graph.edges()) if self.pillar_graph else 0,
            },
        }
