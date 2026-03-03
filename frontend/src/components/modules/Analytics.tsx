import { useState, useEffect } from "react";
import { api } from "../../lib/api";
import type { DashboardStats } from "../../types";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Legend
} from "recharts";

export default function Analytics() {
    const [dbStats, setDbStats] = useState<any>(null);
    const [postStats, setPostStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [dbRes, postRes] = await Promise.all([
                api.getDatabaseStats(),
                api.getPostStats()
            ]);
            setDbStats(dbRes);
            setPostStats(postRes);
            setError(null);
        } catch (e: any) {
            setError(e.message || "Failed to load analytics data");
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="page-body" style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh" }}>
                <div className="spinner" style={{ width: 40, height: 40 }} />
            </div>
        );
    }

    if (error) {
        return (
            <div className="page-body">
                <div className="alert alert-error">⚠ {error}</div>
                <button className="btn btn-primary" onClick={loadData} style={{ marginTop: 12 }}>Retry</button>
            </div>
        );
    }

    // Format data for Recharts
    const platformData = dbStats?.platforms
        ? Object.entries(dbStats.platforms).map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value }))
        : [];

    const emotionData = dbStats?.emotions
        ? Object.entries(dbStats.emotions).map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), count: value }))
        : [];

    const COLORS = ['#14b8a6', '#a78bfa', '#f472b6', '#38bdf8', '#fbbf24', '#f87171'];

    return (
        <div className="page-body">
            <div>
                <h1 className="display-title">Performance <em>Analytics</em></h1>
                <p className="sub-text" style={{ marginTop: 6, marginBottom: 24 }}>
                    Track emotional resonance, database growth, and content insights.
                </p>
            </div>

            {/* Top Metrics Row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 24 }}>
                <div className="card" style={{ padding: 20 }}>
                    <div className="mono-label" style={{ color: "var(--text-dim)", marginBottom: 8 }}>Total Intelligence DB Posts</div>
                    <div style={{ fontSize: 32, fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--teal)" }}>
                        {dbStats?.total_posts || 0}
                    </div>
                </div>

                <div className="card" style={{ padding: 20 }}>
                    <div className="mono-label" style={{ color: "var(--text-dim)", marginBottom: 8 }}>Average DB ERS</div>
                    <div style={{ fontSize: 32, fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--violet)" }}>
                        {dbStats?.avg_ers?.toFixed(1) || 0}
                    </div>
                </div>

                <div className="card" style={{ padding: 20 }}>
                    <div className="mono-label" style={{ color: "var(--text-dim)", marginBottom: 8 }}>Max ERS Discovered</div>
                    <div style={{ fontSize: 32, fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--pink)" }}>
                        {dbStats?.max_ers?.toFixed(1) || 0}
                    </div>
                </div>

                <div className="card" style={{ padding: 20 }}>
                    <div className="mono-label" style={{ color: "var(--text-dim)", marginBottom: 8 }}>Scheduled Posts</div>
                    <div style={{ fontSize: 32, fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--sky)" }}>
                        {postStats?.scheduled || 0}
                    </div>
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: 24 }}>
                {/* Emotion Distribution Chart */}
                <div className="card">
                    <div className="card-header">
                        <div className="section-title">Emotion Distribution</div>
                    </div>
                    <div style={{ height: 300, marginTop: 20 }}>
                        {emotionData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={emotionData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                                    <XAxis dataKey="name" tick={{ fill: "var(--text-dim)" }} axisLine={false} tickLine={false} />
                                    <YAxis tick={{ fill: "var(--text-dim)" }} axisLine={false} tickLine={false} />
                                    <Tooltip
                                        cursor={{ fill: "rgba(255,255,255,0.05)" }}
                                        contentStyle={{ backgroundColor: "#111", borderColor: "var(--border)", borderRadius: 8 }}
                                    />
                                    <Bar dataKey="count" fill="var(--teal)" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%", color: "var(--text-muted)" }}>
                                No emotion data available
                            </div>
                        )}
                    </div>
                </div>

                {/* Platform Breakdown Chart */}
                <div className="card">
                    <div className="card-header">
                        <div className="section-title">Platform Origins</div>
                    </div>
                    <div style={{ height: 300, marginTop: 20 }}>
                        {platformData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={platformData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={100}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {platformData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: "#111", borderColor: "var(--border)", borderRadius: 8 }}
                                    />
                                    <Legend verticalAlign="bottom" height={36} iconType="circle" />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%", color: "var(--text-muted)" }}>
                                No platform data available
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
