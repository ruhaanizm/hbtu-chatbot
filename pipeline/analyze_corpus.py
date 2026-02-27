# pipeline/analyze_corpus.py

import os
import json
import re
from bs4 import BeautifulSoup
from collections import Counter

PDF_TEXT_DIR = "data/processed/pdf_text"
HTML_DIR = "data/raw/html"
OUTPUT_FILE = "data/processed/review_candidates.json"

ACADEMIC_KEYWORDS = [
    "admission", "btech", "mtech", "phd", "department",
    "faculty", "syllabus", "fee", "hostel", "scholarship",
    "placement", "training", "exam", "calendar",
    "registration", "semester", "academic",
    "notice", "circular", "guidelines", "eligibility",
    "प्रवेश", "शुल्क", "विभाग", "छात्रावास",
    "परीक्षा", "छात्रवृत्ति", "प्लेसमेंट",
    "सत्र", "सेमेस्टर", "पात्रता"
]


def clean_html_text(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text(separator=" ")


def load_documents():
    documents = []

    # Load PDF text files
    for filename in os.listdir(PDF_TEXT_DIR):
        if filename.endswith(".txt"):
            path = os.path.join(PDF_TEXT_DIR, filename)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                documents.append({
                    "id": filename,
                    "source_type": "pdf",
                    "text": text
                })

    # Load HTML files
    for filename in os.listdir(HTML_DIR):
        if filename.endswith(".html"):
            path = os.path.join(HTML_DIR, filename)
            text = clean_html_text(path)
            documents.append({
                "id": filename,
                "source_type": "html",
                "text": text
            })

    return documents


def compute_metrics(text):
    text = text.strip()

    length = len(text)
    if length == 0:
        return None

    letters = sum(c.isalpha() for c in text)
    digits = sum(c.isdigit() for c in text)

    alphabet_ratio = letters / length
    digit_ratio = digits / length

    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    hindi_ratio = hindi_chars / length

    keyword_score = sum(
        1 for kw in ACADEMIC_KEYWORDS
        if kw.lower() in text.lower()
    )

    camscanner_penalty = text.lower().count("camscanner") * 2

    noise_penalty = 0
    if alphabet_ratio < 0.4:
        noise_penalty += 5
    if length < 300:
        noise_penalty += 5

    import math

    # Length scaling (log-based to avoid size dominance)
    length_score = math.log(length + 1)

    # Strong penalty for numeric-heavy docs
    digit_penalty = digit_ratio * 15

    # Strong penalty for low alphabet ratio
    alpha_penalty = 0
    if alphabet_ratio < 0.5:
        alpha_penalty = 10

    # Final score
    score = (
        length_score
        + keyword_score * 8
        + hindi_ratio * 5
        - digit_penalty
        - noise_penalty
        - camscanner_penalty
        - alpha_penalty
    )
    return {
        "length": length,
        "alphabet_ratio": round(alphabet_ratio, 3),
        "digit_ratio": round(digit_ratio, 3),
        "hindi_ratio": round(hindi_ratio, 3),
        "keyword_score": keyword_score,
        "score": round(score, 2)
    }


def main():
    documents = load_documents()
    results = []

    for doc in documents:
        metrics = compute_metrics(doc["text"])
        if metrics is None:
            continue

        results.append({
            "id": doc["id"],
            "source_type": doc["source_type"],
            **metrics
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    os.makedirs("data/processed", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nAnalysis complete. Review file saved to {OUTPUT_FILE}")
    print(f"Total documents analyzed: {len(results)}")


if __name__ == "__main__":
    main()