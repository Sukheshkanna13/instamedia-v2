import { useState } from "react";
import { api } from "../../lib/api";

interface ScrapedPost {
  text: string;
  likes: number;
  comments: number;
  shares: number;
  platform: string;
  emotion: string;
  ers: number;
}

export default function DatabaseExpansion() {
  const [keywords, setKeywords] = useState("");
  const [platforms, setPlatforms] = useState<string[]>(["instagram"]);
  const [count, setCount] = useState(20);
  const [loading, setLoading] = useState(false);
  const [scrapedPosts, setScrapedPosts] = useState<ScrapedPost[]>([]);
  const [selectedPosts, setSelectedPosts] = useState<Set<number>>(new Set());
  const [adding, setAdding] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadStats = async () => {
    try {
      const data = await api.getDatabaseStats();
      setStats(data);
    } catch (e) {
      console.error("Failed to load stats:", e);
    }
  };

  const handleScrape = async () => {
    if (!keywords.trim()) {
      setError("Please enter keywords to search");
      return;
    }

    if (platforms.length === 0) {
      setError("Please select at least one platform");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setScrapedPosts([]);
    setSelectedPosts(new Set());

    try {
      const result = await api.scrapePosts(keywords, platforms, count);
      setScrapedPosts(result.scraped_posts);
      
      if (result.mode === "mock") {
        setSuccess(`${result.message} (Demo mode - using sample data)`);
      } else {
        setSuccess(result.message);
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const togglePost = (index: number) => {
    const newSelected = new Set(selectedPosts);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedPosts(newSelected);
  };

  const selectAll = () => {
    if (selectedPosts.size === scrapedPosts.length) {
      setSelectedPosts(new Set());
    } else {
      setSelectedPosts(new Set(scrapedPosts.map((_, i) => i)));
    }
  };

  const handleAddSelected = async () => {
    if (selectedPosts.size === 0) {
      setError("Please select at least one post to add");
      return;
    }

    setAdding(true);
    setError(null);
    setSuccess(null);

    try {
      const postsToAdd = Array.from(selectedPosts).map(i => scrapedPosts[i]);
      const result = await api.addScrapedPosts(postsToAdd);
      
      setSuccess(`✅ ${result.message}! Total posts in database: ${result.total_posts}`);
      setScrapedPosts([]);
      setSelectedPosts(new Set());
      await loadStats();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setAdding(false);
    }
  };

  const togglePlatform = (platform: string) => {
    if (platforms.includes(platform)) {
      setPlatforms(platforms.filter(p => p !== platform));
    } else {
      setPlatforms([...platforms, platform]);
    }
  };

  const ersColor = (ers: number) => {
    if (ers >= 75) return "var(--emerald)";
    if (ers >= 60) return "var(--teal)";
    if (ers >= 45) return "var(--amber)";
    return "var(--coral)";
  };

  return (
    <div className="page-body">
      <div>
        <h1 className="display-title">Database <em>Expansion</em></h1>
        <p className="sub-text" style={{ marginTop: 6 }}>
          Expand your emotional database by scraping posts from social media
        </p>
      </div>

      {/* Current Stats */}
      {stats && (
        <div className="card">
          <div className="card-header">
            <div className="section-title">Current Database</div>
          </div>
          <div className="grid-3" style={{ gap: 16 }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 32, fontWeight: 900, color: "var(--teal)" }}>
                {stats.total_posts}
              </div>
              <div className="mono-label">Total Posts</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 32, fontWeight: 900, color: "var(--violet)" }}>
                {stats.avg_ers}
              </div>
              <div className="mono-label">Avg ERS</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 32, fontWeight: 900, color: "var(--amber)" }}>
                {Object.keys(stats.platforms).length}
              </div>
              <div className="mono-label">Platforms</div>
            </div>
          </div>
        </div>
      )}

      {/* Scraping Form */}
      <div className="card">
        <div className="card-header">
          <div className="section-title">Scrape New Posts</div>
        </div>

        <div className="field" style={{ marginBottom: 16 }}>
          <label className="field-label">Keywords / Search Terms</label>
          <input
            className="input"
            placeholder="e.g., sustainability, eco-friendly, green living"
            value={keywords}
            onChange={e => setKeywords(e.target.value)}
          />
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Enter keywords to find relevant posts
          </div>
        </div>

        <div className="field" style={{ marginBottom: 16 }}>
          <label className="field-label">Platforms</label>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            {["instagram", "linkedin", "twitter"].map(platform => (
              <label
                key={platform}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  cursor: "pointer",
                  padding: "8px 16px",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r)",
                  background: platforms.includes(platform) ? "rgba(0,212,184,0.1)" : "transparent",
                  borderColor: platforms.includes(platform) ? "var(--teal)" : "var(--border)",
                }}
              >
                <input
                  type="checkbox"
                  checked={platforms.includes(platform)}
                  onChange={() => togglePlatform(platform)}
                  style={{ cursor: "pointer" }}
                />
                <span style={{ textTransform: "capitalize" }}>{platform}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="field" style={{ marginBottom: 16 }}>
          <label className="field-label">Number of Posts (max 100)</label>
          <input
            type="number"
            className="input"
            value={count}
            onChange={e => setCount(Math.min(100, Math.max(1, parseInt(e.target.value) || 20)))}
            min="1"
            max="100"
          />
        </div>

        <button
          className="btn btn-primary btn-lg"
          onClick={handleScrape}
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="spinner" style={{ borderTopColor: "#000" }} />
              Scraping posts...
            </>
          ) : (
            <>🔍 Scrape Posts</>
          )}
        </button>
      </div>

      {error && <div className="alert alert-error">⚠ {error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Scraped Posts */}
      {scrapedPosts.length > 0 && (
        <div className="card">
          <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div className="section-title">
              Scraped Posts ({selectedPosts.size} of {scrapedPosts.length} selected)
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-ghost btn-sm" onClick={selectAll}>
                {selectedPosts.size === scrapedPosts.length ? "Deselect All" : "Select All"}
              </button>
              <button
                className="btn btn-primary btn-sm"
                onClick={handleAddSelected}
                disabled={adding || selectedPosts.size === 0}
              >
                {adding ? "Adding..." : `Add ${selectedPosts.size} Selected`}
              </button>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {scrapedPosts.map((post, index) => (
              <div
                key={index}
                onClick={() => togglePost(index)}
                style={{
                  padding: 16,
                  border: "1px solid var(--border)",
                  borderRadius: "var(--r)",
                  cursor: "pointer",
                  background: selectedPosts.has(index) ? "rgba(0,212,184,0.05)" : "transparent",
                  borderColor: selectedPosts.has(index) ? "var(--teal)" : "var(--border)",
                  transition: "all 0.2s ease",
                }}
              >
                <div style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
                  <input
                    type="checkbox"
                    checked={selectedPosts.has(index)}
                    onChange={() => togglePost(index)}
                    style={{ marginTop: 4, cursor: "pointer" }}
                  />
                  
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
                      <span className="badge badge-sky">{post.platform}</span>
                      <span className="badge badge-violet">{post.emotion}</span>
                      <span
                        className="badge"
                        style={{
                          background: `${ersColor(post.ers)}20`,
                          color: ersColor(post.ers),
                          border: `1px solid ${ersColor(post.ers)}`,
                        }}
                      >
                        ERS: {post.ers}
                      </span>
                    </div>
                    
                    <div style={{ fontSize: 14, lineHeight: 1.6, color: "var(--text)" }}>
                      {post.text}
                    </div>
                    
                    <div style={{ display: "flex", gap: 16, marginTop: 8, fontSize: 12, color: "var(--text-muted)" }}>
                      <span>❤️ {post.likes}</span>
                      <span>💬 {post.comments}</span>
                      <span>🔄 {post.shares}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && scrapedPosts.length === 0 && !error && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <div className="empty-title">Expand Your Database</div>
            <div className="empty-sub">
              Search for posts by keywords and platform.<br />
              Review scraped posts and add them to your emotional database.<br />
              This helps improve AI recommendations and content quality.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
