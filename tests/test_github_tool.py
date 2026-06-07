import unittest

from tools.github_tool import search_github_repositories


class GithubToolTest(unittest.TestCase):
    def test_search_github_repositories_returns_list(self) -> None:
        repos = search_github_repositories("AI agent", max_results=3)

        self.assertIsInstance(repos, list)


if __name__ == "__main__":
    unittest.main()
