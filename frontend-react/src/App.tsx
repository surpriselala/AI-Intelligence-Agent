import { useEffect, useMemo, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { getDashboardData, filterItems, sortItems } from "./api/dashboardApi";
import { FilterBar } from "./components/FilterBar";
import { Sidebar } from "./components/Sidebar";
import { Topbar } from "./components/Topbar";
import { ArchivePage } from "./pages/ArchivePage";
import { DashboardPage } from "./pages/DashboardPage";
import type { ContentKind, DashboardPayload } from "./types/dashboard";

export default function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTopic, setActiveTopic] = useState("All");
  const [data, setData] = useState<DashboardPayload | null>(null);
  const [pages, setPages] = useState<Record<ContentKind, number>>({
    articles: 1,
    news: 1,
    projects: 1,
  });

  useEffect(() => {
    void getDashboardData().then(setData);
  }, []);

  const filteredHistory = useMemo(() => {
    if (!data) return { articles: [], news: [], projects: [] };
    return {
      articles: sortItems(filterItems(data.history.articles, searchQuery, activeTopic)),
      news: sortItems(filterItems(data.history.news, searchQuery, activeTopic)),
      projects: sortItems(filterItems(data.history.projects, searchQuery, activeTopic)),
    };
  }, [activeTopic, data, searchQuery]);

  const filteredDashboard = useMemo(() => {
    if (!data) return null;
    return {
      ...data,
      dashboard: {
        articles: filterItems(data.dashboard.articles, searchQuery, activeTopic).slice(0, 4),
        news: filterItems(data.dashboard.news, searchQuery, activeTopic).slice(0, 4),
        projects: filterItems(data.dashboard.projects, searchQuery, activeTopic).slice(0, 4),
      },
    };
  }, [activeTopic, data, searchQuery]);

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

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <Topbar query={searchQuery} onQueryChange={handleSearchChange} />

        {!filteredDashboard ? (
          <div className="empty-state">Loading dashboard...</div>
        ) : (
          <Routes>
            <Route
              element={<DashboardPage data={filteredDashboard} filterBar={filterBar} />}
              path="/"
            />
            <Route
              element={
                <ArchivePage
                  category="articles"
                  filterBar={filterBar}
                  items={filteredHistory.articles}
                  onPageChange={(page) => setPage("articles", page)}
                  page={pages.articles}
                />
              }
              path="/articles"
            />
            <Route
              element={
                <ArchivePage
                  category="news"
                  filterBar={filterBar}
                  items={filteredHistory.news}
                  onPageChange={(page) => setPage("news", page)}
                  page={pages.news}
                />
              }
              path="/news"
            />
            <Route
              element={
                <ArchivePage
                  category="projects"
                  filterBar={filterBar}
                  items={filteredHistory.projects}
                  onPageChange={(page) => setPage("projects", page)}
                  page={pages.projects}
                />
              }
              path="/github-projects"
            />
            <Route element={<Navigate replace to="/" />} path="*" />
          </Routes>
        )}
      </main>
    </div>
  );
}
