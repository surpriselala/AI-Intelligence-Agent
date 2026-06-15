import { Bell, Search } from "lucide-react";

interface TopbarProps {
  query: string;
  onQueryChange: (query: string) => void;
}

export function Topbar({ query, onQueryChange }: TopbarProps) {
  return (
    <header className="topbar">
      <div>
        <h1>AI Intelligence Agent Dashboard</h1>
        <p>Your AI-powered hub for articles, news, and GitHub insights.</p>
      </div>
      <div className="topbar-actions">
        <label className="search-box">
          <Search size={18} />
          <input
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Search content, topics, repositories..."
            type="search"
            value={query}
          />
        </label>
        <button className="icon-button" type="button" aria-label="Notifications">
          <Bell size={20} />
        </button>
        <div className="avatar">AI</div>
      </div>
    </header>
  );
}
