import unittest
from unittest.mock import patch

from agents.paper_agent import (
    CHINESE_SUMMARY_FALLBACK,
    _merge_paper_summary,
    _score_paper_relevance,
    _select_papers_with_keyword_score,
    _translate_text_to_chinese,
    select_important_papers,
    summarize_paper,
)


class PaperAgentTest(unittest.TestCase):
    def test_select_important_papers_returns_empty_for_invalid_input(self) -> None:
        self.assertEqual(select_important_papers([], top_k=3), [])
        self.assertEqual(select_important_papers([{"title": "A"}], top_k=0), [])

    def test_select_important_papers_uses_keyword_score_without_api_key(self) -> None:
        papers = [
            {"title": "Quantum Hall phase", "summary": "Condensed matter physics."},
            {"title": "New RAG Agent", "summary": "A system for LLM applications."},
            {"title": "General statistics", "summary": "A math note."},
        ]

        with patch("agents.paper_agent._get_openai_api_key", return_value=None):
            selected = select_important_papers(papers, top_k=1)

        self.assertEqual(selected, [papers[1]])

    def test_select_papers_with_keyword_score_falls_back_to_original_order(self) -> None:
        papers = [
            {"title": "Paper A", "summary": "No keyword."},
            {"title": "Paper B", "summary": "No keyword."},
        ]

        selected = _select_papers_with_keyword_score(papers, top_k=1)

        self.assertEqual(selected, [papers[0]])

    def test_score_paper_relevance_weights_title_more_than_summary(self) -> None:
        paper = {
            "title": "LLM Agent System",
            "summary": "This paper studies RAG and machine learning.",
        }

        self.assertGreater(_score_paper_relevance(paper), 0)

    def test_summarize_paper_includes_chinese_summary(self) -> None:
        with patch("agents.paper_agent._get_openai_api_key", return_value=None):
            with patch("agents.paper_agent._translate_text_to_chinese", return_value="中文摘要"):
                summary = summarize_paper(
                    {
                        "title": "Example Paper",
                        "summary": "English abstract.",
                        "url": "https://example.com/paper",
                    }
                )

        self.assertEqual(summary["chinese_summary"], "中文摘要")

    def test_summarize_paper_uses_openai_structured_summary_when_available(self) -> None:
        generated_summary = {
            "one_sentence_summary": "Short English summary.",
            "chinese_summary": "中文摘要",
            "research_problem": "Problem",
            "core_method": "Method",
            "innovation": "Innovation",
            "why_it_matters": "Impact",
            "learning_value": "Learning",
        }

        with patch("agents.paper_agent._get_openai_api_key", return_value="test-key"):
            with patch(
                "agents.paper_agent._summarize_paper_with_openai",
                return_value=generated_summary,
            ):
                summary = summarize_paper(
                    {
                        "title": "Example Paper",
                        "summary": "English abstract.",
                        "url": "https://example.com/paper",
                    }
                )

        self.assertEqual(summary["one_sentence_summary"], "Short English summary.")
        self.assertEqual(summary["research_problem"], "Problem")
        self.assertEqual(summary["url"], "https://example.com/paper")

    def test_merge_paper_summary_preserves_metadata(self) -> None:
        with patch("agents.paper_agent._get_openai_api_key", return_value=None):
            with patch("agents.paper_agent._translate_text_to_chinese", return_value="中文摘要"):
                summary = summarize_paper(
                    {
                        "title": "Example Paper",
                        "summary": "English abstract.",
                        "url": "https://example.com/paper",
                    }
                )

        with patch("agents.paper_agent._translate_text_to_chinese", return_value="中文摘要"):
            merged = _merge_paper_summary(
                {
                    "title": "Original Title",
                    "summary": "Abstract",
                    "url": "https://example.com",
                },
                {"one_sentence_summary": "Generated"},
            )

        self.assertEqual(summary["chinese_summary"], "中文摘要")
        self.assertEqual(merged["title"], "Original Title")
        self.assertEqual(merged["one_sentence_summary"], "Generated")
        self.assertEqual(merged["url"], "https://example.com")

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
