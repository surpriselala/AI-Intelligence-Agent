"""GitHub repository collection tool for fetching AI-related projects."""

import os
from typing import Any

from dotenv import load_dotenv


GITHUB_SEARCH_API_URL = "https://api.github.com/search/repositories"


def search_github_repositories(
    query: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Search GitHub and return normalized repository dictionaries.

    Args:
        query: Search keywords or a GitHub repository search query.
        max_results: Maximum number of repositories to return.

    Returns:
        A list of dictionaries with name, description, stars, language, url,
        created_at, and updated_at fields. Returns an empty list when input is
        invalid or GitHub fails.
    """
    if not query.strip() or max_results <= 0:
        return []

    try:
        import requests
    except ImportError as error:
        print(f"Failed to import requests package: {error}")
        return []

    load_dotenv()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": min(max_results, 100),
    }

    try:
        response = requests.get(
            GITHUB_SEARCH_API_URL,
            headers=headers,
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items", [])
        if not isinstance(items, list):
            return []

        repositories = []
        for item in items[:max_results]:
            try:
                repositories.append(_repository_to_dict(item))
            except Exception as error:
                print(f"Failed to parse GitHub repository: {error}")

        return repositories
    except Exception as error:
        print(f"Failed to search GitHub repositories: {error}")
        return []


def _repository_to_dict(item: dict[str, Any]) -> dict[str, Any]:
    """Convert one GitHub API repository item into a plain dictionary."""
    return {
        "name": _normalize_text(str(item.get("full_name") or item.get("name") or "")),
        "description": _normalize_text(str(item.get("description") or "")),
        "stars": int(item.get("stargazers_count") or 0),
        "language": _normalize_text(str(item.get("language") or "")),
        "url": str(item.get("html_url") or ""),
        "created_at": str(item.get("created_at") or ""),
        "updated_at": str(item.get("updated_at") or ""),
    }


def _normalize_text(value: str) -> str:
    """Collapse repeated whitespace and newlines into single spaces."""
    return " ".join(value.split())
