# pipeline/ocr.py

import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import hashlib
import subprocess

PDF_DIR = "data/raw/pdf"
OUTPUT_DIR = "data/processed/pdf_text"

# Set Tesseract path manually if needed (uncomment if required)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

POPPLER_PATH = None  # Set path if pdf2image doesn't auto-detect

os.makedirs(OUTPUT_DIR, exist_ok=True)


def is_text_pdf(filepath):
    """
    Check if PDF contains extractable text using pdftotext.
    """
    try:
        result = subprocess.run(
            ["pdftotext", filepath, "-"],
            capture_output=True
        )

        text = result.stdout.decode("utf-8", errors="ignore").strip()
        return len(text) > 50

    except Exception:
        return False


def extract_text_pdf(filepath):
    """
    Extract text directly using pdftotext.
    """
    try:
        result = subprocess.run(
            ["pdftotext", filepath, "-"],
            capture_output=True
        )

        return result.stdout.decode("utf-8", errors="ignore")

    except Exception:
        return ""
    



def ocr_pdf(filepath):
    """
    OCR scanned PDF using Tesseract (Hindi + English).
    """
    text_output = ""

    try:
        images = convert_from_path(
            filepath,
            dpi=300,
            poppler_path=POPPLER_PATH
        )

        for image in images:
            text = pytesseract.image_to_string(
                image,
                lang="hin+eng",
                config="--psm 6"
            )
            text_output += text + "\n"

    except Exception as e:
        print(f"OCR Error: {filepath} -> {e}")

    return text_output


def clean_text(text):
    """
    Basic cleaning (we'll do deeper cleaning later)
    """
    text = text.replace("\x0c", " ")
    text = text.replace("\r", " ")
    text = text.strip()
    return text


def process_all_pdfs():
    files = os.listdir(PDF_DIR)
    total = len(files)

    for i, filename in enumerate(files):
        filepath = os.path.join(PDF_DIR, filename)

        if not filename.lower().endswith(".pdf"):
            continue

        print(f"[{i+1}/{total}] Processing: {filename}")

        try:
            if is_text_pdf(filepath):
                text = extract_text_pdf(filepath)
                print("  → Extracted via pdftotext")
            else:
                text = ocr_pdf(filepath)
                print("  → Extracted via OCR")

            text = clean_text(text)

            if len(text) < 30:
                print("  → Skipped (too little text)")
                continue

            output_filename = filename.replace(".pdf", ".txt")
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            with open(output_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(text)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("\nPDF processing completed.")


if __name__ == "__main__":
    process_all_pdfs()