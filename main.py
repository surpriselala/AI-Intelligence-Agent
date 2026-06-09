"""Command-line entry point for the MVP workflow."""

from agents.github_agent import select_important_repositories, summarize_repository
from agents.paper_agent import select_important_papers, summarize_paper
from agents.report_agent import build_daily_report, get_daily_report_path, save_report
from config import (
    AI_KEYWORDS,
    ARXIV_MAX_RESULTS,
    GITHUB_MAX_RESULTS,
    REPORT_FILENAME_PREFIX,
    REPORT_OUTPUT_DIR,
    SELECTION_TOP_K,
)
from tools.arxiv_tool import search_arxiv_papers
from tools.github_tool import search_github_repositories


def main() -> None:
    """Run the fixed MVP workflow and save a Markdown report."""
    query = " OR ".join(AI_KEYWORDS)

    papers = search_arxiv_papers(query, max_results=ARXIV_MAX_RESULTS)
    repos = search_github_repositories(query, max_results=GITHUB_MAX_RESULTS)

    selected_papers = select_important_papers(papers, top_k=SELECTION_TOP_K)
    selected_repos = select_important_repositories(repos, top_k=SELECTION_TOP_K)

    paper_summaries = [summarize_paper(paper) for paper in selected_papers]
    repo_summaries = [summarize_repository(repo) for repo in selected_repos]

    report = build_daily_report(
        paper_summaries=paper_summaries,
        repo_summaries=repo_summaries,
    )
    output_path = get_daily_report_path(
        output_dir=REPORT_OUTPUT_DIR,
        filename_prefix=REPORT_FILENAME_PREFIX,
    )
    save_report(report, output_path)
    print(f"Report saved to {output_path}")


if __name__ == "__main__":
    main()
