"""Pydantic response schemas for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class DashboardItem(BaseModel):
    id: str
    type: str
    title: str
    summary: str
    url: str
    date: str
    source: str | None = None
    stars: int | None = None
    language: str | None = None
    tags: list[str] = Field(default_factory=list)
    score: float = 0
    order: int = 0


class DashboardTotals(BaseModel):
    articles: int
    news: int
    projects: int
    reports: int
    stars: int


class DashboardGroups(BaseModel):
    articles: list[DashboardItem] = Field(default_factory=list)
    news: list[DashboardItem] = Field(default_factory=list)
    projects: list[DashboardItem] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    generated_at: str
    totals: DashboardTotals
    dashboard: DashboardGroups


class PaginatedDashboardItems(BaseModel):
    items: list[DashboardItem]
    page: int
    page_size: int
    total: int
    total_pages: int


class ReportListItem(BaseModel):
    report_date: str
    title: str | None = None
    output_path: str | None = None


class ReportListResponse(BaseModel):
    items: list[ReportListItem]


class ReportDetailResponse(BaseModel):
    report_date: str
    title: str | None = None
    content_markdown: str
    output_path: str | None = None
