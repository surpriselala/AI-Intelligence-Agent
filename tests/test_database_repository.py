import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Article, GithubRepository, News, Report, ReportItem, Run, Base
from database.repository import save_daily_report


class DatabaseRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = self.session_factory()

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_save_daily_report_persists_report_and_items(self) -> None:
        save_daily_report(
            session=self.session,
            report_date=date(2026, 6, 14),
            report_content="# Report\n",
            output_path="outputs/daily_ai_report_2026-06-14.md",
            paper_summaries=[
                {
                    "title": "Example Paper",
                    "summary": "Paper abstract",
                    "one_sentence_summary": "Paper summary",
                    "authors": ["Author A"],
                    "published_date": "2026-06-14",
                    "url": "https://arxiv.org/abs/2606.00001",
                }
            ],
            repo_summaries=[
                {
                    "name": "owner/repo",
                    "description": "Repo description",
                    "stars": 123,
                    "language": "Python",
                    "url": "https://github.com/owner/repo",
                }
            ],
            news_summaries=[
                {
                    "title": "Example News",
                    "source": "Example Source",
                    "summary": "News summary",
                    "published_date": "2026-06-14",
                    "url": "https://example.com/news",
                }
            ],
        )
        self.session.commit()

        self.assertEqual(self.session.query(Run).count(), 1)
        self.assertEqual(self.session.query(Report).count(), 1)
        self.assertEqual(self.session.query(Article).count(), 1)
        self.assertEqual(self.session.query(GithubRepository).count(), 1)
        self.assertEqual(self.session.query(News).count(), 1)
        self.assertEqual(self.session.query(ReportItem).count(), 3)

        article = self.session.query(Article).one()
        self.assertEqual(article.summary_data["one_sentence_summary"], "Paper summary")

        repo = self.session.query(GithubRepository).one()
        self.assertEqual(repo.full_name, "owner/repo")
        self.assertEqual(repo.stars, 123)

    def test_save_daily_report_rerun_updates_report_without_duplicate_items(self) -> None:
        report_date = date(2026, 6, 14)
        paper = {
            "title": "Example Paper",
            "summary": "Paper abstract",
            "one_sentence_summary": "First summary",
            "url": "https://arxiv.org/abs/2606.00001",
        }

        save_daily_report(
            session=self.session,
            report_date=report_date,
            report_content="# First\n",
            output_path="outputs/daily_ai_report_2026-06-14.md",
            paper_summaries=[paper],
            repo_summaries=[],
            news_summaries=[],
        )
        self.session.commit()

        updated_paper = dict(paper)
        updated_paper["one_sentence_summary"] = "Updated summary"
        save_daily_report(
            session=self.session,
            report_date=report_date,
            report_content="# Second\n",
            output_path="outputs/daily_ai_report_2026-06-14.md",
            paper_summaries=[updated_paper],
            repo_summaries=[],
            news_summaries=[],
        )
        self.session.commit()

        self.assertEqual(self.session.query(Run).count(), 2)
        self.assertEqual(self.session.query(Report).count(), 1)
        self.assertEqual(self.session.query(Article).count(), 1)
        self.assertEqual(self.session.query(ReportItem).count(), 1)

        report = self.session.query(Report).one()
        self.assertEqual(report.content_markdown, "# Second\n")

        article = self.session.query(Article).one()
        self.assertEqual(article.summary_data["one_sentence_summary"], "Updated summary")


if __name__ == "__main__":
    unittest.main()
