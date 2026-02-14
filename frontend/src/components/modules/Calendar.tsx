import { useState, useEffect } from "react";
import { api } from "../../lib/api";
import type { ScheduledPost } from "../../types";

const DAYS = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
const MONTHS = ["January","February","March","April","May","June",
                "July","August","September","October","November","December"];

const PLATFORM_ICON: Record<string, string> = {
  instagram:"📸", linkedin:"💼", twitter:"✕", tiktok:"◈", both:"◈"
};

function getDaysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year: number, month: number) {
  return new Date(year, month, 1).getDay();
}

export default function Calendar() {
  const today = new Date();
  const [year,  setYear]  = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth());
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [selected, setSelected] = useState<ScheduledPost[]>([]);
  const [selectedDay, setSelectedDay] = useState<number|null>(null);
  const [loading, setLoading]  = useState(true);

  useEffect(() => {
    api.getCalendarPosts("default")
      .then(r => setPosts(r.posts ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const prevMonth = () => {
    if (month === 0) { setMonth(11); setYear(y => y - 1); }
    else setMonth(m => m - 1);
  };

  const nextMonth = () => {
    if (month === 11) { setMonth(0); setYear(y => y + 1); }
    else setMonth(m => m + 1);
  };

  // Get posts for a specific day
  const getPostsForDay = (day: number): ScheduledPost[] => {
    return posts.filter(p => {
      try {
        const d = new Date(p.scheduled_time);
        return d.getFullYear() === year && d.getMonth() === month && d.getDate() === day;
      } catch { return false; }
    });
  };

  const handleDayClick = (day: number) => {
    const dayPosts = getPostsForDay(day);
    setSelectedDay(day);
    setSelected(dayPosts);
  };

  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);
  const totalCells = Math.ceil((firstDay + daysInMonth) / 7) * 7;

  const fmtTime = (iso: string) => {
    try {
      return new Date(iso).toLocaleTimeString("en",{hour:"2-digit",minute:"2-digit"});
    } catch { return ""; }
  };

  return (
    <div className="page-body">
      <div>
        <h1 className="display-title">Content <em>Calendar</em></h1>
        <p className="sub-text" style={{ marginTop:6 }}>
          Visualize and manage your scheduled content pipeline
        </p>
      </div>

      {/* Stats row */}
      <div className="grid-3">
        {[
          { label:"Scheduled",  val: posts.filter(p=>p.status==="scheduled").length,  color:"var(--teal)" },
          { label:"Published",  val: posts.filter(p=>p.status==="published").length,  color:"var(--emerald)" },
          { label:"This Month", val: posts.filter(p=>{ try { const d=new Date(p.scheduled_time); return d.getMonth()===month && d.getFullYear()===year; } catch{return false;} }).length, color:"var(--violet)" },
        ].map(s => (
          <div key={s.label} className="stat-card">
            <div className="stat-card-label">{s.label}</div>
            <div className="stat-card-value" style={{ color:s.color, fontSize:28 }}>{s.val}</div>
          </div>
        ))}
      </div>

      <div className="grid-2" style={{ gap:20, alignItems:"start" }}>

        {/* ── CALENDAR GRID ── */}
        <div className="card" style={{ padding:20 }}>
          {/* Month nav */}
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:20 }}>
            <button className="btn-icon" onClick={prevMonth}>‹</button>
            <div style={{ fontFamily:"var(--font-display)", fontSize:18, fontWeight:700, letterSpacing:"-0.02em" }}>
              {MONTHS[month]} {year}
            </div>
            <button className="btn-icon" onClick={nextMonth}>›</button>
          </div>

          {/* Calendar */}
          <div className="calendar-grid">
            {DAYS.map(d => (
              <div key={d} className="cal-header-cell">{d}</div>
            ))}

            {Array.from({ length: totalCells }, (_, i) => {
              const cellDay = i - firstDay + 1;
              const isValid = cellDay >= 1 && cellDay <= daysInMonth;
              const isToday = isValid && cellDay === today.getDate()
                && month === today.getMonth() && year === today.getFullYear();
              const dayPosts = isValid ? getPostsForDay(cellDay) : [];
              const isSelected = selectedDay === cellDay;

              return (
                <div key={i}
                  className={`cal-day ${isToday ? "today" : ""} ${!isValid ? "other-month" : ""}`}
                  style={{
                    cursor: isValid ? "pointer" : "default",
                    background: isSelected && isValid ? "rgba(0,212,184,0.06)" : undefined
                  }}
                  onClick={() => isValid && handleDayClick(cellDay)}
                >
                  <div className="cal-day-num">{isValid ? cellDay : ""}</div>
                  {dayPosts.slice(0,2).map((p, pi) => (
                    <div key={pi} className={`cal-event ${p.platform}`}>
                      {fmtTime(p.scheduled_time)} {p.content.substring(0,15)}…
                    </div>
                  ))}
                  {dayPosts.length > 2 && (
                    <div className="mono-label" style={{ fontSize:8, color:"var(--text-muted)", paddingLeft:3 }}>
                      +{dayPosts.length - 2} more
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* ── DAY DETAIL / POST LIST ── */}
        <div>
          {selectedDay && (
            <div className="card" style={{ marginBottom:16 }}>
              <div className="card-header">
                <div>
                  <div className="mono-label">Selected Day</div>
                  <div className="section-title" style={{ marginTop:4 }}>
                    {MONTHS[month]} {selectedDay}, {year}
                  </div>
                </div>
                <span className="badge badge-teal">{selected.length} post{selected.length!==1?"s":""}</span>
              </div>

              {selected.length === 0 ? (
                <div className="empty-state" style={{ padding:"24px 0" }}>
                  <div className="empty-icon">📭</div>
                  <div className="empty-sub">No posts scheduled for this day.</div>
                </div>
              ) : (
                <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
                  {selected.map((p, i) => (
                    <div key={i} style={{
                      background:"var(--s2)", border:"1px solid var(--border)",
                      borderRadius:"var(--r)", padding:"14px"
                    }}>
                      <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:8 }}>
                        <span style={{ fontSize:16 }}>{PLATFORM_ICON[p.platform] ?? "◈"}</span>
                        <span className={`badge badge-${p.platform}`}>{p.platform}</span>
                        <span className="mono-label">{fmtTime(p.scheduled_time)}</span>
                        {p.resonance_score > 0 && (
                          <span className="badge badge-teal" style={{ marginLeft:"auto" }}>
                            ERS {p.resonance_score}
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize:13, lineHeight:1.65, color:"var(--text)", marginBottom:8 }}>
                        {p.content}
                      </div>
                      {p.image_style && (
                        <div style={{ fontSize:11, color:"var(--text-dim)", fontStyle:"italic" }}>
                          🖼 {p.image_style}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* All upcoming posts list */}
          <div className="card">
            <div className="card-header">
              <div className="section-title">All Scheduled Posts</div>
              <span className="mono-label">{posts.filter(p=>p.status==="scheduled").length} upcoming</span>
            </div>

            {loading && <div className="empty-state" style={{padding:"24px 0"}}>
              <div className="spinner" />
            </div>}

            {!loading && posts.length === 0 && (
              <div className="empty-state" style={{padding:"24px 0"}}>
                <div className="empty-icon">📅</div>
                <div className="empty-sub">
                  No posts scheduled yet.<br />
                  Create content in the Studio and schedule it.
                </div>
              </div>
            )}

            {posts.length > 0 && (
              <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                {[...posts].sort((a,b) =>
                  new Date(a.scheduled_time).getTime() - new Date(b.scheduled_time).getTime()
                ).slice(0,10).map((p, i) => {
                  const d = new Date(p.scheduled_time);
                  return (
                    <div key={i} style={{
                      display:"flex", gap:12, alignItems:"flex-start",
                      padding:"10px 0",
                      borderBottom: i < 9 ? "1px solid var(--border)" : "none"
                    }}>
                      <div style={{ textAlign:"center", width:36, flexShrink:0 }}>
                        <div style={{ fontFamily:"var(--font-display)", fontSize:18, fontWeight:900,
                          color:"var(--teal)", lineHeight:1 }}>
                          {d.getDate()}
                        </div>
                        <div className="mono-label" style={{ fontSize:8 }}>
                          {d.toLocaleString("en",{month:"short"})}
                        </div>
                      </div>
                      <div style={{ flex:1, minWidth:0 }}>
                        <div style={{ fontSize:12, lineHeight:1.5, color:"var(--text)",
                          overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap", marginBottom:4 }}>
                          {p.content}
                        </div>
                        <div style={{ display:"flex", gap:6 }}>
                          <span className={`badge badge-${p.platform}`}>{p.platform}</span>
                          <span className={`badge ${p.status === "scheduled" ? "badge-teal" : "badge-emerald"}`}>
                            {p.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
