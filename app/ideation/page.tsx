"use client";

import { useState } from "react";

interface ContentIdea {
    id: string;
    title: string;
    hook: string;
    angle: string;
    platform: "Instagram" | "LinkedIn" | "Both";
    predicted_ers: number;
}

const FOCUS_OPTIONS = [
    "General brand storytelling",
    "Founder journey & vulnerability",
    "Product education",
    "Customer success stories",
    "Industry hot takes",
    "Behind-the-scenes",
    "Community celebration",
    "Product launch announcement",
    "Company culture & values",
    "Educational content series",
    "User-generated content",
    "Seasonal campaigns",
    "Event promotion",
    "Partnership announcement",
    "Thought leadership",
    "Custom (describe below)",
];

const ANGLE_COLOR: Record<string, string> = {
    Vulnerability: "var(--coral)",
    Authority: "var(--teal)",
    Community: "var(--violet)",
    Aspiration: "var(--amber)",
    Education: "var(--sky)",
    Honesty: "var(--emerald)",
};

const angleColor = (angle: string) => ANGLE_COLOR[angle] ?? "var(--text-dim)";

const ersColor = (s: number) => {
    if (s >= 75) return "var(--emerald)";
    if (s >= 60) return "var(--teal)";
    if (s >= 45) return "var(--amber)";
    return "var(--coral)";
};

export default function IdeationPage() {
    const [focus, setFocus] = useState("General brand storytelling");
    const [custom, setCustom] = useState("");
    const [showCustom, setShowCustom] = useState(false);
    const [ideas, setIdeas] = useState<ContentIdea[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selected, setSelected] = useState<string | null>(null);

    const handleFocusChange = (value: string) => {
        setFocus(value);
        setShowCustom(value === "Custom (describe below)");
    };

    const handleGenerate = async () => {
        const focusArea = showCustom ? custom : focus;

        if (showCustom && !custom.trim()) {
            setError("Please describe your custom focus area");
            return;
        }

        if (showCustom && custom.length < 20) {
            setError("Please provide more detail (at least 20 characters)");
            return;
        }

        setLoading(true);
        setError(null);
        setIdeas([]);
        try {
            const res = await fetch("/api/ideate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ brand_id: "default", focus_area: focusArea }),
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || "Ideation failed");
            setIdeas(data.result?.ideas ?? []);
        } catch (e) {
            setError((e as Error).message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-body">
            <div>
                <h1 className="display-title">
                    Content <em>Ideation</em>
                </h1>
                <p className="sub-text" style={{ marginTop: 6 }}>
                    AI generates content ideas conditioned on your Brand DNA + emotional memory
                </p>
            </div>

            {/* Controls */}
            <div className="card">
                <div className="card-header">
                    <div className="section-title">What Are We Writing About?</div>
                </div>

                <div className="field" style={{ marginBottom: 16 }}>
                    <label className="field-label">Focus Area</label>
                    <select
                        className="select"
                        value={focus}
                        onChange={(e) => handleFocusChange(e.target.value)}
                    >
                        {FOCUS_OPTIONS.map((f) => (
                            <option key={f}>{f}</option>
                        ))}
                    </select>
                </div>

                {showCustom && (
                    <div className="field" style={{ marginBottom: 16 }}>
                        <label className="field-label">
                            Describe Your Custom Focus Area
                            <span style={{ color: "var(--text-muted)", fontWeight: 400, marginLeft: 8 }}>
                                (Be specific - min 20 characters)
                            </span>
                        </label>
                        <textarea
                            className="input"
                            placeholder="Example: Launch of our new eco-friendly product line targeting millennials..."
                            value={custom}
                            onChange={(e) => setCustom(e.target.value)}
                            rows={4}
                            style={{ resize: "vertical", minHeight: "100px", fontFamily: "var(--font-sans)", lineHeight: 1.6 }}
                        />
                        <div
                            style={{
                                display: "flex",
                                justifyContent: "space-between",
                                marginTop: 6,
                                fontSize: 11,
                                color: custom.length < 20 ? "var(--coral)" : custom.length > 500 ? "var(--amber)" : "var(--text-muted)",
                            }}
                        >
                            <span>
                                {custom.length < 20 && "Need at least 20 characters"}
                                {custom.length >= 20 && custom.length <= 500 && "✓ Good detail level"}
                                {custom.length > 500 && "Consider being more concise"}
                            </span>
                            <span>{custom.length} / 500</span>
                        </div>
                    </div>
                )}

                {!showCustom && (
                    <div
                        style={{
                            padding: 12,
                            background: "rgba(0,212,184,0.05)",
                            border: "1px solid rgba(0,212,184,0.1)",
                            borderRadius: "var(--r)",
                            marginBottom: 16,
                        }}
                    >
                        <div style={{ fontSize: 12, color: "var(--text-dim)", lineHeight: 1.6 }}>
                            💡 <strong>Tip:</strong> Select &quot;Custom (describe below)&quot; for more specific
                            content ideas tailored to your exact needs.
                        </div>
                    </div>
                )}

                <button className="btn btn-primary btn-lg" onClick={handleGenerate} disabled={loading}>
                    {loading ? (
                        <>
                            <div className="spinner" style={{ borderTopColor: "#000" }} /> Generating ideas...
                        </>
                    ) : (
                        <>✦ Generate 5 Ideas</>
                    )}
                </button>
            </div>

            {error && <div className="alert alert-error">⚠ {error}</div>}

            {/* Idea cards */}
            {ideas.length > 0 && (
                <div>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                        <div className="section-title">Generated Ideas</div>
                        <button className="btn btn-ghost btn-sm" onClick={handleGenerate} disabled={loading}>
                            ↺ Regenerate
                        </button>
                    </div>

                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }} className="stagger">
                        {ideas.map((idea) => (
                            <div
                                key={idea.id}
                                className={`idea-card ${selected === idea.id ? "selected" : ""}`}
                                onClick={() => {
                                    setSelected(idea.id);
                                }}
                            >
                                <div className="idea-predicted-ers" style={{ color: ersColor(idea.predicted_ers) }}>
                                    {idea.predicted_ers}
                                </div>

                                <div style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
                                            <span
                                                style={{
                                                    fontFamily: "var(--font-display)",
                                                    fontSize: 15,
                                                    fontWeight: 700,
                                                    letterSpacing: "-0.02em",
                                                }}
                                            >
                                                {idea.title}
                                            </span>
                                            <span className="badge badge-sky">{idea.platform}</span>
                                            <span className="badge" style={{ color: angleColor(idea.angle) }}>
                                                {idea.angle}
                                            </span>
                                        </div>

                                        <div
                                            style={{
                                                fontFamily: "var(--font-display)",
                                                fontSize: 14,
                                                fontStyle: "italic",
                                                color: "var(--text-dim)",
                                                lineHeight: 1.6,
                                            }}
                                        >
                                            &quot;{idea.hook}&quot;
                                        </div>
                                    </div>

                                    <div style={{ flexShrink: 0, textAlign: "right" }}>
                                        <div
                                            style={{
                                                fontFamily: "var(--font-display)",
                                                fontSize: 22,
                                                fontWeight: 900,
                                                color: ersColor(idea.predicted_ers),
                                                lineHeight: 1,
                                            }}
                                        >
                                            {idea.predicted_ers}
                                        </div>
                                        <div className="mono-label" style={{ fontSize: 8, marginTop: 2 }}>
                                            pred. ERS
                                        </div>
                                    </div>
                                </div>

                                {selected === idea.id && (
                                    <div
                                        style={{
                                            marginTop: 12,
                                            padding: "8px 12px",
                                            background: "rgba(0,212,184,0.06)",
                                            border: "1px solid rgba(0,212,184,0.15)",
                                            borderRadius: "var(--r)",
                                            fontFamily: "var(--font-mono)",
                                            fontSize: 10,
                                            color: "var(--teal)",
                                        }}
                                    >
                                        ✓ Selected — go to Creative Studio to generate the full post
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {!loading && ideas.length === 0 && !error && (
                <div className="card">
                    <div className="empty-state">
                        <div className="empty-icon">✦</div>
                        <div className="empty-title">Ideas on Demand</div>
                        <div className="empty-sub">
                            Choose a focus area and click Generate.
                            <br />
                            The AI uses your Brand DNA + ESG memory to
                            <br />
                            create ideas that actually match your voice.
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
