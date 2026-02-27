import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

CHUNKS_FILE = "data/processed/chunks.json"
INDEX_DIR = "data/index"

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def main():
    os.makedirs(INDEX_DIR, exist_ok=True)

    print("Loading chunks...")
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [chunk["text"] for chunk in chunks]

    print("Loading embedding model...")
    model = SentenceTransformer(EMBED_MODEL)

    print("Generating embeddings...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    dimension = embeddings.shape[1]

    print("Building FAISS index...")
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(INDEX_DIR, "faiss.index"))

    with open(os.path.join(INDEX_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print("\nIndex built successfully.")
    print(f"Total vectors indexed: {len(embeddings)}")


if __name__ == "__main__":
    main()