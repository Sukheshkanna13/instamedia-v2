"""
Test Winner Filter Functionality
Phase 5, Day 5
"""
from services.apify_ingestion import ApifyIngestionService

# Mock collection and embedder
class MockCollection:
    def __init__(self):
        self.items = []
    
    def add(self, documents, metadatas, ids):
        for doc, meta, id in zip(documents, metadatas, ids):
            self.items.append({"doc": doc, "meta": meta, "id": id})

def mock_embedder(text):
    return [0.1] * 384

print("🧪 Testing Winner Filter\n")

# Create service
service = ApifyIngestionService(
    apify_client=None,
    collection=MockCollection(),
    embedder=mock_embedder
)

# Test data: 10 posts with varying ERS scores
test_posts = [
    {"text": "Post 1", "ers": 100, "likesCount": 500, "commentsCount": 0, "sharesCount": 0},
    {"text": "Post 2", "ers": 90, "likesCount": 450, "commentsCount": 0, "sharesCount": 0},
    {"text": "Post 3", "ers": 80, "likesCount": 400, "commentsCount": 0, "sharesCount": 0},
    {"text": "Post 4", "ers": 70, "likesCount": 350, "commentsCount": 0, "sharesCount": 0},
    {"text": "Post 5", "ers": 60, "likesCount": 300, "commentsCount": 0, "sharesCount": 0},
    {"text": "Post 6", "ers": 50, "likesCount": 250, "commentsCount": 0, "sharesCount": 0},
    {"text": "Post 7", "ers": 40, "likesCount": 200, "commentsCount": 0, "sharesCount": 0},
    {"text": "Post 8", "ers": 30, "likesCount": 150, "commentsCount": 0, "sharesCount": 0},
    {"text": "Post 9", "ers": 20, "likesCount": 100, "commentsCount": 0, "sharesCount": 0},
    {"text": "Post 10", "ers": 10, "likesCount": 50, "commentsCount": 0, "sharesCount": 0},
]

print("📊 Test Data:")
print(f"   Total posts: {len(test_posts)}")
print(f"   ERS range: {min(p['ers'] for p in test_posts)} - {max(p['ers'] for p in test_posts)}")
print(f"   Average ERS: {sum(p['ers'] for p in test_posts) / len(test_posts):.2f}\n")

# Test 1: Top 20% (default)
print("1️⃣ Testing top 20% filter...")
result = service.filter_top_performers(test_posts, percentile=0.2)

print(f"   Total posts: {result['total_posts']}")
print(f"   Winners: {result['winner_count']}")
print(f"   Cutoff ERS: {result['cutoff_ers']:.2f}")
print(f"   Winner avg ERS: {result['winner_avg_ers']:.2f}")
print(f"   Overall avg ERS: {result['overall_avg_ers']:.2f}")
print(f"   Improvement ratio: {result['improvement_ratio']:.2f}x")

expected_winners = 2  # 20% of 10 = 2
status = "✅" if result['winner_count'] == expected_winners else "❌"
print(f"   {status} Expected {expected_winners} winners, got {result['winner_count']}")

# Verify winners are top posts
winner_ers = [p['ers'] for p in result['winners']]
print(f"   Winner ERS scores: {winner_ers}")
expected_ers = [100, 90]
status = "✅" if winner_ers == expected_ers else "❌"
print(f"   {status} Winners have highest ERS scores\n")

# Test 2: Top 50%
print("2️⃣ Testing top 50% filter...")
result = service.filter_top_performers(test_posts, percentile=0.5)

print(f"   Winners: {result['winner_count']}")
print(f"   Cutoff ERS: {result['cutoff_ers']:.2f}")
print(f"   Improvement ratio: {result['improvement_ratio']:.2f}x")

expected_winners = 5  # 50% of 10 = 5
status = "✅" if result['winner_count'] == expected_winners else "❌"
print(f"   {status} Expected {expected_winners} winners, got {result['winner_count']}\n")

# Test 3: Top 10%
print("3️⃣ Testing top 10% filter...")
result = service.filter_top_performers(test_posts, percentile=0.1)

print(f"   Winners: {result['winner_count']}")
print(f"   Cutoff ERS: {result['cutoff_ers']:.2f}")
print(f"   Improvement ratio: {result['improvement_ratio']:.2f}x")

expected_winners = 1  # 10% of 10 = 1 (minimum 1)
status = "✅" if result['winner_count'] == expected_winners else "❌"
print(f"   {status} Expected {expected_winners} winner, got {result['winner_count']}\n")

# Test 4: Empty list
print("4️⃣ Testing empty list...")
result = service.filter_top_performers([], percentile=0.2)

print(f"   Winners: {result['winner_count']}")
print(f"   Total posts: {result['total_posts']}")
status = "✅" if result['winner_count'] == 0 else "❌"
print(f"   {status} Handles empty list correctly\n")

# Test 5: Verify metadata
print("5️⃣ Testing winner metadata...")
result = service.filter_top_performers(test_posts, percentile=0.2)

for i, winner in enumerate(result['winners'], 1):
    has_flag = winner.get('is_winner', False)
    has_rank = 'percentile_rank' in winner
    status = "✅" if has_flag and has_rank else "❌"
    print(f"   {status} Winner {i}: is_winner={has_flag}, percentile_rank={winner.get('percentile_rank', 0):.2f}")

print("\n✅ All tests complete!")
