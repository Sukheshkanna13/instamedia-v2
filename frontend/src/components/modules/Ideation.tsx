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
];

const ANGLE_COLOR: Record<string, string> = {
  Vulnerability:   "var(--coral)",
  Authority:       "var(--teal)",
  Community:       "var(--violet)",
  Aspiration:      "var(--amber)",
  Education:       "var(--sky)",
  Honesty:         "var(--emerald)",
};

const angleColor = (angle: string) =>
  ANGLE_COLOR[angle] ?? "var(--text-dim)";

interface Props {
  onSelectIdea?: (idea: ContentIdea) => void;
}

export default function Ideation({ onSelectIdea }: Props) {
  const [focus,    setFocus]    = useState("General brand storytelling");
  const [custom,   setCustom]   = useState("");
  const [ideas,    setIdeas]    = useState<ContentIdea[]>([]);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState<string|null>(null);
  const [selected, setSelected] = useState<string|null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setIdeas([]);
    try {
      const res = await api.ideate("default", custom || focus);
      setIdeas(res.result?.ideas ?? []);
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

  const ersColor = (s: number) => {
    if (s >= 75) return "var(--emerald)";
    if (s >= 60) return "var(--teal)";
    if (s >= 45) return "var(--amber)";
    return "var(--coral)";
  };

  return (
    <div className="page-body">
      <div>
        <h1 className="display-title">Content <em>Ideation</em></h1>
        <p className="sub-text" style={{ marginTop:6 }}>
          AI generates content ideas conditioned on your Brand DNA + emotional memory
        </p>
      </div>

      {/* Controls */}
      <div className="card">
        <div className="card-header">
          <div className="section-title">What Are We Writing About?</div>
        </div>

        <div className="grid-2" style={{ gap:16, marginBottom:16 }}>
          <div className="field">
            <label className="field-label">Focus Area</label>
            <select className="select" value={focus} onChange={e => setFocus(e.target.value)}>
              {FOCUS_OPTIONS.map(f => <option key={f}>{f}</option>)}
            </select>
          </div>

          <div className="field">
            <label className="field-label">Custom Direction (optional)</label>
            <input className="input"
              placeholder="Or describe what you want to write about..."
              value={custom}
              onChange={e => setCustom(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleGenerate()}
            />
          </div>
        </div>

        <button className="btn btn-primary btn-lg" onClick={handleGenerate} disabled={loading}>
          {loading
            ? <><div className="spinner" style={{borderTopColor:"#000"}} /> Generating ideas...</>
            : <>✦ Generate 5 Ideas</>
          }
        </button>
      </div>

      {error && <div className="alert alert-error">⚠ {error}</div>}

      {/* Idea cards */}
      {ideas.length > 0 && (
        <div>
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:16 }}>
            <div className="section-title">Generated Ideas</div>
            <button className="btn btn-ghost btn-sm" onClick={handleGenerate} disabled={loading}>↺ Regenerate</button>
          </div>

          <div style={{ display:"flex", flexDirection:"column", gap:12 }} className="stagger">
            {ideas.map((idea) => (
              <div
                key={idea.id}
                className={`idea-card ${selected === idea.id ? "selected" : ""}`}
                onClick={() => handleSelect(idea)}
              >
                {/* Predicted ERS watermark */}
                <div className="idea-predicted-ers" style={{ color: ersColor(idea.predicted_ers) }}>
                  {idea.predicted_ers}
                </div>

                <div style={{ display:"flex", alignItems:"flex-start", gap:16 }}>
                  <div style={{ flex:1, minWidth:0 }}>
                    {/* Title + badges */}
                    <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:8, flexWrap:"wrap" }}>
                      <span style={{
                        fontFamily:"var(--font-display)", fontSize:15, fontWeight:700,
                        letterSpacing:"-0.02em"
                      }}>
                        {idea.title}
                      </span>
                      <span className="badge badge-sky">{idea.platform}</span>
                      <span className="badge" style={{
                        background:`rgba(${angleColor(idea.angle).replace(/var\(--/, "").replace(/\)/, "")},0.1)`,
                        border:`1px solid`,
                        color: angleColor(idea.angle)
                      }}>
                        {idea.angle}
                      </span>
                    </div>

                    {/* Hook */}
                    <div style={{
                      fontFamily:"var(--font-display)", fontSize:14, fontStyle:"italic",
                      color:"var(--text-dim)", lineHeight:1.6
                    }}>
                      "{idea.hook}"
                    </div>
                  </div>

                  {/* Predicted ERS display */}
                  <div style={{ flexShrink:0, textAlign:"right" }}>
                    <div style={{
                      fontFamily:"var(--font-display)", fontSize:22, fontWeight:900,
                      color: ersColor(idea.predicted_ers), lineHeight:1
                    }}>{idea.predicted_ers}</div>
                    <div className="mono-label" style={{ fontSize:8, marginTop:2 }}>pred. ERS</div>
                  </div>
                </div>

                {selected === idea.id && (
                  <div style={{
                    marginTop:12, padding:"8px 12px",
                    background:"rgba(0,212,184,0.06)", border:"1px solid rgba(0,212,184,0.15)",
                    borderRadius:"var(--r)", fontFamily:"var(--font-mono)", fontSize:10, color:"var(--teal)"
                  }}>
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
              Choose a focus area and click Generate.<br />
              The AI uses your Brand DNA + ESG memory to<br />
              create ideas that actually match your voice.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
