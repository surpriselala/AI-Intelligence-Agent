"""GitHub repository collection tool for fetching AI-related projects."""

import base64
import os
from typing import Any

from dotenv import load_dotenv


GITHUB_SEARCH_API_URL = "https://api.github.com/search/repositories"
GITHUB_REPOSITORY_API_URL = "https://api.github.com/repos"


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

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": min(max_results, 100),
    }

    try:
        response = requests.get(
            GITHUB_SEARCH_API_URL,
            headers=_get_github_headers(),
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


def fetch_repository_readme(
    full_name: str,
    max_chars: int = 6000,
) -> str:
    """Fetch and decode a repository README excerpt from the GitHub API."""
    if not full_name.strip() or "/" not in full_name or max_chars <= 0:
        return ""

    try:
        import requests
    except ImportError as error:
        print(f"Failed to import requests package: {error}")
        return ""

    url = f"{GITHUB_REPOSITORY_API_URL}/{full_name}/readme"

    try:
        response = requests.get(
            url,
            headers=_get_github_headers(),
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload.get("content", "")
        encoding = payload.get("encoding", "")
        if not isinstance(content, str) or encoding != "base64":
            return ""

        compact_content = "".join(content.split())
        decoded = base64.b64decode(compact_content).decode("utf-8", errors="replace")
        return decoded.strip()[:max_chars]
    except Exception as error:
        print(f"Failed to fetch GitHub README for {full_name}: {error}")
        return ""


def _repository_to_dict(item: dict[str, Any]) -> dict[str, Any]:
    """Convert one GitHub API repository item into a plain dictionary."""
    license_data = item.get("license") or {}
    if not isinstance(license_data, dict):
        license_data = {}

    return {
        "name": _normalize_text(str(item.get("full_name") or item.get("name") or "")),
        "description": _normalize_text(str(item.get("description") or "")),
        "stars": int(item.get("stargazers_count") or 0),
        "language": _normalize_text(str(item.get("language") or "")),
        "url": str(item.get("html_url") or ""),
        "created_at": str(item.get("created_at") or ""),
        "updated_at": str(item.get("updated_at") or ""),
        "topics": _normalize_topics(item.get("topics", [])),
        "homepage": str(item.get("homepage") or ""),
        "license": str(license_data.get("spdx_id") or license_data.get("name") or ""),
    }


def _normalize_text(value: str) -> str:
    """Collapse repeated whitespace and newlines into single spaces."""
    return " ".join(value.split())


def _normalize_topics(value: Any) -> list[str]:
    """Return a clean list of GitHub topic strings."""
    if not isinstance(value, list):
        return []
    return [_normalize_text(str(topic)) for topic in value if str(topic).strip()]


def _get_github_headers() -> dict[str, str]:
    """Build GitHub API headers, including GITHUB_TOKEN when configured."""
    load_dotenv()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    return headers
