"""
High-performance visual search engine for sarees.
Implements multi-layered retrieval: FashionCLIP visual embeddings +
HSV colour histogram re-ranking + metadata synergy.
"""

import os
import io
import base64
import requests
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Union, List, Dict, Any, Optional

from src.embeddings import FashionEmbeddingModel
from src.vector_store import SareeVectorStore
from src.colour_analysis import (
    compute_hsv_histogram,
    compare_color_histograms,
    extract_dominant_colors
)

COLOR_HIST_PATH = Path("data/color_histograms.npz")

# In-memory LRU cache for fetched query image URLs
_URL_IMAGE_CACHE: Dict[str, Image.Image] = {}

def _prepare_query_image(img: Image.Image, max_dim: int = 512) -> Image.Image:
    """Downscale query image if excessively large to accelerate CLIP and OpenCV processing."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    if max(img.size) > max_dim:
        img = img.copy()
        img.thumbnail((max_dim, max_dim), Image.Resampling.BILINEAR)
    return img

class SareeSearchEngine:
    _instance = None

    def __init__(self):
        self.embed_model = FashionEmbeddingModel.get_instance()
        self.vector_store = SareeVectorStore()
        self.color_histograms = {}
        self._load_color_histograms()

    def _load_color_histograms(self):
        if COLOR_HIST_PATH.exists():
            try:
                npz = np.load(COLOR_HIST_PATH)
                self.color_histograms = {k: npz[k] for k in npz.files}
                print(f"Loaded {len(self.color_histograms)} precomputed colour histograms.")
            except Exception as e:
                print(f"Warning: Could not load colour histograms from {COLOR_HIST_PATH}: {e}")
        else:
            print(f"Note: {COLOR_HIST_PATH} not found. Colour re-ranking will compute histograms on the fly.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def load_image_from_source(source: Union[str, bytes, Image.Image]) -> Image.Image:
        """
        Load a PIL Image from:
        - PIL Image instance
        - Image URL (http/https) with memory cache
        - Base64 string
        - Local file path
        - Raw bytes
        """
        if isinstance(source, Image.Image):
            return _prepare_query_image(source)

        if isinstance(source, bytes):
            return _prepare_query_image(Image.open(io.BytesIO(source)))

        if isinstance(source, str):
            source_str = source.strip()

            # Check in-memory cache for URLs
            if source_str in _URL_IMAGE_CACHE:
                return _URL_IMAGE_CACHE[source_str]

            # Check for data URL base64
            if source_str.startswith("data:image"):
                base64_data = source_str.split(",", 1)[1]
                img_bytes = base64.b64decode(base64_data)
                return _prepare_query_image(Image.open(io.BytesIO(img_bytes)))

            # Check for regular base64 string
            if len(source_str) > 200 and not source_str.startswith("http") and not os.path.exists(source_str):
                try:
                    img_bytes = base64.b64decode(source_str)
                    return _prepare_query_image(Image.open(io.BytesIO(img_bytes)))
                except Exception:
                    pass

            # Check for HTTP/HTTPS URL
            if source_str.startswith("http://") or source_str.startswith("https://"):
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(source_str, headers=headers, timeout=8)
                resp.raise_for_status()
                fetched_img = _prepare_query_image(Image.open(io.BytesIO(resp.content)))
                if len(_URL_IMAGE_CACHE) < 100:
                    _URL_IMAGE_CACHE[source_str] = fetched_img
                return fetched_img

            # Check for local file path
            if os.path.exists(source_str):
                return _prepare_query_image(Image.open(source_str))

        raise ValueError("Invalid image input format. Expected PIL Image, URL, file path, or Base64.")

    def search_by_image(
        self,
        image_source: Union[str, bytes, Image.Image],
        top_k: int = 5,
        over_retrieve: int = 40,
        clip_weight: float = 0.65,
        color_weight: float = 0.35,
        fabric_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform fine-grained visual similarity search with FashionCLIP + HSV color reranking.
        """
        # 1. Load and prepare query image
        query_image = self.load_image_from_source(image_source)

        # 2. Extract query visual embedding and color histogram
        query_embedding = self.embed_model.encode_image(query_image)
        query_hist = compute_hsv_histogram(query_image)
        query_dominant = extract_dominant_colors(query_image, k=2)

        # 3. Retrieve initial candidates from ChromaDB
        where_clause = None
        if fabric_filter:
            where_clause = {"fabric": fabric_filter}

        candidates = self.vector_store.search_by_vector(
            query_embedding=query_embedding,
            top_k=max(over_retrieve, top_k * 3),
            where_filter=where_clause
        )

        if not candidates:
            return []

        # 4. Multi-signal re-ranking
        ranked_results = []
        for cand in candidates:
            doc_id = cand["id"]
            meta = cand["metadata"]
            vec_sim = cand["vector_similarity"]

            # Compute or lookup color histogram similarity
            cand_hist = self.color_histograms.get(doc_id)
            if cand_hist is None:
                # If local file exists, compute
                local_p = meta.get("local_image_path")
                if local_p and os.path.exists(local_p):
                    try:
                        with Image.open(local_p) as cimg:
                            cand_hist = compute_hsv_histogram(cimg.convert("RGB"))
                            self.color_histograms[doc_id] = cand_hist
                    except Exception:
                        cand_hist = None

            if cand_hist is not None:
                color_sim = compare_color_histograms(query_hist, cand_hist)
            else:
                color_sim = vec_sim  # Fallback to vector sim if image missing

            # Calculate composite score
            composite_score = (clip_weight * vec_sim) + (color_weight * color_sim)

            # Generate dynamic match explanation
            fabric_name = meta.get("fabric", "Saree")
            primary_col = meta.get("primary_color", "")
            features_list = meta.get("features", "")

            explanation_parts = []
            if color_sim >= 0.70:
                explanation_parts.append(f"Highly harmonious {primary_col} palette")
            elif color_sim >= 0.50:
                explanation_parts.append(f"Matching tone in {primary_col}")

            if vec_sim >= 0.80:
                explanation_parts.append(f"identical weave & drape structure")
            elif vec_sim >= 0.65:
                explanation_parts.append(f"similar {fabric_name} texture & pattern")

            if features_list:
                explanation_parts.append(f"features {features_list}")

            explanation = f"Matched on {', '.join(explanation_parts)}." if explanation_parts else f"Visually cohesive {fabric_name}."

            ranked_results.append({
                "id": doc_id,
                "sku": meta.get("sku", ""),
                "name": meta.get("name", ""),
                "stock": meta.get("stock", 0),
                "retail_price": meta.get("retail_price", 0.0),
                "discounted_price": meta.get("discounted_price", 0.0),
                "image_url": meta.get("image_url", ""),
                "website_link": meta.get("website_link", ""),
                "fabric": fabric_name,
                "primary_color": primary_col,
                "features": features_list,
                "dominant_hex": meta.get("dominant_hex", ""),
                "similarity_score": round(float(composite_score), 4),
                "similarity_pct": round(float(composite_score) * 100, 1),
                "vector_score": round(float(vec_sim), 4),
                "color_score": round(float(color_sim), 4),
                "match_explanation": explanation
            })

        # 5. Sort by composite score descending
        ranked_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return ranked_results[:top_k]

    def search_by_text(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Natural language text search against the visual saree catalogue.
        """
        text_embedding = self.embed_model.encode_text(query_text)
        candidates = self.vector_store.search_by_vector(
            query_embedding=text_embedding,
            top_k=top_k
        )

        results = []
        for cand in candidates:
            meta = cand["metadata"]
            sim = cand["vector_similarity"]
            results.append({
                "id": cand["id"],
                "sku": meta.get("sku", ""),
                "name": meta.get("name", ""),
                "stock": meta.get("stock", 0),
                "retail_price": meta.get("retail_price", 0.0),
                "discounted_price": meta.get("discounted_price", 0.0),
                "image_url": meta.get("image_url", ""),
                "website_link": meta.get("website_link", ""),
                "fabric": meta.get("fabric", "Saree"),
                "primary_color": meta.get("primary_color", ""),
                "features": meta.get("features", ""),
                "dominant_hex": meta.get("dominant_hex", ""),
                "similarity_score": round(float(sim), 4),
                "similarity_pct": round(float(sim) * 100, 1),
                "vector_score": round(float(sim), 4),
                "color_score": round(float(sim), 4),
                "match_explanation": f"Matches search description '{query_text}'"
            })
        return results
