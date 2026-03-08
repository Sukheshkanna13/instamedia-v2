import { useState, useEffect } from "react";
import { api } from "../../lib/api";
import type { AnalyzeResponse, GeneratedPost, ContentIdea, MediaFormat, GeneratedMedia } from "../../types";
import ScoreRing from "../ui/ScoreRing";

const VERDICT_LABEL: Record<string, string> = {
  STRONG_MATCH: "Strong Match",
  GOOD_MATCH: "Good Match",
  WEAK_MATCH: "Needs Work",
  MISMATCH: "Misaligned",
};

interface Props {
  selectedIdea?: ContentIdea | null;
}

export default function CreativeStudio({ selectedIdea }: Props) {
  const [topic, setTopic] = useState(selectedIdea?.title ?? "");
  const [platform, setPlatform] = useState<string>(selectedIdea?.platform ?? "Instagram");
  const [draft, setDraft] = useState("");
  const [generated, setGenerated] = useState<GeneratedPost | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [genLoading, setGenLoading] = useState(false);
  const [anaLoading, setAnaLoading] = useState(false);
  const [scheduled, setScheduled] = useState(false);
  const [schedDate, setSchedDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [imageStyle, setImageStyle] = useState("");

  // Phase 6: Multi-Modal Media Generation
  const [mediaFormat, setMediaFormat] = useState<MediaFormat>("image");
  const [generatedMedia, setGeneratedMedia] = useState<GeneratedMedia | null>(null);
  const [mediaLoading, setMediaLoading] = useState(false);
  const [showMediaGenerator, setShowMediaGenerator] = useState(false);

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
      setImageStyle(post.image_style_prompt ?? "");
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

  const handlePublish = () => {
    if (!draft.trim()) return;
    const text = encodeURIComponent(draft);
    let url = "";

    switch (platform.toLowerCase()) {
      case "twitter":
        url = `https://twitter.com/intent/tweet?text=${text}`;
        break;
      case "linkedin":
        url = `https://www.linkedin.com/feed/?shareActive=true&text=${text}`;
        break;
      case "instagram":
        navigator.clipboard.writeText(draft);
        alert("Post text copied to clipboard! Opening Instagram...");
        url = "https://instagram.com";
        break;
      default:
        url = `https://${platform.toLowerCase()}.com`;
    }

    const newWindow = window.open(url, "_blank");
    if (newWindow) newWindow.opener = null;
  };


  const handleGenerateMedia = async () => {
    if (!draft.trim()) return;
    setMediaLoading(true);
    setError(null);
    try {
      const hashtags = generated?.hashtags ?? [];

      const res = await api.generateMedia({
        caption: draft,
        hashtags,
        format: mediaFormat,
        brand_id: "default",
        image_prompt: imageStyle // Pass the explicitly edited style
      });

      setGeneratedMedia(res.result);

    } catch (e) {
      setError((e as Error).message);
    } finally {
      setMediaLoading(false);
    }
  };

  const score = analysis?.analysis?.resonance_score ?? 0;
  const verdict = analysis?.analysis?.verdict;
  const missingSignals = analysis?.analysis?.missing_signals ?? [];
  const bannedFound = analysis?.banned_words_found ?? [];

  return (
    <div className="page-body">
      <div>
        <h1 className="display-title">Creative <em>Studio</em></h1>
        <p className="sub-text" style={{ marginTop: 6 }}>
          Generate → Edit → Score → Schedule. Left: your content. Right: emotional alignment.
        </p>
      </div>

      {/* Controls row */}
      <div className="card card-sm">
        <div style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
          <div className="field" style={{ flex: 2, minWidth: 200 }}>
            <label className="field-label">Topic / Idea</label>
            <input className="input"
              placeholder="e.g. 'The mistake that almost ended us'"
              value={topic}
              onChange={e => setTopic(e.target.value)}
            />
          </div>
          <div className="field" style={{ flex: 1, minWidth: 120 }}>
            <label className="field-label">Platform</label>
            <select className="select" value={platform} onChange={e => setPlatform(e.target.value)}>
              {["Instagram", "LinkedIn", "Twitter", "TikTok"].map(p => <option key={p}>{p}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={genLoading || !topic.trim()}>
            {genLoading ? <><div className="spinner" style={{ borderTopColor: "#000" }} /> Writing...</>
              : "✦ Generate Post"}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">⚠ {error}</div>}

      {/* Split screen */}
      <div className="studio-split">

        {/* ── LEFT: Editor ── */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

          <div className="card card-accent-teal">
            <div className="card-header">
              <div className="section-title">Post Editor</div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="copy-btn" onClick={handleCopy}>
                  {copied ? "✓ Copied" : "⊕ Copy"}
                </button>
                <button className="btn btn-primary btn-sm" onClick={handleAnalyze}
                  disabled={anaLoading || !draft.trim()}>
                  {anaLoading ? <><div className="spinner" style={{ borderTopColor: "#000", width: 12, height: 12 }} /> Scoring...</>
                    : "⚡ Score Tone"}
                </button>
              </div>
            </div>

            <textarea className="textarea" rows={8}
              placeholder="Your post will appear here after generation, or write your own draft..."
              value={draft}
              onChange={e => setDraft(e.target.value)}
            />

            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
              <span className="mono-label">{draft.length} characters</span>
              {generated?.hashtags && generated.hashtags.length > 0 && (
                <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                  {generated.hashtags.map(h => (
                    <span key={h} className="badge badge-sky">#{h.replace(/^#/, "")}</span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Image Style Prompt - Now Editable */}
          {generated?.image_style_prompt && (
            <div className="card card-sm" style={{ borderColor: "rgba(167,139,250,0.2)" }}>
              <div className="mono-label" style={{ color: "var(--violet)", marginBottom: 6 }}>
                🖼 AI Image Style Brief
              </div>
              <textarea
                className="textarea"
                rows={3}
                style={{ fontSize: 13, background: "rgba(0,0,0,0.2)", borderColor: "rgba(167,139,250,0.1)" }}
                value={imageStyle}
                onChange={e => setImageStyle(e.target.value)}
                placeholder="Describe the image you want to generate..."
              />
            </div>
          )}

          {/* Phase 6: Multi-Modal Media Generator */}
          <div className="card card-accent-teal">
            <div className="card-header">
              <div className="section-title">🎨 Media Generator</div>
              <button
                className="copy-btn"
                onClick={() => setShowMediaGenerator(!showMediaGenerator)}
              >
                {showMediaGenerator ? "▼ Hide" : "▶ Show"}
              </button>
            </div>

            {showMediaGenerator && (
              <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 12 }}>
                {/* Format Selection */}
                <div>
                  <div className="mono-label" style={{ marginBottom: 8 }}>Select Format</div>
                  <div style={{ display: "flex", gap: 8 }}>
                    {(["image", "carousel", "video"] as MediaFormat[]).map(format => (
                      <button
                        key={format}
                        className={`btn ${mediaFormat === format ? "btn-primary" : "btn-ghost"}`}
                        onClick={() => setMediaFormat(format)}
                        disabled={mediaLoading}
                        style={{ flex: 1, textTransform: "capitalize" }}
                      >
                        {format === "image" && "🖼 Image"}
                        {format === "carousel" && "📱 Carousel"}
                        {format === "video" && "🎬 Video"}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Format Description */}
                <div style={{ fontSize: 12, color: "var(--text-dim)", fontStyle: "italic" }}>
                  {mediaFormat === "image" && "Generate a single high-quality image (1024x1024) for your post"}
                  {mediaFormat === "carousel" && "Generate 3-5 slides with cohesive visual storytelling"}
                  {mediaFormat === "video" && "Generate 5-8 keyframe storyboard for video planning"}
                </div>

                {/* Generate Button */}
                <button
                  className="btn btn-primary"
                  onClick={handleGenerateMedia}
                  disabled={mediaLoading || !draft.trim()}
                  style={{ width: "100%" }}
                >
                  {mediaLoading ? (
                    <>
                      <div className="spinner" style={{ borderTopColor: "#000" }} />
                      Generating {mediaFormat}...
                    </>
                  ) : (
                    `✦ Generate ${mediaFormat.charAt(0).toUpperCase() + mediaFormat.slice(1)}`
                  )}
                </button>

                {/* Loading State */}
                {mediaLoading && (
                  <div className="card card-sm" style={{ background: "rgba(20,184,166,0.05)" }}>
                    <div style={{ textAlign: "center", padding: "20px 0" }}>
                      <div className="spinner" style={{ width: 32, height: 32, margin: "0 auto 12px" }} />
                      <div className="mono-label">
                        {mediaFormat === "image" && "Creating image with AWS Bedrock Titan..."}
                        {mediaFormat === "carousel" && "Generating carousel slides..."}
                        {mediaFormat === "video" && "Creating video storyboard..."}
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 6 }}>
                        This may take 10-45 seconds
                      </div>
                    </div>
                  </div>
                )}

                {/* Generated Media Display */}
                {generatedMedia && !mediaLoading && (
                  <div className="fade-up">
                    {/* Single Image */}
                    {generatedMedia.format === "image" && generatedMedia.image_url && (
                      <div className="card card-sm">
                        <div className="mono-label" style={{ marginBottom: 10 }}>
                          Generated Image
                        </div>
                        <img
                          src={generatedMedia.image_url}
                          alt="Generated content"
                          style={{
                            width: "100%",
                            borderRadius: 8,
                            border: "1px solid var(--border)"
                          }}
                        />
                        <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                          <a
                            href={generatedMedia.image_url}
                            download
                            className="btn btn-ghost btn-sm"
                            style={{ flex: 1 }}
                          >
                            ⬇ Download
                          </a>
                          <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => window.open(generatedMedia.image_url, '_blank')}
                            style={{ flex: 1 }}
                          >
                            🔍 View Full
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Carousel */}
                    {generatedMedia.format === "carousel" && generatedMedia.slides && (
                      <div className="card card-sm">
                        <div className="mono-label" style={{ marginBottom: 10 }}>
                          Carousel ({generatedMedia.slides.length} slides)
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                          {generatedMedia.slides.map((slide, idx) => (
                            <div
                              key={idx}
                              style={{
                                padding: 12,
                                border: "1px solid var(--border)",
                                borderRadius: 8,
                                background: "rgba(255,255,255,0.02)"
                              }}
                            >
                              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                                <span className="badge badge-teal">Slide {slide.slide_number}</span>
                                <span style={{ fontWeight: 600, fontSize: 13 }}>{slide.title}</span>
                              </div>
                              <p style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 10 }}>
                                {slide.content}
                              </p>
                              {slide.image_url && (
                                <img
                                  src={slide.image_url}
                                  alt={`Slide ${slide.slide_number}`}
                                  style={{
                                    width: "100%",
                                    aspectRatio: "1/1",
                                    objectFit: "cover",
                                    borderRadius: 6,
                                    border: "1px solid var(--border)",
                                    background: "#000"
                                  }}
                                />
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Video Storyboard */}
                    {generatedMedia.format === "video" && generatedMedia.storyboard && (
                      <div className="card card-sm">
                        <div className="mono-label" style={{ marginBottom: 10 }}>
                          Video Storyboard ({generatedMedia.storyboard.length} scenes)
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                          {generatedMedia.storyboard.map((scene, idx) => (
                            <div
                              key={idx}
                              style={{
                                padding: 12,
                                border: "1px solid var(--border)",
                                borderRadius: 8,
                                background: "rgba(255,255,255,0.02)"
                              }}
                            >
                              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                                <span className="badge badge-violet">Scene {scene.scene_number}</span>
                                <span className="badge badge-sky">{scene.duration}</span>
                              </div>
                              <p style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 10 }}>
                                {scene.description}
                              </p>
                              {scene.image_url && (
                                <img
                                  src={scene.image_url}
                                  alt={`Scene ${scene.scene_number}`}
                                  style={{
                                    width: "100%",
                                    aspectRatio: "16/9",
                                    objectFit: "cover",
                                    borderRadius: 6,
                                    border: "1px solid var(--border)",
                                    background: "#000"
                                  }}
                                />
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Generation Stats */}
                    <div style={{ fontSize: 11, color: "var(--text-dim)", textAlign: "center" }}>
                      Generated in {generatedMedia.generation_time_seconds.toFixed(1)}s
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Schedule */}
          <div className="card card-sm">
            <div className="mono-label" style={{ marginBottom: 10 }}>📅 Action</div>
            <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: 10 }}>
              <button
                className="btn btn-primary"
                onClick={handlePublish}
                disabled={!draft.trim()}
                style={{ flex: 1, minWidth: "140px" }}
              >
                🚀 Publish Now
              </button>
            </div>
            <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
              <input className="input" type="datetime-local" style={{ flex: 1, minWidth: "200px" }}
                value={schedDate}
                onChange={e => setSchedDate(e.target.value)}
              />
              <button className="btn btn-ghost" onClick={handleSchedule}
                disabled={!draft || !schedDate}>
                Schedule Later
              </button>
            </div>
            {scheduled && <div className="alert alert-success" style={{ marginTop: 10 }}>
              ✓ Post added to calendar.
            </div>}
          </div>
        </div>

        {/* ── RIGHT: Emotional Aligner ── */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

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
                <div className="spinner" style={{ width: 28, height: 28, marginBottom: 12 }} />
                <div className="empty-sub">Running emotional analysis...</div>
              </div>
            </div>
          )}

          {analysis && (
            <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 14 }}>

              {/* Score card */}
              <div className="card card-accent-teal">
                <div style={{ display: "flex", alignItems: "center", gap: 20, marginBottom: 16 }}>
                  <ScoreRing score={score} size={100} />
                  <div style={{ flex: 1 }}>
                    <div style={{ marginBottom: 8 }}>
                      <span className={`badge badge-${verdict ?? "teal"}`}>
                        {VERDICT_LABEL[verdict ?? ""] ?? verdict}
                      </span>
                    </div>
                    {analysis.analysis?.emotional_archetype && (
                      <div style={{
                        fontFamily: "var(--font-display)", fontSize: 15, fontWeight: 700,
                        fontStyle: "italic", marginBottom: 4
                      }}>
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
                  <div className="alert alert-error" style={{ marginBottom: 12 }}>
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
                  <div style={{ marginTop: 12 }}>
                    <div className="mono-label" style={{ marginBottom: 6 }}>Missing Emotional Signals</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                      {missingSignals.map(s => <span key={s} className="badge badge-coral">{s}</span>)}
                    </div>
                  </div>
                )}
              </div>

              {/* Rewrite suggestion */}
              {analysis.analysis?.rewrite_suggestion && (
                <div className="card card-sm">
                  <div className="insight-block rewrite" style={{ margin: 0 }}>
                    <div className="insight-block-label">✦ Suggested Rewrite</div>
                    <div className="insight-block-text" style={{ color: "var(--text)", marginBottom: 10 }}>
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
                  <div className="mono-label" style={{ marginBottom: 10 }}>Reference Posts Used</div>
                  {analysis.reference_posts.slice(0, 3).map((p, i) => (
                    <div key={i} style={{
                      display: "flex", gap: 10, alignItems: "flex-start",
                      padding: "10px 0",
                      borderBottom: i < 2 ? "1px solid var(--border)" : "none"
                    }}>
                      <span className="badge badge-teal">ERS {p.ers.toFixed(0)}</span>
                      <span style={{ fontSize: 11, color: "var(--text-dim)", lineHeight: 1.5 }}>
                        {p.text.substring(0, 120)}...
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
