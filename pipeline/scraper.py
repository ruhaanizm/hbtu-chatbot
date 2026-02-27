# pipeline/scraper.py

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import hashlib

BASE_DOMAIN = "hbtu.ac.in"
START_URL = "https://hbtu.ac.in/"

RAW_DIR = "data/raw"
HTML_DIR = os.path.join(RAW_DIR, "html")
PDF_DIR = os.path.join(RAW_DIR, "pdf")

MAX_PAGES = 300  # safety limit


def ensure_dirs():
    os.makedirs(HTML_DIR, exist_ok=True)
    os.makedirs(PDF_DIR, exist_ok=True)


def is_valid_url(url):
    parsed = urlparse(url)
    return (
        parsed.scheme in ["http", "https"]
        and BASE_DOMAIN in parsed.netloc
    )


def get_filename_from_url(url, extension):
    hash_object = hashlib.md5(url.encode())
    return f"{hash_object.hexdigest()}.{extension}"


def save_html(content, url):
    filename = get_filename_from_url(url, "html")
    filepath = os.path.join(HTML_DIR, filename)
    with open(filepath, "w", encoding="utf-8", errors="ignore") as f:
        f.write(content)


def save_pdf(content, url):
    filename = get_filename_from_url(url, "pdf")
    filepath = os.path.join(PDF_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)


def scrape():
    ensure_dirs()

    visited = set()
    queue = deque([START_URL])

    session = requests.Session()
    session.headers.update({
        "User-Agent": "HBTU-RAG-Indexer/1.0"
    })

    page_count = 0

    while queue and page_count < MAX_PAGES:
        url = queue.popleft()

        if url in visited:
            continue

        if not is_valid_url(url):
            continue

        try:
            print(f"[Crawling] {url}")
            response = session.get(url, timeout=10)

            if response.status_code != 200:
                continue

            visited.add(url)

            content_type = response.headers.get("Content-Type", "")

            if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                save_pdf(response.content, url)
                print("  → Saved PDF")
                continue

            if "text/html" in content_type:
                html = response.text
                save_html(html, url)
                page_count += 1

                soup = BeautifulSoup(html, "html.parser")

                for tag in soup.find_all("a", href=True):
                    next_url = urljoin(url, tag["href"])
                    if is_valid_url(next_url) and next_url not in visited:
                        queue.append(next_url)

        except Exception as e:
            print(f"[Error] {url} -> {e}")
            continue

    print("\nScraping completed.")
    print(f"Total HTML pages saved: {page_count}")
    print(f"Total URLs visited: {len(visited)}")


if __name__ == "__main__":
    scrape()