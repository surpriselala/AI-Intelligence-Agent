"""Report API routes."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import ReportDetailResponse, ReportListItem, ReportListResponse
from database.models import Report


router = APIRouter(prefix="/api", tags=["reports"])


@router.get("/reports", response_model=ReportListResponse)
def read_reports(db: Session = Depends(get_db)) -> ReportListResponse:
    """Return generated report metadata ordered by date."""
    reports = db.query(Report).order_by(Report.report_date.desc()).all()
    return ReportListResponse(
        items=[
            ReportListItem(
                report_date=report.report_date.isoformat(),
                title=report.title,
                output_path=report.output_path,
            )
            for report in reports
        ]
    )


@router.get("/reports/{report_date}", response_model=ReportDetailResponse)
def read_report_detail(
    report_date: date,
    db: Session = Depends(get_db),
) -> ReportDetailResponse:
    """Return one complete Markdown report by date."""
    report = db.query(Report).filter(Report.report_date == report_date).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportDetailResponse(
        report_date=report.report_date.isoformat(),
        title=report.title,
        content_markdown=report.content_markdown,
        output_path=report.output_path,
    )
