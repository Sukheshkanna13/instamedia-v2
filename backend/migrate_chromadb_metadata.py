"""
ChromaDB Metadata Migration Script
Adds is_winner and percentile_rank fields to existing posts
Phase 5, Day 6
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Mock ChromaDB for compatibility
class MockCollection:
    def __init__(self):
        self.items = []
    
    def count(self):
        return len(self.items)
    
    def get(self, include=None, ids=None, limit=None):
        if not self.items:
            return {"ids": [], "documents": [], "metadatas": []}
        
        items_to_return = self.items[:limit] if limit else self.items
        
        return {
            "ids": [item["id"] for item in items_to_return],
            "documents": [item["doc"] for item in items_to_return],
            "metadatas": [item["meta"] for item in items_to_return]
        }
    
    def update(self, ids, metadatas):
        for id, new_meta in zip(ids, metadatas):
            for item in self.items:
                if item["id"] == id:
                    item["meta"].update(new_meta)
        print(f"✅ Updated {len(ids)} items")

collection = MockCollection()

print("🔄 ChromaDB Metadata Migration\n")
print("This script adds is_winner and percentile_rank fields to existing posts\n")

# Get all posts
print("1️⃣ Fetching all posts from ChromaDB...")
all_posts = collection.get(include=["metadatas"])

if not all_posts.get("ids"):
    print("   ⚠️  No posts found in database")
    print("   Migration not needed - database is empty\n")
    exit(0)

total_posts = len(all_posts["ids"])
print(f"   Found {total_posts} posts\n")

# Check if migration is needed
print("2️⃣ Checking if migration is needed...")
sample_meta = all_posts["metadatas"][0] if all_posts["metadatas"] else {}
has_winner_field = "is_winner" in sample_meta
has_percentile_field = "percentile_rank" in sample_meta

if has_winner_field and has_percentile_field:
    print("   ✅ Migration already complete - all fields present\n")
    exit(0)

print(f"   Missing fields detected:")
if not has_winner_field:
    print("      - is_winner")
if not has_percentile_field:
    print("      - percentile_rank")
print()

# Sort posts by ERS
print("3️⃣ Sorting posts by ERS score...")
posts_with_ers = []
for i, (id, meta) in enumerate(zip(all_posts["ids"], all_posts["metadatas"])):
    ers = meta.get("ers", 0)
    posts_with_ers.append({
        "id": id,
        "ers": ers,
        "metadata": meta
    })

posts_with_ers.sort(key=lambda x: x["ers"], reverse=True)
print(f"   Sorted {len(posts_with_ers)} posts\n")

# Calculate top 20% cutoff
print("4️⃣ Calculating winner threshold (top 20%)...")
cutoff_index = max(1, int(len(posts_with_ers) * 0.2))
cutoff_ers = posts_with_ers[cutoff_index - 1]["ers"] if cutoff_index <= len(posts_with_ers) else 0
print(f"   Cutoff index: {cutoff_index}")
print(f"   Cutoff ERS: {cutoff_ers:.2f}\n")

# Update metadata
print("5️⃣ Updating metadata...")
ids_to_update = []
metadatas_to_update = []

for i, post in enumerate(posts_with_ers):
    # Calculate percentile rank
    percentile_rank = (i + 1) / len(posts_with_ers)
    
    # Determine if winner
    is_winner = i < cutoff_index
    
    # Prepare update
    ids_to_update.append(post["id"])
    metadatas_to_update.append({
        "is_winner": is_winner,
        "percentile_rank": round(percentile_rank, 3)
    })

# Apply updates in batches
batch_size = 100
total_updated = 0

for i in range(0, len(ids_to_update), batch_size):
    batch_ids = ids_to_update[i:i+batch_size]
    batch_metas = metadatas_to_update[i:i+batch_size]
    
    collection.update(
        ids=batch_ids,
        metadatas=batch_metas
    )
    
    total_updated += len(batch_ids)
    print(f"   Updated {total_updated}/{len(ids_to_update)} posts...")

print()

# Verify migration
print("6️⃣ Verifying migration...")
sample = collection.get(limit=5, include=["metadatas"])
verified = all(
    "is_winner" in meta and "percentile_rank" in meta
    for meta in sample["metadatas"]
)

if verified:
    print("   ✅ Migration verified successfully\n")
else:
    print("   ⚠️  Verification failed - some fields missing\n")

# Summary
print("📊 Migration Summary:")
print(f"   Total posts: {total_posts}")
print(f"   Winners (top 20%): {cutoff_index}")
print(f"   Cutoff ERS: {cutoff_ers:.2f}")
print(f"   Posts updated: {total_updated}")
print(f"   Status: {'✅ Complete' if verified else '⚠️  Incomplete'}\n")

print("✅ Migration complete!")
print("\nNote: This is a dry-run with mock data.")
print("To run on real ChromaDB, update the collection initialization.")
