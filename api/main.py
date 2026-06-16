"""FastAPI entry point for the AI Intelligence Agent API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import articles, dashboard, github, news, reports
from api.schemas import HealthResponse


app = FastAPI(
    title="AI Intelligence Agent API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"http://(127\.0\.0\.1|localhost):517[0-9]",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return API health status."""
    return HealthResponse(status="ok")


app.include_router(dashboard.router)
app.include_router(articles.router)
app.include_router(news.router)
app.include_router(github.router)
app.include_router(reports.router)
