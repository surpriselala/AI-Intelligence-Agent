import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { getArchiveItems, getDashboardData } from "./api/dashboardApi";
import { FilterBar } from "./components/FilterBar";
import { Sidebar } from "./components/Sidebar";
import { Topbar } from "./components/Topbar";
import { ArchivePage } from "./pages/ArchivePage";
import { DashboardPage } from "./pages/DashboardPage";
import type {
  ContentKind,
  DashboardItem,
  DashboardPayload,
  PaginatedResult,
} from "./types/dashboard";

const PAGE_SIZE = 10;

const emptyArchiveData: Record<ContentKind, PaginatedResult<DashboardItem> | null> = {
  articles: null,
  news: null,
  projects: null,
};

const emptyLoadingState: Record<ContentKind, boolean> = {
  articles: false,
  news: false,
  projects: false,
};

const emptyErrorState: Record<ContentKind, string> = {
  articles: "",
  news: "",
  projects: "",
};

export default function App() {
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTopic, setActiveTopic] = useState("All");
  const [dashboardData, setDashboardData] = useState<DashboardPayload | null>(null);
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState("");
  const [archiveData, setArchiveData] = useState(emptyArchiveData);
  const [archiveLoading, setArchiveLoading] = useState(emptyLoadingState);
  const [archiveErrors, setArchiveErrors] = useState(emptyErrorState);
  const [pages, setPages] = useState<Record<ContentKind, number>>({
    articles: 1,
    news: 1,
    projects: 1,
  });

  const activeArchiveCategory = useMemo<ContentKind | null>(() => {
    if (location.pathname === "/articles") return "articles";
    if (location.pathname === "/news") return "news";
    if (location.pathname === "/github-projects") return "projects";
    return null;
  }, [location.pathname]);

  useEffect(() => {
    let ignore = false;
    setDashboardLoading(true);
    setDashboardError("");

    void getDashboardData({ query: searchQuery, topic: activeTopic })
      .then((payload) => {
        if (!ignore) setDashboardData(payload);
      })
      .catch((error: unknown) => {
        if (!ignore) setDashboardError(toErrorMessage(error));
      })
      .finally(() => {
        if (!ignore) setDashboardLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [activeTopic, searchQuery]);

  const loadArchive = useCallback(
    (category: ContentKind) => {
      setArchiveLoading((current) => ({ ...current, [category]: true }));
      setArchiveErrors((current) => ({ ...current, [category]: "" }));

      void getArchiveItems(category, {
        page: pages[category],
        pageSize: PAGE_SIZE,
        query: searchQuery,
        topic: activeTopic,
      })
        .then((payload) => {
          setArchiveData((current) => ({ ...current, [category]: payload }));
        })
        .catch((error: unknown) => {
          setArchiveErrors((current) => ({ ...current, [category]: toErrorMessage(error) }));
        })
        .finally(() => {
          setArchiveLoading((current) => ({ ...current, [category]: false }));
        });
    },
    [activeTopic, pages, searchQuery],
  );

  useEffect(() => {
    if (activeArchiveCategory) {
      loadArchive(activeArchiveCategory);
    }
  }, [activeArchiveCategory, loadArchive]);

  function handleSearchChange(nextQuery: string) {
    setSearchQuery(nextQuery);
    resetPages();
  }

  function handleTopicChange(topic: string) {
    setActiveTopic(topic);
    resetPages();
  }

  function setPage(category: ContentKind, page: number) {
    setPages((current) => ({ ...current, [category]: page }));
  }

  function resetPages() {
    setPages({ articles: 1, news: 1, projects: 1 });
  }

  const filterBar = (
    <FilterBar activeTopic={activeTopic} onTopicChange={handleTopicChange} />
  );

  const dashboardContent = dashboardError ? (
    <ApiState
      message={dashboardError}
      title="Dashboard data could not be loaded."
      variant="error"
    />
  ) : dashboardLoading && !dashboardData ? (
    <ApiState message="Loading the latest dashboard data..." title="Loading" />
  ) : dashboardData ? (
    <DashboardPage data={dashboardData} filterBar={filterBar} />
  ) : (
    <ApiState message="No dashboard data returned from the API." title="No data" />
  );

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <Topbar query={searchQuery} onQueryChange={handleSearchChange} />

        <Routes>
          <Route element={dashboardContent} path="/" />
          <Route
            element={
              <ArchivePage
                category="articles"
                errorMessage={archiveErrors.articles}
                filterBar={filterBar}
                isLoading={archiveLoading.articles}
                onPageChange={(page) => setPage("articles", page)}
                page={pages.articles}
                result={archiveData.articles}
              />
            }
            path="/articles"
          />
          <Route
            element={
              <ArchivePage
                category="news"
                errorMessage={archiveErrors.news}
                filterBar={filterBar}
                isLoading={archiveLoading.news}
                onPageChange={(page) => setPage("news", page)}
                page={pages.news}
                result={archiveData.news}
              />
            }
            path="/news"
          />
          <Route
            element={
              <ArchivePage
                category="projects"
                errorMessage={archiveErrors.projects}
                filterBar={filterBar}
                isLoading={archiveLoading.projects}
                onPageChange={(page) => setPage("projects", page)}
                page={pages.projects}
                result={archiveData.projects}
              />
            }
            path="/github-projects"
          />
          <Route element={<Navigate replace to="/" />} path="*" />
        </Routes>
      </main>
    </div>
  );
}

function ApiState({
  message,
  title,
  variant = "loading",
}: {
  message: string;
  title: string;
  variant?: "loading" | "error";
}) {
  return (
    <section className={`api-state ${variant === "error" ? "api-state-error" : ""}`}>
      <h2>{title}</h2>
      <p>{message}</p>
      {variant === "error" ? (
        <code>.venv/bin/python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000</code>
      ) : null}
    </section>
  );
}

function toErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  return "Unknown API error";
}
