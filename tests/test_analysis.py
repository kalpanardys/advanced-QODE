import os
import sys
import unittest
from pathlib import Path

# Ensure repo root is importable for tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis import HistoryManager, QodeAnalyzer, TokenUsageTracker
from exporters import validate_output_filename


class TestQodeAnalysis(unittest.TestCase):
    def test_extract_entities_finds_known_values(self):
        analyzer = QodeAnalyzer('sample_questions.xlsm')
        result = analyzer.extract_entities('Show me the Business role and Confluence tool path')
        self.assertIn('Business', result.get('roles', []))
        self.assertIn('Confluence', result.get('tools', []))

    def test_analyze_query_returns_global_summary_when_unknown(self):
        analyzer = QodeAnalyzer('sample_questions.xlsm')
        result = analyzer.analyze_query('Tell me about a missing entity')
        self.assertTrue(result.get('fallback'))
        self.assertIn('global_summary', result)
        self.assertGreater(result['global_summary']['total_tasks'], 0)

    def test_token_estimation_counts_words(self):
        tokens = TokenUsageTracker.estimate_tokens('Hello world from QODE')
        self.assertEqual(tokens, 4)


class TestExportValidation(unittest.TestCase):
    def test_validate_output_filename_defaults_extension(self):
        path = validate_output_filename('analysis_report', default_extension='.txt')
        self.assertEqual(path.suffix, '.txt')

    def test_validate_output_filename_rejects_unsupported_extension(self):
        with self.assertRaises(ValueError):
            validate_output_filename('analysis_report.exe')


class TestHistoryManager(unittest.TestCase):
    def test_history_records_and_reads(self):
        temp_file = Path('temp_history.json')
        if temp_file.exists():
            temp_file.unlink()
        history = HistoryManager(str(temp_file))
        history.record('test query', {'roles': ['Business']}, 7, 'displayed')
        self.assertEqual(len(history.get_history()), 1)
        self.assertEqual(history.get_history()[0]['query'], 'test query')
        temp_file.unlink()


if __name__ == '__main__':
    unittest.main()
