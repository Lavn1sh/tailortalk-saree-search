"""
Script to build the ChromaDB vector index and precompute HSV colour histograms
for the entire saree catalogue.
"""

import os
import sys
import json
import time
from pathlib import Path
import numpy as np
from PIL import Image
from tqdm import tqdm

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.embeddings import FashionEmbeddingModel
from src.vector_store import SareeVectorStore
from src.colour_analysis import compute_hsv_histogram, extract_dominant_colors

ENRICHED_MANIFEST_PATH = Path("data/enriched_manifest.json")
COLOR_HIST_PATH = Path("data/color_histograms.npz")
COLOR_PALETTES_PATH = Path("data/color_palettes.json")

def main():
    if not ENRICHED_MANIFEST_PATH.exists():
        print(f"Error: {ENRICHED_MANIFEST_PATH} not found. Run download_images.py and enhance_metadata.py first.")
        return

    with open(ENRICHED_MANIFEST_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"Loaded {len(items)} enriched saree items.")

    # Initialize Embedding Model & ChromaDB
    embed_model = FashionEmbeddingModel.get_instance()
    vector_store = SareeVectorStore()

    valid_items = []
    pil_images = []
    color_histograms = {}
    color_palettes = {}

    print("\n[Step 1/3] Loading images and computing HSV colour histograms...")
    for item in tqdm(items, desc="Processing Images"):
        local_path = item.get("local_image_path")
        if not local_path or not Path(local_path).exists():
            continue

        try:
            with Image.open(local_path) as img:
                rgb_img = img.convert("RGB")
                # Compute color histogram
                hist = compute_hsv_histogram(rgb_img)
                color_histograms[item["id"]] = hist

                # Extract dominant colors
                palettes = extract_dominant_colors(rgb_img, k=3)
                color_palettes[item["id"]] = palettes

                # Keep in memory for batch embedding
                # Resize to max 384 for fast batch processing
                resized = rgb_img.resize((224, 224), Image.Resampling.BICUBIC)
                pil_images.append(resized)
                valid_items.append(item)
        except Exception as e:
            print(f"Warning: Could not process {local_path}: {e}")

    print(f"\nSuccessfully processed {len(valid_items)} images.")

    # Save Color Histograms NPZ
    np.savez_compressed(COLOR_HIST_PATH, **color_histograms)
    print(f"Saved {len(color_histograms)} colour histograms -> {COLOR_HIST_PATH}")

    # Save Color Palettes JSON
    with open(COLOR_PALETTES_PATH, "w", encoding="utf-8") as f:
        json.dump(color_palettes, f, indent=2)
    print(f"Saved colour palettes -> {COLOR_PALETTES_PATH}")

    print("\n[Step 2/3] Generating FashionCLIP visual embeddings...")
    start_embed = time.time()
    embeddings = embed_model.encode_images_batch(pil_images, batch_size=32)
    print(f"Generated {embeddings.shape} embeddings in {time.time() - start_embed:.2f}s")

    print("\n[Step 3/3] Upserting to ChromaDB vector store...")
    ids = [item["id"] for item in valid_items]
    metadatas = []
    documents = []

    for item in valid_items:
        # Include dominant colors in metadata for rich display
        palettes = color_palettes.get(item["id"], [])
        hex_colors = [p["hex"] for p in palettes]

        meta = {
            "sku": item.get("sku", ""),
            "name": item.get("name", ""),
            "stock": item.get("stock", 0),
            "retail_price": item.get("retail_price", 0.0),
            "discounted_price": item.get("discounted_price", 0.0),
            "image_url": item.get("image_url", ""),
            "website_link": item.get("website_link", ""),
            "local_image_path": item.get("local_image_path", ""),
            "fabric": item.get("fabric", "Saree"),
            "primary_color": item.get("primary_color", "Classic"),
            "features": item.get("features", []),
            "dominant_hex": hex_colors
        }
        metadatas.append(meta)
        documents.append(item.get("text_description", item.get("name", "")))

    vector_store.add_items(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )

    print(f"\nSuccessfully indexed {vector_store.count()} sarees in ChromaDB ({vector_store.persist_directory})!")
    print("Vector Indexing Completed Successfully.")

if __name__ == "__main__":
    main()
