"use client";

import { useState } from "react";
import ScoreRing from "@/components/ui/ScoreRing";

interface GeneratedPost {
    post_text: string;
    hashtags: string[];
    image_style_prompt: string;
    cta: string;
    word_count: number;
}

interface AnalysisResult {
    resonance_score: number;
    verdict: string;
    emotional_archetype: string;
    what_works: string;
    what_is_missing: string;
    missing_signals: string[];
    rewrite_suggestion: string;
}

interface AnalyzeResponse {
    success: boolean;
    analysis: AnalysisResult;
    reference_posts: Array<{ text: string; ers: number; semantic_sim: number; platform: string }>;
    processing_time_seconds: number;
    db_size: number;
    banned_words_found: string[];
}

type MediaFormat = "image" | "carousel" | "video";

const VERDICT_LABEL: Record<string, string> = {
    STRONG_MATCH: "Strong Match",
    GOOD_MATCH: "Good Match",
    WEAK_MATCH: "Needs Work",
    MISMATCH: "Misaligned",
};

export default function StudioPage() {
    const [topic, setTopic] = useState("");
    const [platform, setPlatform] = useState("Instagram");
    const [draft, setDraft] = useState("");
    const [generated, setGenerated] = useState<GeneratedPost | null>(null);
    const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
    const [genLoading, setGenLoading] = useState(false);
    const [anaLoading, setAnaLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [copied, setCopied] = useState(false);
    const [imageStyle, setImageStyle] = useState("");
    const [mediaFormat, setMediaFormat] = useState<MediaFormat>("image");
    const [showMediaGenerator, setShowMediaGenerator] = useState(false);
    const [mediaLoading, setMediaLoading] = useState(false);

    const handleGenerate = async () => {
        if (!topic.trim()) return;
        setGenLoading(true);
        setError(null);
        try {
            const res = await fetch("/api/studio/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    idea_title: topic,
                    idea_hook: draft || topic,
                    angle: "storytelling",
                    platform,
                    brand_id: "default",
                }),
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || "Generation failed");
            const post = data.result;
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
            const res = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ draft, brand_id: "default" }),
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || "Analysis failed");
            setAnalysis(data);
        } catch (e) {
            setError((e as Error).message);
        } finally {
            setAnaLoading(false);
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
        window.open(url, "_blank", "noopener");
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
                        <input
                            className="input"
                            placeholder="e.g. 'The mistake that almost ended us'"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                        />
                    </div>
                    <div className="field" style={{ flex: 1, minWidth: 120 }}>
                        <label className="field-label">Platform</label>
                        <select className="select" value={platform} onChange={(e) => setPlatform(e.target.value)}>
                            {["Instagram", "LinkedIn", "Twitter", "TikTok"].map((p) => (
                                <option key={p}>{p}</option>
                            ))}
                        </select>
                    </div>
                    <button className="btn btn-primary" onClick={handleGenerate} disabled={genLoading || !topic.trim()}>
                        {genLoading ? (
                            <>
                                <div className="spinner" style={{ borderTopColor: "#000" }} /> Writing...
                            </>
                        ) : (
                            "✦ Generate Post"
                        )}
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
                                <button
                                    className="btn btn-primary btn-sm"
                                    onClick={handleAnalyze}
                                    disabled={anaLoading || !draft.trim()}
                                >
                                    {anaLoading ? (
                                        <>
                                            <div className="spinner" style={{ borderTopColor: "#000", width: 12, height: 12 }} /> Scoring...
                                        </>
                                    ) : (
                                        "⚡ Score Tone"
                                    )}
                                </button>
                            </div>
                        </div>

                        <textarea
                            className="textarea"
                            rows={8}
                            placeholder="Your post will appear here after generation, or write your own draft..."
                            value={draft}
                            onChange={(e) => setDraft(e.target.value)}
                        />

                        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
                            <span className="mono-label">{draft.length} characters</span>
                            {generated?.hashtags && generated.hashtags.length > 0 && (
                                <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                                    {generated.hashtags.map((h) => (
                                        <span key={h} className="badge badge-sky">
                                            #{h.replace(/^#/, "")}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Image Style Prompt */}
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
                                onChange={(e) => setImageStyle(e.target.value)}
                                placeholder="Describe the image you want to generate..."
                            />
                        </div>
                    )}

                    {/* Media Generator */}
                    <div className="card card-accent-teal">
                        <div className="card-header">
                            <div className="section-title">🎨 Media Generator</div>
                            <button className="copy-btn" onClick={() => setShowMediaGenerator(!showMediaGenerator)}>
                                {showMediaGenerator ? "▼ Hide" : "▶ Show"}
                            </button>
                        </div>
                        {showMediaGenerator && (
                            <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 12 }}>
                                <div>
                                    <div className="mono-label" style={{ marginBottom: 8 }}>Select Format</div>
                                    <div style={{ display: "flex", gap: 8 }}>
                                        {(["image", "carousel", "video"] as MediaFormat[]).map((format) => (
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
                                <div style={{ fontSize: 12, color: "var(--text-dim)", fontStyle: "italic" }}>
                                    {mediaFormat === "image" && "Generate a single high-quality image (1024x1024) for your post"}
                                    {mediaFormat === "carousel" && "Generate 3-5 slides with cohesive visual storytelling"}
                                    {mediaFormat === "video" && "Generate 5-8 keyframe storyboard for video planning"}
                                </div>
                                <button
                                    className="btn btn-primary"
                                    disabled={mediaLoading || !draft.trim()}
                                    style={{ width: "100%" }}
                                    onClick={() => setMediaLoading(false)}
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
                            </div>
                        )}
                    </div>

                    {/* Action */}
                    <div className="card card-sm">
                        <div className="mono-label" style={{ marginBottom: 10 }}>📅 Action</div>
                        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
                            <button className="btn btn-primary" onClick={handlePublish} disabled={!draft.trim()} style={{ flex: 1 }}>
                                🚀 Publish Now
                            </button>
                        </div>
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
                                    Write or generate a draft, then click &quot;Score Tone&quot;
                                    <br />
                                    to see how well it matches your brand&apos;s emotional DNA.
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
                                            <div
                                                style={{
                                                    fontFamily: "var(--font-display)",
                                                    fontSize: 15,
                                                    fontWeight: 700,
                                                    fontStyle: "italic",
                                                    marginBottom: 4,
                                                }}
                                            >
                                                {analysis.analysis.emotional_archetype}
                                            </div>
                                        )}
                                        <div className="mono-label">
                                            {analysis.processing_time_seconds}s · {analysis.db_size} posts in memory
                                        </div>
                                    </div>
                                </div>

                                {bannedFound.length > 0 && (
                                    <div className="alert alert-error" style={{ marginBottom: 12 }}>
                                        ⚠ Banned words detected: {bannedFound.join(", ")}
                                    </div>
                                )}

                                {analysis.analysis?.what_works && (
                                    <div className="insight-block works">
                                        <div className="insight-block-label">✓ What Works</div>
                                        <div className="insight-block-text">{analysis.analysis.what_works}</div>
                                    </div>
                                )}

                                {analysis.analysis?.what_is_missing && (
                                    <div className="insight-block missing">
                                        <div className="insight-block-label">✗ What&apos;s Missing</div>
                                        <div className="insight-block-text">{analysis.analysis.what_is_missing}</div>
                                    </div>
                                )}

                                {missingSignals.length > 0 && (
                                    <div style={{ marginTop: 12 }}>
                                        <div className="mono-label" style={{ marginBottom: 6 }}>Missing Emotional Signals</div>
                                        <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                                            {missingSignals.map((s) => (
                                                <span key={s} className="badge badge-coral">{s}</span>
                                            ))}
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
                                        <button className="copy-btn" onClick={() => setDraft(analysis.analysis.rewrite_suggestion)}>
                                            ↳ Apply rewrite
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Reference posts */}
                            {analysis.reference_posts?.length > 0 && (
                                <div className="card card-sm">
                                    <div className="mono-label" style={{ marginBottom: 10 }}>Reference Posts Used</div>
                                    {analysis.reference_posts.slice(0, 3).map((p, i) => (
                                        <div
                                            key={i}
                                            style={{
                                                display: "flex",
                                                gap: 10,
                                                alignItems: "flex-start",
                                                padding: "10px 0",
                                                borderBottom: i < 2 ? "1px solid var(--border)" : "none",
                                            }}
                                        >
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
