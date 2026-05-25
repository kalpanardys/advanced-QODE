import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx

from utils import (load_qode_data, get_predecessors, criticality_mapping,
                   get_predecessor_role)


class HistoryManager:
    """Persistent query history for analysis sessions."""

    def __init__(self, file_path='qode_history.json'):
        self.file_path = Path(file_path)
        self.history = self._load_history()

    def _load_history(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as fh:
                    return json.load(fh)
            except (ValueError, OSError):
                return []
        return []

    def record(self, query, entity_matches, token_usage, response_summary):
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'query': query,
            'entities': entity_matches,
            'token_usage': token_usage,
            'summary': response_summary,
        }
        self.history.append(entry)
        self._save_history()

    def _save_history(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as fh:
            json.dump(self.history, fh, indent=2)

    def get_history(self):
        return list(self.history)


class TokenUsageTracker:
    """Simple token estimation for query analysis."""

    @staticmethod
    def estimate_tokens(text):
        return len(re.findall(r"\w+", text or ''))


class QodeAnalyzer:
    """Analyze QODE process data, extract entities, and traverse graphs."""

    def __init__(self, file_path='sample_questions.xlsm'):
        self.file_path = file_path
        self.df = load_qode_data(file_path)
        self.df = self._sanitize_dataframe(self.df)
        self.process_graph = self._build_process_graph()
        self.role_graph = self._build_relationship_graph('Team / owner role')
        self.tool_graph = self._build_relationship_graph('Automation tool')
        self.pillar_graph = self._build_relationship_graph('Practice type')
        self.roles = sorted(set(self.df['Team / owner role'].dropna().astype(str)))
        self.tools = sorted(set(self.df['Automation tool'].dropna().astype(str)))
        self.pillars = sorted(set(self.df['Practice type'].dropna().astype(str)))

    def _sanitize_dataframe(self, df):
        for col in df.select_dtypes(include=['object','string']).columns:
            df[col] = df[col].astype(str).str.strip().replace({'nan': ''})
        return df

    def _build_process_graph(self):
        graph = nx.DiGraph()
        for _, row in self.df.iterrows():
            node_label = str(row['S#'])
            graph.add_node(node_label, role=row.get('Team / owner role', ''),
                           tool=row.get('Automation tool', ''),
                           pillar=row.get('Practice type', ''),
                           criticality=criticality_mapping(row.get('Criticality', 'low')),
                           output_type=row.get('Output type', ''),
                           time=float(row.get('Total time taken') or 0),
                           manual_time=float(row.get('Manual time spent') or 0))

            predecessors = get_predecessors(row, include_init=True)
            for index, pred in enumerate(predecessors, start=1):
                if pred == 'INIT':
                    source = 'INIT'
                    graph.add_node('INIT', role='INIT', tool='INIT', pillar='INIT',
                                   criticality=1, output_type='root', time=0.0, manual_time=0.0)
                else:
                    source = str(pred)
                edge_label = f'A{node_label}{chr(64 + index) if index > 1 else ""}'
                graph.add_edge(source, node_label, label=edge_label,
                               duration=float(row.get('Total time taken') or 0),
                               criticality=criticality_mapping(row.get('Criticality', 'low')),
                               summary=[float(row.get('Total time taken') or 0),
                                        criticality_mapping(row.get('Criticality', 'low')),
                                        edge_label])
        return graph

    def _build_relationship_graph(self, attribute_column):
        graph = nx.DiGraph()
        for _, row in self.df.iterrows():
            current_attribute = row.get(attribute_column, '')
            if not current_attribute:
                continue
            graph.add_node(current_attribute)
            predecessors = get_predecessors(row)
            for pred in predecessors:
                if pred == 'INIT':
                    continue
                predecessor_attribute = self.df.loc[self.df['S#'] == pred, attribute_column].values
                if len(predecessor_attribute) > 0:
                    predecessor_attribute = str(predecessor_attribute[0])
                    if predecessor_attribute:
                        graph.add_node(predecessor_attribute)
                        existing = graph.get_edge_data(predecessor_attribute, current_attribute)
                        if existing:
                            existing['label'] += f', {pred}'
                        else:
                            graph.add_edge(predecessor_attribute, current_attribute,
                                           label=f'{predecessor_attribute}->{current_attribute}')
        return graph

    def extract_entities(self, query):
        normalized = str(query).lower()
        matches = {
            'roles': [value for value in self.roles if value.lower() in normalized],
            'tools': [value for value in self.tools if value.lower() in normalized],
            'pillars': [value for value in self.pillars if value.lower() in normalized],
        }
        return {k: v for k, v in matches.items() if v}

    def find_paths_for_entity(self, entity, entity_type='role', max_hops=4):
        candidates = []
        if entity_type == 'role':
            candidates = [str(s) for s in self.df.loc[self.df['Team / owner role'].str.lower() == entity.lower(), 'S#']]
        elif entity_type == 'tool':
            candidates = [str(s) for s in self.df.loc[self.df['Automation tool'].str.lower() == entity.lower(), 'S#']]
        elif entity_type == 'pillar':
            candidates = [str(s) for s in self.df.loc[self.df['Practice type'].str.lower() == entity.lower(), 'S#']]

        paths = []
        for start in candidates:
            for end in self._find_leaf_nodes():
                try:
                    for path in nx.all_simple_paths(self.process_graph, source=start, target=end, cutoff=max_hops):
                        paths.append(path)
                except nx.NetworkXNoPath:
                    continue
        return sorted(paths, key=lambda p: (len(p), self._path_total_time(p)), reverse=True)

    def _find_leaf_nodes(self):
        return [node for node in self.process_graph.nodes if self.process_graph.out_degree(node) == 0]

    def _path_total_time(self, path):
        return sum(self.process_graph.edges[path[i], path[i + 1]]['duration'] for i in range(len(path) - 1))

    def _path_average_criticality(self, path):
        weights = [self.process_graph.edges[path[i], path[i + 1]]['criticality'] for i in range(len(path) - 1)]
        return sum(weights) / len(weights) if weights else 0

    def find_multi_hop_connections(self, source_entity, target_entity, source_type='role', target_type='tool', max_hops=5):
        source_nodes = self._find_entity_nodes(source_entity, source_type)
        target_nodes = self._find_entity_nodes(target_entity, target_type)
        paths = []
        for source in source_nodes:
            for target in target_nodes:
                if source == target:
                    continue
                try:
                    for path in nx.all_simple_paths(self.process_graph, source=source, target=target, cutoff=max_hops):
                        paths.append(path)
                except nx.NetworkXNoPath:
                    continue
        return sorted(paths, key=lambda p: (len(p), self._path_total_time(p)), reverse=True)

    def _find_entity_nodes(self, entity_value, entity_type):
        entity_value = str(entity_value).strip().lower()
        if entity_type == 'role':
            selector = self.df['Team / owner role'].str.lower() == entity_value
        elif entity_type == 'tool':
            selector = self.df['Automation tool'].str.lower() == entity_value
        elif entity_type == 'pillar':
            selector = self.df['Practice type'].str.lower() == entity_value
        else:
            selector = self.df['Team / owner role'].str.lower() == entity_value
        return [str(s) for s in self.df.loc[selector, 'S#']]

    def get_longest_process_path(self):
        if not nx.is_directed_acyclic_graph(self.process_graph):
            return []
        path = nx.dag_longest_path(self.process_graph, weight='duration')
        return path

    def get_global_summary(self):
        total_tasks = len(self.df)
        summary = {
            'total_tasks': total_tasks,
            'roles': len(self.roles),
            'tools': len(self.tools),
            'pillars': len(self.pillars),
            'longest_path': self.get_longest_process_path(),
            'top_roles': Counter(self.df['Team / owner role']).most_common(5),
            'top_tools': Counter(self.df['Automation tool']).most_common(5),
        }
        return summary

    def build_structured_report(self, query, analysis_result):
        sections = {
            'Query': query,
            'Entity matches': analysis_result.get('entity_matches', {}),
            'Results': analysis_result.get('results', []),
            'Fallback summary': analysis_result.get('fallback', ''),
            'Global summary': analysis_result.get('global_summary', {}),
        }
        return sections

    def analyze_query(self, query, max_hops=4):
        token_usage = TokenUsageTracker.estimate_tokens(query)
        entity_matches = self.extract_entities(query)
        analysis_result = {
            'entity_matches': entity_matches,
            'token_usage': token_usage,
            'results': [],
            'fallback': None,
            'global_summary': self.get_global_summary(),
        }

        if entity_matches:
            for kind in ['roles', 'tools', 'pillars']:
                for value in entity_matches.get(kind, []):
                    if kind == 'roles':
                        paths = self.find_paths_for_entity(value, entity_type='role', max_hops=max_hops)
                    elif kind == 'tools':
                        paths = self.find_paths_for_entity(value, entity_type='tool', max_hops=max_hops)
                    else:
                        paths = self.find_paths_for_entity(value, entity_type='pillar', max_hops=max_hops)
                    rendered_paths = [self.render_path(path) for path in paths[:3]]
                    analysis_result['results'].append({
                        'type': kind[:-1],
                        'value': value,
                        'paths': paths[:5],
                        'path_descriptions': rendered_paths,
                        'top_path_time': self._path_total_time(paths[0]) if paths else 0,
                        'top_path_criticality': self._path_average_criticality(paths[0]) if paths else 0,
                    })
            if not analysis_result['results']:
                analysis_result['fallback'] = 'No matching graph paths were found for extracted entities.'
        else:
            analysis_result['fallback'] = 'No direct entity match found. Returning global summary and fallback overview.'

        return analysis_result

    def render_path(self, path):
        if not path:
            return ''
        labels = []
        for index, node in enumerate(path):
            node_data = self.process_graph.nodes.get(node, {})
            labels.append(f"{node}({node_data.get('role', '')}|{node_data.get('tool', '')})")
        return ' -> '.join(labels)

    def summarize_analysis(self, analysis_result):
        """Create a concise, human-friendly narrative from analysis results.

        This is a lightweight substitute for an LLM: it converts the
        technical analysis into structured narrative blocks: Overview,
        Findings, and Recommendations.
        """
        lines = []
        # Overview
        gs = analysis_result.get('global_summary', {})
        lines.append('Overview')
        lines.append('-' * 8)
        lines.append(f"Total tasks: {gs.get('total_tasks', 0)}; Roles: {gs.get('roles', 0)}; Tools: {gs.get('tools', 0)}")
        lines.append('')

        # Findings
        lines.append('Findings')
        lines.append('-' * 8)
        matches = analysis_result.get('entity_matches', {})
        if matches:
            for k, v in matches.items():
                lines.append(f"Detected {k}: {', '.join(v)}")
        else:
            lines.append('No direct entities matched in the query.')

        for res in analysis_result.get('results', []):
            lines.append(f"\n{res['type'].title()} '{res['value']}' — {len(res['paths'])} matching path(s).")
            for idx, p in enumerate(res.get('path_descriptions', [])[:2], start=1):
                lines.append(f"  Example path {idx}: {p}")

        # Recommendations
        lines.append('')
        lines.append('Recommendations')
        lines.append('-' * 12)
        if matches:
            lines.append('Consider reviewing the example paths to identify hand-off points and automation opportunities.')
        else:
            lines.append('Run a broader analysis or provide an example role/tool name to get targeted paths.')

        return '\n'.join(lines)


class LLMSummarizer:
    """Provider-agnostic LLM summarizer.

    Usage:
      summarizer = LLMSummarizer(provider='mock')
      summary = summarizer.summarize(analysis_result, query)
    """

    def __init__(self, provider='mock', model=None, api_key=None):
        self.provider = provider or 'mock'
        self.model = model
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')

    def summarize(self, analysis_result, query_text=None):
        # Mock provider: return the existing lightweight summarizer
        if self.provider == 'mock':
            analyzer = QodeAnalyzer()  # uses sample_questions.xlsm by default
            return analyzer.summarize_analysis(analysis_result)

        # OpenAI provider (optional): try to import openai and call ChatCompletion
        if self.provider == 'openai':
            try:
                import openai
            except Exception:
                raise RuntimeError('openai package is required for openai provider')
            if not self.api_key:
                raise RuntimeError('OPENAI_API_KEY not set for openai provider')
            openai.api_key = self.api_key
            prompt = self._build_prompt(analysis_result, query_text)
            resp = openai.ChatCompletion.create(
                model=self.model or 'gpt-4o-mini',
                messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                          {'role': 'user', 'content': prompt}],
                temperature=0.3,
                max_tokens=512,
            )
            return resp.choices[0].message.content

        raise ValueError(f'Unsupported LLM provider: {self.provider}')

    def _build_prompt(self, analysis_result, query_text=None):
        parts = []
        parts.append('Create a concise, structured summary (Overview, Findings, Recommendations)')
        if query_text:
            parts.append(f'User query: {query_text}')
        parts.append('Analysis result (JSON):')
        parts.append(json.dumps(analysis_result, default=str))
        return '\n\n'.join(parts)
