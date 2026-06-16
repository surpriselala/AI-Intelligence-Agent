import type {
  ContentKind,
  DashboardItem,
  DashboardPayload,
  ListParams,
  PaginatedResult,
} from "../types/dashboard";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(
  /\/$/,
  "",
);

interface ApiPaginatedResult<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

const categoryPaths: Record<ContentKind, string> = {
  articles: "/api/articles",
  news: "/api/news",
  projects: "/api/github-projects",
};

export async function getDashboardData(
  params: Pick<ListParams, "query" | "topic"> = {},
): Promise<DashboardPayload> {
  return requestJson<DashboardPayload>(withQuery("/api/dashboard", params));
}

export async function getArticles(
  params: ListParams = {},
): Promise<PaginatedResult<DashboardItem>> {
  return getArchiveItems("articles", params);
}

export async function getNews(
  params: ListParams = {},
): Promise<PaginatedResult<DashboardItem>> {
  return getArchiveItems("news", params);
}

export async function getGithubProjects(
  params: ListParams = {},
): Promise<PaginatedResult<DashboardItem>> {
  return getArchiveItems("projects", params);
}

export async function getArchiveItems(
  category: ContentKind,
  params: ListParams = {},
): Promise<PaginatedResult<DashboardItem>> {
  const response = await requestJson<ApiPaginatedResult<DashboardItem>>(
    withQuery(categoryPaths[category], params),
  );
  return {
    items: response.items,
    page: response.page,
    pageSize: response.page_size,
    total: response.total,
    totalPages: response.total_pages,
  };
}

export function categoryTitle(category: ContentKind): string {
  const labels: Record<ContentKind, string> = {
    articles: "Articles",
    news: "News",
    projects: "GitHub Projects",
  };
  return labels[category];
}

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

function withQuery(path: string, params: ListParams): string {
  const search = new URLSearchParams();
  if (params.page) search.set("page", String(params.page));
  if (params.pageSize) search.set("page_size", String(params.pageSize));

  const query = params.query?.trim();
  if (query) search.set("query", query);

  const topic = params.topic?.trim();
  if (topic && topic !== "All") search.set("topic", topic);

  const queryString = search.toString();
  return queryString ? `${path}?${queryString}` : path;
}
