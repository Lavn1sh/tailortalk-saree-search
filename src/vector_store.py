"""
Vector Store module managing persistent ChromaDB index for saree embeddings.
"""

import os
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "saree_catalogue"

class SareeVectorStore:
    def __init__(self, persist_directory: Path = CHROMA_DIR):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def count(self) -> int:
        return self.collection.count()

    def add_items(
        self,
        ids: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict[str, Any]],
        documents: List[str]
    ):
        """Add batch of embedded saree products to ChromaDB."""
        # Convert numpy embeddings to python list of floats
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        # Clean metadata values to primitive types supported by ChromaDB
        cleaned_metadatas = []
        for m in metadatas:
            clean_m = {}
            for k, v in m.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_m[k] = v
                elif isinstance(v, list):
                    clean_m[k] = ", ".join(str(x) for x in v)
                elif v is None:
                    clean_m[k] = ""
                else:
                    clean_m[k] = str(v)
            cleaned_metadatas.append(clean_m)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings_list,
            metadatas=cleaned_metadatas,
            documents=documents
        )

    def search_by_vector(
        self,
        query_embedding: np.ndarray,
        top_k: int = 50,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query ChromaDB by embedding vector.
        Returns candidates with distance, metadata, and id.
        """
        if isinstance(query_embedding, np.ndarray):
            query_emb = query_embedding.tolist()
        else:
            query_emb = query_embedding

        kwargs = {
            "query_embeddings": [query_emb],
            "n_results": min(top_k, max(1, self.count())),
            "include": ["metadatas", "distances", "documents"]
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)
        
        candidates = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for idx in range(len(results["ids"][0])):
                doc_id = results["ids"][0][idx]
                meta = results["metadatas"][0][idx] if results["metadatas"] else {}
                dist = results["distances"][0][idx] if results["distances"] else 0.0
                doc = results["documents"][0][idx] if results["documents"] else ""
                
                # Cosine distance in Chroma is 1 - cosine_similarity (range 0 to 2)
                # Convert to cosine similarity [0, 1]
                cosine_sim = max(0.0, min(1.0, 1.0 - (dist / 2.0)))

                candidates.append({
                    "id": doc_id,
                    "metadata": meta,
                    "document": doc,
                    "cosine_distance": float(dist),
                    "vector_similarity": float(cosine_sim)
                })

        return candidates
