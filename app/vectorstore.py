import os
import json
import faiss
import numpy as np
from app.config import INDEX_DIR, TOP_K

_index = None
_metadata = None


def load_index():
    global _index, _metadata

    if _index is None:
        print("Loading FAISS index...")
        _index = faiss.read_index(os.path.join(INDEX_DIR, "faiss.index"))

        with open(os.path.join(INDEX_DIR, "metadata.json"), "r", encoding="utf-8") as f:
            _metadata = json.load(f)

    return _index, _metadata


def search(query_embedding):
    index, metadata = load_index()

    distances, indices = index.search(query_embedding, TOP_K)

    results = []

    for idx, score in zip(indices[0], distances[0]):
        if idx < len(metadata):
            results.append({
                "score": float(score),
                "text": metadata[idx]["text"],
                "doc_id": metadata[idx]["doc_id"]
            })

    return results