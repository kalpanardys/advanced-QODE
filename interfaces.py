"""
Shared interfaces for QODE diagram builders.
"""

from abc import ABC, abstractmethod
import pandas as pd
import pydot


class DiagramBuilder(ABC):
    """
    Abstract base class for diagram builders.
    """

    @abstractmethod
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from the source file.

        Args:
            file_path (str): Path to the data file.

        Returns:
            pd.DataFrame: Loaded and filtered data.
        """
        pass

    @abstractmethod
    def build_graph(self, df: pd.DataFrame) -> pydot.Dot:
        """
        Build the graph from the data.

        Args:
            df (pd.DataFrame): The data to build from.

        Returns:
            pydot.Dot: The constructed graph.
        """
        pass

    @abstractmethod
    def write_output(self, dot_graph: pydot.Dot, filename: str) -> None:
        """
        Write the graph to output.

        Args:
            dot_graph (pydot.Dot): The graph to write.
            filename (str): Output filename.
        """
        pass


class GraphExporter(ABC):
    """
    Abstract base class for graph exporters.
    """

    @abstractmethod
    def write_raw(self, dot_graph: pydot.Dot, filename: str) -> None:
        """
        Write raw Graphviz source.

        Args:
            dot_graph (pydot.Dot): The graph.
            filename (str): Output filename.
        """
        pass

    def write_png(self, dot_graph: pydot.Dot, filename: str) -> None:
        """
        Write PNG image (optional implementation).

        Args:
            dot_graph (pydot.Dot): The graph.
            filename (str): Output filename.
        """
        dot_graph.write_png(filename)

    def write_svg(self, dot_graph: pydot.Dot, filename: str) -> None:
        """
        Write SVG image (optional implementation).

        Args:
            dot_graph (pydot.Dot): The graph.
            filename (str): Output filename.
        """
        dot_graph.write_svg(filename)


class PredecessorResolver(ABC):
    """
    Abstract base class for resolving predecessors.
    """

    @abstractmethod
    def get_predecessors(self, row: pd.Series) -> list:
        """
        Get list of valid predecessors for a row.

        Args:
            row (pd.Series): The row.

        Returns:
            list: List of predecessor S# values.
        """
        pass

    @abstractmethod
    def get_role_for_pred(self, df: pd.DataFrame, pred_s_no, role_column: str):
        """
        Get the role/tool for a predecessor.

        Args:
            df (pd.DataFrame): The DataFrame.
            pred_s_no: Predecessor S#.
            role_column (str): Column name.

        Returns:
            str: The role/tool.
        """
        pass


class CriticalPathAnalyzer(ABC):
    """
    Abstract base class for critical path analysis (specific to process networks).
    """

    @abstractmethod
    def find_critical_paths(self, df: pd.DataFrame, node_list: dict) -> list:
        """
        Find critical paths in the graph.

        Args:
            df (pd.DataFrame): The data.
            node_list (dict): Node information.

        Returns:
            list: List of critical paths.
        """
        pass
