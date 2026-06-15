import { Calendar, Star } from "lucide-react";
import type { ContentKind, DashboardItem } from "../types/dashboard";
import { formatNumber, initials } from "../utils/format";

interface ContentCardProps {
  category: ContentKind;
  item: DashboardItem;
}

export function ContentCard({ category, item }: ContentCardProps) {
  return (
    <article className="content-card">
      <div className={`thumb ${category}`}>{initials(item.title)}</div>
      <div className="card-body">
        <h3 className="card-title">
          <a href={item.url || "#"} rel="noreferrer" target="_blank">
            {item.title}
          </a>
        </h3>
        <div className="card-meta">
          <span>
            <Calendar size={14} />
            {item.date}
          </span>
          {item.source ? <span>{item.source}</span> : null}
          {item.stars ? (
            <span>
              <Star size={14} />
              {formatNumber(item.stars)} stars
            </span>
          ) : null}
          {item.language ? <span>{item.language}</span> : null}
        </div>
        <p className="summary">{item.summary}</p>
        {item.tags?.length ? (
          <div className="tag-list">
            {item.tags.slice(0, 3).map((tag) => (
              <span className="tag" key={tag}>
                {tag}
              </span>
            ))}
          </div>
        ) : null}
      </div>
    </article>
  );
}
