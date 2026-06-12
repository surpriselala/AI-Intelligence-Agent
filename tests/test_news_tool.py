import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tools.news_tool import (
    _news_entry_to_dict,
    _normalize_text,
    _strip_html,
    collect_ai_news,
)


class NewsToolTest(unittest.TestCase):
    def test_collect_ai_news_returns_empty_for_invalid_max_results(self) -> None:
        self.assertEqual(collect_ai_news(max_results=0), [])

    def test_collect_ai_news_returns_empty_for_empty_feeds(self) -> None:
        self.assertEqual(collect_ai_news(max_results=3, feeds=[]), [])

    def test_collect_ai_news_parses_feed_entries(self) -> None:
        fake_entry = {
            "title": " New\nAI  Model ",
            "summary": "<p>A useful model update.</p>",
            "link": "https://example.com/news",
            "published": "2026-06-11",
        }
        fake_feedparser = SimpleNamespace(
            parse=lambda url: SimpleNamespace(entries=[fake_entry])
        )

        with patch.dict("sys.modules", {"feedparser": fake_feedparser}):
            news_items = collect_ai_news(
                max_results=1,
                feeds=[
                    {
                        "name": "Example Feed",
                        "url": "https://example.com/rss",
                        "source_type": "rss",
                    }
                ],
            )

        self.assertEqual(
            news_items,
            [
                {
                    "title": "New AI Model",
                    "source": "Example Feed",
                    "summary": "A useful model update.",
                    "published_date": "2026-06-11",
                    "url": "https://example.com/news",
                    "source_type": "rss",
                }
            ],
        )

    def test_collect_ai_news_skips_failed_feed(self) -> None:
        def raise_error(url):
            raise RuntimeError("feed failed")

        fake_feedparser = SimpleNamespace(parse=raise_error)

        with patch.dict("sys.modules", {"feedparser": fake_feedparser}):
            news_items = collect_ai_news(
                max_results=1,
                feeds=[{"name": "Bad Feed", "url": "https://example.com/rss"}],
            )

        self.assertEqual(news_items, [])

    def test_news_entry_to_dict_handles_object_entries(self) -> None:
        entry = SimpleNamespace(
            title="Example",
            description="<b>Description</b>",
            link="https://example.com",
            updated="2026-06-11",
        )

        news_item = _news_entry_to_dict(
            entry,
            {"name": "Example Feed", "source_type": "rss"},
        )

        self.assertEqual(news_item["title"], "Example")
        self.assertEqual(news_item["summary"], "Description")
        self.assertEqual(news_item["published_date"], "2026-06-11")

    def test_strip_html_extracts_text(self) -> None:
        self.assertEqual(_strip_html("<p>Hello <b>AI</b></p>"), "Hello AI")

    def test_normalize_text_collapses_whitespace(self) -> None:
        self.assertEqual(_normalize_text("A\n  B\tC"), "A B C")


if __name__ == "__main__":
    unittest.main()
