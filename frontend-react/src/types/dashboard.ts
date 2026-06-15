export type ViewKey = "dashboard" | "articles" | "news" | "projects";
export type ContentKind = "articles" | "news" | "projects";

export interface DashboardItem {
  id: string;
  type: ContentKind;
  title: string;
  summary: string;
  url: string;
  date: string;
  source?: string;
  stars?: number;
  language?: string;
  tags?: string[];
  score?: number;
  order?: number;
}

export interface DashboardPayload {
  generated_at: string;
  totals: {
    articles: number;
    news: number;
    projects: number;
    stars: number;
    reports: number;
  };
  dashboard: Record<ContentKind, DashboardItem[]>;
  history: Record<ContentKind, DashboardItem[]>;
}

export interface PaginatedResult<T> {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}
