import type { ReactNode } from "react";
import { ContentCard } from "../components/ContentCard";
import { Pagination } from "../components/Pagination";
import { categoryTitle, paginateItems } from "../api/dashboardApi";
import type { ContentKind, DashboardItem } from "../types/dashboard";

interface ArchivePageProps {
  category: ContentKind;
  items: DashboardItem[];
  filterBar: ReactNode;
  page: number;
  onPageChange: (page: number) => void;
}

const descriptions: Record<ContentKind, string> = {
  articles:
    "Today first, then past report items. Score sorting is ready for later; currently everything is ordered by report date.",
  news: "Today first, then past industry news from generated reports.",
  projects:
    "Today first, then past GitHub project picks, ordered by date until score data exists.",
};

export function ArchivePage({ category, filterBar, items, onPageChange, page }: ArchivePageProps) {
  const paginated = paginateItems(items, page);

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
          <span>{paginated.total} total · 10 per page</span>
        </div>
        <div className="history-list">
          {paginated.items.length ? (
            paginated.items.map((item) => (
              <ContentCard category={category} item={item} key={item.id} />
            ))
          ) : (
            <div className="empty-state">No matching items found.</div>
          )}
        </div>
      </section>

      <Pagination
        onPageChange={onPageChange}
        page={paginated.page}
        total={paginated.total}
        totalPages={paginated.totalPages}
      />
    </>
  );
}
