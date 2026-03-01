import { useState, useEffect } from "react";
import { api } from "../../lib/api";

interface DriftEvent {
  timestamp: string;
  drift_magnitude: number;
  emotional_signals_changed: string[];
  acknowledged: boolean;
}

export default function BrandDrift() {
  const [driftEvents, setDriftEvents] = useState<DriftEvent[]>([]);
  const [currentDrift, setCurrentDrift] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [baselineEPM, setBaselineEPM] = useState<number[]>([]);
  const [rollingEPM, setRollingEPM] = useState<number[]>([]);

  useEffect(() => {
    // In production, this would fetch from /api/drift/events
    // For now, simulate with mock data
    setTimeout(() => {
      setCurrentDrift(0.08); // Below 0.15 threshold
      setDriftEvents([
        {
          timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          drift_magnitude: 0.12,
          emotional_signals_changed: ["vulnerability", "authenticity"],
          acknowledged: true,
        },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  const getDriftStatus = (magnitude: number) => {
    if (magnitude < 0.10) return { label: "Stable", color: "var(--emerald)", icon: "✓" };
    if (magnitude < 0.15) return { label: "Minor Drift", color: "var(--amber)", icon: "⚠" };
    return { label: "Significant Drift", color: "var(--coral)", icon: "⚠" };
  };

  const status = getDriftStatus(currentDrift);

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
        <h1 className="display-title">Brand <em>Drift</em> Detection</h1>
        <p className="sub-text" style={{ marginTop: 6 }}>
          Monitor your brand's emotional signature over time and get alerted when it shifts from baseline
        </p>
      </div>

      {/* Current Drift Status */}
      <div className="card card-accent-teal">
        <div className="card-header">
          <div className="section-title">Current Drift Status</div>
          <span className={`badge`} style={{ background: `${status.color}20`, color: status.color, border: `1px solid ${status.color}` }}>
            {status.icon} {status.label}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
          {/* Drift Magnitude Gauge */}
          <div style={{ position: "relative", width: 140, height: 140 }}>
            <svg width="140" height="140" style={{ transform: "rotate(-90deg)" }}>
              {/* Background circle */}
              <circle
                cx="70"
                cy="70"
                r="60"
                fill="none"
                stroke="var(--border)"
                strokeWidth="12"
              />
              {/* Progress circle */}
              <circle
                cx="70"
                cy="70"
                r="60"
                fill="none"
                stroke={status.color}
                strokeWidth="12"
                strokeDasharray={`${(currentDrift / 0.20) * 377} 377`}
                strokeLinecap="round"
                style={{ transition: "stroke-dasharray 0.6s ease" }}
              />
            </svg>
            <div
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: 32,
                  fontWeight: 900,
                  color: status.color,
                  lineHeight: 1,
                }}
              >
                {(currentDrift * 100).toFixed(0)}
              </div>
              <div className="mono-label" style={{ fontSize: 9, marginTop: 4 }}>
                DRIFT SCORE
              </div>
            </div>
          </div>

          {/* Explanation */}
          <div style={{ flex: 1 }}>
            <div style={{ marginBottom: 16 }}>
              <div className="mono-label" style={{ marginBottom: 6 }}>WHAT THIS MEANS</div>
              <p style={{ fontSize: 13, color: "var(--text-dim)", lineHeight: 1.6 }}>
                {currentDrift < 0.10 && "Your brand's emotional signature is stable and consistent with your historical baseline. Keep creating content that resonates!"}
                {currentDrift >= 0.10 && currentDrift < 0.15 && "Your recent content shows minor emotional drift from your baseline. This is normal variation, but monitor it."}
                {currentDrift >= 0.15 && "⚠ Significant drift detected. Your recent content's emotional signature has shifted notably from your brand's baseline. Review your recent posts."}
              </p>
            </div>

            <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
              <div>
                <div className="mono-label" style={{ fontSize: 9, marginBottom: 4 }}>THRESHOLD</div>
                <div style={{ fontFamily: "var(--font-display)", fontSize: 18, fontWeight: 700 }}>
                  0.15
                </div>
              </div>
              <div>
                <div className="mono-label" style={{ fontSize: 9, marginBottom: 4 }}>BASELINE POSTS</div>
                <div style={{ fontFamily: "var(--font-display)", fontSize: 18, fontWeight: 700 }}>
                  50
                </div>
              </div>
              <div>
                <div className="mono-label" style={{ fontSize: 9, marginBottom: 4 }}>ROLLING WINDOW</div>
                <div style={{ fontFamily: "var(--font-display)", fontSize: 18, fontWeight: 700 }}>
                  30 posts
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="card">
        <div className="card-header">
          <div className="section-title">How Brand Drift Detection Works</div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 16 }}>
          {[
            {
              step: "1",
              title: "Baseline EPM",
              desc: "We calculate your Emotional Persona Model from your top 20% highest-performing posts (ERS > 70)",
              icon: "🧬",
            },
            {
              step: "2",
              title: "Rolling EPM",
              desc: "Every day, we calculate a rolling EPM from your most recent 30 published posts",
              icon: "📊",
            },
            {
              step: "3",
              title: "Cosine Distance",
              desc: "We measure the cosine distance between baseline and rolling EPM. Distance > 0.15 triggers an alert",
              icon: "📐",
            },
            {
              step: "4",
              title: "Alert & Recommend",
              desc: "If drift is detected, we show which emotional signals changed and recommend corrective actions",
              icon: "🔔",
            },
          ].map((item) => (
            <div
              key={item.step}
              style={{
                padding: 16,
                background: "var(--s2)",
                border: "1px solid var(--border)",
                borderRadius: "var(--r)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: "50%",
                    background: "var(--teal)",
                    color: "#000",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: "var(--font-display)",
                    fontSize: 14,
                    fontWeight: 900,
                  }}
                >
                  {item.step}
                </div>
                <div style={{ fontSize: 20 }}>{item.icon}</div>
              </div>
              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>{item.title}</div>
              <div style={{ fontSize: 11, color: "var(--text-dim)", lineHeight: 1.5 }}>{item.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Drift History */}
      <div className="card">
        <div className="card-header">
          <div className="section-title">Drift Event History</div>
          <span className="badge badge-teal">{driftEvents.length} events</span>
        </div>

        {driftEvents.length === 0 ? (
          <div className="empty-state" style={{ padding: "32px 0" }}>
            <div className="empty-icon">✓</div>
            <div className="empty-sub">No drift events detected. Your brand voice is stable!</div>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {driftEvents.map((event, i) => {
              const eventStatus = getDriftStatus(event.drift_magnitude);
              return (
                <div
                  key={i}
                  style={{
                    padding: 16,
                    background: event.acknowledged ? "var(--s2)" : `${eventStatus.color}08`,
                    border: `1px solid ${event.acknowledged ? "var(--border)" : eventStatus.color}`,
                    borderRadius: "var(--r)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
                    <div
                      style={{
                        width: 48,
                        height: 48,
                        borderRadius: "var(--r)",
                        background: `${eventStatus.color}20`,
                        border: `2px solid ${eventStatus.color}`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 20,
                        flexShrink: 0,
                      }}
                    >
                      {eventStatus.icon}
                    </div>

                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                        <span
                          className="badge"
                          style={{ background: `${eventStatus.color}20`, color: eventStatus.color, border: `1px solid ${eventStatus.color}` }}
                        >
                          Drift: {(event.drift_magnitude * 100).toFixed(0)}%
                        </span>
                        <span className="mono-label">
                          {new Date(event.timestamp).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          })}
                        </span>
                        {event.acknowledged && <span className="badge badge-emerald">✓ Acknowledged</span>}
                      </div>

                      <div style={{ marginBottom: 10 }}>
                        <div className="mono-label" style={{ fontSize: 9, marginBottom: 4 }}>
                          EMOTIONAL SIGNALS CHANGED
                        </div>
                        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                          {event.emotional_signals_changed.map((signal) => (
                            <span key={signal} className="badge badge-coral">
                              {signal}
                            </span>
                          ))}
                        </div>
                      </div>

                      {!event.acknowledged && (
                        <button className="btn btn-ghost btn-sm">Acknowledge & Set New Baseline</button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Recommendations */}
      <div className="card" style={{ background: "rgba(0,212,184,0.05)", border: "1px solid rgba(0,212,184,0.15)" }}>
        <div className="card-header">
          <div className="section-title">Recommendations</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[
            "Review your last 10 posts and compare them to your top-performing content",
            "Check if recent posts match your Brand DNA tone descriptors",
            "Use the Emotional Aligner to score drafts before publishing",
            "If drift is intentional (brand evolution), acknowledge the event and set a new baseline",
          ].map((rec, i) => (
            <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
              <div style={{ color: "var(--teal)", fontSize: 16, marginTop: 2 }}>→</div>
              <div style={{ fontSize: 13, color: "var(--text-dim)", lineHeight: 1.6 }}>{rec}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
