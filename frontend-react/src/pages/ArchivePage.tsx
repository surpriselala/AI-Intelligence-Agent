import type { ReactNode } from "react";
import { ContentCard } from "../components/ContentCard";
import { Pagination } from "../components/Pagination";
import { categoryTitle } from "../api/dashboardApi";
import type { ContentKind, DashboardItem, PaginatedResult } from "../types/dashboard";

interface ArchivePageProps {
  category: ContentKind;
  result: PaginatedResult<DashboardItem> | null;
  filterBar: ReactNode;
  page: number;
  isLoading: boolean;
  errorMessage: string;
  onPageChange: (page: number) => void;
}

const descriptions: Record<ContentKind, string> = {
  articles:
    "Today first, then past report items. Score sorting is ready for later; currently everything is ordered by report date.",
  news: "Today first, then past industry news from generated reports.",
  projects:
    "Today first, then past GitHub project picks, ordered by date until score data exists.",
};

export function ArchivePage({
  category,
  errorMessage,
  filterBar,
  isLoading,
  onPageChange,
  page,
  result,
}: ArchivePageProps) {
  const items = result?.items || [];
  const total = result?.total || 0;
  const totalPages = result?.totalPages || 1;
  const currentPage = result?.page || page;
  const pageSize = result?.pageSize || 10;

  return (
    <>
      {filterBar}

      <div className="page-heading">
        <h2>{categoryTitle(category)}</h2>
        <p>{descriptions[category]}</p>
      </div>

      <section className="history-section">
        <div className="history-header">
          <h3>{categoryTitle(category)} Archive</h3>
          <span>
            {total} total · {pageSize} per page
          </span>
        </div>
        <div className="history-list">
          {errorMessage ? (
            <div className="api-state api-state-error compact">
              <h2>Archive data could not be loaded.</h2>
              <p>{errorMessage}</p>
            </div>
          ) : isLoading && !result ? (
            <div className="empty-state">Loading archive items...</div>
          ) : items.length ? (
            items.map((item) => (
              <ContentCard category={category} item={item} key={item.id} />
            ))
          ) : (
            <div className="empty-state">No matching items found.</div>
          )}
        </div>
      </section>

      {!errorMessage ? (
        <Pagination
          onPageChange={onPageChange}
          page={currentPage}
          total={total}
          totalPages={totalPages}
        />
      ) : null}
    </>
  );
}
