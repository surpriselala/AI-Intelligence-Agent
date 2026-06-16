import unittest
import warnings
from datetime import date
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.exceptions import StarletteDeprecationWarning

warnings.filterwarnings("ignore", category=StarletteDeprecationWarning)
from starlette.testclient import TestClient

from api.deps import get_db
from api.main import app
from database.models import Base
from database.repository import save_daily_report


class ApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = self.session_factory()
        save_daily_report(
            session=self.session,
            report_date=date(2026, 6, 14),
            report_content="# Report\n",
            output_path="outputs/daily_ai_report_2026-06-14.md",
            paper_summaries=[
                {
                    "title": "Agent Paper",
                    "summary": "Paper abstract",
                    "one_sentence_summary": "Paper summary",
                    "url": "https://arxiv.org/abs/2606.00001",
                    "tags": ["Agent", "LLM"],
                }
            ],
            repo_summaries=[
                {
                    "name": "owner/repo",
                    "description": "Repo description",
                    "one_sentence_summary": "Repo summary",
                    "stars": 123,
                    "language": "Python",
                    "url": "https://github.com/owner/repo",
                    "tags": ["LLM", "Agent"],
                }
            ],
            news_summaries=[
                {
                    "title": "AI News",
                    "source": "Example Source",
                    "summary": "News summary",
                    "one_sentence_summary": "News summary",
                    "url": "https://example.com/news",
                    "tags": ["AI News"],
                }
            ],
        )
        self.session.commit()

        def override_get_db() -> Generator[Session, None, None]:
            db = self.session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_health_returns_ok(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_dashboard_returns_latest_report_groups(self) -> None:
        response = self.client.get("/api/dashboard")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["generated_at"], "2026-06-14")
        self.assertEqual(payload["totals"]["articles"], 1)
        self.assertEqual(payload["totals"]["news"], 1)
        self.assertEqual(payload["totals"]["projects"], 1)
        self.assertEqual(payload["totals"]["stars"], 123)
        self.assertEqual(payload["dashboard"]["articles"][0]["title"], "Agent Paper")

    def test_list_routes_are_paginated_and_filterable(self) -> None:
        articles = self.client.get("/api/articles?page=1&page_size=10&topic=Agent")
        news = self.client.get("/api/news?page=1&page_size=10")
        projects = self.client.get("/api/github-projects?page=1&page_size=10&query=repo")

        self.assertEqual(articles.status_code, 200)
        self.assertEqual(articles.json()["total"], 1)
        self.assertEqual(news.status_code, 200)
        self.assertEqual(news.json()["items"][0]["source"], "Example Source")
        self.assertEqual(projects.status_code, 200)
        self.assertEqual(projects.json()["items"][0]["stars"], 123)

    def test_reports_routes_return_list_and_detail(self) -> None:
        report_list = self.client.get("/api/reports")
        detail = self.client.get("/api/reports/2026-06-14")
        missing = self.client.get("/api/reports/2026-06-15")

        self.assertEqual(report_list.status_code, 200)
        self.assertEqual(report_list.json()["items"][0]["report_date"], "2026-06-14")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["content_markdown"], "# Report\n")
        self.assertEqual(missing.status_code, 404)


if __name__ == "__main__":
    unittest.main()
