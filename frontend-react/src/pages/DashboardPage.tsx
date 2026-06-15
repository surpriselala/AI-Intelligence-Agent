import { FileText, Flame, Github, Globe2 } from "lucide-react";
import type { ReactNode } from "react";
import { ContentSection } from "../components/ContentSection";
import { StatCard } from "../components/StatCard";
import type { DashboardPayload } from "../types/dashboard";
import { formatNumber } from "../utils/format";

interface DashboardPageProps {
  data: DashboardPayload;
  filterBar: ReactNode;
}

export function DashboardPage({ data, filterBar }: DashboardPageProps) {
  return (
    <>
      <section className="overview-card" aria-label="Today's update overview">
        <div className="overview-copy">
          <div className="overview-icon">
            <Flame size={30} />
          </div>
          <div>
            <h2>Today's Update Overview</h2>
            <p>
              Stay ahead with the latest AI research, news, and open-source projects.
              Here's what we found for you today.
            </p>
          </div>
        </div>
        <div className="stats-grid">
          <StatCard icon={FileText} label="Articles" note="Latest report picks" value={data.totals.articles} />
          <StatCard icon={Globe2} label="News" note="Curated source updates" value={data.totals.news} />
          <StatCard icon={Github} label="GitHub Projects" note="Open-source highlights" value={data.totals.projects} />
          <StatCard icon={Flame} label="Total Stars" note="Across tracked projects" value={formatNumber(data.totals.stars)} />
        </div>
      </section>

      {filterBar}

      <div className="dashboard-grid">
        <ContentSection
          category="articles"
          items={data.dashboard.articles}
          viewAllPath="/articles"
        />
        <ContentSection category="news" items={data.dashboard.news} viewAllPath="/news" />
        <ContentSection
          category="projects"
          items={data.dashboard.projects}
          viewAllPath="/github-projects"
        />
      </div>
    </>
  );
}
