"""Command-line entry point for the MVP workflow."""

from datetime import date
from typing import Any

from agents.github_agent import select_important_repositories, summarize_repository
from agents.news_agent import select_important_news, summarize_news_item
from agents.paper_agent import select_important_papers, summarize_paper
from agents.report_agent import build_daily_report, get_daily_report_path, save_report
from config import (
    AI_KEYWORDS,
    ARXIV_MAX_RESULTS,
    BASE_DIR,
    GITHUB_SELECTION_TOP_K,
    GITHUB_MAX_RESULTS,
    NEWS_SELECTION_TOP_K,
    NEWS_MAX_RESULTS,
    PAPER_SELECTION_TOP_K,
    REPORT_FILENAME_PREFIX,
    REPORT_OUTPUT_DIR,
)
from database.db import get_database_url
from database.repository import save_daily_report_result
from tools.dashboard_data_tool import build_dashboard_data
from tools.arxiv_tool import search_arxiv_papers
from tools.github_tool import search_github_repositories
from tools.news_tool import collect_ai_news


def main() -> None:
    """Run the fixed MVP workflow and save a Markdown report."""
    report_date = date.today()
    query = " OR ".join(AI_KEYWORDS)

    papers = search_arxiv_papers(query, max_results=ARXIV_MAX_RESULTS)
    repos = search_github_repositories(query, max_results=GITHUB_MAX_RESULTS)
    news_items = collect_ai_news(max_results=NEWS_MAX_RESULTS)

    selected_papers = select_important_papers(papers, top_k=PAPER_SELECTION_TOP_K)
    selected_repos = select_important_repositories(repos, top_k=GITHUB_SELECTION_TOP_K)
    selected_news = select_important_news(news_items, top_k=NEWS_SELECTION_TOP_K)

    paper_summaries = [
        _merge_source_and_summary(paper, summarize_paper(paper))
        for paper in selected_papers
    ]
    repo_summaries = [
        _merge_source_and_summary(repo, summarize_repository(repo))
        for repo in selected_repos
    ]
    news_summaries = [
        _merge_source_and_summary(news_item, summarize_news_item(news_item))
        for news_item in selected_news
    ]

    report = build_daily_report(
        paper_summaries=paper_summaries,
        repo_summaries=repo_summaries,
        news_summaries=news_summaries,
    )
    output_path = get_daily_report_path(
        output_dir=REPORT_OUTPUT_DIR,
        filename_prefix=REPORT_FILENAME_PREFIX,
        report_date=report_date,
    )
    save_report(report, output_path)
    dashboard_data_path = BASE_DIR / "frontend" / "data" / "dashboard_data.js"
    build_dashboard_data(REPORT_OUTPUT_DIR, dashboard_data_path)
    _persist_report_if_configured(
        report_date=report_date,
        report=report,
        output_path=output_path,
        paper_summaries=paper_summaries,
        repo_summaries=repo_summaries,
        news_summaries=news_summaries,
    )
    print(f"Report saved to {output_path}")
    print(f"Dashboard data saved to {dashboard_data_path}")


def _merge_source_and_summary(
    source_item: dict[str, Any],
    summary_item: dict[str, Any],
) -> dict[str, Any]:
    """Keep source metadata while allowing the generated summary to override text."""
    merged = dict(source_item)
    merged.update(summary_item)
    return merged


def _persist_report_if_configured(
    *,
    report_date: date,
    report: str,
    output_path: Any,
    paper_summaries: list[dict[str, Any]],
    repo_summaries: list[dict[str, Any]],
    news_summaries: list[dict[str, Any]],
) -> None:
    """Persist the report when DATABASE_URL is configured."""
    if not get_database_url():
        return

    try:
        save_daily_report_result(
            report_date=report_date,
            report_content=report,
            output_path=output_path,
            paper_summaries=paper_summaries,
            repo_summaries=repo_summaries,
            news_summaries=news_summaries,
        )
        print("Database persistence completed.")
    except Exception as error:
        print(f"Database persistence failed: {error}")


if __name__ == "__main__":
    main()
