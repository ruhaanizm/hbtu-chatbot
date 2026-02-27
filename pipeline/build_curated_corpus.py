import os
import json

RANKED_FILE = "data/processed/review_candidates.json"
OUTPUT_FILE = "data/processed/corpus.json"

TOP_N = 250


def load_text(doc_id, source_type):
    if source_type == "pdf":
        path = os.path.join("data/processed/pdf_text", doc_id)
    else:
        path = os.path.join("data/raw/html", doc_id)

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def main():
    with open(RANKED_FILE, "r", encoding="utf-8") as f:
        ranked_docs = json.load(f)

    selected = ranked_docs[:TOP_N]
    corpus = []

    for doc in selected:
        # Hard filters
        if doc["alphabet_ratio"] < 0.5:
            continue
        if doc["digit_ratio"] > 0.25:
            continue
        if doc["length"] < 500 or doc["length"] > 200000:
            continue

        full_text = load_text(doc["id"], doc["source_type"])
        full_text = full_text.strip()

        # Limit document size (25k words max)
        words = full_text.split()
        MAX_WORDS = 8000

        words = full_text.split()
        if len(words) > MAX_WORDS:
            full_text = " ".join(words[:MAX_WORDS])

        if len(full_text) < 500:
            continue

        corpus.append({
            "doc_id": doc["id"],
            "source_type": doc["source_type"],
            "score": doc["score"],
            "text": full_text
        })

    os.makedirs("data/processed", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)

    print(f"\nCurated corpus created: {OUTPUT_FILE}")
    print(f"Total documents kept: {len(corpus)}")


if __name__ == "__main__":
    main()