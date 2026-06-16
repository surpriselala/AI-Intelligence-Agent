"""Shared item query and mapping helpers for API routes."""

from __future__ import annotations

import math
from typing import Any

from sqlalchemy.orm import Session

from api.schemas import DashboardItem, PaginatedDashboardItems
from database.models import Article, GithubRepository, News, Report, ReportItem


ITEM_TYPES = {
    "articles": "article",
    "news": "news",
    "projects": "github_repository",
}


def get_latest_report(db: Session) -> Report | None:
    """Return the latest report by report date."""
    return db.query(Report).order_by(Report.report_date.desc()).first()


def get_report_items_for_category(
    db: Session,
    category: str,
) -> list[DashboardItem]:
    """Return all report-backed items for one frontend category."""
    item_type = ITEM_TYPES[category]
    rows = (
        db.query(ReportItem, Report)
        .join(Report, Report.id == ReportItem.report_id)
        .filter(ReportItem.item_type == item_type)
        .order_by(Report.report_date.desc(), ReportItem.rank.asc())
        .all()
    )
    return [
        mapped
        for report_item, report in rows
        if (mapped := map_report_item(db, report_item, report)) is not None
    ]


def get_latest_dashboard_items(
    db: Session,
    report: Report,
    limit_per_category: int = 4,
) -> dict[str, list[DashboardItem]]:
    """Return dashboard groups from the latest report."""
    grouped = {"articles": [], "news": [], "projects": []}
    report_items = (
        db.query(ReportItem)
        .filter(ReportItem.report_id == report.id)
        .order_by(ReportItem.rank.asc())
        .all()
    )

    for report_item in report_items:
        mapped = map_report_item(db, report_item, report)
        if mapped is None:
            continue
        if len(grouped[mapped.type]) < limit_per_category:
            grouped[mapped.type].append(mapped)

    return grouped


def paginate_dashboard_items(
    items: list[DashboardItem],
    *,
    page: int,
    page_size: int,
) -> PaginatedDashboardItems:
    """Paginate already mapped items."""
    if page < 1:
        page = 1
    page_size = min(max(page_size, 1), 50)
    total = len(items)
    total_pages = max(1, math.ceil(total / page_size))
    current_page = min(page, total_pages)
    start = (current_page - 1) * page_size
    return PaginatedDashboardItems(
        items=items[start : start + page_size],
        page=current_page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


def filter_dashboard_items(
    items: list[DashboardItem],
    *,
    query: str = "",
    topic: str = "",
) -> list[DashboardItem]:
    """Filter mapped items by text query and topic."""
    normalized_query = query.strip().lower()
    normalized_topic = topic.strip().lower()

    def matches(item: DashboardItem) -> bool:
        haystack = " ".join(
            str(value)
            for value in [
                item.title,
                item.summary,
                item.date,
                item.source,
                item.language,
                *item.tags,
            ]
            if value
        ).lower()
        return (
            (not normalized_query or normalized_query in haystack)
            and (not normalized_topic or normalized_topic in haystack)
        )

    return [item for item in items if matches(item)]


def map_report_item(
    db: Session,
    report_item: ReportItem,
    report: Report,
) -> DashboardItem | None:
    """Map a stored report item to the shared API item shape."""
    if report_item.item_type == "article":
        article = db.get(Article, report_item.item_id)
        if article is None:
            return None
        return DashboardItem(
            id=f"article-{article.id}-{report_item.id}",
            type="articles",
            title=article.title,
            summary=_summary(article.summary_data, article.abstract),
            url=article.url,
            date=report.report_date.isoformat(),
            tags=_string_list(article.tags),
            score=report_item.score_snapshot or 0,
            order=report_item.rank,
        )

    if report_item.item_type == "news":
        news = db.get(News, report_item.item_id)
        if news is None:
            return None
        return DashboardItem(
            id=f"news-{news.id}-{report_item.id}",
            type="news",
            title=news.title,
            summary=_summary(news.summary_data, news.content),
            url=news.url,
            date=report.report_date.isoformat(),
            source=news.source,
            tags=_string_list(news.tags),
            score=report_item.score_snapshot or 0,
            order=report_item.rank,
        )

    if report_item.item_type == "github_repository":
        repo = db.get(GithubRepository, report_item.item_id)
        if repo is None:
            return None
        return DashboardItem(
            id=f"project-{repo.id}-{report_item.id}",
            type="projects",
            title=repo.full_name,
            summary=_summary(repo.summary_data, repo.description),
            url=repo.url,
            date=report.report_date.isoformat(),
            stars=repo.stars,
            language=repo.language,
            tags=_string_list(repo.tags or repo.topics),
            score=report_item.score_snapshot or 0,
            order=report_item.rank,
        )

    return None


def _summary(summary_data: Any, fallback: str | None) -> str:
    if isinstance(summary_data, dict):
        for key in ("one_sentence_summary", "summary", "main_features", "what_happened"):
            value = summary_data.get(key)
            if value:
                return str(value)
    return fallback or ""


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, tuple):
        return [str(item) for item in value if item]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(value)]
