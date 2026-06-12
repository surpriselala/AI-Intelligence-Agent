"""Build static dashboard data from generated Markdown reports."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPORT_FILE_PATTERN = re.compile(r"daily_ai_report_(\d{4}-\d{2}-\d{2})\.md$")
SECTION_PATTERNS = {
    "articles": re.compile(r"^### Paper \d+:\s*(.+)$"),
    "projects": re.compile(r"^### Project \d+:\s*(.+)$"),
    "news": re.compile(r"^### News \d+:\s*(.+)$"),
}
SECTION_HEADINGS = {
    "## 1. Research Papers": "articles",
    "## 2. GitHub Projects": "projects",
    "## 3. Industry News": "news",
}


def build_dashboard_data(
    reports_dir: str | Path,
    output_path: str | Path,
) -> Path:
    """Parse Markdown reports and write a JavaScript dashboard data file."""
    reports = parse_reports(reports_dir)
    payload = build_dashboard_payload(reports)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    path.write_text(f"window.AI_DASHBOARD_DATA = {serialized};\n", encoding="utf-8")
    return path


def parse_reports(reports_dir: str | Path) -> list[dict[str, Any]]:
    """Parse all dated report Markdown files in a directory."""
    report_paths = sorted(Path(reports_dir).glob("daily_ai_report_*.md"))
    reports = []
    for report_path in report_paths:
        match = REPORT_FILE_PATTERN.match(report_path.name)
        if not match:
            continue
        try:
            reports.append(parse_report(report_path, match.group(1)))
        except OSError as error:
            print(f"Failed to parse report {report_path}: {error}")
    return sorted(reports, key=lambda report: report["date"], reverse=True)


def parse_report(report_path: str | Path, report_date: str | None = None) -> dict[str, Any]:
    """Parse the English section of one Markdown report."""
    path = Path(report_path)
    date_value = report_date or _date_from_filename(path)
    content = path.read_text(encoding="utf-8")
    english_content = content.split("\n---\n", 1)[0]
    items = {"articles": [], "projects": [], "news": []}

    current_category = None
    current_item = None
    order_by_category = {"articles": 0, "projects": 0, "news": 0}

    for line in english_content.splitlines():
        stripped = line.strip()
        if stripped in SECTION_HEADINGS:
            current_category = SECTION_HEADINGS[stripped]
            current_item = None
            continue

        if current_category is None:
            continue

        item_title = _match_item_title(current_category, stripped)
        if item_title is not None:
            order_by_category[current_category] += 1
            current_item = {
                "title": item_title,
                "date": date_value,
                "score": 0,
                "order": order_by_category[current_category],
                "category": current_category,
            }
            items[current_category].append(current_item)
            continue

        if current_item is not None and stripped.startswith("- "):
            key, value = _parse_field(stripped)
            if key:
                current_item[key] = value

    return {
        "date": date_value,
        "path": str(path),
        "articles": items["articles"],
        "projects": items["projects"],
        "news": items["news"],
    }


def build_dashboard_payload(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Build frontend-friendly aggregate data from parsed reports."""
    all_items = {
        "articles": _collect_items(reports, "articles"),
        "projects": _collect_items(reports, "projects"),
        "news": _collect_items(reports, "news"),
    }
    latest_report = reports[0] if reports else None
    latest = {
        "articles": latest_report["articles"] if latest_report else [],
        "projects": latest_report["projects"] if latest_report else [],
        "news": latest_report["news"] if latest_report else [],
    }
    dashboard = {
        category: sort_items(items)[:4]
        for category, items in all_items.items()
    }
    totals = {
        "articles": len(all_items["articles"]),
        "projects": len(all_items["projects"]),
        "news": len(all_items["news"]),
        "stars": sum(_parse_int(item.get("stars", "0")) for item in all_items["projects"]),
        "reports": len(reports),
    }
    return {
        "generated_at": latest_report["date"] if latest_report else "",
        "totals": totals,
        "dashboard": dashboard,
        "latest": latest,
        "history": all_items,
        "reports": reports,
    }


def sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by score first, then date, then report order."""
    return sorted(
        items,
        key=lambda item: (
            _parse_int(item.get("score", 0)),
            item.get("date", ""),
            -_parse_int(item.get("order", 0)),
        ),
        reverse=True,
    )


def _collect_items(reports: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    items = []
    for report in reports:
        items.extend(report.get(category, []))
    return sort_items(items)


def _date_from_filename(path: Path) -> str:
    match = REPORT_FILE_PATTERN.match(path.name)
    return match.group(1) if match else ""


def _match_item_title(category: str, line: str) -> str | None:
    match = SECTION_PATTERNS[category].match(line)
    return match.group(1).strip() if match else None


def _parse_field(line: str) -> tuple[str | None, str]:
    text = line[2:]
    if ":" not in text:
        return None, ""
    raw_key, value = text.split(":", 1)
    key = raw_key.strip().lower().replace(" ", "_")
    return key, value.strip()


def _parse_int(value: Any) -> int:
    try:
        return int(str(value).replace(",", "").strip())
    except ValueError:
        return 0
