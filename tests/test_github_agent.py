import unittest
from unittest.mock import patch

from agents.github_agent import (
    GITHUB_SUMMARY_FALLBACK,
    _merge_repository_summary,
    _score_repository_value,
    _select_repositories_with_local_score,
    select_important_repositories,
    summarize_repository,
)


class GithubAgentTest(unittest.TestCase):
    def test_select_important_repositories_returns_empty_for_invalid_input(self) -> None:
        self.assertEqual(select_important_repositories([], top_k=3), [])
        self.assertEqual(select_important_repositories([{"name": "A"}], top_k=0), [])

    def test_select_important_repositories_uses_local_score_without_api_key(self) -> None:
        repos = [
            {"name": "owner/web-ui", "description": "A dashboard.", "stars": 5000},
            {
                "name": "owner/rag-agent",
                "description": "An LLM RAG agent framework.",
                "stars": 100,
            },
        ]

        with patch("agents.github_agent._get_openai_api_key", return_value=None):
            selected = select_important_repositories(repos, top_k=1)

        self.assertEqual(selected, [repos[0]])

    def test_select_repositories_with_local_score_prefers_relevance_and_stars(self) -> None:
        repos = [
            {"name": "owner/a", "description": "Small note.", "stars": 5},
            {
                "name": "owner/llm-agent",
                "description": "RAG and machine learning tools.",
                "stars": 20,
            },
        ]

        selected = _select_repositories_with_local_score(repos, top_k=1)

        self.assertEqual(selected, [repos[1]])

    def test_score_repository_value_uses_keywords_and_stars(self) -> None:
        repo = {
            "name": "owner/llm-agent",
            "description": "RAG and machine learning framework.",
            "stars": 1200,
        }

        self.assertGreater(_score_repository_value(repo), 0)

    def test_summarize_repository_includes_chinese_summary(self) -> None:
        with patch("agents.github_agent._get_openai_api_key", return_value=None):
            summary = summarize_repository(
                {
                    "name": "owner/example",
                    "description": "Example AI project.",
                    "stars": 10,
                    "url": "https://github.com/owner/example",
                }
            )

        self.assertEqual(summary["chinese_summary"], GITHUB_SUMMARY_FALLBACK)
        self.assertEqual(summary["name"], "owner/example")
        self.assertEqual(summary["url"], "https://github.com/owner/example")

    def test_summarize_repository_uses_openai_structured_summary_when_available(self) -> None:
        generated_summary = {
            "one_sentence_summary": "Short summary.",
            "chinese_summary": "中文摘要",
            "main_features": "Features",
            "technical_highlights": "Highlights",
            "learning_value": "Learning",
            "recommended_for": "Developers",
            "possible_use_cases": "Apps",
        }

        with patch("agents.github_agent._get_openai_api_key", return_value="test-key"):
            with patch(
                "agents.github_agent._summarize_repository_with_openai",
                return_value=generated_summary,
            ):
                summary = summarize_repository(
                    {
                        "name": "owner/example",
                        "description": "Example AI project.",
                        "stars": 10,
                        "url": "https://github.com/owner/example",
                    }
                )

        self.assertEqual(summary["one_sentence_summary"], "Short summary.")
        self.assertEqual(summary["main_features"], "Features")
        self.assertEqual(summary["stars"], 10)

    def test_merge_repository_summary_preserves_metadata(self) -> None:
        merged = _merge_repository_summary(
            {
                "name": "owner/original",
                "description": "Original description.",
                "stars": 99,
                "url": "https://github.com/owner/original",
            },
            {"one_sentence_summary": "Generated"},
        )

        self.assertEqual(merged["name"], "owner/original")
        self.assertEqual(merged["one_sentence_summary"], "Generated")
        self.assertEqual(merged["stars"], 99)
        self.assertEqual(merged["url"], "https://github.com/owner/original")


if __name__ == "__main__":
    unittest.main()
