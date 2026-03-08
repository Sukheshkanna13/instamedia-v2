"use client";

import { useState, useEffect } from "react";

interface ScheduledPost {
    id: string;
    brand_id: string;
    content: string;
    image_style?: string;
    platform: string;
    scheduled_time: string;
    status: "draft" | "scheduled" | "published";
    resonance_score: number;
}

const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];

const PLATFORM_ICON: Record<string, string> = {
    instagram: "📸", linkedin: "💼", twitter: "✕", tiktok: "◈", both: "◈"
};

function getDaysInMonth(year: number, month: number) {
    return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year: number, month: number) {
    return new Date(year, month, 1).getDay();
}

export default function CalendarPage() {
    const today = new Date();
    const [year, setYear] = useState(today.getFullYear());
    const [month, setMonth] = useState(today.getMonth());
    const [posts, setPosts] = useState<ScheduledPost[]>([]);
    const [selected, setSelected] = useState<ScheduledPost[]>([]);
    const [selectedDay, setSelectedDay] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);

    const [reschedulingId, setReschedulingId] = useState<string | null>(null);
    const [rescheduleTime, setRescheduleTime] = useState<string>("");

    useEffect(() => {
        fetch("/api/posts?brand_id=default")
            .then(r => r.json())
            .then(data => {
                if (data.success) setPosts(data.posts ?? []);
            })
            .catch(() => { })
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
        setReschedulingId(null);
    };

    const handleDelete = async (postId: string) => {
        if (!confirm("Are you sure you want to delete this post?")) return;
        try {
            const res = await fetch("/api/posts", {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ post_id: postId })
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || "Failed to delete");

            setPosts(prev => prev.filter(p => p.id !== postId));
            setSelected(prev => prev.filter(p => p.id !== postId));
        } catch (e) {
            alert("Failed to delete post: " + (e as Error).message);
        }
    };

    const handleReschedule = async (postId: string) => {
        if (!rescheduleTime) return;
        try {
            // NOTE: PATCH endpoint needs to be implemented in phase 3
            const res = await fetch(`/api/posts/${postId}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ scheduled_time: rescheduleTime })
            });
            if (!res.ok) throw new Error("Reschedule endpoint not available yet (Phase 3)");
            const data = await res.json();

            setPosts(prev => prev.map(p => p.id === postId ? { ...p, scheduled_time: rescheduleTime } : p));
            setSelected(prev => prev.map(p => p.id === postId ? { ...p, scheduled_time: rescheduleTime } : p));
            setReschedulingId(null);
        } catch (e) {
            alert("Failed to reschedule post: " + (e as Error).message);
        }
    };

    const handlePublish = (platform: string, content: string) => {
        const text = encodeURIComponent(content);
        let url = "";

        switch (platform.toLowerCase()) {
            case "twitter":
                url = `https://twitter.com/intent/tweet?text=${text}`;
                break;
            case "linkedin":
                url = `https://www.linkedin.com/feed/?shareActive=true&text=${text}`;
                break;
            case "instagram":
                navigator.clipboard.writeText(content);
                alert("Post text copied to clipboard! Opening Instagram...");
                url = "https://instagram.com";
                break;
            default:
                url = `https://${platform}.com`;
        }

        const newWindow = window.open(url, "_blank");
        if (newWindow) newWindow.opener = null;
    };

    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);
    const totalCells = Math.ceil((firstDay + daysInMonth) / 7) * 7;

    const fmtTime = (iso: string) => {
        try {
            return new Date(iso).toLocaleTimeString("en", { hour: "2-digit", minute: "2-digit" });
        } catch { return ""; }
    };

    return (
        <div className="page-body">
            <div>
                <h1 className="display-title">Content <em>Calendar</em></h1>
                <p className="sub-text" style={{ marginTop: 6 }}>
                    Visualize and manage your scheduled content pipeline
                </p>
            </div>

            <div className="grid-3">
                {[
                    { label: "Scheduled", val: posts.filter(p => p.status === "scheduled").length, color: "var(--teal)" },
                    { label: "Published", val: posts.filter(p => p.status === "published").length, color: "var(--emerald)" },
                    { label: "This Month", val: posts.filter(p => { try { const d = new Date(p.scheduled_time); return d.getMonth() === month && d.getFullYear() === year; } catch { return false; } }).length, color: "var(--violet)" },
                ].map(s => (
                    <div key={s.label} className="stat-card">
                        <div className="stat-card-label">{s.label}</div>
                        <div className="stat-card-value" style={{ color: s.color, fontSize: 28 }}>{s.val}</div>
                    </div>
                ))}
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", gap: 20, alignItems: "flex-start", width: "100%" }}>
                <div className="card" style={{ padding: 20, flex: "1 1 500px", minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
                        <button className="btn-icon" onClick={prevMonth}>‹</button>
                        <div style={{ fontFamily: "var(--font-display)", fontSize: 18, fontWeight: 700, letterSpacing: "-0.02em" }}>
                            {MONTHS[month]} {year}
                        </div>
                        <button className="btn-icon" onClick={nextMonth}>›</button>
                    </div>

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
                                    {dayPosts.slice(0, 2).map((p, pi) => (
                                        <div key={pi} className={`cal-event ${p.platform}`}>
                                            {fmtTime(p.scheduled_time)} {p.content.substring(0, 15)}…
                                        </div>
                                    ))}
                                    {dayPosts.length > 2 && (
                                        <div className="mono-label" style={{ fontSize: 8, color: "var(--text-muted)", paddingLeft: 3 }}>
                                            +{dayPosts.length - 2} more
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 16, flex: "1 1 350px", minWidth: 0 }}>
                    {selectedDay && (
                        <div className="card" style={{ marginBottom: 16 }}>
                            <div className="card-header">
                                <div>
                                    <div className="mono-label">Selected Day</div>
                                    <div className="section-title" style={{ marginTop: 4 }}>
                                        {MONTHS[month]} {selectedDay}, {year}
                                    </div>
                                </div>
                                <span className="badge badge-teal">{selected.length} post{selected.length !== 1 ? "s" : ""}</span>
                            </div>

                            {selected.length === 0 ? (
                                <div className="empty-state" style={{ padding: "24px 0" }}>
                                    <div className="empty-icon">📭</div>
                                    <div className="empty-sub">No posts scheduled for this day.</div>
                                </div>
                            ) : (
                                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                                    {selected.map((p, i) => (
                                        <div key={i} style={{
                                            background: "var(--s2)", border: "1px solid var(--border)",
                                            borderRadius: "var(--r)", padding: "14px"
                                        }}>
                                            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                                                <span style={{ fontSize: 16 }}>{PLATFORM_ICON[p.platform] ?? "◈"}</span>
                                                <span className={`badge badge-${p.platform}`}>{p.platform}</span>
                                                <span className="mono-label">{fmtTime(p.scheduled_time)}</span>
                                                {p.resonance_score > 0 && (
                                                    <span className="badge badge-teal" style={{ marginLeft: "auto" }}>
                                                        ERS {p.resonance_score}
                                                    </span>
                                                )}
                                            </div>
                                            <div style={{ fontSize: 13, lineHeight: 1.65, color: "var(--text)", marginBottom: 8 }}>
                                                {p.content}
                                            </div>
                                            {p.image_style && (
                                                <div style={{ fontSize: 11, color: "var(--text-dim)", fontStyle: "italic", marginBottom: 8 }}>
                                                    🖼 {p.image_style}
                                                </div>
                                            )}

                                            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                                                {reschedulingId === p.id ? (
                                                    <div style={{ display: "flex", gap: 8, alignItems: "center", width: "100%" }}>
                                                        <input
                                                            type="datetime-local"
                                                            className="input"
                                                            style={{ flex: 1 }}
                                                            value={rescheduleTime}
                                                            onChange={e => setRescheduleTime(e.target.value)}
                                                        />
                                                        <button className="btn btn-primary btn-sm" onClick={() => handleReschedule(p.id)}>
                                                            Save
                                                        </button>
                                                        <button className="btn btn-ghost btn-sm" onClick={() => setReschedulingId(null)}>
                                                            Cancel
                                                        </button>
                                                    </div>
                                                ) : (
                                                    <>
                                                        <button
                                                            className="btn btn-ghost btn-sm"
                                                            style={{ color: "var(--teal)" }}
                                                            onClick={() => handlePublish(p.platform, p.content)}
                                                        >
                                                            🚀 Publish Now
                                                        </button>
                                                        <button
                                                            className="btn btn-ghost btn-sm"
                                                            onClick={() => {
                                                                setReschedulingId(p.id);
                                                                setRescheduleTime(p.scheduled_time.slice(0, 16));
                                                            }}
                                                        >
                                                            🕒 Reschedule
                                                        </button>
                                                        <button
                                                            className="btn btn-ghost btn-sm"
                                                            style={{ color: "var(--coral)" }}
                                                            onClick={() => handleDelete(p.id)}
                                                        >
                                                            x Delete
                                                        </button>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    <div className="card">
                        <div className="card-header">
                            <div className="section-title">All Scheduled Posts</div>
                            <span className="mono-label">{posts.filter(p => p.status === "scheduled").length} upcoming</span>
                        </div>

                        {loading && <div className="empty-state" style={{ padding: "24px 0" }}>
                            <div className="spinner" />
                        </div>}

                        {!loading && posts.length === 0 && (
                            <div className="empty-state" style={{ padding: "24px 0" }}>
                                <div className="empty-icon">📅</div>
                                <div className="empty-sub">
                                    No posts scheduled yet.<br />
                                    Create content in the Studio and schedule it.
                                </div>
                            </div>
                        )}

                        {posts.length > 0 && (
                            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                                {[...posts].sort((a, b) =>
                                    new Date(a.scheduled_time).getTime() - new Date(b.scheduled_time).getTime()
                                ).slice(0, 10).map((p, i) => {
                                    const d = new Date(p.scheduled_time);
                                    return (
                                        <div key={i} style={{
                                            display: "flex", gap: 12, alignItems: "flex-start",
                                            padding: "10px 0",
                                            borderBottom: i < 9 ? "1px solid var(--border)" : "none"
                                        }}>
                                            <div style={{ textAlign: "center", width: 36, flexShrink: 0 }}>
                                                <div style={{
                                                    fontFamily: "var(--font-display)", fontSize: 18, fontWeight: 900,
                                                    color: "var(--teal)", lineHeight: 1
                                                }}>
                                                    {d.getDate()}
                                                </div>
                                                <div className="mono-label" style={{ fontSize: 8 }}>
                                                    {d.toLocaleString("en", { month: "short" })}
                                                </div>
                                            </div>
                                            <div style={{ flex: 1, minWidth: 0 }}>
                                                <div style={{
                                                    fontSize: 12, lineHeight: 1.5, color: "var(--text)",
                                                    overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", marginBottom: 4
                                                }}>
                                                    {p.content}
                                                </div>
                                                <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                                                    <span className={`badge badge-${p.platform}`}>{p.platform}</span>
                                                    <span className={`badge ${p.status === "scheduled" ? "badge-teal" : "badge-emerald"}`}>
                                                        {p.status}
                                                    </span>
                                                    <button
                                                        className="btn-icon"
                                                        style={{ marginLeft: "auto", width: 24, height: 24, fontSize: 13, color: "var(--teal)", border: "none", background: "transparent" }}
                                                        title="Publish Now"
                                                        onClick={() => handlePublish(p.platform, p.content)}
                                                    >
                                                        🚀
                                                    </button>
                                                    <button
                                                        className="btn-icon"
                                                        style={{ marginLeft: "auto", width: 24, height: 24, fontSize: 12, color: "var(--coral)", border: "none", background: "transparent" }}
                                                        title="Delete Post"
                                                        onClick={() => handleDelete(p.id)}
                                                    >
                                                        ×
                                                    </button>
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
