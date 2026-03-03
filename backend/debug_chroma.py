import sys
import os
sys.path.append(os.path.dirname(__file__))
from app import collection

all_p = collection.get(include=["metadatas"])
print(f"Total returned: {len(all_p['ids']) if all_p else 0}")
if all_p and all_p.get("metadatas"):
    print("Metadata type:", type(all_p["metadatas"]))
    print("First metadata:", all_p["metadatas"][0])
    print("Length of metadatas array:", len(all_p["metadatas"]))
else:
    print("No metadatas found")
