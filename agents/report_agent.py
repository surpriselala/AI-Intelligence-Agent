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
    lines = _build_english_report_section(
        paper_summaries=paper_summaries,
        repo_summaries=repo_summaries,
        news_summaries=news_summaries,
    )
    lines.extend(
        [
            "---",
            "",
        ]
    )
    lines.extend(
        _build_chinese_report_section(
            paper_summaries=paper_summaries,
            repo_summaries=repo_summaries,
            news_summaries=news_summaries,
        )
    )

    return "\n".join(lines).rstrip() + "\n"


def _build_english_report_section(
    paper_summaries: list[dict[str, Any]],
    repo_summaries: list[dict[str, Any]],
    news_summaries: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Build the English section of the daily report."""
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

    return lines


def _build_chinese_report_section(
    paper_summaries: list[dict[str, Any]],
    repo_summaries: list[dict[str, Any]],
    news_summaries: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Build the Chinese section of the daily report."""
    lines = [
        "# 每日 AI 技术情报报告",
        "",
        f"日期：{date.today().isoformat()}",
        "",
        "## 1. 研究论文",
        "",
    ]

    if paper_summaries:
        for index, paper in enumerate(paper_summaries, start=1):
            lines.extend(
                [
                    f"### 论文 {index}：{paper.get('title', '未命名论文')}",
                    f"- 摘要：{paper.get('chinese_summary', paper.get('one_sentence_summary', '待补充'))}",
                    f"- 研究问题：{paper.get('chinese_research_problem', paper.get('research_problem', '待补充'))}",
                    f"- 核心方法：{paper.get('chinese_core_method', paper.get('core_method', '待补充'))}",
                    f"- 创新点：{paper.get('chinese_innovation', paper.get('innovation', '待补充'))}",
                    f"- 重要性：{paper.get('chinese_why_it_matters', paper.get('why_it_matters', '待补充'))}",
                    f"- 学习价值：{paper.get('chinese_learning_value', paper.get('learning_value', '待补充'))}",
                    f"- 链接：{paper.get('url', '')}",
                    "",
                ]
            )
    else:
        lines.extend(["暂无入选论文。", ""])

    lines.extend(["## 2. GitHub 项目", ""])

    if repo_summaries:
        for index, repo in enumerate(repo_summaries, start=1):
            lines.extend(
                [
                    f"### 项目 {index}：{repo.get('name', '未命名项目')}",
                    f"- 摘要：{repo.get('chinese_summary', repo.get('one_sentence_summary', '待补充'))}",
                    f"- 主要功能：{repo.get('chinese_main_features', repo.get('main_features', '待补充'))}",
                    f"- 技术亮点：{repo.get('chinese_technical_highlights', repo.get('technical_highlights', '待补充'))}",
                    f"- 学习价值：{repo.get('chinese_learning_value', repo.get('learning_value', '待补充'))}",
                    f"- 推荐人群：{repo.get('chinese_recommended_for', repo.get('recommended_for', '待补充'))}",
                    f"- 使用场景：{repo.get('chinese_possible_use_cases', repo.get('possible_use_cases', '待补充'))}",
                    f"- Stars：{repo.get('stars', 0)}",
                    f"- 链接：{repo.get('url', '')}",
                    "",
                ]
            )
    else:
        lines.extend(["暂无入选 GitHub 项目。", ""])

    if news_summaries is not None:
        lines.extend(["## 3. 行业新闻", ""])
        if news_summaries:
            for index, news in enumerate(news_summaries, start=1):
                lines.extend(
                    [
                        f"### 新闻 {index}：{news.get('title', '未命名新闻')}",
                        f"- 摘要：{news.get('chinese_summary', news.get('summary', '待补充'))}",
                        f"- 影响：{news.get('chinese_impact', news.get('impact', '待补充'))}",
                        f"- 链接：{news.get('url', '')}",
                        "",
                    ]
                )
        else:
            lines.extend(["暂无入选行业新闻。", ""])

    return lines


def get_daily_report_path(
    output_dir: str | Path,
    filename_prefix: str = "daily_ai_report",
    report_date: date | None = None,
) -> Path:
    """Build the output path for one report file per calendar day."""
    current_date = report_date or date.today()
    filename = f"{filename_prefix}_{current_date.isoformat()}.md"
    return Path(output_dir) / filename


def save_report(report: str, output_path: str | Path) -> Path:
    """Save a Markdown report, creating the output directory if needed."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return path
