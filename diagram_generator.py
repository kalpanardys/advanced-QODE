"""
Concrete implementations of diagram builders and exporters.
"""

import math
import pydot
import networkx as nx
from interfaces import DiagramBuilder, GraphExporter
from utils import (
    load_qode_data, get_predecessors, get_predecessor_role, isnan,
    criticality_mapping, find_leaf_nodes, get_avg_criticality, node_to_edge
)


class DotExporter(GraphExporter):
    """
    Concrete exporter for Graphviz DOT format.
    """

    def write_raw(self, dot_graph: pydot.Dot, filename: str) -> None:
        dot_graph.write_raw(filename)


class PeopleDiagramBuilder(DiagramBuilder):
    """
    Builder for people diagrams (role-based).
    """

    def __init__(self):
        self.node_list = {}
        self.dot_graph = pydot.Dot(graph_type='digraph')

    def load_data(self, file_path: str):
        return load_qode_data(file_path)

    def build_graph(self, df):
        # Select relevant columns
        selected_columns = ["S#","Predecessor 1 (incl. INIT)","Predecessor 2 (optional)","Predecessor 3 (optional)","Predecessor 4 (optional)","Predecessor 5 (optional)","Team / owner role","Total time taken","Manual time spent"]
        final_df = df[selected_columns].copy()
        
        # Create nodes
        distinct_roles = final_df["Team / owner role"].unique()
        for role in distinct_roles:
            temp_node = pydot.Node(role, fillcolor="#ADD8E6", style="filled")
            temp_node.set_shape("box")
            self.node_list[role] = {"value": temp_node}
            self.dot_graph.add_node(temp_node)
        
        # Create edges
        for i in range(len(final_df)):
            row = final_df.iloc[i]
            current_role = row["Team / owner role"]
            total_time = row["Total time taken"]
            manual_time = row["Manual time spent"]
            
            preds = get_predecessors(row)
            color = "#000000" if (total_time - manual_time) != 0 else "#FFA500"
            
            for pred in preds:
                pred_role = get_predecessor_role(final_df, pred, 'Team / owner role')
                edge = pydot.Edge(self.node_list[pred_role]["value"], self.node_list[current_role]["value"], 
                                arrowsize=0.3, weight=0.5, color=color, penwidth=0.7, decorate="true")
                self.dot_graph.add_edge(edge)
        
        return self.dot_graph

    def write_output(self, dot_graph: pydot.Dot, filename: str) -> None:
        exporter = DotExporter()
        exporter.write_raw(dot_graph, filename)


class TechnologyDiagramBuilder(DiagramBuilder):
    """
    Builder for technology diagrams (tool-based).
    """

    def __init__(self):
        self.node_list = {}
        self.edge_list = []
        self.dot_graph = pydot.Dot(graph_type='digraph')

    def load_data(self, file_path: str):
        return load_qode_data(file_path)

    def build_graph(self, df):
        # Select relevant columns
        selected_columns = ["S#","Predecessor 1 (incl. INIT)","Predecessor 2 (optional)","Predecessor 3 (optional)","Predecessor 4 (optional)","Predecessor 5 (optional)","Automation tool"]
        final_df = df[selected_columns].copy()
        
        # Create nodes
        distinct_tools = final_df["Automation tool"].unique()
        for tool in distinct_tools:
            temp_node = pydot.Node(tool, fillcolor="#ADD8E6", style="filled")
            self.node_list[tool] = {"value": temp_node}
            self.dot_graph.add_node(temp_node)
        
        # Create edges with consolidation
        for i in range(len(final_df)):
            row = final_df.iloc[i]
            current_tool = row["Automation tool"]
            preds = get_predecessors(row)
            
            for pred in preds:
                pred_tool = get_predecessor_role(final_df, pred, 'Automation tool')
                self._check_edge_present(f'A{pred}', self.node_list[pred_tool]["value"], self.node_list[current_tool]["value"])
        
        # Add consolidated edges
        for edge in self.edge_list:
            temp_edge = pydot.Edge(edge["head"], edge["tail"], arrowsize=0.5, color="#000000", penwidth=0.7, fontsize=8.0)
            temp_edge.set_label(edge["label"])
            self.dot_graph.add_edge(temp_edge)
        
        return self.dot_graph

    def _check_edge_present(self, label, node_1, node_2):
        for edge in self.edge_list:
            if edge["head"] == node_1 and edge["tail"] == node_2:
                edge["label"] += f'  {label}'
                return
        self.edge_list.append({"head": node_1, "tail": node_2, "label": label})

    def write_output(self, dot_graph: pydot.Dot, filename: str) -> None:
        exporter = DotExporter()
        exporter.write_raw(dot_graph, filename)


class ProcessNetworkDiagramBuilder(DiagramBuilder):
    """
    Builder for process network diagrams (with critical paths).
    """

    def __init__(self):
        self.node_list = {}
        self.dot_graph = pydot.Dot(graph_type='digraph')
        self.qode_graph = nx.DiGraph()

    def load_data(self, file_path: str):
        return load_qode_data(file_path)

    def build_graph(self, df):
        # Select and prepare columns
        selected_columns = ["S#", "Total time taken", "Manual time spent", 
                           "Predecessor 1 (incl. INIT)", "Predecessor 2 (optional)",
                           "Predecessor 3 (optional)", "Predecessor 4 (optional)",
                           "Predecessor 5 (optional)", "Criticality", "Team / owner role",
                           "Input", "Output", "Automation tool", "Output type"]
        final_df = df[selected_columns].copy()
        
        # Add node numbers
        final_df['node'] = range(1, len(final_df) + 1)
        # Also add to original df for find_critical_paths
        df['node'] = range(1, len(df) + 1)
        
        # Create pydot nodes
        self._create_pydot_nodes(final_df)
        
        # Calculate lead times
        self._calculate_lead_times(final_df)
        
        # Create pydot edges
        self._create_pydot_edges(final_df)
        
        # Create networkx graph for critical path analysis
        self._create_networkx_graph(final_df)
        
        return self.dot_graph

    def _create_pydot_nodes(self, final_df):
        # Create E0 (requirement) node
        self.node_list[0] = {
            "value": pydot.Node('E0 \nRequirement \n (Jira)', fillcolor="#ADD8E6", style="filled", shape="box"),
            "time": 0,
            "node_no": 'E0'
        }
        self.dot_graph.add_node(self.node_list[0]["value"])
        
        # Create E1+ nodes for each row
        for i in range(len(final_df)):
            s_num = final_df.iat[i, 0]
            input_val = final_df.iat[i, 10]
            output_val = final_df.iat[i, 11]
            tool = final_df.iat[i, 12]
            node = pydot.Node(f'E{i+1} \n {input_val} to {output_val} \n ({tool})',
                            fillcolor="#FFFFFF", style="filled", shape="box")
            self.node_list[s_num] = {"value": node, "time": 0, "node_no": f'E{i+1}'}
            self.dot_graph.add_node(node)

    def _calculate_lead_times(self, final_df):
        # Initialize first node time
        self.node_list[1]["time"] = final_df.iat[0, 1]
        
        # Iterate twice to propagate times through the network
        for _ in range(2):
            for i in range(len(final_df)):
                current_node = final_df.iat[i, 0]
                current_time = final_df.iat[i, 1]
                
                for pred_col_idx in range(3, 8):  # Predecessor columns
                    pred = final_df.iat[i, pred_col_idx]
                    if not isnan(pred):
                        if pred == "INIT":
                            if current_node != 1:
                                new_time = round((current_time + self.node_list[1]["time"]), 2)
                                if new_time > self.node_list[current_node]["time"]:
                                    self.node_list[current_node]["time"] = new_time
                        else:
                            new_time = round((current_time + self.node_list[pred]["time"]), 2)
                            if new_time > self.node_list[current_node]["time"]:
                                self.node_list[current_node]["time"] = new_time

    def _create_pydot_edges(self, final_df):
        # Create edge from E0 to E1
        edge_label = f'A1 \n {final_df.iat[0, 1]},{final_df.iat[0, 2]} (0) \n {final_df.iat[0, 9]}'
        edge = pydot.Edge(self.node_list[0]["value"], self.node_list[1]["value"])
        edge.set_label(edge_label)
        self.dot_graph.add_edge(edge)
        
        # Create edges for all rows
        for i in range(len(final_df)):
            current_node = final_df.iat[i, 0]
            current_time = final_df.iat[i, 1]
            manual_time = final_df.iat[i, 2]
            
            for pred_col_idx in range(3, 8):  # Predecessor columns
                pred = final_df.iat[i, pred_col_idx]
                pred_suffix = ['', '(A)', '(B)', '(C)', '(D)'][pred_col_idx - 3]
                
                if not isnan(pred):
                    if pred == "INIT":
                        if current_node != 1:
                            pred_time = self.node_list[1]["time"]
                            edge_label = f'A{current_node} \n {current_time},{manual_time} ({pred_time}) \n {final_df.iat[i, 9]}'
                            edge = pydot.Edge(self.node_list[1]["value"], self.node_list[current_node]["value"])
                            edge.set_label(edge_label)
                            self.dot_graph.add_edge(edge)
                    else:
                        pred_time = self.node_list[pred]["time"]
                        edge_label = f'A{current_node}{pred_suffix} \n {current_time},{manual_time} ({pred_time}) \n {final_df.iat[i, 9]}'
                        edge = pydot.Edge(self.node_list[pred]["value"], self.node_list[current_node]["value"])
                        edge.set_label(edge_label)
                        self.dot_graph.add_edge(edge)

    def _create_networkx_graph(self, final_df):
        # Add all nodes
        self.qode_graph.add_node('E0')
        for i in range(1, len(final_df) + 1):
            self.qode_graph.add_node(f'E{i}')
        
        # Add edges with weights [time, criticality, label]
        self.qode_graph.add_edge('E0', 'E1', weight=[final_df.iat[0, 1], 2, 'A1'])
        
        for i in range(len(final_df)):
            current_node = final_df.iat[i, 0]
            current_time = final_df.iat[i, 1]
            criticality = criticality_mapping(final_df.iat[i, 8])
            
            for pred_col_idx in range(3, 8):  # Predecessor columns
                pred = final_df.iat[i, pred_col_idx]
                pred_suffix = ['', '(A)', '(B)', '(C)', '(D)'][pred_col_idx - 3]
                
                if not isnan(pred):
                    if pred == "INIT":
                        if current_node != 1:
                            self.qode_graph.add_edge('E1', f'E{current_node}', 
                                                   weight=[current_time, criticality, f'A{current_node}'])
                    else:
                        self.qode_graph.add_edge(f'E{pred}', f'E{current_node}', 
                                               weight=[current_time, criticality, f'A{current_node}{pred_suffix}'])

    def find_critical_paths(self, final_df):
        """
        Find the critical paths in the process network.
        
        Args:
            final_df: DataFrame with process data.
            
        Returns:
            list: List of critical paths (each as a list of edge labels).
        """
        # Find leaf nodes (no outgoing edges that are material outputs)
        leaf_nodes = find_leaf_nodes(self.qode_graph)
        material_leaf_nodes = []
        
        for leaf in leaf_nodes:
            node_idx = int(leaf[1:])  # Extract number from 'En'
            if node_idx == 0:
                continue
            output_type = final_df.loc[final_df['node'] == node_idx, 'Output type'].iloc[0]
            if output_type.lower() == "material":
                material_leaf_nodes.append(leaf)
        
        if not material_leaf_nodes:
            return []
        
        # Find maximum time among material leaf nodes
        max_time = 0
        for leaf in material_leaf_nodes:
            node_idx = int(leaf[1:])
            s_num = final_df.loc[final_df['node'] == node_idx, 'S#'].iloc[0]
            if self.node_list[s_num]["time"] > max_time:
                max_time = self.node_list[s_num]["time"]
        
        # Select nodes with maximum time
        final_leaf_nodes = []
        for leaf in material_leaf_nodes:
            node_idx = int(leaf[1:])
            s_num = final_df.loc[final_df['node'] == node_idx, 'S#'].iloc[0]
            if self.node_list[s_num]["time"] == max_time:
                final_leaf_nodes.append(leaf)
        
        # Find all paths to final leaf nodes with maximum time
        paths_list = []
        for leaf in final_leaf_nodes:
            try:
                paths = list(nx.all_simple_paths(self.qode_graph, source='E0', target=leaf))
                paths_list.extend(paths)
            except nx.NetworkXNoPath:
                continue
        
        # Filter paths by maximum time
        max_time_paths = []
        for path in paths_list:
            path_time = 0
            for i in range(len(path) - 1):
                edge_data = self.qode_graph.get_edge_data(path[i], path[i + 1])
                if edge_data:
                    path_time += edge_data["weight"][0]
            if path_time == max_time:
                max_time_paths.append(path)
        
        # Find paths with highest average criticality
        if not max_time_paths:
            return []
        
        criticality_values = [get_avg_criticality(self.qode_graph, path) for path in max_time_paths]
        max_criticality = max(criticality_values)
        
        critical_paths = [path for path, crit in zip(max_time_paths, criticality_values) if crit == max_criticality]
        
        # Return paths with maximum length
        if critical_paths:
            max_length = max(len(p) for p in critical_paths)
            longest_paths = [p for p in critical_paths if len(p) == max_length]
            return [node_to_edge(self.qode_graph, path) for path in longest_paths]
        
        return []

    def write_output(self, dot_graph: pydot.Dot, filename: str) -> None:
        exporter = DotExporter()
        exporter.write_raw(dot_graph, filename)