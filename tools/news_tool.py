"""AI news collection tool for fetching recent RSS items."""

from html.parser import HTMLParser
from typing import Any

from config import NEWS_FEEDS, NEWS_PER_FEED_LIMIT


def collect_ai_news(
    max_results: int = 10,
    feeds: list[dict[str, str]] | None = None,
    per_feed_limit: int = NEWS_PER_FEED_LIMIT,
) -> list[dict[str, Any]]:
    """Collect AI news from configured RSS feeds."""
    if max_results <= 0 or per_feed_limit <= 0:
        return []

    try:
        import feedparser
    except ImportError as error:
        print(f"Failed to import feedparser package: {error}")
        return []

    feed_configs = feeds if feeds is not None else NEWS_FEEDS
    if not feed_configs:
        return []

    news_items = []
    for feed_config in feed_configs:
        try:
            parsed_feed = feedparser.parse(feed_config.get("url", ""))
            entries = getattr(parsed_feed, "entries", [])
            feed_item_count = 0
            for entry in entries:
                try:
                    news_items.append(_news_entry_to_dict(entry, feed_config))
                    feed_item_count += 1
                except Exception as error:
                    print(f"Failed to parse news entry: {error}")
                if len(news_items) >= max_results:
                    return news_items
                if feed_item_count >= per_feed_limit:
                    break
        except Exception as error:
            print(f"Failed to parse news feed {feed_config.get('name', '')}: {error}")

    return news_items[:max_results]


def _news_entry_to_dict(
    entry: Any,
    feed_config: dict[str, str],
) -> dict[str, Any]:
    """Convert one feedparser entry into a plain dictionary."""
    summary = (
        _get_entry_value(entry, "summary")
        or _get_entry_value(entry, "description")
        or _get_entry_value(entry, "subtitle")
    )
    published_date = (
        _get_entry_value(entry, "published")
        or _get_entry_value(entry, "updated")
        or ""
    )
    return {
        "title": _normalize_text(_get_entry_value(entry, "title")),
        "source": feed_config.get("name", ""),
        "summary": _normalize_text(_strip_html(summary)),
        "published_date": _normalize_text(published_date),
        "url": str(_get_entry_value(entry, "link")),
        "source_type": feed_config.get("source_type", "rss"),
    }


def _get_entry_value(entry: Any, field: str) -> str:
    """Read a feedparser entry field from dict-like or object-like entries."""
    if isinstance(entry, dict):
        return str(entry.get(field) or "")
    return str(getattr(entry, field, "") or "")


def _normalize_text(value: str) -> str:
    """Collapse repeated whitespace and newlines into single spaces."""
    return " ".join(value.split())


def _strip_html(value: str) -> str:
    """Strip HTML tags from a feed summary."""
    parser = _HTMLTextExtractor()
    parser.feed(value)
    parser.close()
    return parser.text


class _HTMLTextExtractor(HTMLParser):
    """Tiny HTML text extractor for RSS summaries."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    @property
    def text(self) -> str:
        return " ".join(self._parts)

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._parts.append(data.strip())
