"""
ChromaDB Optimization Service
Phase 5, Day 6: Query Performance and ERS-Based Retrieval
"""
import time
from typing import Dict, List, Optional, Tuple


class ChromaDBOptimizer:
    """Service for optimized ChromaDB queries with ERS-based retrieval"""
    
    def __init__(self, collection):
        """
        Initialize optimizer
        
        Args:
            collection: ChromaDB collection instance
        """
        self.collection = collection
    
    def query_by_ers(
        self,
        min_ers: Optional[float] = None,
        max_ers: Optional[float] = None,
        limit: int = 10,
        include_metadata: bool = True
    ) -> Dict:
        """
        Query posts by ERS range with performance tracking
        
        Args:
            min_ers: Minimum ERS score (optional)
            max_ers: Maximum ERS score (optional)
            limit: Maximum number of results
            include_metadata: Whether to include metadata
            
        Returns:
            Dict with results and performance metrics
        """
        start_time = time.time()
        
        # Build where clause
        where_clause = {}
        if min_ers is not None and max_ers is not None:
            where_clause = {
                "$and": [
                    {"ers": {"$gte": min_ers}},
                    {"ers": {"$lte": max_ers}}
                ]
            }
        elif min_ers is not None:
            where_clause = {"ers": {"$gte": min_ers}}
        elif max_ers is not None:
            where_clause = {"ers": {"$lte": max_ers}}
        
        # Query with where clause
        include_list = ["documents", "metadatas"] if include_metadata else ["documents"]
        
        try:
            if where_clause:
                results = self.collection.get(
                    where=where_clause,
                    limit=limit,
                    include=include_list
                )
            else:
                results = self.collection.get(
                    limit=limit,
                    include=include_list
                )
            
            query_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "success": True,
                "results": results,
                "count": len(results.get("ids", [])),
                "query_time_ms": round(query_time, 2),
                "performance": "excellent" if query_time < 50 else "good" if query_time < 100 else "slow"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_time_ms": (time.time() - start_time) * 1000
            }
    
    def query_winners_only(
        self,
        limit: int = 10,
        platform: Optional[str] = None
    ) -> Dict:
        """
        Query only winner posts with optional platform filter
        
        Args:
            limit: Maximum number of results
            platform: Optional platform filter (instagram, linkedin, twitter)
            
        Returns:
            Dict with results and performance metrics
        """
        start_time = time.time()
        
        # Build where clause
        if platform:
            where_clause = {
                "$and": [
                    {"is_winner": True},
                    {"source": platform}
                ]
            }
        else:
            where_clause = {"is_winner": True}
        
        try:
            results = self.collection.get(
                where=where_clause,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            query_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "results": results,
                "count": len(results.get("ids", [])),
                "query_time_ms": round(query_time, 2),
                "performance": "excellent" if query_time < 50 else "good" if query_time < 100 else "slow"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_time_ms": (time.time() - start_time) * 1000
            }
    
    def query_by_percentile(
        self,
        max_percentile: float = 0.2,
        limit: int = 10
    ) -> Dict:
        """
        Query posts by percentile rank (e.g., top 20%)
        
        Args:
            max_percentile: Maximum percentile rank (0.2 = top 20%)
            limit: Maximum number of results
            
        Returns:
            Dict with results and performance metrics
        """
        start_time = time.time()
        
        try:
            results = self.collection.get(
                where={"percentile_rank": {"$lte": max_percentile}},
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            query_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "results": results,
                "count": len(results.get("ids", [])),
                "query_time_ms": round(query_time, 2),
                "performance": "excellent" if query_time < 50 else "good" if query_time < 100 else "slow"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_time_ms": (time.time() - start_time) * 1000
            }
    
    def semantic_search_with_ers_boost(
        self,
        query_embedding: List[float],
        min_ers: Optional[float] = None,
        n_results: int = 10,
        ers_weight: float = 0.3
    ) -> Dict:
        """
        Semantic search with ERS score boosting
        
        Combines semantic similarity with ERS scores for better results.
        Higher ERS posts get a boost in ranking.
        
        Args:
            query_embedding: Query vector embedding
            min_ers: Minimum ERS threshold (optional)
            n_results: Number of results to return
            ers_weight: Weight for ERS boost (0.0-1.0)
            
        Returns:
            Dict with results and performance metrics
        """
        start_time = time.time()
        
        try:
            # Build where clause
            where_clause = {"ers": {"$gte": min_ers}} if min_ers is not None else None
            
            # Perform semantic search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results * 2,  # Get more results for re-ranking
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Re-rank with ERS boost
            ranked_results = self._rerank_with_ers(
                results,
                ers_weight=ers_weight,
                limit=n_results
            )
            
            query_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "results": ranked_results,
                "count": len(ranked_results.get("ids", [])),
                "query_time_ms": round(query_time, 2),
                "performance": "excellent" if query_time < 100 else "good" if query_time < 200 else "slow"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_time_ms": (time.time() - start_time) * 1000
            }
    
    def _rerank_with_ers(
        self,
        results: Dict,
        ers_weight: float = 0.3,
        limit: int = 10
    ) -> Dict:
        """
        Re-rank search results by combining semantic similarity and ERS
        
        Args:
            results: ChromaDB query results
            ers_weight: Weight for ERS score (0.0-1.0)
            limit: Number of results to return
            
        Returns:
            Re-ranked results
        """
        if not results.get("ids") or not results["ids"][0]:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        # Extract results
        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        
        # Calculate combined scores
        scored_items = []
        for i, (id, doc, meta, dist) in enumerate(zip(ids, documents, metadatas, distances)):
            # Semantic similarity (1 - distance, normalized to 0-1)
            semantic_score = max(0, 1 - dist)
            
            # ERS score (normalized to 0-1, assuming max ERS ~500)
            ers_score = min(1.0, meta.get("ers", 0) / 500.0)
            
            # Combined score
            combined_score = (semantic_score * (1 - ers_weight)) + (ers_score * ers_weight)
            
            scored_items.append({
                "id": id,
                "document": doc,
                "metadata": meta,
                "distance": dist,
                "semantic_score": semantic_score,
                "ers_score": ers_score,
                "combined_score": combined_score
            })
        
        # Sort by combined score
        scored_items.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # Take top N
        top_items = scored_items[:limit]
        
        # Reconstruct results format
        return {
            "ids": [[item["id"] for item in top_items]],
            "documents": [[item["document"] for item in top_items]],
            "metadatas": [[item["metadata"] for item in top_items]],
            "distances": [[item["distance"] for item in top_items]],
            "scores": [[item["combined_score"] for item in top_items]]
        }
    
    def benchmark_queries(self, iterations: int = 10) -> Dict:
        """
        Benchmark different query types for performance analysis
        
        Args:
            iterations: Number of iterations per query type
            
        Returns:
            Dict with benchmark results
        """
        benchmarks = {}
        
        # Benchmark 1: Simple get all
        times = []
        for _ in range(iterations):
            start = time.time()
            self.collection.get(limit=10, include=["documents"])
            times.append((time.time() - start) * 1000)
        benchmarks["get_all"] = {
            "avg_ms": round(sum(times) / len(times), 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2)
        }
        
        # Benchmark 2: ERS range query
        times = []
        for _ in range(iterations):
            start = time.time()
            self.collection.get(
                where={"ers": {"$gte": 50}},
                limit=10,
                include=["documents", "metadatas"]
            )
            times.append((time.time() - start) * 1000)
        benchmarks["ers_range"] = {
            "avg_ms": round(sum(times) / len(times), 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2)
        }
        
        # Benchmark 3: Winner query
        times = []
        for _ in range(iterations):
            start = time.time()
            self.collection.get(
                where={"is_winner": True},
                limit=10,
                include=["documents", "metadatas"]
            )
            times.append((time.time() - start) * 1000)
        benchmarks["winners_only"] = {
            "avg_ms": round(sum(times) / len(times), 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2)
        }
        
        # Benchmark 4: Complex AND query
        times = []
        for _ in range(iterations):
            start = time.time()
            self.collection.get(
                where={
                    "$and": [
                        {"is_winner": True},
                        {"source": "instagram"}
                    ]
                },
                limit=10,
                include=["documents", "metadatas"]
            )
            times.append((time.time() - start) * 1000)
        benchmarks["complex_and"] = {
            "avg_ms": round(sum(times) / len(times), 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2)
        }
        
        return {
            "iterations": iterations,
            "benchmarks": benchmarks,
            "summary": {
                "fastest": min(b["avg_ms"] for b in benchmarks.values()),
                "slowest": max(b["avg_ms"] for b in benchmarks.values()),
                "all_under_100ms": all(b["avg_ms"] < 100 for b in benchmarks.values())
            }
        }
    
    def get_metadata_schema(self) -> Dict:
        """
        Get current metadata schema from collection
        
        Returns:
            Dict with schema information
        """
        try:
            # Get a sample of documents
            sample = self.collection.get(limit=5, include=["metadatas"])
            
            if not sample.get("metadatas"):
                return {
                    "success": False,
                    "message": "No documents in collection"
                }
            
            # Extract all unique metadata keys
            all_keys = set()
            for metadata in sample["metadatas"]:
                all_keys.update(metadata.keys())
            
            # Determine types
            schema = {}
            for key in all_keys:
                # Get first non-None value for type detection
                sample_value = None
                for metadata in sample["metadatas"]:
                    if key in metadata and metadata[key] is not None:
                        sample_value = metadata[key]
                        break
                
                schema[key] = {
                    "type": type(sample_value).__name__ if sample_value is not None else "unknown",
                    "present_in_sample": sum(1 for m in sample["metadatas"] if key in m)
                }
            
            return {
                "success": True,
                "schema": schema,
                "sample_size": len(sample["metadatas"]),
                "total_fields": len(schema)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
