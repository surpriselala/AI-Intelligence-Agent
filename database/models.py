"""SQLAlchemy models for Phase 1 persistence."""

from __future__ import annotations

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.types import JSON


Base = declarative_base()


class Run(Base):
    """One execution of the daily intelligence workflow."""

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    run_type = Column(String(50), nullable=False, default="daily")
    status = Column(String(50), nullable=False, default="running")
    report_date = Column(Date, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    articles_count = Column(Integer, nullable=False, default=0)
    news_count = Column(Integer, nullable=False, default=0)
    github_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    run_metadata = Column("metadata", JSON, nullable=True)


class Report(Base):
    """A generated Markdown daily report."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=True)
    report_date = Column(Date, nullable=False, unique=True, index=True)
    title = Column(Text, nullable=True)
    content_markdown = Column(Text, nullable=False)
    output_path = Column(Text, nullable=True)
    dashboard_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Article(Base):
    """A selected research paper or technical article."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    authors = Column(JSON, nullable=True)
    abstract = Column(Text, nullable=True)
    source = Column(String(100), nullable=True, default="arXiv")
    source_type = Column(String(50), nullable=True, default="paper")
    external_id = Column(String(255), nullable=True)
    url = Column(Text, nullable=False, unique=True, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    collected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    summary_data = Column(JSON, nullable=True)
    raw_data = Column(JSON, nullable=True)
    total_score = Column(Float, nullable=False, default=0)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)


class News(Base):
    """A selected AI industry news item."""

    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    source_type = Column(String(50), nullable=True, default="rss")
    external_id = Column(String(255), nullable=True)
    url = Column(Text, nullable=False, unique=True, index=True)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    collected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    company = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    summary_data = Column(JSON, nullable=True)
    raw_data = Column(JSON, nullable=True)
    total_score = Column(Float, nullable=False, default=0)
    tags = Column(JSON, nullable=True)


class GithubRepository(Base):
    """A selected GitHub repository."""

    __tablename__ = "github_repositories"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True)
    owner = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=False, unique=True, index=True)
    stars = Column(Integer, nullable=False, default=0)
    forks = Column(Integer, nullable=False, default=0)
    language = Column(String(100), nullable=True)
    topics = Column(JSON, nullable=True)
    repo_created_at = Column(DateTime(timezone=True), nullable=True)
    repo_updated_at = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    summary_data = Column(JSON, nullable=True)
    raw_data = Column(JSON, nullable=True)
    total_score = Column(Float, nullable=False, default=0)
    tags = Column(JSON, nullable=True)


class ReportItem(Base):
    """A selected item snapshot inside one report."""

    __tablename__ = "report_items"
    __table_args__ = (
        UniqueConstraint("report_id", "item_type", "item_id", name="uq_report_item"),
    )

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    item_type = Column(String(50), nullable=False)
    item_id = Column(Integer, nullable=False)
    section = Column(String(50), nullable=False)
    rank = Column(Integer, nullable=False)
    score_snapshot = Column(Float, nullable=False, default=0)
    published_at_snapshot = Column(DateTime(timezone=True), nullable=True)
    snapshot_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
