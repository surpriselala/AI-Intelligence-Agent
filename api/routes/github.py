"""GitHub project list API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from api.routes.items import (
    filter_dashboard_items,
    get_report_items_for_category,
    paginate_dashboard_items,
)
from api.schemas import PaginatedDashboardItems


router = APIRouter(prefix="/api", tags=["github"])


@router.get("/github-projects", response_model=PaginatedDashboardItems)
def read_github_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    query: str = "",
    topic: str = "",
    db: Session = Depends(get_db),
) -> PaginatedDashboardItems:
    """Return paginated report-backed GitHub repositories."""
    items = get_report_items_for_category(db, "projects")
    filtered = filter_dashboard_items(items, query=query, topic=topic)
    return paginate_dashboard_items(filtered, page=page, page_size=page_size)
