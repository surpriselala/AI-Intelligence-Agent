"""arXiv collection tool for fetching recent AI papers."""

from typing import Any


def search_arxiv_papers(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search arXiv and return normalized paper dictionaries.

    Args:
        query: Search keywords or an arXiv query string.
        max_results: Maximum number of papers to return.

    Returns:
        A list of dictionaries with title, authors, summary, published_date, and
        url fields. Returns an empty list when input is invalid or arXiv fails.
    """
    if not query.strip() or max_results <= 0:
        return []

    try:
        import arxiv
    except ImportError as error:
        print(f"Failed to import arXiv package: {error}")
        return []

    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        client = arxiv.Client()
        papers = []

        for result in client.results(search):
            try:
                papers.append(_paper_to_dict(result))
            except Exception as error:
                print(f"Failed to parse arXiv paper: {error}")

        return papers
    except Exception as error:
        print(f"Failed to search arXiv papers: {error}")
        return []


def _paper_to_dict(result: Any) -> dict[str, Any]:
    """Convert one arXiv SDK result object into a plain dictionary."""
    return {
        "title": _normalize_text(result.title),
        "authors": [author.name for author in result.authors],
        "summary": _normalize_text(result.summary),
        "published_date": result.published.date().isoformat(),
        "url": result.entry_id,
    }


def _normalize_text(value: str) -> str:
    """Collapse repeated whitespace and newlines into single spaces."""
    return " ".join(value.split())
