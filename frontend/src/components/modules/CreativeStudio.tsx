import { useState, useEffect } from "react";
import { api } from "../../lib/api";
import type { AnalyzeResponse, GeneratedPost, ContentIdea } from "../../types";
import ScoreRing from "../ui/ScoreRing";

const VERDICT_LABEL: Record<string, string> = {
  STRONG_MATCH: "Strong Match",
  GOOD_MATCH:   "Good Match",
  WEAK_MATCH:   "Needs Work",
  MISMATCH:     "Misaligned",
};

interface Props {
  selectedIdea?: ContentIdea | null;
}

export default function CreativeStudio({ selectedIdea }: Props) {
  const [topic,     setTopic]     = useState(selectedIdea?.title ?? "");
  const [platform,  setPlatform]  = useState<string>(selectedIdea?.platform ?? "Instagram");
  const [draft,     setDraft]     = useState("");
  const [generated, setGenerated] = useState<GeneratedPost | null>(null);
  const [analysis,  setAnalysis]  = useState<AnalyzeResponse | null>(null);
  const [genLoading,setGenLoading]= useState(false);
  const [anaLoading,setAnaLoading]= useState(false);
  const [scheduled, setScheduled] = useState(false);
  const [schedDate, setSchedDate] = useState("");
  const [error,     setError]     = useState<string|null>(null);
  const [copied,    setCopied]    = useState(false);

  // When parent passes in a selected idea, pre-fill
  useEffect(() => {
    if (selectedIdea) {
      setTopic(selectedIdea.title);
      setPlatform(selectedIdea.platform === "Both" ? "Instagram" : selectedIdea.platform);
      setDraft(selectedIdea.hook);
    }
  }, [selectedIdea]);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setGenLoading(true);
    setError(null);
    try {
      const res = await api.studioGenerate({
        idea_title: topic,
        idea_hook: draft || topic,
        angle: selectedIdea?.angle ?? "storytelling",
        platform,
        brand_id: "default",
      });
      const post = res.result;
      setGenerated(post);
      setDraft(post.post_text ?? "");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setGenLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!draft.trim() || draft.length < 10) return;
    setAnaLoading(true);
    setError(null);
    try {
      const res = await api.analyze(draft, "default");
      setAnalysis(res);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setAnaLoading(false);
    }
  };

  const handleSchedule = async () => {
    if (!draft || !schedDate) return;
    try {
      await api.schedulePost({
        content: draft,
        platform: platform.toLowerCase() as "instagram",
        scheduled_time: schedDate,
        brand_id: "default",
        resonance_score: analysis?.analysis?.resonance_score ?? 0,
        image_style: generated?.image_style_prompt ?? "",
        hashtags: generated?.hashtags ?? [],
        status: "scheduled",
      });
      setScheduled(true);
      setTimeout(() => setScheduled(false), 4000);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(draft);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const score = analysis?.analysis?.resonance_score ?? 0;
  const verdict = analysis?.analysis?.verdict;
  const missingSignals = analysis?.analysis?.missing_signals ?? [];
  const bannedFound = analysis?.banned_words_found ?? [];

  return (
    <div className="page-body">
      <div>
        <h1 className="display-title">Creative <em>Studio</em></h1>
        <p className="sub-text" style={{ marginTop:6 }}>
          Generate → Edit → Score → Schedule. Left: your content. Right: emotional alignment.
        </p>
      </div>

      {/* Controls row */}
      <div className="card card-sm">
        <div style={{ display:"flex", gap:12, alignItems:"flex-end", flexWrap:"wrap" }}>
          <div className="field" style={{ flex:2, minWidth:200 }}>
            <label className="field-label">Topic / Idea</label>
            <input className="input"
              placeholder="e.g. 'The mistake that almost ended us'"
              value={topic}
              onChange={e => setTopic(e.target.value)}
            />
          </div>
          <div className="field" style={{ flex:1, minWidth:120 }}>
            <label className="field-label">Platform</label>
            <select className="select" value={platform} onChange={e => setPlatform(e.target.value)}>
              {["Instagram","LinkedIn","Twitter","TikTok"].map(p => <option key={p}>{p}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={genLoading || !topic.trim()}>
            {genLoading ? <><div className="spinner" style={{borderTopColor:"#000"}} /> Writing...</>
                       : "✦ Generate Post"}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">⚠ {error}</div>}

      {/* Split screen */}
      <div className="studio-split">

        {/* ── LEFT: Editor ── */}
        <div style={{ display:"flex", flexDirection:"column", gap:16 }}>

          <div className="card card-accent-teal">
            <div className="card-header">
              <div className="section-title">Post Editor</div>
              <div style={{ display:"flex", gap:8 }}>
                <button className="copy-btn" onClick={handleCopy}>
                  {copied ? "✓ Copied" : "⊕ Copy"}
                </button>
                <button className="btn btn-primary btn-sm" onClick={handleAnalyze}
                  disabled={anaLoading || !draft.trim()}>
                  {anaLoading ? <><div className="spinner" style={{borderTopColor:"#000",width:12,height:12}} /> Scoring...</>
                              : "⚡ Score Tone"}
                </button>
              </div>
            </div>

            <textarea className="textarea" rows={8}
              placeholder="Your post will appear here after generation, or write your own draft..."
              value={draft}
              onChange={e => setDraft(e.target.value)}
            />

            <div style={{ display:"flex", justifyContent:"space-between", marginTop:8 }}>
              <span className="mono-label">{draft.length} characters</span>
              {generated?.hashtags && generated.hashtags.length > 0 && (
                <div style={{ display:"flex", gap:4, flexWrap:"wrap" }}>
                  {generated.hashtags.map(h => (
                    <span key={h} className="badge badge-sky">#{h.replace(/^#/,"")}</span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Image Style Prompt */}
          {generated?.image_style_prompt && (
            <div className="card card-sm" style={{ borderColor:"rgba(167,139,250,0.2)" }}>
              <div className="mono-label" style={{ color:"var(--violet)", marginBottom:6 }}>
                🖼 AI Image Style Brief
              </div>
              <p style={{ fontSize:13, color:"var(--text-dim)", lineHeight:1.6, fontStyle:"italic" }}>
                "{generated.image_style_prompt}"
              </p>
            </div>
          )}

          {/* Schedule */}
          <div className="card card-sm">
            <div className="mono-label" style={{ marginBottom:10 }}>📅 Schedule Post</div>
            <div style={{ display:"flex", gap:10, alignItems:"center" }}>
              <input className="input" type="datetime-local" style={{ flex:1 }}
                value={schedDate}
                onChange={e => setSchedDate(e.target.value)}
              />
              <button className="btn btn-ghost" onClick={handleSchedule}
                disabled={!draft || !schedDate}>
                Schedule
              </button>
            </div>
            {scheduled && <div className="alert alert-success" style={{ marginTop:10 }}>
              ✓ Post added to calendar.
            </div>}
          </div>
        </div>

        {/* ── RIGHT: Emotional Aligner ── */}
        <div style={{ display:"flex", flexDirection:"column", gap:16 }}>

          {!analysis && !anaLoading && (
            <div className="card">
              <div className="empty-state">
                <div className="empty-icon">⚡</div>
                <div className="empty-title">Emotional Aligner</div>
                <div className="empty-sub">
                  Write or generate a draft, then click "Score Tone"<br />
                  to see how well it matches your brand's emotional DNA.
                </div>
              </div>
            </div>
          )}

          {anaLoading && (
            <div className="card">
              <div className="empty-state">
                <div className="spinner" style={{ width:28, height:28, marginBottom:12 }} />
                <div className="empty-sub">Running emotional analysis...</div>
              </div>
            </div>
          )}

          {analysis && (
            <div className="fade-up" style={{ display:"flex", flexDirection:"column", gap:14 }}>

              {/* Score card */}
              <div className="card card-accent-teal">
                <div style={{ display:"flex", alignItems:"center", gap:20, marginBottom:16 }}>
                  <ScoreRing score={score} size={100} />
                  <div style={{ flex:1 }}>
                    <div style={{ marginBottom:8 }}>
                      <span className={`badge badge-${verdict ?? "teal"}`}>
                        {VERDICT_LABEL[verdict ?? ""] ?? verdict}
                      </span>
                    </div>
                    {analysis.analysis?.emotional_archetype && (
                      <div style={{ fontFamily:"var(--font-display)", fontSize:15, fontWeight:700,
                        fontStyle:"italic", marginBottom:4 }}>
                        {analysis.analysis.emotional_archetype}
                      </div>
                    )}
                    <div className="mono-label">
                      {analysis.processing_time_seconds}s · {analysis.db_size} posts in memory
                    </div>
                  </div>
                </div>

                {/* Banned words alert */}
                {bannedFound.length > 0 && (
                  <div className="alert alert-error" style={{ marginBottom:12 }}>
                    ⚠ Banned words detected: {bannedFound.join(", ")}
                  </div>
                )}

                {/* Insights */}
                {analysis.analysis?.what_works && (
                  <div className="insight-block works">
                    <div className="insight-block-label">✓ What Works</div>
                    <div className="insight-block-text">{analysis.analysis.what_works}</div>
                  </div>
                )}

                {analysis.analysis?.what_is_missing && (
                  <div className="insight-block missing">
                    <div className="insight-block-label">✗ What's Missing</div>
                    <div className="insight-block-text">{analysis.analysis.what_is_missing}</div>
                  </div>
                )}

                {/* Missing signals */}
                {missingSignals.length > 0 && (
                  <div style={{ marginTop:12 }}>
                    <div className="mono-label" style={{ marginBottom:6 }}>Missing Emotional Signals</div>
                    <div style={{ display:"flex", flexWrap:"wrap", gap:5 }}>
                      {missingSignals.map(s => <span key={s} className="badge badge-coral">{s}</span>)}
                    </div>
                  </div>
                )}
              </div>

              {/* Rewrite suggestion */}
              {analysis.analysis?.rewrite_suggestion && (
                <div className="card card-sm">
                  <div className="insight-block rewrite" style={{ margin:0 }}>
                    <div className="insight-block-label">✦ Suggested Rewrite</div>
                    <div className="insight-block-text" style={{ color:"var(--text)", marginBottom:10 }}>
                      {analysis.analysis.rewrite_suggestion}
                    </div>
                    <button className="copy-btn" onClick={() => {
                      setDraft(analysis.analysis.rewrite_suggestion);
                    }}>↳ Apply rewrite</button>
                  </div>
                </div>
              )}

              {/* Reference posts */}
              {analysis.reference_posts?.length > 0 && (
                <div className="card card-sm">
                  <div className="mono-label" style={{ marginBottom:10 }}>Reference Posts Used</div>
                  {analysis.reference_posts.slice(0,3).map((p, i) => (
                    <div key={i} style={{
                      display:"flex", gap:10, alignItems:"flex-start",
                      padding:"10px 0",
                      borderBottom: i < 2 ? "1px solid var(--border)" : "none"
                    }}>
                      <span className="badge badge-teal">ERS {p.ers.toFixed(0)}</span>
                      <span style={{ fontSize:11, color:"var(--text-dim)", lineHeight:1.5 }}>
                        {p.text.substring(0,120)}...
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
