import tempfile
import unittest
from pathlib import Path

from tools.dashboard_data_tool import (
    build_dashboard_data,
    build_dashboard_payload,
    parse_report,
    sort_items,
)


class DashboardDataToolTest(unittest.TestCase):
    def test_parse_report_extracts_english_items(self) -> None:
        report = """# Daily AI Intelligence Report

Date: 2026-06-12

## 1. Research Papers

### Paper 1: Example Paper
- Summary: Paper summary
- Link: https://example.com/paper

## 2. GitHub Projects

### Project 1: owner/repo
- Summary: Repo summary
- Stars: 123
- Link: https://github.com/owner/repo

## 3. Industry News

### News 1: Example News
- Source: Example Source
- Summary: News summary
- Link: https://example.com/news

---

# 每日 AI 技术情报报告
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "daily_ai_report_2026-06-12.md"
            report_path.write_text(report, encoding="utf-8")

            parsed = parse_report(report_path)

        self.assertEqual(parsed["date"], "2026-06-12")
        self.assertEqual(parsed["articles"][0]["title"], "Example Paper")
        self.assertEqual(parsed["projects"][0]["stars"], "123")
        self.assertEqual(parsed["news"][0]["source"], "Example Source")

    def test_build_dashboard_payload_counts_items_and_stars(self) -> None:
        reports = [
            {
                "date": "2026-06-12",
                "path": "report.md",
                "articles": [{"title": "Paper", "date": "2026-06-12", "score": 0, "order": 1}],
                "projects": [
                    {
                        "title": "Repo",
                        "date": "2026-06-12",
                        "score": 0,
                        "order": 1,
                        "stars": "1,200",
                    }
                ],
                "news": [{"title": "News", "date": "2026-06-12", "score": 0, "order": 1}],
            }
        ]

        payload = build_dashboard_payload(reports)

        self.assertEqual(payload["totals"]["articles"], 1)
        self.assertEqual(payload["totals"]["projects"], 1)
        self.assertEqual(payload["totals"]["news"], 1)
        self.assertEqual(payload["totals"]["stars"], 1200)
        self.assertEqual(payload["dashboard"]["articles"][0]["title"], "Paper")

    def test_sort_items_uses_score_then_date(self) -> None:
        items = [
            {"title": "Older", "score": 0, "date": "2026-06-10", "order": 1},
            {"title": "Higher score", "score": 2, "date": "2026-06-09", "order": 1},
            {"title": "Newer", "score": 0, "date": "2026-06-12", "order": 1},
        ]

        sorted_items = sort_items(items)

        self.assertEqual([item["title"] for item in sorted_items], ["Higher score", "Newer", "Older"])

    def test_build_dashboard_data_writes_javascript_file(self) -> None:
        report = """# Daily AI Intelligence Report

Date: 2026-06-12

## 1. Research Papers

### Paper 1: Example Paper
- Summary: Paper summary
- Link: https://example.com/paper
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "daily_ai_report_2026-06-12.md").write_text(report, encoding="utf-8")
            output_path = temp_path / "dashboard_data.js"

            saved_path = build_dashboard_data(temp_path, output_path)

            self.assertEqual(saved_path, output_path)
            self.assertIn("window.AI_DASHBOARD_DATA", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
