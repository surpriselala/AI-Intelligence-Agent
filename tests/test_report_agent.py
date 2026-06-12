import tempfile
import unittest
from datetime import date
from pathlib import Path

from agents.report_agent import build_daily_report, get_daily_report_path, save_report


class ReportAgentTest(unittest.TestCase):
    def test_build_daily_report_returns_markdown(self) -> None:
        report = build_daily_report([], [])

        self.assertIsInstance(report, str)
        self.assertIn("# Daily AI Intelligence Report", report)
        self.assertIn("## 1. Research Papers", report)
        self.assertIn("## 2. GitHub Projects", report)
        self.assertIn("---", report)
        self.assertIn("# 每日 AI 技术情报报告", report)
        self.assertIn("## 1. 研究论文", report)
        self.assertIn("## 2. GitHub 项目", report)

    def test_build_daily_report_uses_chinese_fields_when_available(self) -> None:
        report = build_daily_report(
            paper_summaries=[
                {
                    "title": "Example Paper",
                    "one_sentence_summary": "English summary",
                    "chinese_summary": "中文摘要",
                    "url": "https://example.com/paper",
                }
            ],
            repo_summaries=[],
        )

        self.assertIn("- Summary: English summary", report)
        self.assertIn("- 摘要：中文摘要", report)

    def test_build_daily_report_includes_news_when_provided(self) -> None:
        report = build_daily_report(
            paper_summaries=[],
            repo_summaries=[],
            news_summaries=[
                {
                    "title": "Example News",
                    "source": "Example Source",
                    "one_sentence_summary": "English news summary",
                    "chinese_summary": "中文新闻摘要",
                    "what_happened": "Something happened",
                    "chinese_what_happened": "发生了一件事",
                    "why_it_matters": "Important",
                    "chinese_why_it_matters": "很重要",
                    "impact": "Developer impact",
                    "chinese_impact": "开发者影响",
                    "related_technologies": "LLM",
                    "chinese_related_technologies": "LLM",
                    "url": "https://example.com/news",
                }
            ],
        )

        self.assertIn("## 3. Industry News", report)
        self.assertIn("- Source: Example Source", report)
        self.assertIn("- What Happened: Something happened", report)
        self.assertIn("## 3. 行业新闻", report)
        self.assertIn("- 摘要：中文新闻摘要", report)
        self.assertIn("- 发生了什么：发生了一件事", report)

    def test_save_report_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "daily_ai_report.md"

            saved_path = save_report("hello\n", output_path)

            self.assertEqual(saved_path, output_path)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "hello\n")

    def test_get_daily_report_path_uses_report_date(self) -> None:
        output_path = get_daily_report_path(
            output_dir="outputs",
            filename_prefix="daily_ai_report",
            report_date=date(2026, 6, 8),
        )

        self.assertEqual(output_path, Path("outputs") / "daily_ai_report_2026-06-08.md")


if __name__ == "__main__":
    unittest.main()
