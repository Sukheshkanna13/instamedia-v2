"use client";

import { useState, useEffect } from "react";

// Safely parse a value that may be a JSON string, an array, or undefined
// Handles double-encoded strings from Supabase
function safeArray(val: unknown): string[] {
    if (Array.isArray(val)) return val;
    if (typeof val === "string") {
        try {
            // Parse once
            let parsed = JSON.parse(val);
            // If it's still a string (double encoded), parse again
            while (typeof parsed === "string") {
                parsed = JSON.parse(parsed);
            }
            if (Array.isArray(parsed)) return parsed;
        } catch {
            return [];
        }
    }
    return [];
}

interface BrandDNA {
    brand_id: string;
    brand_name: string;
    mission: string;
    tone_descriptors: string[];
    hex_colors: string[];
    banned_words: string[];
    typography: string;
    logo_url: string;
}

const DEFAULT_DNA: BrandDNA = {
    brand_id: "default",
    brand_name: "",
    mission: "",
    tone_descriptors: [],
    hex_colors: [],
    banned_words: [],
    typography: "",
    logo_url: "",
};

const TONE_PRESETS = [
    "Bold", "Empathetic", "Direct", "Witty", "Professional",
    "Inspirational", "Playful", "Authoritative", "Raw", "Warm",
    "Conversational", "Minimalist",
];

export default function BrandDNAPage() {
    const [dna, setDna] = useState<BrandDNA>(DEFAULT_DNA);
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const [loading, setLoading] = useState(true);

    // Editable field temps
    const [newTone, setNewTone] = useState("");
    const [newColor, setNewColor] = useState("#00D4B8");
    const [newBanned, setNewBanned] = useState("");

    useEffect(() => {
        async function fetchDNA() {
            try {
                const res = await fetch("/api/brand-dna?brand_id=default");
                const data = await res.json();
                if (data.success && data.data?.brand_name) {
                    const d = data.data;
                    setDna({
                        brand_id: d.brand_id ?? "default",
                        brand_name: d.brand_name ?? "",
                        mission: d.mission ?? "",
                        tone_descriptors: safeArray(d.tone_descriptors),
                        hex_colors: safeArray(d.hex_colors),
                        banned_words: safeArray(d.banned_words),
                        typography: d.typography ?? "",
                        logo_url: d.logo_url ?? "",
                    });
                }
            } catch {
                // Use defaults
            } finally {
                setLoading(false);
            }
        }
        fetchDNA();
    }, []);

    const handleSave = async () => {
        setSaving(true);
        setSaved(false);
        try {
            const res = await fetch("/api/brand-dna", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dna),
            });
            const data = await res.json();
            if (data.success) {
                setSaved(true);
                setTimeout(() => setSaved(false), 3000);
            }
        } catch {
            // Handle silently
        } finally {
            setSaving(false);
        }
    };

    const addTone = (tone: string) => {
        if (tone && !dna.tone_descriptors.includes(tone)) {
            setDna({ ...dna, tone_descriptors: [...dna.tone_descriptors, tone] });
        }
        setNewTone("");
    };

    const removeTone = (tone: string) => {
        setDna({ ...dna, tone_descriptors: dna.tone_descriptors.filter((t) => t !== tone) });
    };

    const addColor = () => {
        if (newColor && !dna.hex_colors.includes(newColor)) {
            setDna({ ...dna, hex_colors: [...dna.hex_colors, newColor] });
        }
    };

    const removeColor = (c: string) => {
        setDna({ ...dna, hex_colors: dna.hex_colors.filter((x) => x !== c) });
    };

    const addBanned = () => {
        if (newBanned.trim() && !dna.banned_words.includes(newBanned.trim())) {
            setDna({ ...dna, banned_words: [...dna.banned_words, newBanned.trim()] });
        }
        setNewBanned("");
    };

    const removeBanned = (w: string) => {
        setDna({ ...dna, banned_words: dna.banned_words.filter((x) => x !== w) });
    };

    if (loading) {
        return (
            <div className="page-body">
                <div className="card"><div className="empty-state"><div className="spinner" style={{ width: 24, height: 24 }} /></div></div>
            </div>
        );
    }

    return (
        <div className="page-body">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                    <h1 className="display-title">Brand <em>DNA Vault</em></h1>
                    <p className="sub-text" style={{ marginTop: 6 }}>
                        Define your brand identity. Every AI-generated post is filtered through this DNA.
                    </p>
                </div>
                <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                    {saving ? <><div className="spinner" style={{ borderTopColor: "#000" }} /> Saving...</> :
                        saved ? "✓ Saved!" : "💾 Save DNA"}
                </button>
            </div>

            {/* Brand Name & Mission */}
            <div className="card card-accent-teal">
                <div className="section-title" style={{ marginBottom: 14 }}>Identity</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 14 }}>
                    <div className="field">
                        <label className="field-label">Brand Name</label>
                        <input className="input" placeholder="Your brand name" value={dna.brand_name}
                            onChange={(e) => setDna({ ...dna, brand_name: e.target.value })} />
                    </div>
                    <div className="field">
                        <label className="field-label">Typography / Font</label>
                        <input className="input" placeholder="e.g. Inter, Poppins" value={dna.typography}
                            onChange={(e) => setDna({ ...dna, typography: e.target.value })} />
                    </div>
                </div>
                <div className="field">
                    <label className="field-label">Mission Statement</label>
                    <textarea className="textarea" rows={3} placeholder="What is your brand's mission?"
                        value={dna.mission} onChange={(e) => setDna({ ...dna, mission: e.target.value })} />
                </div>
            </div>

            {/* Tone Descriptors */}
            <div className="card">
                <div className="section-title" style={{ marginBottom: 14 }}>🎙 Tone Descriptors</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
                    {TONE_PRESETS.map((t) => (
                        <button key={t}
                            className={`badge ${dna.tone_descriptors.includes(t) ? "badge-teal" : ""}`}
                            style={{ cursor: "pointer" }}
                            onClick={() => dna.tone_descriptors.includes(t) ? removeTone(t) : addTone(t)}
                        >
                            {dna.tone_descriptors.includes(t) && "✓ "}{t}
                        </button>
                    ))}
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                    <input className="input" placeholder="Add custom tone..." value={newTone}
                        onChange={(e) => setNewTone(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && addTone(newTone)} />
                    <button className="btn btn-ghost" onClick={() => addTone(newTone)}>Add</button>
                </div>
                {dna.tone_descriptors.length > 0 && (
                    <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 6 }}>
                        {dna.tone_descriptors.map((t) => (
                            <span key={t} className="badge badge-teal" onClick={() => removeTone(t)} style={{ cursor: "pointer" }}>
                                {t} ×
                            </span>
                        ))}
                    </div>
                )}
            </div>

            {/* Brand Colors */}
            <div className="card">
                <div className="section-title" style={{ marginBottom: 14 }}>🎨 Brand Colors</div>
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12 }}>
                    <input type="color" value={newColor} onChange={(e) => setNewColor(e.target.value)}
                        style={{ width: 48, height: 36, padding: 2, background: "transparent", border: "1px solid var(--border)", borderRadius: "var(--r)" }} />
                    <input className="input" placeholder="#00D4B8" value={newColor}
                        onChange={(e) => setNewColor(e.target.value)} style={{ width: 120 }} />
                    <button className="btn btn-ghost" onClick={addColor}>Add Color</button>
                </div>
                {dna.hex_colors.length > 0 && (
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                        {dna.hex_colors.map((c) => (
                            <div key={c} onClick={() => removeColor(c)} style={{
                                width: 48, height: 48, borderRadius: 12, background: c,
                                border: "2px solid rgba(255,255,255,0.1)", cursor: "pointer",
                                display: "flex", alignItems: "flex-end", justifyContent: "center", paddingBottom: 2,
                            }}>
                                <span style={{ fontSize: 8, color: "#fff", textShadow: "0 1px 3px rgba(0,0,0,0.8)" }}>
                                    {c}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Banned Words */}
            <div className="card">
                <div className="section-title" style={{ marginBottom: 14 }}>🚫 Banned Words</div>
                <p style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 10 }}>
                    Words that should never appear in generated content.
                </p>
                <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                    <input className="input" placeholder="Add banned word..." value={newBanned}
                        onChange={(e) => setNewBanned(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && addBanned()} />
                    <button className="btn btn-ghost" onClick={addBanned}>Add</button>
                </div>
                {dna.banned_words.length > 0 && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                        {dna.banned_words.map((w) => (
                            <span key={w} className="badge badge-coral" onClick={() => removeBanned(w)} style={{ cursor: "pointer" }}>
                                {w} ×
                            </span>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
