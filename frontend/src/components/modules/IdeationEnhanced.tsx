import { useState } from "react";
import { api } from "../../lib/api";
import type { ContentIdea } from "../../types";

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

const CONTENT_GOALS = [
  "Drive engagement",
  "Build awareness",
  "Generate leads",
  "Educate audience",
  "Build community",
  "Showcase expertise",
  "Drive conversions",
  "Tell brand story",
];

const TONE_OPTIONS = [
  "Professional",
  "Casual",
  "Inspiring",
  "Educational",
  "Humorous",
  "Empathetic",
  "Bold",
  "Authentic",
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

interface Props {
  onSelectIdea?: (idea: ContentIdea) => void;
}

export default function IdeationEnhanced({ onSelectIdea }: Props) {
  // Form state
  const [step, setStep] = useState(1);
  const [focus, setFocus] = useState("General brand storytelling");
  const [customFocus, setCustomFocus] = useState("");
  const [showCustom, setShowCustom] = useState(false);
  const [targetAudience, setTargetAudience] = useState("");
  const [contentGoal, setContentGoal] = useState("Drive engagement");
  const [tonePreferences, setTonePreferences] = useState<string[]>(["Professional"]);
  const [platforms, setPlatforms] = useState<string[]>(["Instagram"]);
  const [additionalContext, setAdditionalContext] = useState("");

  // Results state
  const [ideas, setIdeas] = useState<ContentIdea[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  const handleFocusChange = (value: string) => {
    setFocus(value);
    setShowCustom(value === "Custom (describe below)");
  };

  const toggleTone = (tone: string) => {
    if (tonePreferences.includes(tone)) {
      setTonePreferences(tonePreferences.filter(t => t !== tone));
    } else {
      setTonePreferences([...tonePreferences, tone]);
    }
  };

  const togglePlatform = (platform: string) => {
    if (platforms.includes(platform)) {
      setPlatforms(platforms.filter(p => p !== platform));
    } else {
      setPlatforms([...platforms, platform]);
    }
  };

  const canProceedToStep2 = () => {
    if (showCustom) {
      return customFocus.length >= 20;
    }
    return true;
  };

  const canGenerate = () => {
    return tonePreferences.length > 0 && platforms.length > 0;
  };

  const handleGenerate = async () => {
    const focusArea = showCustom ? customFocus : focus;

    setLoading(true);
    setError(null);
    setIdeas([]);

    try {
      // Build enhanced context string for the API
      const contextString = `
Focus: ${focusArea}
${targetAudience ? `Target Audience: ${targetAudience}` : ""}
Goal: ${contentGoal}
Tone: ${tonePreferences.join(", ")}
Platforms: ${platforms.join(", ")}
${additionalContext ? `Additional Context: ${additionalContext}` : ""}
      `.trim();

      const res = await api.ideate("default", contextString);
      setIdeas(res.result?.ideas ?? []);
      setStep(3); // Move to results
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (idea: ContentIdea) => {
    setSelected(idea.id);
    onSelectIdea?.(idea);
  };

  const handleReset = () => {
    setStep(1);
    setIdeas([]);
    setSelected(null);
    setError(null);
  };

  const ersColor = (s: number) => {
    if (s >= 75) return "var(--emerald)";
    if (s >= 60) return "var(--teal)";
    if (s >= 45) return "var(--amber)";
    return "var(--coral)";
  };

  return (
    <div className="page-body">
      <div>
        <h1 className="display-title">
          Content <em>Ideation</em>
        </h1>
        <p className="sub-text" style={{ marginTop: 6 }}>
          AI generates personalized content ideas based on your detailed context
        </p>
      </div>

      {/* Progress Indicator */}
      {step < 3 && (
        <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
          {[1, 2].map((s) => (
            <div
              key={s}
              style={{
                flex: 1,
                height: 4,
                background: s <= step ? "var(--teal)" : "var(--border)",
                borderRadius: 2,
                transition: "background 0.3s ease",
              }}
            />
          ))}
        </div>
      )}

      {/* Step 1: Focus Area */}
      {step === 1 && (
        <div className="card">
          <div className="card-header">
            <div className="section-title">Step 1: What Are You Creating?</div>
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
                <span
                  style={{
                    color: "var(--text-muted)",
                    fontWeight: 400,
                    marginLeft: 8,
                  }}
                >
                  (Be specific - min 20 characters)
                </span>
              </label>
              <textarea
                className="input"
                placeholder="Example: Launch of our new eco-friendly product line targeting millennials who care about sustainability and want to make a positive environmental impact..."
                value={customFocus}
                onChange={(e) => setCustomFocus(e.target.value)}
                rows={4}
                style={{
                  resize: "vertical",
                  minHeight: "100px",
                  fontFamily: "var(--font-sans)",
                  lineHeight: 1.6,
                }}
              />
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginTop: 6,
                  fontSize: 11,
                  color:
                    customFocus.length < 20
                      ? "var(--coral)"
                      : customFocus.length > 500
                      ? "var(--amber)"
                      : "var(--text-muted)",
                }}
              >
                <span>
                  {customFocus.length < 20 && "Need at least 20 characters"}
                  {customFocus.length >= 20 &&
                    customFocus.length <= 500 &&
                    "✓ Good detail level"}
                  {customFocus.length > 500 && "Consider being more concise"}
                </span>
                <span>{customFocus.length} / 500</span>
              </div>
            </div>
          )}

          <div style={{ display: "flex", gap: 12 }}>
            <button
              className="btn btn-primary btn-lg"
              onClick={() => setStep(2)}
              disabled={!canProceedToStep2()}
            >
              Next: Add Context →
            </button>
            <button
              className="btn btn-ghost btn-lg"
              onClick={handleGenerate}
              disabled={!canProceedToStep2() || loading}
            >
              {loading ? "Generating..." : "Skip & Generate"}
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Additional Context */}
      {step === 2 && (
        <div className="card">
          <div className="card-header">
            <div className="section-title">Step 2: Add More Context (Optional)</div>
          </div>

          <div className="field" style={{ marginBottom: 16 }}>
            <label className="field-label">Target Audience</label>
            <input
              className="input"
              placeholder="e.g., Millennials interested in sustainability"
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value)}
            />
          </div>

          <div className="field" style={{ marginBottom: 16 }}>
            <label className="field-label">Content Goal</label>
            <select
              className="select"
              value={contentGoal}
              onChange={(e) => setContentGoal(e.target.value)}
            >
              {CONTENT_GOALS.map((g) => (
                <option key={g}>{g}</option>
              ))}
            </select>
          </div>

          <div className="field" style={{ marginBottom: 16 }}>
            <label className="field-label">
              Tone Preferences (select multiple)
            </label>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {TONE_OPTIONS.map((tone) => (
                <button
                  key={tone}
                  onClick={() => toggleTone(tone)}
                  className="badge"
                  style={{
                    cursor: "pointer",
                    background: tonePreferences.includes(tone)
                      ? "var(--teal)"
                      : "var(--bg-dim)",
                    color: tonePreferences.includes(tone)
                      ? "#000"
                      : "var(--text-dim)",
                    border: "1px solid",
                    borderColor: tonePreferences.includes(tone)
                      ? "var(--teal)"
                      : "var(--border)",
                  }}
                >
                  {tone}
                </button>
              ))}
            </div>
          </div>

          <div className="field" style={{ marginBottom: 16 }}>
            <label className="field-label">Platform Priority (select multiple)</label>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {["Instagram", "LinkedIn", "Twitter", "TikTok"].map((platform) => (
                <button
                  key={platform}
                  onClick={() => togglePlatform(platform)}
                  className="badge"
                  style={{
                    cursor: "pointer",
                    background: platforms.includes(platform)
                      ? "var(--violet)"
                      : "var(--bg-dim)",
                    color: platforms.includes(platform) ? "#fff" : "var(--text-dim)",
                    border: "1px solid",
                    borderColor: platforms.includes(platform)
                      ? "var(--violet)"
                      : "var(--border)",
                  }}
                >
                  {platform}
                </button>
              ))}
            </div>
          </div>

          <div className="field" style={{ marginBottom: 16 }}>
            <label className="field-label">
              Additional Context (optional)
            </label>
            <textarea
              className="input"
              placeholder="Any other details that might help generate better ideas..."
              value={additionalContext}
              onChange={(e) => setAdditionalContext(e.target.value)}
              rows={3}
              style={{
                resize: "vertical",
                fontFamily: "var(--font-sans)",
                lineHeight: 1.6,
              }}
            />
          </div>

          <div style={{ display: "flex", gap: 12 }}>
            <button className="btn btn-ghost btn-lg" onClick={() => setStep(1)}>
              ← Back
            </button>
            <button
              className="btn btn-primary btn-lg"
              onClick={handleGenerate}
              disabled={!canGenerate() || loading}
            >
              {loading ? (
                <>
                  <div className="spinner" style={{ borderTopColor: "#000" }} />
                  Generating ideas...
                </>
              ) : (
                <>✦ Generate 5 Ideas</>
              )}
            </button>
          </div>
        </div>
      )}

      {error && <div className="alert alert-error">⚠ {error}</div>}

      {/* Step 3: Results */}
      {step === 3 && ideas.length > 0 && (
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 16,
            }}
          >
            <div className="section-title">Generated Ideas</div>
            <button
              className="btn btn-ghost btn-sm"
              onClick={handleReset}
              disabled={loading}
            >
              ↺ Start Over
            </button>
          </div>

          <div
            style={{ display: "flex", flexDirection: "column", gap: 12 }}
            className="stagger"
          >
            {ideas.map((idea) => (
              <div
                key={idea.id}
                className={`idea-card ${selected === idea.id ? "selected" : ""}`}
                onClick={() => handleSelect(idea)}
              >
                <div
                  className="idea-predicted-ers"
                  style={{ color: ersColor(idea.predicted_ers) }}
                >
                  {idea.predicted_ers}
                </div>

                <div style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        marginBottom: 8,
                        flexWrap: "wrap",
                      }}
                    >
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
                      <span
                        className="badge"
                        style={{
                          background: `rgba(${angleColor(idea.angle)
                            .replace(/var\(--/, "")
                            .replace(/\)/, "")},0.1)`,
                          border: `1px solid`,
                          color: angleColor(idea.angle),
                        }}
                      >
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
                      "{idea.hook}"
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
                    <div
                      className="mono-label"
                      style={{ fontSize: 8, marginTop: 2 }}
                    >
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

      {!loading && ideas.length === 0 && step < 3 && !error && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-icon">✦</div>
            <div className="empty-title">Enhanced Ideation</div>
            <div className="empty-sub">
              Provide detailed context for better, more personalized ideas.
              <br />
              The more context you provide, the better the AI recommendations.
              <br />
              Skip Step 2 for quick generation with basic context.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
