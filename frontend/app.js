(function () {
  const data = window.AI_DASHBOARD_DATA || emptyData();
  const PAGE_SIZE = 10;
  const state = {
    view: "dashboard",
    query: "",
    pages: {
      articles: 1,
      news: 1,
      projects: 1,
    },
  };

  const labels = {
    articles: "Articles",
    news: "News",
    projects: "GitHub Projects",
  };

  const statDefinitions = [
    ["articles", "Articles", "A"],
    ["news", "News", "N"],
    ["projects", "GitHub Projects", "G"],
    ["reports", "Trending Topics", "T"],
  ];

  document.addEventListener("DOMContentLoaded", () => {
    bindNavigation();
    bindSearch();
    bindFilters();
    render();
  });

  function bindNavigation() {
    document.querySelectorAll("[data-view]").forEach((button) => {
      button.addEventListener("click", () => {
        if (!button.dataset.view) return;
        state.view = button.dataset.view;
        document.querySelectorAll(".nav-item").forEach((item) => {
          item.classList.toggle("active", item.dataset.view === state.view);
        });
        document.querySelectorAll(".view").forEach((view) => {
          view.classList.toggle("active", view.id === `${state.view}View`);
        });
        render();
      });
    });
  }

  function bindSearch() {
    const input = document.getElementById("searchInput");
    input.addEventListener("input", () => {
      state.query = input.value.trim().toLowerCase();
      resetPages();
      render();
    });
  }

  function bindFilters() {
    document.querySelectorAll("[data-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        const input = document.getElementById("searchInput");
        input.value = button.dataset.filter;
        state.query = button.dataset.filter.toLowerCase();
        resetPages();
        document.querySelectorAll(".filter-pill").forEach((pill) => {
          pill.classList.toggle("active", pill === button);
        });
        render();
      });
    });
  }

  function render() {
    renderStats();
    renderDashboard();
    renderHistoryPage("articles", "articlesPage");
    renderHistoryPage("news", "newsPage");
    renderHistoryPage("projects", "projectsPage");
  }

  function renderStats() {
    const grid = document.getElementById("statsGrid");
    grid.innerHTML = statDefinitions
      .map(([key, label, icon]) => {
        const value = key === "stars" ? formatNumber(data.totals[key] || 0) : data.totals[key] || 0;
        return `
          <article class="stat-card">
            <div class="stat-icon">${icon}</div>
            <div class="stat-label">${label}</div>
            <div class="stat-value">${value}</div>
            <div class="stat-note">Sorted by latest report date</div>
          </article>
        `;
      })
      .join("");
  }

  function renderDashboard() {
    setList("dashboardArticles", filterItems(data.dashboard.articles || []).map((item) => card(item, "articles")).join(""));
    setList("dashboardNews", filterItems(data.dashboard.news || []).map((item) => card(item, "news")).join(""));
    setList("dashboardProjects", filterItems(data.dashboard.projects || []).map((item) => card(item, "projects")).join(""));
  }

  function renderHistoryPage(category, elementId) {
    const container = document.getElementById(elementId);
    const historyItems = filterItems(data.history[category] || []);
    const totalPages = Math.max(1, Math.ceil(historyItems.length / PAGE_SIZE));
    const currentPage = Math.min(state.pages[category], totalPages);
    state.pages[category] = currentPage;
    const start = (currentPage - 1) * PAGE_SIZE;
    const pageItems = historyItems.slice(start, start + PAGE_SIZE);
    container.innerHTML = `
      ${historySection(`${labels[category]} Archive`, pageItems, category, historyItems.length)}
      ${pagination(category, currentPage, totalPages, historyItems.length)}
    `;
    container.querySelectorAll("[data-page-action]").forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.dataset.pageAction;
        if (action === "prev") state.pages[category] = Math.max(1, state.pages[category] - 1);
        if (action === "next") state.pages[category] = Math.min(totalPages, state.pages[category] + 1);
        renderHistoryPage(category, elementId);
      });
    });
  }

  function historySection(title, items, category, totalCount) {
    return `
      <section class="history-section">
        <div class="history-header">
          <h3>${title}</h3>
          <span class="card-meta">${totalCount} total · 10 per page</span>
        </div>
        <div class="history-list">
          ${items.length ? items.map((item) => card(item, category)).join("") : `<div class="empty-state">No items found.</div>`}
        </div>
      </section>
    `;
  }

  function pagination(category, currentPage, totalPages, totalItems) {
    if (totalItems <= PAGE_SIZE) return "";
    return `
      <div class="pagination">
        <button type="button" data-page-action="prev" ${currentPage === 1 ? "disabled" : ""}>Previous</button>
        <span>Page ${currentPage} of ${totalPages}</span>
        <button type="button" data-page-action="next" ${currentPage === totalPages ? "disabled" : ""}>Next</button>
      </div>
    `;
  }

  function card(item, category) {
    const href = item.link || item.url || "#";
    const meta = metaLine(item, category);
    const summary = item.summary || item.one_sentence_summary || item.what_happened || item.main_features || "";
    const tags = tagsFor(item, category);
    return `
      <article class="content-card">
        <div class="thumb ${category === "news" ? "news" : category === "projects" ? "project" : ""}">${initials(item.title)}</div>
        <div>
          <h3 class="card-title"><a href="${escapeAttribute(href)}" target="_blank" rel="noreferrer">${escapeHtml(item.title)}</a></h3>
          <div class="card-meta">${meta}</div>
          <p class="summary">${escapeHtml(summary)}</p>
          ${tags.length ? `<div class="tag-list">${tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div>` : ""}
        </div>
      </article>
    `;
  }

  function metaLine(item, category) {
    const today = data.generated_at && item.date === data.generated_at ? "Today" : item.date;
    const parts = [today];
    if (category === "news" && item.source) parts.push(item.source);
    if (category === "projects" && item.stars) parts.push(`${formatNumber(item.stars)} stars`);
    if (item.score) parts.push(`Score ${item.score}`);
    return parts.filter(Boolean).map(escapeHtml).join(" · ");
  }

  function tagsFor(item, category) {
    if (category === "projects") {
      return [item.language, "LLM", "AI"].filter(Boolean).slice(0, 3);
    }
    if (category === "news") {
      return [item.source, "AI News"].filter(Boolean).slice(0, 2);
    }
    return ["Research", "AI"].slice(0, 2);
  }

  function filterItems(items) {
    if (!state.query) return items;
    return items.filter((item) => {
      const haystack = [
        item.title,
        item.summary,
        item.one_sentence_summary,
        item.what_happened,
        item.main_features,
        item.source,
        item.date,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return haystack.includes(state.query);
    });
  }

  function setList(id, html) {
    document.getElementById(id).innerHTML = html || `<div class="empty-state">No items found.</div>`;
  }

  function resetPages() {
    state.pages = {
      articles: 1,
      news: 1,
      projects: 1,
    };
  }

  function initials(title) {
    return String(title || "AI")
      .split(/[\s/:-]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0])
      .join("")
      .toUpperCase();
  }

  function formatNumber(value) {
    const numeric = Number(String(value).replace(/,/g, ""));
    if (!Number.isFinite(numeric)) return value;
    if (numeric >= 1000) return `${(numeric / 1000).toFixed(numeric >= 10000 ? 1 : 0)}K`;
    return String(numeric);
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function escapeAttribute(value) {
    return escapeHtml(value).replace(/`/g, "&#096;");
  }

  function emptyData() {
    return {
      totals: { articles: 0, news: 0, projects: 0, stars: 0, reports: 0 },
      dashboard: { articles: [], news: [], projects: [] },
      latest: { articles: [], news: [], projects: [] },
      history: { articles: [], news: [], projects: [] },
      reports: [],
    };
  }
})();
