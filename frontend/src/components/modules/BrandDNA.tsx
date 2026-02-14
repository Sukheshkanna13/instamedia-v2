import { useState, useEffect, KeyboardEvent } from "react";
import { api } from "../../lib/api";
import type { BrandDNA } from "../../types";

const TONE_SUGGESTIONS = [
  "Empathetic","Bold","Honest","Vulnerable","Authoritative",
  "Conversational","Inspiring","Direct","Human","Curious"
];

const DEFAULT_DNA: Partial<BrandDNA> = {
  brand_id: "default", brand_name: "", mission: "",
  tone_descriptors: [], hex_colors: [], banned_words: [], typography: "", logo_url: ""
};

export default function BrandDNAVault() {
  const [dna,     setDna]     = useState<Partial<BrandDNA>>(DEFAULT_DNA);
  const [saving,  setSaving]  = useState(false);
  const [saved,   setSaved]   = useState(false);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState<string|null>(null);

  // Tag input states
  const [toneInput,    setToneInput]    = useState("");
  const [colorInput,   setColorInput]   = useState("");
  const [bannedInput,  setBannedInput]  = useState("");

  useEffect(() => {
    api.getBrandDNA().then(res => {
      if (res.data && Object.keys(res.data).length > 0) {
        // Parse JSON strings from DB back to arrays
        const d = res.data as Record<string,unknown>;
        const parsed: Partial<BrandDNA> = { ...DEFAULT_DNA };
        for (const key of Object.keys(d)) {
          if (["tone_descriptors","hex_colors","banned_words"].includes(key)) {
            const val = d[key];
            (parsed as Record<string,unknown>)[key] = typeof val === "string"
              ? JSON.parse(val || "[]") : (val ?? []);
          } else {
            (parsed as Record<string,unknown>)[key] = d[key];
          }
        }
        setDna(parsed);
      }
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const addTag = (field: keyof BrandDNA, val: string) => {
    const cleaned = val.trim().replace(/,/g,"");
    if (!cleaned) return;
    const current = (dna[field] as string[]) ?? [];
    if (!current.includes(cleaned)) {
      setDna(prev => ({ ...prev, [field]: [...current, cleaned] }));
    }
  };

  const removeTag = (field: keyof BrandDNA, val: string) => {
    const current = (dna[field] as string[]) ?? [];
    setDna(prev => ({ ...prev, [field]: current.filter(t => t !== val) }));
  };

  const handleTagKey = (
    e: KeyboardEvent<HTMLInputElement>,
    field: keyof BrandDNA,
    inputVal: string,
    setInput: (v:string)=>void
  ) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(field, inputVal);
      setInput("");
    }
    if (e.key === "Backspace" && !inputVal) {
      const current = (dna[field] as string[]) ?? [];
      if (current.length > 0) removeTag(field, current[current.length-1]);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await api.saveBrandDNA(dna);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return (
    <div className="page-body">
      <div className="empty-state"><div className="spinner" style={{width:28,height:28}} /></div>
    </div>
  );

  return (
    <div className="page-body">
      <div>
        <h1 className="display-title">Brand <em>DNA</em> Vault</h1>
        <p className="sub-text" style={{ marginTop:6 }}>
          The foundation layer — rules, voice, and assets the AI uses before generating anything
        </p>
      </div>

      <div className="grid-2" style={{ alignItems:"start" }}>

        {/* ── LEFT COLUMN ── */}
        <div style={{ display:"flex", flexDirection:"column", gap:20 }}>

          {/* Identity */}
          <div className="card card-accent-teal">
            <div className="card-header">
              <div className="section-title">Brand Identity</div>
              <span className="badge badge-teal">Core</span>
            </div>

            <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
              <div className="field">
                <label className="field-label">Brand Name</label>
                <input className="input"
                  placeholder="e.g. Acme Inc."
                  value={dna.brand_name ?? ""}
                  onChange={e => setDna(p => ({...p, brand_name: e.target.value}))}
                />
              </div>

              <div className="field">
                <label className="field-label">Mission Statement</label>
                <textarea className="textarea" rows={3}
                  placeholder="What does your brand exist to do? Be honest and specific — the AI uses this to filter content ideas."
                  value={dna.mission ?? ""}
                  onChange={e => setDna(p => ({...p, mission: e.target.value}))}
                />
              </div>

              <div className="field">
                <label className="field-label">Typography / Font Direction</label>
                <input className="input"
                  placeholder="e.g. Serif headlines, clean sans-serif body"
                  value={dna.typography ?? ""}
                  onChange={e => setDna(p => ({...p, typography: e.target.value}))}
                />
              </div>
            </div>
          </div>

          {/* Tone Descriptors */}
          <div className="card card-accent-violet">
            <div className="card-header">
              <div className="section-title">Tone Descriptors</div>
              <span className="badge badge-violet">{dna.tone_descriptors?.length ?? 0} added</span>
            </div>

            <div className="field" style={{ marginBottom:12 }}>
              <label className="field-label">Add Tone Words</label>
              <div className="tag-list" onClick={() => document.getElementById("tone-input")?.focus()}>
                {(dna.tone_descriptors ?? []).map(t => (
                  <div key={t} className="tag-chip">
                    {t}
                    <button className="tag-chip-remove" onClick={() => removeTag("tone_descriptors", t)}>×</button>
                  </div>
                ))}
                <input id="tone-input"
                  style={{ border:"none", outline:"none", background:"transparent",
                           color:"var(--text)", fontFamily:"var(--font-body)",
                           fontSize:13, minWidth:100, flex:1 }}
                  placeholder={dna.tone_descriptors?.length ? "" : "Type tone + Enter"}
                  value={toneInput}
                  onChange={e => setToneInput(e.target.value)}
                  onKeyDown={e => handleTagKey(e, "tone_descriptors", toneInput, setToneInput)}
                />
              </div>
            </div>

            {/* Suggestions */}
            <div>
              <div className="mono-label" style={{ marginBottom:8 }}>Quick Add</div>
              <div style={{ display:"flex", flexWrap:"wrap", gap:6 }}>
                {TONE_SUGGESTIONS.filter(t => !(dna.tone_descriptors ?? []).includes(t)).map(t => (
                  <button key={t}
                    style={{ background:"var(--s2)", border:"1px solid var(--border)",
                             borderRadius:4, padding:"3px 10px",
                             fontFamily:"var(--font-mono)", fontSize:10,
                             color:"var(--text-dim)", cursor:"pointer",
                             transition:"all 0.15s" }}
                    onClick={() => addTag("tone_descriptors", t)}
                    onMouseEnter={e => (e.currentTarget.style.borderColor = "var(--violet)")}
                    onMouseLeave={e => (e.currentTarget.style.borderColor = "var(--border)")}
                  >+ {t}</button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ── RIGHT COLUMN ── */}
        <div style={{ display:"flex", flexDirection:"column", gap:20 }}>

          {/* Brand Colors */}
          <div className="card card-accent-amber">
            <div className="card-header">
              <div className="section-title">Brand Colors</div>
              <span className="badge badge-amber">{dna.hex_colors?.length ?? 0} colors</span>
            </div>

            <div className="field" style={{ marginBottom:12 }}>
              <label className="field-label">Hex Codes</label>
              <div style={{ display:"flex", gap:8, marginBottom:8 }}>
                <input className="input" style={{ flex:1 }}
                  placeholder="#FF3CAC"
                  value={colorInput}
                  onChange={e => setColorInput(e.target.value)}
                  onKeyDown={e => {
                    if (e.key==="Enter") { addTag("hex_colors", colorInput); setColorInput(""); }
                  }}
                />
                <button className="btn btn-ghost btn-sm"
                  onClick={() => { addTag("hex_colors", colorInput); setColorInput(""); }}>
                  + Add
                </button>
              </div>

              {(dna.hex_colors ?? []).length > 0 && (
                <div style={{ display:"flex", flexWrap:"wrap", gap:6 }}>
                  {(dna.hex_colors ?? []).map(hex => (
                    <div key={hex} className="color-chip">
                      <div className="color-dot" style={{ background: hex }} />
                      {hex}
                      <button className="tag-chip-remove" style={{ color:"var(--text-muted)" }}
                        onClick={() => removeTag("hex_colors", hex)}>×</button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Visual palette preview */}
            {(dna.hex_colors ?? []).length > 0 && (
              <div style={{ display:"flex", gap:4, marginTop:8 }}>
                {(dna.hex_colors ?? []).map((hex, i) => (
                  <div key={i} style={{
                    flex:1, height:32, borderRadius:"var(--r)",
                    background: hex, border:"1px solid rgba(255,255,255,0.1)"
                  }} />
                ))}
              </div>
            )}
          </div>

          {/* Banned Words */}
          <div className="card card-accent-coral">
            <div className="card-header">
              <div className="section-title">Banned Words</div>
              <span className="badge badge-coral">{dna.banned_words?.length ?? 0} blocked</span>
            </div>
            <p style={{ fontSize:12, color:"var(--text-dim)", lineHeight:1.6, marginBottom:14 }}>
              The Emotional Aligner will flag any draft containing these words.
            </p>

            <div className="field">
              <label className="field-label">Add Words to Block</label>
              <div className="tag-list" onClick={() => document.getElementById("banned-input")?.focus()}>
                {(dna.banned_words ?? []).map(w => (
                  <div key={w} className="tag-chip" style={{
                    background:"rgba(255,87,87,0.1)", border:"1px solid rgba(255,87,87,0.2)", color:"var(--coral)"
                  }}>
                    {w}
                    <button className="tag-chip-remove" style={{ color:"var(--coral)" }}
                      onClick={() => removeTag("banned_words", w)}>×</button>
                  </div>
                ))}
                <input id="banned-input"
                  style={{ border:"none", outline:"none", background:"transparent",
                           color:"var(--text)", fontFamily:"var(--font-body)",
                           fontSize:13, minWidth:120, flex:1 }}
                  placeholder={dna.banned_words?.length ? "" : "e.g. 'cheap' → Enter"}
                  value={bannedInput}
                  onChange={e => setBannedInput(e.target.value)}
                  onKeyDown={e => handleTagKey(e, "banned_words", bannedInput, setBannedInput)}
                />
              </div>
            </div>
          </div>

          {/* Logo Upload placeholder */}
          <div className="card">
            <div className="card-header">
              <div className="section-title">Brand Assets</div>
              <span className="badge badge-sky">Storage</span>
            </div>

            <div className="upload-zone" onClick={() => alert("Connect Supabase Storage to enable logo uploads.")}>
              <div style={{ fontSize:28, opacity:0.3 }}>🖼</div>
              <div className="mono-label">Upload Primary Logo</div>
              <div className="sub-text">PNG, SVG or WebP · Max 2MB</div>
              <div style={{ fontFamily:"var(--font-mono)", fontSize:9, color:"var(--text-muted)", marginTop:4 }}>
                Requires Supabase Storage configured
              </div>
            </div>

            {dna.logo_url && (
              <div style={{ marginTop:12, padding:8, background:"var(--s2)",
                            borderRadius:"var(--r)", textAlign:"center" }}>
                <img src={dna.logo_url} alt="Brand logo"
                  style={{ maxHeight:48, objectFit:"contain", opacity:0.9 }} />
              </div>
            )}
          </div>

          {/* Save actions */}
          <div style={{ display:"flex", gap:10, alignItems:"center" }}>
            <button className="btn btn-primary btn-lg" onClick={handleSave} disabled={saving} style={{ flex:1 }}>
              {saving ? <><div className="spinner" style={{borderTopColor:"#000"}} /> Saving...</> : "✓ Save Brand DNA"}
            </button>
            <button className="btn btn-ghost" onClick={() => setDna(DEFAULT_DNA)}>Reset</button>
          </div>

          {saved && <div className="alert alert-success">✓ Brand DNA saved successfully.</div>}
          {error && <div className="alert alert-error">⚠ {error}</div>}
        </div>
      </div>
    </div>
  );
}
