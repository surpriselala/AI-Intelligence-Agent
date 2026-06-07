import tempfile
import unittest
from pathlib import Path

from agents.report_agent import build_daily_report, save_report


class ReportAgentTest(unittest.TestCase):
    def test_build_daily_report_returns_markdown(self) -> None:
        report = build_daily_report([], [])

        self.assertIsInstance(report, str)
        self.assertIn("# Daily AI Intelligence Report", report)
        self.assertIn("## 1. Research Papers", report)
        self.assertIn("## 2. GitHub Projects", report)

    def test_save_report_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "daily_ai_report.md"

            saved_path = save_report("hello\n", output_path)

            self.assertEqual(saved_path, output_path)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "hello\n")


if __name__ == "__main__":
    unittest.main()
