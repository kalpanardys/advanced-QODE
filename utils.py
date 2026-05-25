"""
Shared utilities for QODE diagram generation.
"""

import math
import pandas as pd
import networkx as nx


def isnan(value):
    """
    Check if a value is NaN, handling exceptions gracefully.

    Args:
        value: The value to check.

    Returns:
        bool: True if the value is NaN, False otherwise.
    """
    try:
        return math.isnan(float(value))
    except (ValueError, TypeError):
        return False


def load_qode_data(file_path, sheet_name="Q_Stories", header_row=3, skip_rows=2):
    """
    Load and filter QODE data from an Excel file.

    Args:
        file_path (str): Path to the Excel file.
        sheet_name (str): Name of the sheet to read.
        header_row (int): Row number for headers (0-based).
        skip_rows (int): Number of rows to skip after headers.

    Returns:
        pd.DataFrame: Filtered DataFrame with 'Yes / No' == 'Yes'.
    """
    data = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)[skip_rows:]
    return data[data['Yes / No'] == 'Yes']


def get_predecessors(row, include_init=False):
    """
    Extract predecessor values from a DataFrame row.

    Args:
        row (pd.Series): A row from the DataFrame.
        include_init (bool): If True, include 'INIT' predecessors.

    Returns:
        list: List of predecessor values (S# or 'INIT'), excluding NaN.
    """
    preds = []
    for i in range(1, 6):  # Predecessor 1 to 5
        pred_col = f"Predecessor {i} (incl. INIT)" if i == 1 else f"Predecessor {i} (optional)"
        pred = row.get(pred_col)
        if not isnan(pred) and (include_init or pred != "INIT"):
            preds.append(pred)
        elif include_init and pred == "INIT":
            preds.append(pred)
    return preds


def get_predecessor_role(df, pred_s_no, role_column):
    """
    Get the role/tool for a given predecessor S#.

    Args:
        df (pd.DataFrame): The DataFrame.
        pred_s_no: The S# of the predecessor.
        role_column (str): Column name for the role/tool.

    Returns:
        str: The role/tool value.
    """
    return df.loc[df['S#'] == pred_s_no, role_column].iloc[0]


def criticality_mapping(value):
    """
    Map criticality text to numeric value.

    Args:
        value (str): Criticality level ('hi', 'med', or defaults to 'low').

    Returns:
        int: Numeric criticality (3=high, 2=medium, 1=low).
    """
    if value.lower() == "hi":
        return 3
    if value.lower() == "med":
        return 2
    return 1


def find_leaf_nodes(graph):
    """
    Find leaf nodes in a directed graph (nodes with no outgoing edges).

    Args:
        graph (nx.DiGraph): NetworkX directed graph.

    Returns:
        list: List of leaf node names.
    """
    return [node for node in graph.nodes if graph.out_degree(node) == 0]


def get_avg_criticality(graph, path):
    """
    Calculate average criticality along a graph path.

    Args:
        graph (nx.DiGraph): NetworkX directed graph with weight attributes.
        path (list): Sequence of nodes forming a path.

    Returns:
        float: Average criticality of edges in the path.
    """
    path_length = len(path) - 1
    total = 0
    for i in range(path_length):
        edge_data = graph.get_edge_data(path[i], path[i + 1])
        critical_value = edge_data["weight"][1]  # Index 1 is criticality
        total += critical_value
    return total / path_length if path_length > 0 else 0


def node_to_edge(graph, path):
    """
    Extract edge labels from a path of nodes.

    Args:
        graph (nx.DiGraph): NetworkX directed graph.
        path (list): Sequence of nodes forming a path.

    Returns:
        list: Edge labels along the path.
    """
    result = []
    for i in range(len(path) - 1):
        edge_data = graph.get_edge_data(path[i], path[i + 1])
        result.append(edge_data["weight"][2])  # Index 2 is label
    return result