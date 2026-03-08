"""
Orchestrates META + YouTube scrapers and manages the ChromaDB vector store.
Provides a mock fallback if ChromaDB fails to import (due to Python 3.14 limitations).
"""

from services.ad_scraper.meta_scraper import MetaAdScraper
from services.ad_scraper.youtube_scraper import YouTubeAdScraper
from config import Config

# Try to import real ChromaDB; fallback to mock if it fails (e.g. Python 3.14)
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except Exception as e:
    CHROMA_AVAILABLE = False
    print(f"⚠️  ChromaDB not available ({type(e).__name__}). Using in-memory mock collection for AD ingestion.")

class MockCollection:
    _data = {"ids": [], "documents": [], "metadatas": []}

    def upsert(self, documents, metadatas, ids):
        # Very simple upsert: clear old, add new
        MockCollection._data["ids"] = ids
        MockCollection._data["documents"] = documents
        MockCollection._data["metadatas"] = metadatas
        
    def query(self, query_texts, n_results, where=None, include=None):
        n = min(n_results, len(MockCollection._data["ids"]))
        
        # Simple mock filtering by niche if provided
        filtered_metadatas = []
        filtered_distances = []
        
        for meta in MockCollection._data["metadatas"]:
            if where and "niche" in where and meta.get("niche") != where["niche"]:
                continue
            filtered_metadatas.append(meta)
            filtered_distances.append(0.1)  # Mock high similarity
            
            if len(filtered_metadatas) == n:
                break
                
        # If no items matched the filter, return what we have (mock behavior)
        if not filtered_metadatas and MockCollection._data["metadatas"]:
            filtered_metadatas = MockCollection._data["metadatas"][:n]
            filtered_distances = [0.1] * len(filtered_metadatas)
            
        return {
            "metadatas": [filtered_metadatas],
            "distances": [filtered_distances]
        }

class ADIngestionService:
    def __init__(self):
        if CHROMA_AVAILABLE:
            self.chroma_client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name="best_performing_ads",
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.collection = MockCollection()

        self.meta_scraper = MetaAdScraper(Config.META_ACCESS_TOKEN)
        self.yt_scraper = YouTubeAdScraper(Config.SERPAPI_KEY)

    def scrape_and_ingest(
        self, keyword: str, niche: str, platforms: list = None
    ) -> dict:
        """
        Full pipeline: scrape → normalize → embed → upsert into ChromaDB.
        """
        if platforms is None:
            platforms = ["META", "YOUTUBE"]
            
        all_ads = []

        if "META" in platforms:
            all_ads.extend(self.meta_scraper.fetch_ads(keyword, niche))

        if "YOUTUBE" in platforms:
            all_ads.extend(self.yt_scraper.fetch_ads(keyword, niche))

        if not all_ads:
            return {"status": "no_ads_found", "count": 0}

        # ChromaDB requires: documents (text to embed), metadatas, ids
        documents = [f"{ad['headline']} {ad['body']}" for ad in all_ads]
        metadatas = all_ads
        ids = [f"{ad['platform']}_{ad['ad_id']}_{ad['scraped_at']}" for ad in all_ads]

        self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        return {"status": "success", "ingested_count": len(all_ads)}

    def query_similar_ads(
        self, campaign_brief: str, niche: str, top_k: int = 8
    ) -> list:
        """
        RAG RETRIEVAL — query vector store and attach similarity scores.
        """
        try:
            results = self.collection.query(
                query_texts=[campaign_brief],
                n_results=top_k,
                where={"niche": niche},
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            # Fallback for mock collection which doesn't use the exact same kwargs
            print(f"Query error (likely due to mock): {e}")
            results = self.collection.query(
                query_texts=[campaign_brief],
                n_results=top_k,
                where={"niche": niche}
            )

        if not results.get("metadatas") or not results["metadatas"][0]:
            return []

        ads = results["metadatas"][0]
        distances = results["distances"][0]

        # Cosine distance → similarity: similarity = 1 - distance
        for ad, dist in zip(ads, distances):
            ad["similarity_score"] = round(1 - dist, 4) if isinstance(dist, (int, float)) else 0.9

        return ads
