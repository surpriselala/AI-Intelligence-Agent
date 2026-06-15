"""Persistence operations for generated daily reports."""

from __future__ import annotations

from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from database.db import init_database, session_scope
from database.models import Article, GithubRepository, News, Report, ReportItem, Run


def save_daily_report_result(
    *,
    report_date: date,
    report_content: str,
    output_path: str | Path,
    paper_summaries: list[dict[str, Any]],
    repo_summaries: list[dict[str, Any]],
    news_summaries: list[dict[str, Any]],
    dashboard_payload: dict[str, Any] | None = None,
) -> None:
    """Persist one completed daily report using the configured database."""
    init_database()
    with session_scope() as session:
        save_daily_report(
            session=session,
            report_date=report_date,
            report_content=report_content,
            output_path=output_path,
            paper_summaries=paper_summaries,
            repo_summaries=repo_summaries,
            news_summaries=news_summaries,
            dashboard_payload=dashboard_payload,
        )


def save_daily_report(
    *,
    session: Session,
    report_date: date,
    report_content: str,
    output_path: str | Path,
    paper_summaries: list[dict[str, Any]],
    repo_summaries: list[dict[str, Any]],
    news_summaries: list[dict[str, Any]],
    dashboard_payload: dict[str, Any] | None = None,
) -> Report:
    """Persist one completed report and its selected item snapshots."""
    finished_at = datetime.now(timezone.utc)
    run = Run(
        run_type="daily",
        status="success",
        report_date=report_date,
        finished_at=finished_at,
        articles_count=len(paper_summaries),
        news_count=len(news_summaries),
        github_count=len(repo_summaries),
    )
    session.add(run)
    session.flush()

    report = session.query(Report).filter(Report.report_date == report_date).first()
    if report is None:
        report = Report(report_date=report_date, created_at=finished_at)
        session.add(report)

    report.run_id = run.id
    report.title = f"Daily AI Intelligence Report - {report_date.isoformat()}"
    report.content_markdown = report_content
    report.output_path = str(output_path)
    report.dashboard_payload = dashboard_payload
    report.updated_at = finished_at
    session.flush()

    session.query(ReportItem).filter(ReportItem.report_id == report.id).delete()

    for rank, paper in enumerate(paper_summaries, start=1):
        article = upsert_article(session, paper)
        _add_report_item(
            session=session,
            report_id=report.id,
            item_type="article",
            item_id=article.id,
            section="articles",
            rank=rank,
            item=paper,
            published_at=article.published_at,
        )

    for rank, news_item in enumerate(news_summaries, start=1):
        news = upsert_news(session, news_item)
        _add_report_item(
            session=session,
            report_id=report.id,
            item_type="news",
            item_id=news.id,
            section="news",
            rank=rank,
            item=news_item,
            published_at=news.published_at,
        )

    for rank, repo in enumerate(repo_summaries, start=1):
        repository = upsert_github_repository(session, repo)
        _add_report_item(
            session=session,
            report_id=report.id,
            item_type="github_repository",
            item_id=repository.id,
            section="github_projects",
            rank=rank,
            item=repo,
            published_at=repository.repo_updated_at,
        )

    session.flush()
    return report


def upsert_article(session: Session, item: dict[str, Any]) -> Article:
    """Insert or update an article by URL."""
    title = _clean_text(item.get("title")) or "Untitled paper"
    url = _stable_url(item, "article", title)
    article = session.query(Article).filter(Article.url == url).first()
    if article is None:
        article = Article(url=url)
        session.add(article)

    article.title = title
    article.authors = _json_list(item.get("authors"))
    article.abstract = _clean_text(item.get("summary") or item.get("abstract"))
    article.source = _clean_text(item.get("source")) or "arXiv"
    article.source_type = _clean_text(item.get("source_type")) or "paper"
    article.external_id = _external_id_from_url(url)
    article.published_at = _parse_datetime(item.get("published_date") or item.get("published_at"))
    article.collected_at = datetime.now(timezone.utc)
    article.summary_data = _summary_payload(item)
    article.raw_data = _json_payload(item)
    article.total_score = _float_value(item.get("total_score") or item.get("score"))
    article.category = _clean_text(item.get("category"))
    article.tags = _json_list(item.get("tags"))
    session.flush()
    return article


def upsert_news(session: Session, item: dict[str, Any]) -> News:
    """Insert or update a news item by URL."""
    title = _clean_text(item.get("title")) or "Untitled news"
    url = _stable_url(item, "news", title)
    news = session.query(News).filter(News.url == url).first()
    if news is None:
        news = News(url=url)
        session.add(news)

    news.title = title
    news.source = _clean_text(item.get("source"))
    news.source_type = _clean_text(item.get("source_type")) or "rss"
    news.external_id = _clean_text(item.get("guid") or item.get("id"))
    news.content = _clean_text(item.get("summary") or item.get("content"))
    news.published_at = _parse_datetime(item.get("published_date") or item.get("published_at"))
    news.collected_at = datetime.now(timezone.utc)
    news.company = _clean_text(item.get("company"))
    news.category = _clean_text(item.get("category"))
    news.summary_data = _summary_payload(item)
    news.raw_data = _json_payload(item)
    news.total_score = _float_value(item.get("total_score") or item.get("score"))
    news.tags = _json_list(item.get("tags") or item.get("related_technologies"))
    session.flush()
    return news


def upsert_github_repository(session: Session, item: dict[str, Any]) -> GithubRepository:
    """Insert or update a GitHub repository by full name."""
    full_name = _repo_full_name(item)
    repo = session.query(GithubRepository).filter(GithubRepository.full_name == full_name).first()
    if repo is None:
        repo = GithubRepository(full_name=full_name)
        session.add(repo)

    owner, name = _split_repo_name(full_name)
    repo.name = name
    repo.owner = owner
    repo.description = _clean_text(item.get("description") or item.get("one_sentence_summary"))
    repo.url = _clean_text(item.get("url")) or f"https://github.com/{full_name}"
    repo.stars = _int_value(item.get("stars"))
    repo.forks = _int_value(item.get("forks"))
    repo.language = _clean_text(item.get("language"))
    repo.topics = _json_list(item.get("topics"))
    repo.repo_created_at = _parse_datetime(item.get("created_at") or item.get("repo_created_at"))
    repo.repo_updated_at = _parse_datetime(item.get("updated_at") or item.get("repo_updated_at"))
    repo.collected_at = datetime.now(timezone.utc)
    repo.summary_data = _summary_payload(item)
    repo.raw_data = _json_payload(item)
    repo.total_score = _float_value(item.get("total_score") or item.get("score"))
    repo.tags = _json_list(item.get("tags") or item.get("topics"))
    session.flush()
    return repo


def _add_report_item(
    *,
    session: Session,
    report_id: int,
    item_type: str,
    item_id: int,
    section: str,
    rank: int,
    item: dict[str, Any],
    published_at: datetime | None,
) -> None:
    session.add(
        ReportItem(
            report_id=report_id,
            item_type=item_type,
            item_id=item_id,
            section=section,
            rank=rank,
            score_snapshot=_float_value(item.get("total_score") or item.get("score")),
            published_at_snapshot=published_at,
            snapshot_data=_json_payload(item),
        )
    )


def _summary_payload(item: dict[str, Any]) -> dict[str, Any]:
    ignored_keys = {
        "authors",
        "description",
        "forks",
        "language",
        "published_at",
        "published_date",
        "source",
        "source_type",
        "stars",
        "summary",
        "topics",
        "url",
    }
    return {
        key: value
        for key, value in _json_payload(item).items()
        if key not in ignored_keys
    }


def _json_payload(item: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in item.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            payload[key] = value
        elif isinstance(value, (list, tuple)):
            payload[key] = list(value)
        elif isinstance(value, dict):
            payload[key] = value
        else:
            payload[key] = str(value)
    return payload


def _repo_full_name(item: dict[str, Any]) -> str:
    raw_name = _clean_text(item.get("full_name") or item.get("name"))
    if raw_name and "/" in raw_name:
        return raw_name

    url = _clean_text(item.get("url"))
    if url and "github.com/" in url:
        return url.rstrip("/").split("github.com/", 1)[1]

    name = raw_name or "unknown-repository"
    return f"unknown/{_slugify(name)}"


def _split_repo_name(full_name: str) -> tuple[str, str]:
    if "/" not in full_name:
        return "", full_name
    owner, name = full_name.split("/", 1)
    return owner, name


def _stable_url(item: dict[str, Any], item_type: str, title: str) -> str:
    url = _clean_text(item.get("url"))
    if url:
        return url
    return f"generated:{item_type}:{_slugify(title)}"


def _external_id_from_url(url: str) -> str | None:
    if "arxiv.org/abs/" in url:
        return url.rstrip("/").rsplit("/", 1)[-1]
    return None


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)

    text = _clean_text(value)
    if not text:
        return None

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    try:
        parsed_email_date = parsedate_to_datetime(text)
        return (
            parsed_email_date
            if parsed_email_date.tzinfo
            else parsed_email_date.replace(tzinfo=timezone.utc)
        )
    except (TypeError, ValueError):
        return None


def _json_list(value: Any) -> list[Any] | None:
    if value is None or value == "":
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [value]


def _clean_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _int_value(value: Any) -> int:
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0


def _float_value(value: Any) -> float:
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


def _slugify(value: str) -> str:
    slug = "".join(character.lower() if character.isalnum() else "-" for character in value)
    return "-".join(part for part in slug.split("-") if part) or "untitled"
