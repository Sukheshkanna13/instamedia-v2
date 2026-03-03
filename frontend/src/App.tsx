import { useState } from "react";
import type { Tab, ContentIdea } from "./types";
import Overview from "./components/modules/Overview";
import BrandDNA from "./components/modules/BrandDNA";
import IdeationEnhanced from "./components/modules/IdeationEnhanced";
import CreativeStudio from "./components/modules/CreativeStudio";
import Calendar from "./components/modules/Calendar";
import Connections from "./components/modules/Connections";
import BrandDrift from "./components/modules/BrandDrift";
import ColdStart from "./components/modules/ColdStart";
import DatabaseExpansion from "./components/modules/DatabaseExpansion";
import Analytics from "./components/modules/Analytics";
// ── Sidebar nav config ────────────────────────────────────────────────────────
const NAV = [
  {
    section: "Workspace",
    items: [
      { id: "overview" as Tab, label: "Overview", icon: "◆" },
    ]
  },
  {
    section: "Create",
    items: [
      { id: "dna" as Tab, label: "Brand DNA Vault", icon: "🧬" },
      { id: "ideation" as Tab, label: "Ideation", icon: "✦" },
      { id: "studio" as Tab, label: "Creative Studio", icon: "⚡" },
    ]
  },
  {
    section: "Publish",
    items: [
      { id: "calendar" as Tab, label: "Calendar", icon: "📅" },
      { id: "connections" as Tab, label: "Connections", icon: "🔗" },
    ]
  },
  {
    section: "Intelligence",
    items: [
      { id: "analytics" as Tab, label: "Analytics", icon: "📈" },
      { id: "database" as Tab, label: "Database", icon: "🗄️" },
      { id: "drift" as Tab, label: "Brand Drift", icon: "📊" },
      { id: "coldstart" as Tab, label: "Cold Start", icon: "🎯" },
    ]
  }
];

const PAGE_TITLE: Record<Tab, string> = {
  overview: "Overview",
  dna: "Brand DNA",
  ideation: "Ideation",
  studio: "Creative Studio",
  calendar: "Calendar",
  library: "Post Library",
  connections: "Platform Connections",
  database: "Database Expansion",
  drift: "Brand Drift Detection",
  coldstart: "Cold Start Bootstrap",
  analytics: "Analytics Dashboard",
};

export default function App() {
  const [tab, setTab] = useState<Tab>("overview");
  const [selectedIdea, setSelectedIdea] = useState<ContentIdea | null>(null);

  // When user picks an idea in Ideation, carry it to Studio
  const handleIdeaSelect = (idea: ContentIdea) => {
    setSelectedIdea(idea);
    setTab("studio");
  };

  const renderPage = () => {
    switch (tab) {
      case "overview": return <Overview />;
      case "dna": return <BrandDNA />;
      case "ideation": return <IdeationEnhanced onSelectIdea={handleIdeaSelect} />;
      case "studio": return <CreativeStudio selectedIdea={selectedIdea} />;
      case "calendar": return <Calendar />;
      case "connections": return <Connections />;
      case "database": return <DatabaseExpansion />;
      case "analytics": return <Analytics />;
      case "drift": return <BrandDrift />;
      case "coldstart": return <ColdStart onSelect={(id) => {
        console.log("Bootstrapped with archetype:", id);
        setTab("overview");
      }} />;
      default: return <Overview />;
    }
  };

  return (
    <div className="app-shell">

      {/* ── SIDEBAR ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-glyph">IM</div>
          <div className="logo-wordmark">
            <span className="logo-name">InstaMedia</span>
            <span className="logo-tagline">AI · v2.0</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {NAV.map(group => (
            <div key={group.section}>
              <div className="nav-section-label">{group.section}</div>
              {group.items.map(item => (
                <button
                  key={item.id}
                  className={`nav-item ${tab === item.id ? "active" : ""}`}
                  onClick={() => setTab(item.id)}
                >
                  <span className="nav-icon">{item.icon}</span>
                  {item.label}
                  {item.id === "ideation" && selectedIdea && (
                    <span className="nav-badge">1</span>
                  )}
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-pill">
            <div className="status-dot" />
            <span>AI Engine Online</span>
          </div>
          <div style={{ marginTop: 10, fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text-muted)" }}>
            ESG Prototype v2.0 · $0 Stack
          </div>
        </div>
      </aside>

      {/* ── MAIN ── */}
      <div className="main-content">

        {/* Topbar */}
        <div className="topbar">
          <div className="topbar-title">{PAGE_TITLE[tab]}</div>
          <div className="topbar-actions">
            {selectedIdea && tab !== "studio" && (
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => setTab("studio")}
              >
                ⚡ Resume Studio
              </button>
            )}
            <button
              className="btn btn-primary btn-sm"
              onClick={() => setTab("studio")}
            >
              + New Post
            </button>
          </div>
        </div>

        {/* Page content */}
        {renderPage()}
      </div>
    </div>
  );
}
