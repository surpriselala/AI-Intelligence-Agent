import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from tools.arxiv_tool import _normalize_text, search_arxiv_papers


class ArxivToolTest(unittest.TestCase):
    def test_empty_query_returns_empty_list(self) -> None:
        papers = search_arxiv_papers("", max_results=3)

        self.assertEqual(papers, [])

    def test_zero_max_results_returns_empty_list(self) -> None:
        papers = search_arxiv_papers("AI agent", max_results=0)

        self.assertEqual(papers, [])

    def test_search_arxiv_papers_returns_list(self) -> None:
        fake_arxiv = SimpleNamespace(
            Search=lambda **kwargs: kwargs,
            Client=lambda: SimpleNamespace(results=lambda search: []),
            SortCriterion=SimpleNamespace(SubmittedDate="submitted_date"),
            SortOrder=SimpleNamespace(Descending="descending"),
        )

        with patch.dict("sys.modules", {"arxiv": fake_arxiv}):
            papers = search_arxiv_papers("AI agent", max_results=3)

        self.assertIsInstance(papers, list)

    def test_search_arxiv_papers_parses_sdk_results(self) -> None:
        fake_result = SimpleNamespace(
            title="A\nUseful   Paper",
            authors=[SimpleNamespace(name="Author A"), SimpleNamespace(name="Author B")],
            summary="This paper\n studies AI agents. ",
            published=datetime(2026, 6, 7),
            entry_id="https://arxiv.org/abs/2606.00001",
        )
        fake_arxiv = SimpleNamespace(
            Search=lambda **kwargs: kwargs,
            Client=lambda: SimpleNamespace(results=lambda search: [fake_result]),
            SortCriterion=SimpleNamespace(SubmittedDate="submitted_date"),
            SortOrder=SimpleNamespace(Descending="descending"),
        )

        with patch.dict("sys.modules", {"arxiv": fake_arxiv}):
            papers = search_arxiv_papers("AI agent", max_results=1)

        self.assertEqual(
            papers,
            [
                {
                    "title": "A Useful Paper",
                    "authors": ["Author A", "Author B"],
                    "summary": "This paper studies AI agents.",
                    "published_date": "2026-06-07",
                    "url": "https://arxiv.org/abs/2606.00001",
                }
            ],
        )

    def test_normalize_text_collapses_whitespace(self) -> None:
        self.assertEqual(_normalize_text("A\n  B\tC"), "A B C")


if __name__ == "__main__":
    unittest.main()
