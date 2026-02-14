import { useState, useEffect } from "react";
import { api } from "../../lib/api";
import type { DashboardStats, ScheduledPost } from "../../types";

const PLATFORM_ICON: Record<string, string> = {
  instagram: "📸", linkedin: "💼", twitter: "✕", tiktok: "◈", both: "◈",
};

const STATUS_BADGE: Record<string, string> = {
  scheduled: "badge-teal",
  published: "badge-emerald",
  draft:     "badge-amber",
};

export default function Overview() {
  const [stats,   setStats]   = useState<DashboardStats | null>(null);
  const [recent,  setRecent]  = useState<ScheduledPost[]>([]);
  const [upcoming,setUpcoming]= useState<ScheduledPost[]>([]);
  const [health,  setHealth]  = useState<{ posts_in_chromadb: number; supabase_connected: boolean; llm_provider: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getPostStats().then(setStats).catch(()=>{}),
      api.getRecentPosts("default", 4).then(r => setRecent(r.posts)).catch(()=>{}),
      api.getCalendarPosts("default").then(r => {
        const now = new Date();
        const up = (r.posts ?? [])
          .filter(p => p.status === "scheduled" && new Date(p.scheduled_time) > now)
          .sort((a,b) => new Date(a.scheduled_time).getTime() - new Date(b.scheduled_time).getTime())
          .slice(0, 3);
        setUpcoming(up);
      }).catch(()=>{}),
      api.health().then(setHealth).catch(()=>{}),
    ]).finally(() => setLoading(false));
  }, []);

  const fmtDate = (iso: string) => {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    } catch { return iso; }
  };

  const statCards = [
    { label: "Total Content",     value: stats?.total_content       ?? "—", color: "var(--teal)",    icon: "◈", sub: "posts created" },
    { label: "Scheduled",         value: stats?.scheduled           ?? "—", color: "var(--violet)",  icon: "📅", sub: "upcoming posts" },
    { label: "Avg Resonance",     value: stats?.avg_resonance_score ?? "—", color: "var(--amber)",   icon: "⚡", sub: "ERS score" },
    { label: "Brand Memory",      value: stats?.db_post_count       ?? "—", color: "var(--emerald)", icon: "🧬", sub: "posts in ESG" },
  ];

  return (
    <div className="page-body">
      {/* Header */}
      <div>
        <h1 className="display-title">Brand <em>Overview</em></h1>
        <p className="sub-text" style={{ marginTop: 6 }}>
          Your brand's content performance and AI-powered emotional signal summary
        </p>
      </div>

      {/* System status bar */}
      <div className="card card-sm" style={{ display:"flex", alignItems:"center", gap:24, flexWrap:"wrap" }}>
        <div style={{ display:"flex", alignItems:"center", gap:8 }}>
          <div className={`status-dot ${health ? "" : "offline"}`} />
          <span className="mono-label" style={{ color: health ? "var(--emerald)" : "var(--coral)" }}>
            {health ? "AI ENGINE ONLINE" : "ENGINE OFFLINE"}
          </span>
        </div>
        {health && <>
          <span className="mono-label">LLM: {health.llm_provider}</span>
          <span className="mono-label">Supabase: {health.supabase_connected ? "connected" : "local mode"}</span>
          <span className="mono-label">{health.posts_in_chromadb} posts in ESG memory</span>
        </>}
      </div>

      {/* Stat cards */}
      {loading ? (
        <div className="grid-4">
          {[1,2,3,4].map(i => (
            <div key={i} className="stat-card" style={{ animation: `fadeUp 0.3s ${i*60}ms both` }}>
              <div className="stat-card-label">Loading...</div>
              <div className="stat-card-value" style={{ color: "var(--border2)" }}>—</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid-4 stagger">
          {statCards.map(s => (
            <div key={s.label} className="stat-card">
              <div className="stat-card-icon">{s.icon}</div>
              <div className="stat-card-label">{s.label}</div>
              <div className="stat-card-value" style={{ color: s.color }}>
                {s.value}
              </div>
              <div className="stat-card-sub">{s.sub}</div>
            </div>
          ))}
        </div>
      )}

      <div className="grid-2">
        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="mono-label">Recent Activity</div>
              <div className="section-title" style={{ marginTop: 4 }}>Latest Content</div>
            </div>
          </div>

          {recent.length === 0 ? (
            <div className="empty-state" style={{ padding: "32px 0" }}>
              <div className="empty-icon">📭</div>
              <div className="empty-sub">No posts yet. Create your first in the Studio.</div>
            </div>
          ) : (
            <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
              {recent.map((p, i) => (
                <div key={p.id ?? i} style={{
                  display:"flex", alignItems:"flex-start", gap:12,
                  padding:"12px 0",
                  borderBottom: i < recent.length-1 ? "1px solid var(--border)" : "none"
                }}>
                  <div style={{ fontSize:20 }}>{PLATFORM_ICON[p.platform] ?? "◈"}</div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontSize:12, lineHeight:1.5, color:"var(--text)", marginBottom:4,
                      overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                      {p.content}
                    </div>
                    <div style={{ display:"flex", alignItems:"center", gap:8, flexWrap:"wrap" }}>
                      <span className={`badge ${STATUS_BADGE[p.status] ?? "badge-teal"}`}>{p.status}</span>
                      <span className="mono-label">{fmtDate(p.scheduled_time)}</span>
                      {p.resonance_score > 0 && (
                        <span className="mono-label" style={{ color:"var(--teal)" }}>
                          ERS {p.resonance_score}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Upcoming Content */}
        <div>
          <div className="card" style={{ marginBottom:16 }}>
            <div className="card-header">
              <div>
                <div className="mono-label">Upcoming Content</div>
                <div className="section-title" style={{ marginTop: 4 }}>Scheduled Queue</div>
              </div>
            </div>

            {upcoming.length === 0 ? (
              <div className="empty-state" style={{ padding:"32px 0" }}>
                <div className="empty-icon">📅</div>
                <div className="empty-sub">Nothing scheduled. Go to Calendar to plan content.</div>
              </div>
            ) : (
              <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
                {upcoming.map((p, i) => (
                  <div key={p.id ?? i} style={{
                    background:"var(--s2)", borderRadius:"var(--r)", padding:"14px",
                    border:"1px solid var(--border)", display:"flex", gap:12
                  }}>
                    <div style={{
                      background:"rgba(0,212,184,0.08)", border:"1px solid rgba(0,212,184,0.15)",
                      borderRadius:"var(--r)", padding:"8px 12px", flexShrink:0, textAlign:"center"
                    }}>
                      <div style={{ fontFamily:"var(--font-display)", fontSize:20, fontWeight:900,
                        color:"var(--teal)", lineHeight:1 }}>
                        {new Date(p.scheduled_time).getDate()}
                      </div>
                      <div className="mono-label" style={{ fontSize:8 }}>
                        {new Date(p.scheduled_time).toLocaleString("en",{month:"short"})}
                      </div>
                    </div>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ fontSize:12, lineHeight:1.5, color:"var(--text)", marginBottom:5,
                        overflow:"hidden", textOverflow:"ellipsis",
                        display:"-webkit-box", WebkitLineClamp:2, WebkitBoxOrient:"vertical" }}>
                        {p.content}
                      </div>
                      <div style={{ display:"flex", gap:8 }}>
                        <span className={`badge badge-${p.platform}`}>{p.platform}</span>
                        <span className="mono-label">
                          {new Date(p.scheduled_time).toLocaleTimeString("en",{hour:"2-digit",minute:"2-digit"})}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* AI Automation CTA */}
          <div className="card" style={{
            background:"linear-gradient(135deg, rgba(0,212,184,0.06) 0%, rgba(167,139,250,0.06) 100%)",
            border:"1px solid rgba(0,212,184,0.15)"
          }}>
            <div style={{ marginBottom:12 }}>
              <div className="mono-label" style={{ color:"var(--teal)", marginBottom:4 }}>AI Automation</div>
              <div className="section-title">Auto-Publish Pipeline</div>
            </div>
            <p style={{ fontSize:12, color:"var(--text-dim)", lineHeight:1.7, marginBottom:16 }}>
              Connect your Instagram, LinkedIn, and TikTok accounts to enable fully automated
              publishing with emotional alignment scoring before every post goes live.
            </p>
            <button className="btn btn-primary" style={{ fontSize:11 }}>
              ✦ Coming Soon — Join Waitlist
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
