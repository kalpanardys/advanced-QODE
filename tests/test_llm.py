import os
import sys
import unittest

# Ensure repo root is importable for tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis import LLMSummarizer, QodeAnalyzer


class TestLLMSummarizer(unittest.TestCase):
    def test_mock_summarizer_returns_text(self):
        analyzer = QodeAnalyzer('sample_questions.xlsm')
        result = analyzer.analyze_query('Show me the Jira tool flow')
        summarizer = LLMSummarizer(provider='mock')
        summary = summarizer.summarize(result, 'Show me the Jira tool flow')
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)


if __name__ == '__main__':
    unittest.main()
