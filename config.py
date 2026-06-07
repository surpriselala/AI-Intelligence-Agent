"""Project-wide configuration for the AI intelligence workflow."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

AI_KEYWORDS = [
    "large language model",
    "AI agent",
    "RAG",
    "multimodal AI",
    "AI coding",
    "reasoning model",
]

ARXIV_MAX_RESULTS = 10
GITHUB_MAX_RESULTS = 10
SELECTION_TOP_K = 3

REPORT_OUTPUT_PATH = BASE_DIR / "outputs" / "daily_ai_report.md"
