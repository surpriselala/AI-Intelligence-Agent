import unittest
from unittest.mock import patch

from agents.paper_agent import (
    CHINESE_SUMMARY_FALLBACK,
    _translate_text_to_chinese,
    summarize_paper,
)


class PaperAgentTest(unittest.TestCase):
    def test_summarize_paper_includes_chinese_summary(self) -> None:
        with patch("agents.paper_agent._translate_text_to_chinese", return_value="中文摘要"):
            summary = summarize_paper(
                {
                    "title": "Example Paper",
                    "summary": "English abstract.",
                    "url": "https://example.com/paper",
                }
            )

        self.assertEqual(summary["chinese_summary"], "中文摘要")

    def test_translate_text_to_chinese_returns_fallback_without_api_key(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with patch("agents.paper_agent.load_dotenv", return_value=False):
                translated_text = _translate_text_to_chinese("English abstract.")

        self.assertEqual(translated_text, CHINESE_SUMMARY_FALLBACK)

    def test_translate_text_to_chinese_handles_empty_text(self) -> None:
        translated_text = _translate_text_to_chinese("  ")

        self.assertEqual(translated_text, "待补充")


if __name__ == "__main__":
    unittest.main()
