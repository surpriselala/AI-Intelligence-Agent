import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  note: string;
  value: string | number;
}

export function StatCard({ icon: Icon, label, note, value }: StatCardProps) {
  return (
    <article className="stat-card">
      <div className="stat-icon">
        <Icon size={26} />
      </div>
      <div className="stat-copy">
        <div className="stat-label">{label}</div>
        <div className="stat-value">{value}</div>
        <div className="stat-note">{note}</div>
      </div>
    </article>
  );
}
