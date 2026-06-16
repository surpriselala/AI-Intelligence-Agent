"""Dashboard API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from api.routes.items import filter_dashboard_items, get_latest_dashboard_items, get_latest_report
from api.schemas import DashboardGroups, DashboardResponse, DashboardTotals
from database.models import GithubRepository, Report, ReportItem


router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def read_dashboard(
    query: str = "",
    topic: str = Query("", description="Topic keyword used by the dashboard filter pills."),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    """Return dashboard data from the latest generated report."""
    latest_report = get_latest_report(db)
    if latest_report is None:
        return DashboardResponse(
            generated_at="",
            totals=DashboardTotals(articles=0, news=0, projects=0, reports=0, stars=0),
            dashboard=DashboardGroups(),
        )

    groups = get_latest_dashboard_items(db, latest_report)
    filtered_groups = {
        category: filter_dashboard_items(items, query=query, topic=topic)
        for category, items in groups.items()
    }
    project_ids = [
        item.item_id
        for item in db.query(ReportItem)
        .filter(
            ReportItem.report_id == latest_report.id,
            ReportItem.item_type == "github_repository",
        )
        .all()
    ]
    total_stars = 0
    if project_ids:
        repos = db.query(GithubRepository).filter(GithubRepository.id.in_(project_ids)).all()
        total_stars = sum(repo.stars or 0 for repo in repos)

    article_count = (
        db.query(ReportItem)
        .filter(ReportItem.report_id == latest_report.id, ReportItem.item_type == "article")
        .count()
    )
    news_count = (
        db.query(ReportItem)
        .filter(ReportItem.report_id == latest_report.id, ReportItem.item_type == "news")
        .count()
    )
    project_count = (
        db.query(ReportItem)
        .filter(
            ReportItem.report_id == latest_report.id,
            ReportItem.item_type == "github_repository",
        )
        .count()
    )

    return DashboardResponse(
        generated_at=latest_report.report_date.isoformat(),
        totals=DashboardTotals(
            articles=article_count,
            news=news_count,
            projects=project_count,
            reports=db.query(Report).count(),
            stars=total_stars,
        ),
        dashboard=DashboardGroups(
            articles=filtered_groups["articles"],
            news=filtered_groups["news"],
            projects=filtered_groups["projects"],
        ),
    )
