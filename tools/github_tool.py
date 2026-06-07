"""GitHub repository collection tool placeholder for the MVP skeleton."""

from typing import Any


def search_github_repositories(
    query: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Return AI-related GitHub repositories.

    GitHub API integration will be implemented after the workflow skeleton is
    stable. The current placeholder keeps the MVP pipeline runnable offline.
    """
    if not query or max_results <= 0:
        return []
    return []
