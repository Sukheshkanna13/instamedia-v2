import { useState } from "react";
import type { FullCampaignResponse, AdRecommendationResponse, AdScraperResult, MarketingIntelligenceResponse } from "../../types";

interface Props {
    onClose: () => void;
}

export default function AdsManagerModal({ onClose }: Props) {
    const [activeTab, setActiveTab] = useState<"discovery" | "strategy" | "intelligence">("discovery");
    const [isGenerating, setIsGenerating] = useState(false);
    const [response, setResponse] = useState<FullCampaignResponse | null>(null);

    const [form, setForm] = useState({
        keyword: "fitness supplements",
        niche: "health & wellness",
        platforms: ["META", "YOUTUBE"],
        campaign_goal: "drive product page visits",
        target_audience: "men 25-40 interested in gym and fitness",
        budget: "$500/month",
        tone: "energetic and motivational",
        ad_draft: "Fuel your gains with ProMax Whey. 30g protein per scoop. Shop now.",
        metrics: {
            impressions: 50000,
            clicks: 450,
            conversions: 18,
            spend: 320.00,
            ctr: 0.9,
            cpc: 0.71,
            roas: 2.8
        }
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setForm(f => ({ ...f, [name]: value }));
    };

    const handleCheckboxChange = (platform: "META" | "YOUTUBE") => {
        setForm(f => {
            const active = f.platforms.includes(platform);
            if (active) {
                return { ...f, platforms: f.platforms.filter(p => p !== platform) };
            } else {
                return { ...f, platforms: [...f.platforms, platform] };
            }
        });
    };

    // Extract nested metrics securely
    const handleMetricChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setForm(f => ({
            ...f,
            metrics: {
                ...f.metrics,
                [name]: parseFloat(value) || 0
            }
        }));
    };

    const handleGenerate = async () => {
        setIsGenerating(true);
        setResponse(null);
        try {
            const res = await fetch("http://localhost:5001/api/ads/full-campaign", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form)
            });
            const data = await res.json();
            setResponse(data);
            setActiveTab("strategy"); // Switch focus to results
        } catch (err) {
            console.error(err);
            alert("Failed to generate ADs intelligence. Is backend running?");
        } finally {
            setIsGenerating(false);
        }
    };

    const renderDiscovery = (ads: AdScraperResult[]) => {
        if (!ads || ads.length === 0) return <div className="json-block">No ads retrieved in this run.</div>;
        return (
            <div className="ads-grid">
                {ads.map((ad, idx) => (
                    <div key={`${ad.ad_id}-${idx}`} className="ad-card">
                        {ad.preview_url ? (
                            <img src={ad.preview_url} alt="Ad snapshot" className="ad-card-img" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                        ) : (
                            <div className="ad-card-img" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>No Snippet</div>
                        )}
                        <div className="ad-card-body">
                            <div className="ad-card-meta">
                                <span className={`ad-platform-badge ${ad.platform.toLowerCase()}`}>{ad.platform}</span>
                                <span className="ad-score" title="Efficiency Score">⚡ {ad.efficiency_score?.toFixed(2) || "0.00"}</span>
                            </div>
                            <div className="ad-card-title">{ad.headline || "No Headline"}</div>
                            <div className="ad-card-copy">{ad.body}</div>
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    const renderStrategy = (recRaw?: AdRecommendationResponse) => {
        if (!recRaw) return <div className="json-block">No strategy data returned.</div>;
        if (recRaw.error) return <div className="json-block" style={{ color: 'var(--coral)' }}>{recRaw.error}</div>;

        const recs = recRaw.recommendations;
        if (!recs) return <div className="json-block">Generating strategy failed or is malformed.</div>;
        if (recs.error) return <div className="json-block" style={{ color: 'var(--coral)' }}>{recs.error}</div>;

        return (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div className="panel">
                    <h3 style={{ marginBottom: '12px' }}>Copywriting Concepts</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div>
                            <h4 style={{ color: 'var(--text-dim)', marginBottom: '8px' }}>Headlines</h4>
                            <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                {recs.headlines?.map((h, i) => <li key={i}>{h}</li>) || <li>No headlines generated</li>}
                            </ul>
                        </div>
                        <div>
                            <h4 style={{ color: 'var(--text-dim)', marginBottom: '8px' }}>Hooks & CTAs</h4>
                            <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                {recs.hooks?.map((h, i) => <li key={i}>{h}</li>) || null}
                                {recs.ctas?.map((c, i) => <li key={`cta-${i}`}><strong>[CTA]</strong> {c}</li>) || null}
                            </ul>
                        </div>
                    </div>
                </div>

                <div className="panel" style={{ background: 'var(--s2)' }}>
                    <h3 style={{ marginBottom: '12px' }}>Creative Direction</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div><strong>Visuals:</strong> {recs.creative_direction?.visuals || "N/A"}</div>
                        <div><strong>Formats:</strong> {recs.creative_direction?.formats || "N/A"}</div>
                        <div><strong>Inspiration:</strong> {recs.creative_direction?.inspiration_from_top_ads || "N/A"}</div>
                    </div>
                </div>

                <div className="panel">
                    <h3 style={{ marginBottom: '12px' }}>Targeting & Budgeting</h3>
                    <div style={{ display: 'flex', gap: '20px' }}>
                        <div style={{ flex: 1 }}>
                            <h4 style={{ color: 'var(--text-dim)' }}>Interests</h4>
                            <div>{recs.targeting_suggestions?.interests?.join(", ") || "N/A"}</div>
                        </div>
                        <div style={{ flex: 1 }}>
                            <h4 style={{ color: 'var(--text-dim)' }}>Budget</h4>
                            <div><strong>META:</strong> {recs.budget_allocation?.META || "N/A"}</div>
                            <div><strong>YouTube:</strong> {recs.budget_allocation?.YOUTUBE || "N/A"}</div>
                            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                                Rationale: {recs.budget_allocation?.rationale || "N/A"}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderIntelligence = (intel?: MarketingIntelligenceResponse) => {
        if (!intel) return <div className="json-block">No intelligence data returned.</div>;

        const researchError = intel.market_research?.error;
        const tuningError = intel.campaign_tuning?.error;
        const analyticsError = intel.analytics_insights?.error;

        const isFreeTierSkip = researchError?.includes("preserve Free Tier API quotas");

        if (isFreeTierSkip) {
            return (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '16px', color: 'var(--text-muted)' }}>
                    <span style={{ fontSize: '32px' }}>🔒</span>
                    <h3 style={{ color: 'var(--text)' }}>Marketing Intelligence Agents Skipped</h3>
                    <p style={{ textAlign: 'center', maxWidth: '400px' }}>
                        To prevent generating a <b>HTTP 429 Quota Exceeded</b> error on the Google Gemini Free Tier, these advanced multi-agent checks were skipped.
                    </p>
                    <p style={{ textAlign: 'center', maxWidth: '400px', fontSize: '13px' }}>
                        Your core Strategy and Discovery data successfully generated and is available in the other tabs!
                    </p>
                </div>
            );
        }

        return (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

                <div className="panel">
                    <h3 style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>🌍 Market Research</h3>
                    {researchError ? (
                        <div style={{ color: 'var(--coral)' }}>{researchError}</div>
                    ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                            <div>
                                <h4 style={{ color: 'var(--text-dim)' }}>Audience Insights</h4>
                                <div style={{ fontSize: '13px', marginTop: '4px' }}><strong>Demographics:</strong> {intel.market_research?.audience_insights?.demographics || 'N/A'}</div>
                                <div style={{ fontSize: '13px', marginTop: '4px' }}><strong>Psychographics:</strong> {intel.market_research?.audience_insights?.psychographics || 'N/A'}</div>
                            </div>
                            <div>
                                <h4 style={{ color: 'var(--text-dim)' }}>Content Angles</h4>
                                <ul style={{ paddingLeft: '16px', fontSize: '13px', marginTop: '4px' }}>
                                    {intel.market_research?.content_angles?.map((a: string, i: number) => <li key={i}>{a}</li>)}
                                </ul>
                            </div>
                        </div>
                    )}
                </div>

                <div className="panel">
                    <h3 style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>🛠️ Campaign Tuning (A/B Tests)</h3>
                    {tuningError ? (
                        <div style={{ color: 'var(--coral)' }}>{tuningError}</div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {intel.campaign_tuning?.ab_tests?.map((t: any, i: number) => (
                                <div key={i} style={{ background: 'var(--surface)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                                    <div style={{ fontWeight: 600, color: 'var(--violet)', marginBottom: '4px' }}>Test: {t.element}</div>
                                    <div style={{ display: 'flex', gap: '16px', fontSize: '13px' }}>
                                        <div style={{ flex: 1 }}><strong>A:</strong> {t.variant_a}</div>
                                        <div style={{ flex: 1 }}><strong>B:</strong> {t.variant_b}</div>
                                    </div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '6px', fontStyle: 'italic' }}>Hypothesis: {t.hypothesis}</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="panel">
                    <h3 style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>📊 Analytics & Actions</h3>
                    {analyticsError ? (
                        <div style={{ color: 'var(--coral)' }}>{analyticsError}</div>
                    ) : (
                        <div style={{ display: 'flex', gap: '20px' }}>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--emerald)' }}>
                                    Grade: {intel.analytics_insights?.performance_diagnosis?.overall_grade || 'N/A'}
                                </div>
                                <div style={{ fontSize: '13px', color: 'var(--text-dim)', marginTop: '4px' }}>
                                    {intel.analytics_insights?.performance_diagnosis?.summary || 'N/A'}
                                </div>
                            </div>
                            <div style={{ flex: 1.5, background: 'var(--s2)', padding: '12px', borderRadius: '8px' }}>
                                <h4 style={{ marginBottom: '8px' }}>Top Actions</h4>
                                <ul style={{ paddingLeft: '16px', fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                    {intel.analytics_insights?.action_items?.slice(0, 3).map((a: any, i: number) => (
                                        <li key={i}><strong>{a.timeline}</strong>: {a.action}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    )}
                </div>

            </div>
        );
    };

    return (
        <div className="ads-modal-overlay">
            <div className="ads-modal-container">

                {/* Header */}
                <header className="ads-modal-header">
                    <div className="ads-modal-title">
                        <span style={{ fontSize: '24px' }}>🎯</span>
                        ADs Intelligence Manager
                        <div className="status-pill" style={{ marginLeft: '12px' }}>
                            <div className="status-dot" style={{ background: 'var(--emerald)' }} />
                            <span>Groq Llama 3.3 Online</span>
                        </div>
                    </div>
                    <button className="ads-modal-close" onClick={onClose}>&times;</button>
                </header>

                {/* Body */}
                <div className="ads-modal-body">

                    {/* Sidebar Form */}
                    <aside className="ads-modal-sidebar">
                        <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>Campaign Brief</h3>

                        <div className="form-group">
                            <label>Target Keyword</label>
                            <input type="text" className="input" name="keyword" value={form.keyword} onChange={handleChange} />
                        </div>

                        <div className="form-group">
                            <label>Niche / Industry</label>
                            <input type="text" className="input" name="niche" value={form.niche} onChange={handleChange} />
                        </div>

                        <div className="form-group">
                            <label>Platforms</label>
                            <div style={{ display: 'flex', gap: '12px' }}>
                                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', cursor: 'pointer' }}>
                                    <input type="checkbox" checked={form.platforms.includes("META")} onChange={() => handleCheckboxChange("META")} />
                                    META Ads
                                </label>
                                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', cursor: 'pointer' }}>
                                    <input type="checkbox" checked={form.platforms.includes("YOUTUBE")} onChange={() => handleCheckboxChange("YOUTUBE")} />
                                    YouTube Ads
                                </label>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Current Draft / Concept</label>
                            <textarea className="input" style={{ minHeight: '80px', resize: 'vertical' }} name="ad_draft" value={form.ad_draft} onChange={handleChange} />
                        </div>

                        <div style={{ height: '1px', background: 'var(--border)', margin: '8px 0' }} />

                        <button
                            className="btn btn-primary"
                            style={{ width: '100%', padding: '12px', justifyContent: 'center', fontSize: '14px', fontWeight: 600 }}
                            onClick={handleGenerate}
                            disabled={isGenerating}
                        >
                            {isGenerating ? "⚡ Generating Intelligence..." : "▶ Run full pipeline"}
                        </button>
                        <p style={{ fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', margin: 0 }}>
                            {isGenerating ? "Processing via Groq..." : "Powered by Groq API"}
                        </p>
                    </aside>

                    {/* Main Content Area */}
                    <main className="ads-modal-main">
                        <div className="ads-tabs">
                            <button className={`ads-tab ${activeTab === 'discovery' ? 'active' : ''}`} onClick={() => setActiveTab('discovery')}>
                                🔍 Ad Discovery
                            </button>
                            <button className={`ads-tab ${activeTab === 'strategy' ? 'active' : ''}`} onClick={() => setActiveTab('strategy')}>
                                💡 Campaign Strategy
                            </button>
                            <button className={`ads-tab ${activeTab === 'intelligence' ? 'active' : ''}`} onClick={() => setActiveTab('intelligence')}>
                                🧠 Marketing Intelligence
                            </button>
                        </div>

                        <div className="ads-tab-content">
                            {isGenerating ? (
                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                                    <div className="spinner" style={{ marginBottom: '16px' }}></div>
                                    <p>Scraping realtime META & YouTube Ads...</p>
                                    <p style={{ fontSize: '12px' }}>Running Groq Llama Workflows...</p>
                                </div>
                            ) : !response ? (
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                                    Fill out the campaign brief and run the pipeline to view intelligence.
                                </div>
                            ) : (
                                <>
                                    {activeTab === 'discovery' && renderDiscovery(response?.ad_recommendations?.retrieved_ads || [])}
                                    {activeTab === 'strategy' && renderStrategy(response?.ad_recommendations)}
                                    {activeTab === 'intelligence' && renderIntelligence(response?.marketing_intelligence)}
                                </>
                            )}
                        </div>
                    </main>

                </div>
            </div>
        </div>
    );
}
