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
NEWS_MAX_RESULTS = 10
SELECTION_TOP_K = 3
OPENAI_TRANSLATION_MODEL = "gpt-4o-mini"
OPENAI_PAPER_SELECTION_MODEL = "gpt-4o-mini"
OPENAI_PAPER_SUMMARY_MODEL = "gpt-4o-mini"
OPENAI_GITHUB_SELECTION_MODEL = "gpt-4o-mini"
OPENAI_GITHUB_SUMMARY_MODEL = "gpt-4o-mini"
OPENAI_NEWS_SELECTION_MODEL = "gpt-4o-mini"
OPENAI_NEWS_SUMMARY_MODEL = "gpt-4o-mini"

NEWS_FEEDS = [
    {
        "name": "OpenAI News",
        "url": "https://openai.com/news/rss.xml",
        "source_type": "rss",
    },
    {
        "name": "Anthropic News",
        "url": "https://www.anthropic.com/news/rss.xml",
        "source_type": "rss",
    },
    {
        "name": "Google DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "source_type": "rss",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "source_type": "rss",
    },
    {
        "name": "Microsoft AI Blog",
        "url": "https://blogs.microsoft.com/ai/feed/",
        "source_type": "rss",
    },
    {
        "name": "NVIDIA Blog",
        "url": "https://blogs.nvidia.com/feed/",
        "source_type": "rss",
    },
]

REPORT_OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_FILENAME_PREFIX = "daily_ai_report"
