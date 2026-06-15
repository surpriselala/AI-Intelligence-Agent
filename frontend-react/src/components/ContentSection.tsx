import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { ContentCard } from "./ContentCard";
import type { ContentKind, DashboardItem } from "../types/dashboard";
import { categoryTitle } from "../api/dashboardApi";

interface ContentSectionProps {
  category: ContentKind;
  items: DashboardItem[];
  viewAllPath?: string;
  title?: string;
}

export function ContentSection({ category, items, title, viewAllPath }: ContentSectionProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>{title || categoryTitle(category)}</h2>
        {viewAllPath ? (
          <Link className="link-button" to={viewAllPath}>
            View all
            <ArrowRight size={15} />
          </Link>
        ) : null}
      </div>
      <div className="item-list">
        {items.length ? (
          items.map((item) => <ContentCard category={category} item={item} key={item.id} />)
        ) : (
          <div className="empty-state">No items found.</div>
        )}
      </div>
    </section>
  );
}
