"use client";

import { useState, useEffect } from "react";

interface DashboardStats {
  total_content: number;
  scheduled: number;
  published: number;
  avg_resonance_score: number;
  db_post_count: number;
}

export default function OverviewPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [healthRes, statsRes] = await Promise.allSettled([
          fetch("/api/health").then((r) => r.json()),
          fetch("/api/posts?brand_id=default").then((r) => r.json()),
        ]);

        if (healthRes.status === "fulfilled") setHealth(healthRes.value);
        if (statsRes.status === "fulfilled") {
          const posts = statsRes.value.posts ?? [];
          setStats({
            total_content: posts.length,
            scheduled: posts.filter(
              (p: Record<string, string>) => p.status === "scheduled"
            ).length,
            published: posts.filter(
              (p: Record<string, string>) => p.status === "published"
            ).length,
            avg_resonance_score: 0,
            db_post_count: 0,
          });
        }
      } catch {
        // Silent fail on dashboard
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return (
    <div className="page-body">
      <div>
        <h1 className="display-title">
          Dashboard <em>Overview</em>
        </h1>
        <p className="sub-text" style={{ marginTop: 6 }}>
          Your brand&apos;s content intelligence at a glance. Powered by
          LangGraph AI agents.
        </p>
      </div>

      {/* Status banner */}
      {health && (
        <div
          className="alert alert-success"
          style={{ display: "flex", gap: 16, alignItems: "center" }}
        >
          <span>✅ System Online</span>
          <span className="mono-label">
            Engine: {String(health.ai_engine)} · LLM:{" "}
            {String(health.llm_provider)} · DB:{" "}
            {health.supabase_connected ? "Connected" : "Offline"}
          </span>
        </div>
      )}

      {/* Metric cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
          gap: 16,
        }}
      >
        <MetricCard
          label="Total Content"
          value={stats?.total_content ?? 0}
          icon="📝"
          loading={loading}
        />
        <MetricCard
          label="Scheduled"
          value={stats?.scheduled ?? 0}
          icon="📅"
          loading={loading}
        />
        <MetricCard
          label="Published"
          value={stats?.published ?? 0}
          icon="🚀"
          loading={loading}
        />
        <MetricCard
          label="Posts in Memory"
          value={
            health
              ? Number(health.posts_in_db ?? 0)
              : 0
          }
          icon="🧠"
          loading={loading}
        />
      </div>

      {/* Quick actions */}
      <div className="card">
        <div className="section-title" style={{ marginBottom: 14 }}>
          Quick Actions
        </div>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <a href="/ideation" className="btn btn-primary">
            💡 Generate Ideas
          </a>
          <a href="/studio" className="btn btn-ghost">
            ✦ Open Studio
          </a>
          <a href="/brand-dna" className="btn btn-ghost">
            🧬 Configure Brand DNA
          </a>
          <a href="/calendar" className="btn btn-ghost">
            📅 View Calendar
          </a>
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  icon,
  loading,
}: {
  label: string;
  value: number;
  icon: string;
  loading: boolean;
}) {
  return (
    <div className="card card-sm">
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          marginBottom: 8,
        }}
      >
        <span style={{ fontSize: 20 }}>{icon}</span>
        <span className="mono-label">{label}</span>
      </div>
      <div
        style={{
          fontSize: 32,
          fontWeight: 700,
          fontFamily: "var(--font-display)",
        }}
      >
        {loading ? (
          <div className="spinner" style={{ width: 20, height: 20 }} />
        ) : (
          value
        )}
      </div>
    </div>
  );
}
