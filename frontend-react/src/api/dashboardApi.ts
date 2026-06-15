import { mockDashboardData } from "./mockData";
import type { ContentKind, DashboardItem, DashboardPayload, PaginatedResult } from "../types/dashboard";

const PAGE_SIZE = 10;

export async function getDashboardData(): Promise<DashboardPayload> {
  return mockDashboardData;
}

export function filterItems(
  items: DashboardItem[],
  query: string,
  activeTopic = "All",
): DashboardItem[] {
  const normalizedQuery = query.trim().toLowerCase();
  const normalizedTopic = activeTopic === "All" ? "" : activeTopic.trim().toLowerCase();

  return items.filter((item) => {
    const haystack = [
      item.title,
      item.summary,
      item.date,
      item.source,
      item.language,
      ...(item.tags || []),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    const matchesSearch = !normalizedQuery || haystack.includes(normalizedQuery);
    const matchesTopic = !normalizedTopic || haystack.includes(normalizedTopic);
    return matchesSearch && matchesTopic;
  });
}

export function paginateItems(
  items: DashboardItem[],
  page: number,
  pageSize = PAGE_SIZE,
): PaginatedResult<DashboardItem> {
  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));
  const currentPage = Math.min(Math.max(page, 1), totalPages);
  const start = (currentPage - 1) * pageSize;

  return {
    items: items.slice(start, start + pageSize),
    page: currentPage,
    pageSize,
    total: items.length,
    totalPages,
  };
}

export function sortItems(items: DashboardItem[]): DashboardItem[] {
  return [...items].sort((a, b) => {
    const scoreDiff = (b.score || 0) - (a.score || 0);
    if (scoreDiff !== 0) return scoreDiff;
    const dateDiff = b.date.localeCompare(a.date);
    if (dateDiff !== 0) return dateDiff;
    return (a.order || 0) - (b.order || 0);
  });
}

export function categoryTitle(category: ContentKind): string {
  const labels: Record<ContentKind, string> = {
    articles: "Articles",
    news: "News",
    projects: "GitHub Projects",
  };
  return labels[category];
}
