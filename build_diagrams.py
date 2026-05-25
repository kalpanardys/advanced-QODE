#!/usr/bin/env python3
"""
Command-line runner for QODE diagrams and query-driven analysis.
"""

import argparse
from pathlib import Path

from analysis import HistoryManager, QodeAnalyzer
from exporters import ExportManager, validate_output_filename
from diagram_builders import PeopleDiagramBuilder, TechnologyDiagramBuilder, ProcessNetworkDiagramBuilder


def build_people_diagram(data_file, output_name):
    builder = PeopleDiagramBuilder()
    df = builder.load_data(str(data_file))
    graph = builder.build_graph(df)
    builder.write_output(graph, output_name)
    return output_name


def build_technology_diagram(data_file, output_name):
    builder = TechnologyDiagramBuilder()
    df = builder.load_data(str(data_file))
    graph = builder.build_graph(df)
    builder.write_output(graph, output_name)
    return output_name


def build_process_diagram(data_file, output_name):
    builder = ProcessNetworkDiagramBuilder()
    df = builder.load_data(str(data_file))
    graph = builder.build_graph(df)
    critical_paths = builder.find_critical_paths(df)
    builder.write_output(graph, output_name)
    return output_name, critical_paths


def export_analysis(report_sections, filename, export_format):
    if export_format == 'txt':
        return ExportManager.export_text_report(report_sections, filename)
    if export_format == 'docx':
        return ExportManager.export_docx_report(report_sections, filename)
    if export_format == 'xlsx':
        return ExportManager.export_xlsx_report(report_sections, filename)
    if export_format == 'pptx':
        return ExportManager.export_pptx_report(report_sections, filename)
    if export_format == 'pdf':
        return ExportManager.export_pdf_report(report_sections, filename)
    raise ValueError(f'Unsupported export format: {export_format}')


def parse_args():
    parser = argparse.ArgumentParser(description='Build QODE diagrams and run query-driven analysis.')
    parser.add_argument('--mode', choices=['all', 'people', 'technology', 'process', 'analyze'], default='all',
                        help='Operation mode for diagram generation or analysis.')
    parser.add_argument('--data-file', default='sample_questions.xlsm', help='Input Excel data file.')
    parser.add_argument('--query', type=str, help='User query for entity extraction and graph traversal.')
    parser.add_argument('--output-file', type=str, help='Output filename for exported analysis report.')
    parser.add_argument('--export-format', choices=['txt', 'docx', 'xlsx', 'pptx', 'pdf'], default='txt',
                        help='Export format for analysis report.')
    parser.add_argument('--history-file', default='qode_history.json', help='Path to persistent query history file.')
    parser.add_argument('--show-history', action='store_true', help='Show saved query history instead of running analysis.')
    parser.add_argument('--max-hops', type=int, default=4, help='Maximum number of hops for graph traversal.')
    parser.add_argument('--narrative', action='store_true', help='Include a human-friendly narrative summary in the report.')
    parser.add_argument('--use-llm', action='store_true', help='Use an LLM to generate the narrative summary (provider configured via --llm-provider or OPENAI_API_KEY).')
    parser.add_argument('--llm-provider', choices=['mock', 'openai'], default='mock', help='LLM provider to use when --use-llm is enabled.')
    parser.add_argument('--llm-model', default=None, help='Optional LLM model name to pass to the provider.')
    parser.add_argument('--show-token-dashboard', action='store_true', help='Show aggregated token usage from history and exit.')
    return parser.parse_args()


def build_report_sections(query, analysis_result):
    sections = {
        'Query': str(query),
    }

    matches = analysis_result.get('entity_matches', {})
    if matches:
        summary_lines = []
        for key, values in matches.items():
            summary_lines.append(f"{key.title()}: {', '.join(values)}")
        sections['Entity matches'] = '\n'.join(summary_lines)
    else:
        sections['Entity matches'] = 'No entities were matched from the query.'

    if analysis_result.get('results'):
        result_lines = []
        for item in analysis_result['results']:
            result_lines.append(
                f"{item['type'].title()} '{item['value']}': {len(item['paths'])} matching path(s)."
            )
            if item['path_descriptions']:
                for idx, path_text in enumerate(item['path_descriptions'], start=1):
                    result_lines.append(f"  Path {idx}: {path_text}")
            else:
                result_lines.append('  No paths available for this match.')
        sections['Results'] = '\n'.join(result_lines)
    else:
        sections['Results'] = 'No matching paths were found.'

    if analysis_result.get('fallback'):
        sections['Fallback'] = analysis_result['fallback']

    global_summary = analysis_result.get('global_summary', {})
    sections['Global summary'] = '\n'.join([
        f"Total tasks: {global_summary.get('total_tasks', 0)}",
        f"Distinct roles: {global_summary.get('roles', 0)}",
        f"Distinct tools: {global_summary.get('tools', 0)}",
        f"Distinct pillars: {global_summary.get('pillars', 0)}",
        f"Longest path: {', '.join(global_summary.get('longest_path', []))}",
        f"Top roles: {', '.join(f'{role}({count})' for role, count in global_summary.get('top_roles', []))}",
        f"Top tools: {', '.join(f'{tool}({count})' for tool, count in global_summary.get('top_tools', []))}",
    ])
    return sections


def main():
    args = parse_args()

    print('=' * 60)
    print('QODE Diagram Builder and Analysis Runner')
    print('=' * 60)

    data_file = Path(args.data_file)
    if not data_file.exists():
        print(f'Input file not found: {data_file}')
        return

    if args.show_history:
        history = HistoryManager(args.history_file)
        print('Saved query history:')
        for entry in history.get_history():
            print(f"- {entry['timestamp']}: {entry['query']} (tokens {entry['token_usage']})")
        return

    if args.show_token_dashboard:
        history = HistoryManager(args.history_file)
        entries = history.get_history()
        total_tokens = sum(e.get('token_usage', 0) for e in entries)
        queries = len(entries)
        avg = round(total_tokens / queries, 1) if queries else 0
        print('Token usage dashboard')
        print('---------------------')
        print(f'Total queries: {queries}')
        print(f'Total tokens (est): {total_tokens}')
        print(f'Average tokens per query: {avg}')
        return

    if args.mode in ['all', 'people']:
        print('\n1. Building People Diagram...')
        try:
            output_name = 'Diagram_People_New.dot'
            build_people_diagram(data_file, output_name)
            print(f'   ✓ People diagram saved as {output_name}')
        except Exception as exc:
            print(f'   ✗ Error building people diagram: {exc}')

    if args.mode in ['all', 'technology']:
        print('\n2. Building Technology Diagram...')
        try:
            output_name = 'Diagram_Technology_New.dot'
            build_technology_diagram(data_file, output_name)
            print(f'   ✓ Technology diagram saved as {output_name}')
        except Exception as exc:
            print(f'   ✗ Error building technology diagram: {exc}')

    if args.mode in ['all', 'process']:
        print('\n3. Building Process Network Diagram...')
        try:
            output_name = 'Diagram_Network_New.dot'
            _, critical_paths = build_process_diagram(data_file, output_name)
            print(f'   ✓ Process network diagram saved as {output_name}')
            print(f'   ✓ Found {len(critical_paths)} critical path(s)')
        except Exception as exc:
            print(f'   ✗ Error building process diagram: {exc}')

    if args.mode == 'analyze' or args.query:
        analyzer = QodeAnalyzer(str(data_file))
        query_text = args.query or 'Describe the overall process and tools.'
        print('\n4. Running query-driven analysis...')
        analysis_result = analyzer.analyze_query(query_text, max_hops=args.max_hops)
        report_sections = build_report_sections(query_text, analysis_result)
        if args.narrative:
            if args.use_llm:
                try:
                    from analysis import LLMSummarizer
                    summarizer = LLMSummarizer(provider=args.llm_provider, model=args.llm_model)
                    report_sections['Narrative'] = summarizer.summarize(analysis_result, query_text)
                except Exception as exc:
                    report_sections['Narrative'] = f'LLM summarization failed: {exc}'
            else:
                report_sections['Narrative'] = analyzer.summarize_analysis(analysis_result)

        if args.output_file:
            export_filename = validate_output_filename(args.output_file, default_extension=f'.{args.export_format}')
            export_format = export_filename.suffix.lstrip('.') or args.export_format
            exported_path = export_analysis(report_sections, str(export_filename), export_format)
            print(f'   ✓ Analysis report exported to {exported_path}')
        else:
            print('   Analysis result:')
            for title, content in report_sections.items():
                print(f'\n{title}\n{"-" * len(title)}\n{content}')

        history = HistoryManager(args.history_file)
        history.record(query_text, analysis_result.get('entity_matches', {}), analysis_result['token_usage'],
                       'exported' if args.output_file else 'displayed')

    print('\n' + '=' * 60)
    print('Complete! Use GraphvizOnline to view DOT files if needed:')
    print('https://dreampuf.github.io/GraphvizOnline/')
    print('=' * 60)


if __name__ == '__main__':
    main()
