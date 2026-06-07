import unittest

from tools.arxiv_tool import search_arxiv_papers


class ArxivToolTest(unittest.TestCase):
    def test_search_arxiv_papers_returns_list(self) -> None:
        papers = search_arxiv_papers("AI agent", max_results=3)

        self.assertIsInstance(papers, list)


if __name__ == "__main__":
    unittest.main()
