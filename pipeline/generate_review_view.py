# pipeline/generate_review_view.py

import json
import os
import re
from collections import Counter

INPUT_FILE = "data/processed/review_candidates.json"
OUTPUT_FILE = "data/processed/review_top250.json"

TOP_N = 250


def extract_keywords(text, top_k=10):
    words = re.findall(r'\b\w{4,}\b', text.lower())
    stopwords = {
        "the", "and", "with", "from", "that", "this",
        "have", "been", "will", "shall", "http", "https",
        "www", "hbtu", "kanpur"
    }
    words = [w for w in words if w not in stopwords]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_k)]


def load_full_text(doc_id, source_type):
    if source_type == "pdf":
        path = os.path.join("data/processed/pdf_text", doc_id)
    else:
        path = os.path.join("data/raw/html", doc_id)

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def guess_category(text):
    text_l = text.lower()

    categories = {
        "admission": ["admission", "प्रवेश", "eligibility", "counselling"],
        "hostel": ["hostel", "छात्रावास", "mess", "warden"],
        "exam": ["exam", "परीक्षा", "semester", "result"],
        "placement": ["placement", "प्लेसमेंट", "training"],
        "department": ["department", "विभाग", "laboratory", "faculty"],
        "faculty": ["faculty", "professor", "assistant professor"],
        "regulation": ["rule", "regulation", "नियम", "gazette", "ordinance"],
        "administration": ["dean", "registrar", "vice chancellor", "committee"]
    }

    scores = {}

    for cat, keywords in categories.items():
        scores[cat] = sum(text_l.count(kw) for kw in keywords)

    # Get highest scoring category
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    # Minimum threshold to avoid false positives
    if best_score < 3:
        return "general"

    return best_category


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        ranked_docs = json.load(f)

    top_docs = ranked_docs[:TOP_N]
    review_data = []

    for doc in top_docs:
        full_text = load_full_text(doc["id"], doc["source_type"])
        preview = full_text[:400].replace("\n", " ").strip()
        keywords = extract_keywords(full_text)

        review_data.append({
            "id": doc["id"],
            "source_type": doc["source_type"],
            "score": doc["score"],
            "category_guess": guess_category(full_text),
            "preview": preview,
            "top_keywords": keywords
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2, ensure_ascii=False)

    print(f"Review file created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()