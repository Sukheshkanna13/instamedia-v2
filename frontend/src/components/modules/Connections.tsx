import { useState, useEffect } from "react";
import { api } from "../../lib/api";
import type { BrandDNA } from "../../types";

const PLATFORMS = [
  {
    id: "instagram" as const,
    name: "Instagram",
    icon: "📸",
    color: "var(--coral)",
    description: "Connect to publish posts, stories, and reels automatically",
  },
  {
    id: "linkedin" as const,
    name: "LinkedIn",
    icon: "💼",
    color: "var(--sky)",
    description: "Share professional content and thought leadership posts",
  },
  {
    id: "twitter" as const,
    name: "Twitter / X",
    icon: "✕",
    color: "var(--text)",
    description: "Post tweets and threads with optimal timing",
  },
];

export default function Connections() {
  const [brandDNA, setBrandDNA] = useState<Partial<BrandDNA> | null>(null);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    // Load brand DNA to check connected platforms
    api.getBrandDNA()
      .then(res => setBrandDNA(res.data))
      .catch(() => { })
      .finally(() => setLoading(false));
  }, []);

  const handleConnect = async (platform: string) => {
    setConnecting(platform);
    setError(null);
    try {
      if (!brandDNA) return;
      const current = brandDNA.connected_platforms || [];
      const updated = current.includes(platform)
        ? current.filter(p => p !== platform)
        : [...current, platform];

      const newData = { ...brandDNA, connected_platforms: updated };
      await api.saveBrandDNA(newData);
      setBrandDNA(newData);
      setSuccess(`Successfully ${updated.includes(platform) ? 'connected' : 'disconnected'} ${platform}!`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to update connection");
    } finally {
      setConnecting(null);
    }
  };

  const isConnected = (platform: string) => {
    return brandDNA?.connected_platforms?.includes(platform) ?? false;
  };

  if (loading) {
    return (
      <div className="page-body">
        <div className="empty-state">
          <div className="spinner" style={{ width: 28, height: 28 }} />
        </div>
      </div>
    );
  }

  return (
    <div className="page-body">
      <div>
        <h1 className="display-title">Platform <em>Connections</em></h1>
        <p className="sub-text" style={{ marginTop: 6 }}>
          Connect your social media accounts to enable automated publishing with emotional alignment
        </p>
      </div>

      {success && (
        <div className="alert alert-success">
          ✓ {success}
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          ⚠ {error}
        </div>
      )}

      {/* Connection Status Overview */}
      <div className="card card-sm">
        <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div className={`status-dot ${brandDNA?.connected_platforms?.length ? "" : "offline"}`} />
            <span className="mono-label">
              {brandDNA?.connected_platforms?.length ?? 0} / {PLATFORMS.length} PLATFORMS CONNECTED
            </span>
          </div>
          {brandDNA?.connected_platforms && brandDNA.connected_platforms.length > 0 && (
            <div style={{ display: "flex", gap: 6 }}>
              {brandDNA.connected_platforms.map(p => (
                <span key={p} className="badge badge-emerald">
                  {PLATFORMS.find(pl => pl.id === p)?.icon} {p}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Platform Cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {PLATFORMS.map((platform) => {
          const connected = isConnected(platform.id);
          const isConnecting = connecting === platform.id;

          return (
            <div
              key={platform.id}
              className="card"
              style={{
                borderColor: connected ? platform.color : "var(--border)",
                background: connected
                  ? `linear-gradient(135deg, ${platform.color}08 0%, transparent 100%)`
                  : "var(--s1)",
              }}
            >
              <div style={{ display: "flex", alignItems: "flex-start", gap: 20 }}>
                {/* Platform Icon */}
                <div
                  style={{
                    fontSize: 48,
                    width: 80,
                    height: 80,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: connected ? `${platform.color}15` : "var(--s2)",
                    border: `2px solid ${connected ? platform.color : "var(--border)"}`,
                    borderRadius: "var(--r)",
                  }}
                >
                  {platform.icon}
                </div>

                {/* Platform Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                    <div className="section-title">{platform.name}</div>
                    {connected && (
                      <span className="badge badge-emerald">✓ Connected</span>
                    )}
                  </div>

                  <p style={{ fontSize: 13, color: "var(--text-dim)", lineHeight: 1.6, marginBottom: 16 }}>
                    {platform.description}
                  </p>

                  {connected ? (
                    <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => handleConnect(platform.id)}
                        disabled={isConnecting}
                      >
                        {isConnecting ? "Disconnecting..." : "Disconnect"}
                      </button>
                      <span className="mono-label" style={{ color: "var(--text-muted)" }}>
                        Ready for Web Intent Publishing
                      </span>
                    </div>
                  ) : (
                    <button
                      className="btn btn-primary"
                      onClick={() => handleConnect(platform.id)}
                      disabled={isConnecting}
                      style={{ minWidth: 140 }}
                    >
                      {isConnecting ? (
                        <>
                          <div className="spinner" style={{ borderTopColor: "#000", width: 14, height: 14 }} />
                          Connecting...
                        </>
                      ) : (
                        <>🔗 Connect {platform.name}</>
                      )}
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Connection Notice */}
      <div className="card card-sm" style={{ background: "rgba(0,212,184,0.05)", border: "1px solid rgba(0,212,184,0.15)" }}>
        <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
          <div style={{ fontSize: 20 }}>⚡</div>
          <div style={{ flex: 1 }}>
            <div className="mono-label" style={{ color: "var(--teal)", marginBottom: 4 }}>
              NATIVE WEB INTENT PUBLISHING
            </div>
            <p style={{ fontSize: 12, color: "var(--text-dim)", lineHeight: 1.6 }}>
              You do not need to provide passwords or API tokens! InstaMedia uses "Web Intent" sharing. We generate your content and open your native social app (in a new tab) with your text and images pre-filled so you can confidently hit publish yourself.
            </p>
          </div>
        </div>
      </div>

      {/* Coming Soon Features */}
      <div className="card">
        <div className="card-header">
          <div className="section-title">Coming Soon</div>
          <span className="badge badge-amber">Roadmap</span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[
            { icon: "🤖", label: "Auto-publish on optimal times", desc: "AI analyzes your audience engagement patterns" },
            { icon: "📊", label: "Real-time engagement sync", desc: "Automatically update ESG with post performance" },
            { icon: "🎯", label: "Platform-specific optimization", desc: "Tailor content format per platform" },
          ].map((feature, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                gap: 12,
                padding: "12px 0",
                borderBottom: i < 2 ? "1px solid var(--border)" : "none",
              }}
            >
              <div style={{ fontSize: 20 }}>{feature.icon}</div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>{feature.label}</div>
                <div style={{ fontSize: 11, color: "var(--text-dim)" }}>{feature.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
