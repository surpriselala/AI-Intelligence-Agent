import {
  Bell,
  Bookmark,
  FileText,
  Github,
  Home,
  Newspaper,
  Settings,
  Sparkles,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const primaryNav = [
  { path: "/", label: "Dashboard", icon: Home },
  { path: "/articles", label: "Articles", icon: FileText },
  { path: "/news", label: "News", icon: Newspaper },
  { path: "/github-projects", label: "GitHub Projects", icon: Github },
];

const secondaryNav = [
  { label: "Saved", icon: Bookmark },
  { label: "Bookmarks", icon: Bookmark },
  { label: "Alerts", icon: Bell },
  { label: "Settings", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <Sparkles size={24} />
        </div>
        <div>
          <div className="brand-title">AI Intelligence</div>
          <div className="brand-title">Agent</div>
        </div>
      </div>

      <nav className="nav-list" aria-label="Dashboard navigation">
        {primaryNav.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
              end={item.path === "/"}
              key={item.path}
              to={item.path}
            >
              <span className="nav-icon">
                <Icon size={18} />
              </span>
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      <nav className="nav-list secondary" aria-label="Secondary navigation">
        {secondaryNav.map((item) => {
          const Icon = item.icon;
          return (
            <button className="nav-item muted" key={item.label} type="button">
              <span className="nav-icon">
                <Icon size={17} />
              </span>
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-card">
        <div className="spark">
          <Sparkles size={18} />
        </div>
        <p>Stay ahead with curated AI insights.</p>
      </div>
    </aside>
  );
}
