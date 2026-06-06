"""
Entity loader module - extracts valid entities from Excel data.
Maps Pillars, Roles, Tools, and Processes from the QODE Excel file.
"""

import pandas as pd
from utils import load_qode_data


class EntityLoader:
    """Load and manage valid entities from Excel data."""

    def __init__(self, file_path="sample_questions.xlsm"):
        self.file_path = file_path
        self.pillars = set()
        self.roles = set()
        self.tools = set()
        self.processes = set()
        self._load_entities()

    def _load_entities(self):
        """Extract entities from Excel file."""
        try:
            df = load_qode_data(self.file_path)

            # Extract roles from Team/Owner role column
            if "Team / owner role" in df.columns:
                self.roles = set(df["Team / owner role"].dropna().unique())
                self.roles = {str(r).strip() for r in self.roles if str(r).strip()}

            # Extract tools from Automation tool column
            if "Automation tool" in df.columns:
                self.tools = set(df["Automation tool"].dropna().unique())
                self.tools = {str(t).strip() for t in self.tools if str(t).strip()}

            # Extract processes from Input/Output columns
            if "Input" in df.columns:
                inputs = set(df["Input"].dropna().unique())
                self.processes.update({str(p).strip() for p in inputs if str(p).strip()})

            if "Output" in df.columns:
                outputs = set(df["Output"].dropna().unique())
                self.processes.update({str(p).strip() for p in outputs if str(p).strip()})

            # Default pillars (can be extended from data if available)
            self.pillars = {
                "Governance",
                "Security",
                "Compliance",
                "Reliability",
                "Performance",
                "Cost",
                "Quality",
                "Delivery",
                "Risk",
            }

        except Exception as e:
            print(f"Warning: Could not load entities from Excel: {e}")
            self._set_defaults()

    def _set_defaults(self):
        """Set default entities if file loading fails."""
        self.roles = {"DevOps", "Developer", "QA", "Security", "Architect"}
        self.tools = {"Jenkins", "Jira", "Git", "Docker", "Kubernetes"}
        self.processes = {"Deployment", "Testing", "Build", "Release", "Integration"}
        self.pillars = {"Security", "Compliance", "Reliability", "Performance"}

    def get_all_entities(self):
        """Return all entities as a dictionary."""
        return {
            "pillars": list(self.pillars),
            "roles": list(self.roles),
            "tools": list(self.tools),
            "processes": list(self.processes),
        }

    def get_entity_summary(self):
        """Return a summary of loaded entities."""
        return {
            "pillar_count": len(self.pillars),
            "role_count": len(self.roles),
            "tool_count": len(self.tools),
            "process_count": len(self.processes),
            "total_entities": len(self.pillars) + len(self.roles) + len(self.tools) + len(self.processes),
        }
