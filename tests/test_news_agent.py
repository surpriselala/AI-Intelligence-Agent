import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.news_agent import (
    NEWS_SUMMARY_FALLBACK,
    _format_prompt_template,
    _load_prompt_template,
    _merge_news_summary,
    _score_news_relevance,
    _select_news_with_keyword_score,
    select_important_news,
    summarize_news_item,
)


class NewsAgentTest(unittest.TestCase):
    def test_select_important_news_returns_empty_for_invalid_input(self) -> None:
        self.assertEqual(select_important_news([], top_k=3), [])
        self.assertEqual(select_important_news([{"title": "A"}], top_k=0), [])

    def test_select_important_news_uses_keyword_score_without_api_key(self) -> None:
        news_items = [
            {"title": "Company event", "summary": "General update."},
            {"title": "New LLM API", "summary": "Developer model release."},
        ]

        with patch("agents.news_agent._get_openai_api_key", return_value=None):
            selected = select_important_news(news_items, top_k=1)

        self.assertEqual(selected, [news_items[1]])

    def test_select_news_with_keyword_score_falls_back_to_original_order(self) -> None:
        news_items = [
            {"title": "General update", "summary": "Nothing special."},
            {"title": "Other update", "summary": "Nothing special."},
        ]

        selected = _select_news_with_keyword_score(news_items, top_k=1)

        self.assertEqual(selected, [news_items[0]])

    def test_score_news_relevance_detects_keywords(self) -> None:
        news_item = {
            "title": "New LLM API",
            "summary": "Developer model release and benchmark.",
        }

        self.assertGreater(_score_news_relevance(news_item), 0)

    def test_summarize_news_item_includes_chinese_summary(self) -> None:
        with patch("agents.news_agent._get_openai_api_key", return_value=None):
            summary = summarize_news_item(
                {
                    "title": "Example News",
                    "source": "Example",
                    "summary": "English summary.",
                    "url": "https://example.com/news",
                }
            )

        self.assertEqual(summary["chinese_summary"], NEWS_SUMMARY_FALLBACK)
        self.assertEqual(summary["title"], "Example News")
        self.assertEqual(summary["url"], "https://example.com/news")

    def test_summarize_news_item_uses_openai_summary_when_available(self) -> None:
        generated_summary = {
            "one_sentence_summary": "Short summary.",
            "chinese_summary": "中文摘要",
            "what_happened": "Event",
            "chinese_what_happened": "事件",
            "impact": "Impact",
            "chinese_impact": "影响",
        }

        with patch("agents.news_agent._get_openai_api_key", return_value="test-key"):
            with patch(
                "agents.news_agent._summarize_news_with_openai",
                return_value=generated_summary,
            ):
                summary = summarize_news_item(
                    {
                        "title": "Example News",
                        "source": "Example",
                        "summary": "English summary.",
                        "url": "https://example.com/news",
                    }
                )

        self.assertEqual(summary["one_sentence_summary"], "Short summary.")
        self.assertEqual(summary["chinese_what_happened"], "事件")

    def test_merge_news_summary_preserves_metadata(self) -> None:
        merged = _merge_news_summary(
            {
                "title": "Original title",
                "source": "Example",
                "summary": "Original summary.",
                "url": "https://example.com",
            },
            {"one_sentence_summary": "Generated"},
        )

        self.assertEqual(merged["title"], "Original title")
        self.assertEqual(merged["source"], "Example")
        self.assertEqual(merged["one_sentence_summary"], "Generated")
        self.assertEqual(merged["url"], "https://example.com")

    def test_load_prompt_template_uses_prompt_file_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            prompts_dir = base_dir / "prompts"
            prompts_dir.mkdir()
            (prompts_dir / "news_prompt.txt").write_text("Hello {name}", encoding="utf-8")

            with patch("agents.news_agent.BASE_DIR", base_dir):
                template = _load_prompt_template("news_prompt.txt", "Fallback")

        self.assertEqual(template, "Hello {name}")

    def test_load_prompt_template_uses_fallback_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("agents.news_agent.BASE_DIR", Path(temp_dir)):
                template = _load_prompt_template("missing.txt", "Fallback")

        self.assertEqual(template, "Fallback")

    def test_format_prompt_template_uses_fallback_when_formatting_fails(self) -> None:
        with patch(
            "agents.news_agent._load_prompt_template",
            return_value="Broken {missing}",
        ):
            prompt = _format_prompt_template(
                "news_prompt.txt",
                "Fallback {name}",
                name="News",
            )

        self.assertEqual(prompt, "Fallback News")


if __name__ == "__main__":
    unittest.main()
