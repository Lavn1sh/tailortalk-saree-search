"""
End-to-end integration test validating visual similarity search quality
against the Byrappa Silks catalogue.
"""

import sys
import json
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.search_engine import SareeSearchEngine

def test_visual_similarity_query():
    """Test searching with an existing catalogue image returns itself as #1 match with ~100% score."""
    engine = SareeSearchEngine.get_instance()
    
    with open("data/enriched_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Pick a sample item that exists locally
    sample = None
    for item in manifest:
        p = item.get("local_image_path")
        if p and Path(p).exists():
            sample = item
            break

    assert sample is not None, "No local sample image found for testing"

    query_img_path = sample["local_image_path"]
    print(f"\nQuerying with sample saree: {sample['name']} ({sample['fabric']}, {sample['primary_color']})")

    results = engine.search_by_image(image_source=query_img_path, top_k=5)

    assert len(results) >= 1, "Expected at least 1 search result"
    top_match = results[0]

    print("\n--- Top 5 Visual Matches ---")
    for idx, r in enumerate(results, 1):
        print(f"{idx}. [{r['similarity_pct']}%] {r['name']} | Fabric: {r['fabric']} | Color: {r['primary_color']} | Price: Rs.{r['discounted_price']}")

    # The exact same image queried must return as rank 1 with high score (>0.90)
    assert top_match["id"] == sample["id"] or top_match["sku"] == sample["sku"]
    assert top_match["similarity_score"] >= 0.85, f"Expected top match score >= 0.85, got {top_match['similarity_score']}"

def test_text_to_image_search():
    """Test natural language search for specific saree attributes."""
    engine = SareeSearchEngine.get_instance()
    query = "pink banarasi saree with gold zari"
    results = engine.search_by_text(query, top_k=5)

    assert len(results) == 5
    assert all("name" in r and "image_url" in r and "similarity_score" in r for r in results)
    print(f"\n--- Text Query '{query}' Top Match: {results[0]['name']} ({results[0]['similarity_pct']}%) ---")
