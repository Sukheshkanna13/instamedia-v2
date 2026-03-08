"use client";

import { useState } from "react";

const ARCHETYPES = [
    {
        id: "wellness-d2c",
        name: "Wellness D2C",
        icon: "🧘",
        color: "var(--emerald)",
        description: "Ayurveda, yoga, meditation, holistic health brands",
        toneProfile: ["Vulnerable", "Educational", "Warm", "Authentic"],
        sampleBrands: ["Kapiva", "Organic India", "The Ayurveda Co"],
        avgERS: 72,
        postCount: 85,
    },
    {
        id: "local-food",
        name: "Local Food Brand",
        icon: "🍛",
        color: "var(--amber)",
        description: "Regional cuisine, artisanal food, farm-to-table",
        toneProfile: ["Nostalgic", "Community", "Honest", "Celebratory"],
        sampleBrands: ["Slurrp Farm", "Epigamia", "Country Delight"],
        avgERS: 68,
        postCount: 92,
    },
    {
        id: "fashion-startup",
        name: "Fashion Startup",
        icon: "👗",
        color: "var(--coral)",
        description: "Sustainable fashion, ethnic wear, streetwear",
        toneProfile: ["Bold", "Aspirational", "Inclusive", "Trendy"],
        sampleBrands: ["FabIndia", "Bewakoof", "Nykaa Fashion"],
        avgERS: 75,
        postCount: 110,
    },
    {
        id: "tech-saas",
        name: "Tech SaaS",
        icon: "💻",
        color: "var(--sky)",
        description: "B2B software, productivity tools, developer platforms",
        toneProfile: ["Authoritative", "Educational", "Direct", "Innovative"],
        sampleBrands: ["Zoho", "Freshworks", "Razorpay"],
        avgERS: 65,
        postCount: 78,
    },
    {
        id: "education",
        name: "Education Platform",
        icon: "📚",
        color: "var(--violet)",
        description: "EdTech, online courses, skill development",
        toneProfile: ["Inspiring", "Supportive", "Clear", "Motivational"],
        sampleBrands: ["Unacademy", "upGrad", "Byju's"],
        avgERS: 70,
        postCount: 95,
    },
    {
        id: "fitness",
        name: "Fitness & Health",
        icon: "💪",
        color: "var(--teal)",
        description: "Gyms, fitness apps, sports nutrition",
        toneProfile: ["Motivational", "Energetic", "Disciplined", "Community"],
        sampleBrands: ["Cult.fit", "HealthifyMe", "MuscleBlaze"],
        avgERS: 73,
        postCount: 88,
    },
];

export default function ColdStartPage() {
    const [selected, setSelected] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSelect = (archetypeId: string) => {
        setSelected(archetypeId);
    };

    const handleBootstrap = async () => {
        if (!selected) return;

        setLoading(true);
        // In production: POST /api/database/bootstrap with archetype_id
        setTimeout(() => {
            setLoading(false);
            alert("Brand Bootstrapped successfully! Simulated for now.");
        }, 2000);
    };

    const selectedArchetype = ARCHETYPES.find(a => a.id === selected);

    return (
        <div className="page-body">
            <div>
                <h1 className="display-title">Cold Start <em>Bootstrap</em></h1>
                <p className="sub-text" style={{ marginTop: 6 }}>
                    New brand with no historical data? Start with a similar brand archetype to get value from day one
                </p>
            </div>

            <div className="card card-accent-teal">
                <div className="card-header">
                    <div className="section-title">How Cold Start Works</div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
                    {[
                        { icon: "🎯", title: "Choose Archetype", desc: "Select the brand category closest to yours" },
                        { icon: "🧬", title: "Load ESG Cluster", desc: "We load 50-100 high-performing posts from similar brands" },
                        { icon: "⚡", title: "Start Creating", desc: "Generate ideas and score content immediately" },
                        { icon: "🔄", title: "Auto-Transition", desc: "After 20 of your own posts, we switch to your brand-specific ESG" },
                    ].map((step, i) => (
                        <div key={i} style={{ textAlign: "center" }}>
                            <div style={{ fontSize: 32, marginBottom: 8 }}>{step.icon}</div>
                            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>{step.title}</div>
                            <div style={{ fontSize: 11, color: "var(--text-dim)", lineHeight: 1.5 }}>{step.desc}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div>
                <div style={{ marginBottom: 16 }}>
                    <div className="section-title">Select Your Brand Archetype</div>
                    <p style={{ fontSize: 12, color: "var(--text-dim)", marginTop: 4 }}>
                        Choose the category that best matches your brand. You can switch later if needed.
                    </p>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 16 }}>
                    {ARCHETYPES.map((archetype) => (
                        <div
                            key={archetype.id}
                            className={`card ${selected === archetype.id ? "selected" : ""}`}
                            onClick={() => handleSelect(archetype.id)}
                            style={{
                                cursor: "pointer",
                                borderColor: selected === archetype.id ? archetype.color : "var(--border)",
                                background: selected === archetype.id
                                    ? `linear-gradient(135deg, ${archetype.color}08 0%, transparent 100%)`
                                    : "var(--s1)",
                                transition: "all 0.2s ease",
                            }}
                        >
                            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                                <div
                                    style={{
                                        fontSize: 32,
                                        width: 56,
                                        height: 56,
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        background: `${archetype.color}15`,
                                        border: `2px solid ${archetype.color}`,
                                        borderRadius: "var(--r)",
                                    }}
                                >
                                    {archetype.icon}
                                </div>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontFamily: "var(--font-display)", fontSize: 16, fontWeight: 700, marginBottom: 2 }}>
                                        {archetype.name}
                                    </div>
                                    <div className="mono-label" style={{ fontSize: 9 }}>
                                        {archetype.postCount} POSTS · AVG ERS {archetype.avgERS}
                                    </div>
                                </div>
                                {selected === archetype.id && (
                                    <div style={{ color: archetype.color, fontSize: 20 }}>✓</div>
                                )}
                            </div>

                            <p style={{ fontSize: 12, color: "var(--text-dim)", lineHeight: 1.6, marginBottom: 12 }}>
                                {archetype.description}
                            </p>

                            <div style={{ marginBottom: 12 }}>
                                <div className="mono-label" style={{ fontSize: 9, marginBottom: 6 }}>TONE PROFILE</div>
                                <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                                    {archetype.toneProfile.map((tone) => (
                                        <span
                                            key={tone}
                                            className="badge"
                                            style={{
                                                background: `${archetype.color}15`,
                                                color: archetype.color,
                                                border: `1px solid ${archetype.color}`,
                                                fontSize: 9,
                                            }}
                                        >
                                            {tone}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <div className="mono-label" style={{ fontSize: 9, marginBottom: 4 }}>SIMILAR BRANDS</div>
                                <div style={{ fontSize: 10, color: "var(--text-muted)", fontStyle: "italic" }}>
                                    {archetype.sampleBrands.join(" · ")}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {selectedArchetype && (
                <div className="card card-accent-teal fade-up">
                    <div className="card-header">
                        <div>
                            <div className="mono-label" style={{ color: "var(--teal)", marginBottom: 4 }}>SELECTED ARCHETYPE</div>
                            <div className="section-title">{selectedArchetype.name}</div>
                        </div>
                        <span
                            className="badge"
                            style={{
                                background: `${selectedArchetype.color}20`,
                                color: selectedArchetype.color,
                                border: `1px solid ${selectedArchetype.color}`,
                            }}
                        >
                            {selectedArchetype.icon} {selectedArchetype.postCount} posts
                        </span>
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 20 }}>
                        <div>
                            <div className="mono-label" style={{ marginBottom: 8 }}>WHAT YOU'LL GET</div>
                            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                                {[
                                    `${selectedArchetype.postCount} high-performing posts from similar brands`,
                                    `Average ERS of ${selectedArchetype.avgERS} (strong baseline)`,
                                    "Immediate access to Ideation and Creative Studio",
                                    "Emotional Aligner scores based on archetype patterns",
                                ].map((item, i) => (
                                    <div key={i} style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                                        <div style={{ color: "var(--teal)", fontSize: 14, marginTop: 2 }}>✓</div>
                                        <div style={{ fontSize: 12, color: "var(--text-dim)", lineHeight: 1.5 }}>{item}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <div className="mono-label" style={{ marginBottom: 8 }}>TRANSITION PLAN</div>
                            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                                {[
                                    { posts: "0-20", label: "Bootstrapped ESG", desc: "Using archetype cluster" },
                                    { posts: "20+", label: "Hybrid ESG", desc: "70% your posts, 30% archetype" },
                                    { posts: "50+", label: "Brand-Specific ESG", desc: "100% your posts" },
                                ].map((phase, i) => (
                                    <div
                                        key={i}
                                        style={{
                                            padding: "8px 12px",
                                            background: "var(--s2)",
                                            border: "1px solid var(--border)",
                                            borderRadius: "var(--r)",
                                        }}
                                    >
                                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 2 }}>
                                            <span className="mono-label" style={{ fontSize: 9 }}>{phase.posts} POSTS</span>
                                            <span style={{ fontSize: 10, fontWeight: 600 }}>{phase.label}</span>
                                        </div>
                                        <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{phase.desc}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <button
                        className="btn btn-primary btn-lg"
                        onClick={handleBootstrap}
                        disabled={loading}
                        style={{ width: "100%" }}
                    >
                        {loading ? (
                            <>
                                <div className="spinner" style={{ borderTopColor: "#000" }} />
                                Loading {selectedArchetype.postCount} posts...
                            </>
                        ) : (
                            <>✦ Bootstrap with {selectedArchetype.name}</>
                        )}
                    </button>
                </div>
            )}

            <div className="card card-sm" style={{ background: "rgba(255,184,0,0.05)", border: "1px solid rgba(255,184,0,0.15)" }}>
                <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                    <div style={{ fontSize: 20 }}>⚠</div>
                    <div>
                        <div className="mono-label" style={{ color: "var(--amber)", marginBottom: 4 }}>IMPORTANT NOTE</div>
                        <p style={{ fontSize: 12, color: "var(--text-dim)", lineHeight: 1.6 }}>
                            Bootstrapped ESG provides a starting point, but scores will be based on "Similar Brand Patterns" until you
                            have 20+ posts of your own. The UI will clearly indicate when you're using bootstrapped data vs. your
                            brand-specific ESG.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
