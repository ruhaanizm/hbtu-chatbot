import json
import os
import math

INPUT_FILE = "data/processed/corpus.json"
OUTPUT_FILE = "data/processed/chunks.json"

CHUNK_SIZE = 500
OVERLAP = 80


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    words = text.split()
    chunks = []

    start = 0
    chunk_id = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text
        })

        chunk_id += 1
        start = end - overlap

    return chunks


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    all_chunks = []

    for doc in corpus:
        doc_chunks = chunk_text(doc["text"])

        for chunk in doc_chunks:
            all_chunks.append({
                "doc_id": doc["doc_id"],
                "source_type": doc["source_type"],
                "score": doc["score"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"]
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nChunking complete.")
    print(f"Total chunks created: {len(all_chunks)}")


if __name__ == "__main__":
    main()