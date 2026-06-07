"""Markdown report generation for the AI intelligence workflow."""

from datetime import date
from pathlib import Path
from typing import Any


def build_daily_report(
    paper_summaries: list[dict[str, Any]],
    repo_summaries: list[dict[str, Any]],
    news_summaries: list[dict[str, Any]] | None = None,
) -> str:
    """Build a structured Markdown report from prepared summaries."""
    lines = [
        "# Daily AI Intelligence Report",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "## 1. Research Papers",
        "",
    ]

    if paper_summaries:
        for index, paper in enumerate(paper_summaries, start=1):
            lines.extend(
                [
                    f"### Paper {index}: {paper.get('title', 'Untitled paper')}",
                    f"- Summary: {paper.get('one_sentence_summary', 'TBD')}",
                    f"- Research Problem: {paper.get('research_problem', 'TBD')}",
                    f"- Core Method: {paper.get('core_method', 'TBD')}",
                    f"- Innovation: {paper.get('innovation', 'TBD')}",
                    f"- Why It Matters: {paper.get('why_it_matters', 'TBD')}",
                    f"- Learning Value: {paper.get('learning_value', 'TBD')}",
                    f"- Link: {paper.get('url', '')}",
                    "",
                ]
            )
    else:
        lines.extend(["No papers selected yet.", ""])

    lines.extend(["## 2. GitHub Projects", ""])

    if repo_summaries:
        for index, repo in enumerate(repo_summaries, start=1):
            lines.extend(
                [
                    f"### Project {index}: {repo.get('name', 'Unnamed repository')}",
                    f"- Summary: {repo.get('one_sentence_summary', 'TBD')}",
                    f"- Main Features: {repo.get('main_features', 'TBD')}",
                    f"- Technical Highlights: {repo.get('technical_highlights', 'TBD')}",
                    f"- Learning Value: {repo.get('learning_value', 'TBD')}",
                    f"- Recommended For: {repo.get('recommended_for', 'TBD')}",
                    f"- Possible Use Cases: {repo.get('possible_use_cases', 'TBD')}",
                    f"- Stars: {repo.get('stars', 0)}",
                    f"- Link: {repo.get('url', '')}",
                    "",
                ]
            )
    else:
        lines.extend(["No repositories selected yet.", ""])

    if news_summaries is not None:
        lines.extend(["## 3. Industry News", ""])
        if news_summaries:
            for index, news in enumerate(news_summaries, start=1):
                lines.extend(
                    [
                        f"### News {index}: {news.get('title', 'Untitled news')}",
                        f"- Summary: {news.get('summary', 'TBD')}",
                        f"- Impact: {news.get('impact', 'TBD')}",
                        f"- Link: {news.get('url', '')}",
                        "",
                    ]
                )
        else:
            lines.extend(["No news selected yet.", ""])

    return "\n".join(lines).rstrip() + "\n"


def save_report(report: str, output_path: str | Path) -> Path:
    """Save a Markdown report, creating the output directory if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return path
