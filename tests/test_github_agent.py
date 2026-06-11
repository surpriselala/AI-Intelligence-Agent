import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from agents.github_agent import (
    GITHUB_SUMMARY_FALLBACK,
    _format_prompt_template,
    _load_prompt_template,
    _merge_repository_summary,
    _score_repository_value,
    _select_repositories_with_local_score,
    _summarize_repository_with_openai,
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

    def test_load_prompt_template_uses_prompt_file_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            prompts_dir = base_dir / "prompts"
            prompts_dir.mkdir()
            (prompts_dir / "example_prompt.txt").write_text(
                "Hello {name}",
                encoding="utf-8",
            )

            with patch("agents.github_agent.BASE_DIR", base_dir):
                template = _load_prompt_template("example_prompt.txt", "Fallback")

        self.assertEqual(template, "Hello {name}")

    def test_load_prompt_template_uses_fallback_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("agents.github_agent.BASE_DIR", Path(temp_dir)):
                template = _load_prompt_template("missing.txt", "Fallback")

        self.assertEqual(template, "Fallback")

    def test_format_prompt_template_uses_fallback_when_formatting_fails(self) -> None:
        with patch(
            "agents.github_agent._load_prompt_template",
            return_value="Broken {missing}",
        ):
            prompt = _format_prompt_template(
                "example.txt",
                "Fallback {name}",
                name="Repo",
            )

        self.assertEqual(prompt, "Fallback Repo")

    def test_summarize_repository_with_openai_includes_readme_context(self) -> None:
        captured = {}

        def fake_call_openai_json(**kwargs):
            captured["user_message"] = kwargs["user_message"]
            return {
                "one_sentence_summary": "Summary",
                "technical_highlights": "Uses README details",
            }

        with patch(
            "agents.github_agent.fetch_repository_readme",
            return_value="README has installation and RAG examples.",
        ):
            with patch("agents.github_agent._call_openai_json", fake_call_openai_json):
                summary = _summarize_repository_with_openai(
                    {
                        "name": "owner/repo",
                        "description": "AI project.",
                        "stars": 10,
                        "language": "Python",
                        "topics": ["llm", "rag"],
                        "homepage": "https://example.com",
                        "license": "MIT",
                        "url": "https://github.com/owner/repo",
                    },
                    api_key="test-key",
                )

        self.assertEqual(summary["one_sentence_summary"], "Summary")
        self.assertIn("README has installation", captured["user_message"])
        self.assertIn("llm, rag", captured["user_message"])


if __name__ == "__main__":
    unittest.main()
