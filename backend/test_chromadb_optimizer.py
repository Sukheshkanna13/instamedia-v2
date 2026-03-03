"""
Test ChromaDB Optimizer
Phase 5, Day 6
"""
import time
from services.chromadb_optimizer import ChromaDBOptimizer

# Mock ChromaDB collection with test data
class MockCollection:
    def __init__(self):
        # Create test data: 20 posts with varying ERS scores
        self.items = []
        for i in range(20):
            ers = 100 - (i * 5)  # ERS from 100 down to 5
            is_winner = i < 4  # Top 20% (4 of 20)
            percentile_rank = (i + 1) / 20
            
            self.items.append({
                "id": f"post_{i}",
                "doc": f"Test post {i} with ERS {ers}",
                "meta": {
                    "ers": ers,
                    "is_winner": is_winner,
                    "percentile_rank": percentile_rank,
                    "source": "instagram" if i % 2 == 0 else "linkedin",
                    "likes": ers * 5,
                    "comments": ers // 10,
                    "shares": ers // 20
                }
            })
    
    def count(self):
        return len(self.items)
    
    def get(self, where=None, limit=None, include=None):
        # Filter by where clause
        filtered = self.items
        
        if where:
            filtered = self._apply_where(filtered, where)
        
        # Apply limit
        if limit:
            filtered = filtered[:limit]
        
        # Return in ChromaDB format
        return {
            "ids": [item["id"] for item in filtered],
            "documents": [item["doc"] for item in filtered],
            "metadatas": [item["meta"] for item in filtered]
        }
    
    def query(self, query_embeddings, n_results, where=None, include=None):
        # Mock semantic search - just return top N by ERS
        filtered = self.items
        
        if where:
            filtered = self._apply_where(filtered, where)
        
        # Sort by ERS (mock semantic similarity)
        filtered = sorted(filtered, key=lambda x: x["meta"]["ers"], reverse=True)
        filtered = filtered[:n_results]
        
        # Calculate mock distances (inverse of ERS, normalized)
        max_ers = 100
        distances = [1 - (item["meta"]["ers"] / max_ers) for item in filtered]
        
        return {
            "ids": [[item["id"] for item in filtered]],
            "documents": [[item["doc"] for item in filtered]],
            "metadatas": [[item["meta"] for item in filtered]],
            "distances": [distances]
        }
    
    def _apply_where(self, items, where):
        """Apply where clause filtering"""
        if "$and" in where:
            # Handle AND conditions
            for condition in where["$and"]:
                items = self._apply_single_condition(items, condition)
            return items
        else:
            # Single condition
            return self._apply_single_condition(items, where)
    
    def _apply_single_condition(self, items, condition):
        """Apply a single where condition"""
        filtered = []
        for item in items:
            meta = item["meta"]
            match = True
            
            for key, value in condition.items():
                if isinstance(value, dict):
                    # Handle operators like $gte, $lte
                    if "$gte" in value:
                        if not (key in meta and meta[key] >= value["$gte"]):
                            match = False
                    if "$lte" in value:
                        if not (key in meta and meta[key] <= value["$lte"]):
                            match = False
                else:
                    # Direct equality
                    if not (key in meta and meta[key] == value):
                        match = False
            
            if match:
                filtered.append(item)
        
        return filtered

print("🧪 Testing ChromaDB Optimizer\n")

# Initialize
collection = MockCollection()
optimizer = ChromaDBOptimizer(collection)

print(f"📊 Test Data: {collection.count()} posts\n")

# Test 1: Query by ERS range
print("1️⃣ Testing ERS range query...")
result = optimizer.query_by_ers(min_ers=50, max_ers=100, limit=10)

if result["success"]:
    print(f"   ✅ Found {result['count']} posts")
    print(f"   Query time: {result['query_time_ms']}ms")
    print(f"   Performance: {result['performance']}")
    
    # Verify ERS range
    ers_scores = [m["ers"] for m in result["results"]["metadatas"]]
    all_in_range = all(50 <= ers <= 100 for ers in ers_scores)
    print(f"   {'✅' if all_in_range else '❌'} All results in ERS range 50-100")
else:
    print(f"   ❌ Error: {result['error']}")

# Test 2: Query winners only
print("\n2️⃣ Testing winners-only query...")
result = optimizer.query_winners_only(limit=10)

if result["success"]:
    print(f"   ✅ Found {result['count']} winners")
    print(f"   Query time: {result['query_time_ms']}ms")
    print(f"   Performance: {result['performance']}")
    
    # Verify all are winners
    all_winners = all(m["is_winner"] for m in result["results"]["metadatas"])
    print(f"   {'✅' if all_winners else '❌'} All results are winners")
else:
    print(f"   ❌ Error: {result['error']}")

# Test 3: Query by percentile
print("\n3️⃣ Testing percentile query (top 20%)...")
result = optimizer.query_by_percentile(max_percentile=0.2, limit=10)

if result["success"]:
    print(f"   ✅ Found {result['count']} posts")
    print(f"   Query time: {result['query_time_ms']}ms")
    print(f"   Performance: {result['performance']}")
    
    # Verify percentile range
    percentiles = [m["percentile_rank"] for m in result["results"]["metadatas"]]
    all_in_range = all(p <= 0.2 for p in percentiles)
    print(f"   {'✅' if all_in_range else '❌'} All results in top 20%")
    print(f"   Percentile range: {min(percentiles):.2f} - {max(percentiles):.2f}")
else:
    print(f"   ❌ Error: {result['error']}")

# Test 4: Winners by platform
print("\n4️⃣ Testing winners by platform (Instagram)...")
result = optimizer.query_winners_only(limit=10, platform="instagram")

if result["success"]:
    print(f"   ✅ Found {result['count']} Instagram winners")
    print(f"   Query time: {result['query_time_ms']}ms")
    
    # Verify platform
    all_instagram = all(m["source"] == "instagram" for m in result["results"]["metadatas"])
    all_winners = all(m["is_winner"] for m in result["results"]["metadatas"])
    print(f"   {'✅' if all_instagram else '❌'} All results from Instagram")
    print(f"   {'✅' if all_winners else '❌'} All results are winners")
else:
    print(f"   ❌ Error: {result['error']}")

# Test 5: Semantic search with ERS boost
print("\n5️⃣ Testing semantic search with ERS boost...")
mock_embedding = [0.1] * 384  # Mock query embedding
result = optimizer.semantic_search_with_ers_boost(
    query_embedding=mock_embedding,
    min_ers=30,
    n_results=5,
    ers_weight=0.3
)

if result["success"]:
    print(f"   ✅ Found {result['count']} posts")
    print(f"   Query time: {result['query_time_ms']}ms")
    print(f"   Performance: {result['performance']}")
    
    # Show combined scores
    if "scores" in result["results"]:
        scores = result["results"]["scores"][0]
        print(f"   Combined scores: {[round(s, 3) for s in scores[:3]]}")
else:
    print(f"   ❌ Error: {result['error']}")

# Test 6: Benchmark queries
print("\n6️⃣ Running query benchmarks (10 iterations each)...")
benchmarks = optimizer.benchmark_queries(iterations=10)

print(f"\n   📊 Benchmark Results:")
for query_type, metrics in benchmarks["benchmarks"].items():
    print(f"\n   {query_type}:")
    print(f"      Avg: {metrics['avg_ms']}ms")
    print(f"      Min: {metrics['min_ms']}ms")
    print(f"      Max: {metrics['max_ms']}ms")

print(f"\n   Summary:")
print(f"      Fastest query: {benchmarks['summary']['fastest']}ms")
print(f"      Slowest query: {benchmarks['summary']['slowest']}ms")
print(f"      All under 100ms: {'✅ Yes' if benchmarks['summary']['all_under_100ms'] else '❌ No'}")

# Test 7: Get metadata schema
print("\n7️⃣ Testing metadata schema detection...")
result = optimizer.get_metadata_schema()

if result["success"]:
    print(f"   ✅ Schema detected")
    print(f"   Total fields: {result['total_fields']}")
    print(f"   Sample size: {result['sample_size']}")
    print(f"\n   Fields:")
    for field, info in result["schema"].items():
        print(f"      - {field}: {info['type']}")
else:
    print(f"   ❌ Error: {result['error']}")

print("\n✅ All tests complete!")
