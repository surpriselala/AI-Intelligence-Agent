import unittest
from base64 import b64encode
from types import SimpleNamespace
from unittest.mock import patch

from tools.github_tool import (
    _normalize_text,
    _repository_to_dict,
    fetch_repository_readme,
    search_github_repositories,
)


class GithubToolTest(unittest.TestCase):
    def test_empty_query_returns_empty_list(self) -> None:
        repos = search_github_repositories("", max_results=3)

        self.assertEqual(repos, [])

    def test_zero_max_results_returns_empty_list(self) -> None:
        repos = search_github_repositories("AI agent", max_results=0)

        self.assertEqual(repos, [])

    def test_search_github_repositories_returns_list(self) -> None:
        fake_response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"items": []},
        )
        fake_requests = SimpleNamespace(get=lambda *args, **kwargs: fake_response)

        with patch.dict("sys.modules", {"requests": fake_requests}):
            repos = search_github_repositories("AI agent", max_results=3)

        self.assertIsInstance(repos, list)

    def test_search_github_repositories_parses_api_results(self) -> None:
        fake_item = {
            "full_name": "owner/useful-ai-agent",
            "description": "A\nuseful   AI agent framework.",
            "stargazers_count": 1200,
            "language": "Python",
            "html_url": "https://github.com/owner/useful-ai-agent",
            "created_at": "2026-06-07T00:00:00Z",
            "updated_at": "2026-06-08T00:00:00Z",
            "topics": ["llm", "ai-agent"],
            "homepage": "https://example.com",
            "license": {"spdx_id": "MIT"},
        }
        fake_response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"items": [fake_item]},
        )
        fake_requests = SimpleNamespace(get=lambda *args, **kwargs: fake_response)

        with patch.dict("sys.modules", {"requests": fake_requests}):
            repos = search_github_repositories("AI agent", max_results=1)

        self.assertEqual(
            repos,
            [
                {
                    "name": "owner/useful-ai-agent",
                    "description": "A useful AI agent framework.",
                    "stars": 1200,
                    "language": "Python",
                    "url": "https://github.com/owner/useful-ai-agent",
                    "created_at": "2026-06-07T00:00:00Z",
                    "updated_at": "2026-06-08T00:00:00Z",
                    "topics": ["llm", "ai-agent"],
                    "homepage": "https://example.com",
                    "license": "MIT",
                }
            ],
        )

    def test_search_github_repositories_returns_empty_on_request_error(self) -> None:
        def raise_error(*args, **kwargs):
            raise RuntimeError("network failed")

        fake_requests = SimpleNamespace(get=raise_error)

        with patch.dict("sys.modules", {"requests": fake_requests}):
            repos = search_github_repositories("AI agent", max_results=1)

        self.assertEqual(repos, [])

    def test_repository_to_dict_handles_missing_fields(self) -> None:
        repo = _repository_to_dict({"name": "repo"})

        self.assertEqual(repo["name"], "repo")
        self.assertEqual(repo["description"], "")
        self.assertEqual(repo["stars"], 0)
        self.assertEqual(repo["language"], "")
        self.assertEqual(repo["topics"], [])
        self.assertEqual(repo["homepage"], "")
        self.assertEqual(repo["license"], "")

    def test_normalize_text_collapses_whitespace(self) -> None:
        self.assertEqual(_normalize_text("A\n  B\tC"), "A B C")

    def test_fetch_repository_readme_decodes_base64_content(self) -> None:
        readme_text = "# Project\n\nUseful AI project."
        encoded = b64encode(readme_text.encode("utf-8")).decode("ascii")
        fake_response = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"encoding": "base64", "content": encoded},
        )
        fake_requests = SimpleNamespace(get=lambda *args, **kwargs: fake_response)

        with patch.dict("sys.modules", {"requests": fake_requests}):
            readme = fetch_repository_readme("owner/repo", max_chars=12)

        self.assertEqual(readme, "# Project\n\nU")

    def test_fetch_repository_readme_returns_empty_on_request_error(self) -> None:
        def raise_error(*args, **kwargs):
            raise RuntimeError("network failed")

        fake_requests = SimpleNamespace(get=raise_error)

        with patch.dict("sys.modules", {"requests": fake_requests}):
            readme = fetch_repository_readme("owner/repo")

        self.assertEqual(readme, "")


if __name__ == "__main__":
    unittest.main()
