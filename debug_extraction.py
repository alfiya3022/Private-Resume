#!/usr/bin/env python3
"""
debug_extraction.py

Debug script to test and compare resume extraction between:
  1. RAW: legacy plain extractor (extract_text_from_pdf_plain)
  2. MARKDOWN: raw pymupdf4llm.to_markdown output
  3. CLEANED: new extract_text_from_pdf (markdown cleaned for downstream parsing)

Prints character counts, line counts, segment_sections output, and diff for the same file.
"""

import os
import sys
from pathlib import Path

# Ensure backend directory is in python search path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    import pymupdf4llm
    from app.services.pdf_service import pdf_service
except ImportError as e:
    print(f"Error importing modules: {e}", file=sys.stderr)
    print("Ensure you are running with the project virtual environment (backend\\venv).", file=sys.stderr)
    sys.exit(1)


def debug_file(pdf_path: str):
    if not os.path.isfile(pdf_path):
        print(f"Error: File not found at '{pdf_path}'", file=sys.stderr)
        return

    print("=" * 80)
    print(f"FILE: {pdf_path}")
    print("=" * 80)

    # 1. RAW: extract_text_from_pdf_plain
    try:
        raw_text = pdf_service.extract_text_from_pdf_plain(pdf_path)
    except Exception as e:
        raw_text = f"ERROR: {e}"

    # 2. MARKDOWN: pymupdf4llm.to_markdown
    try:
        markdown_text = pymupdf4llm.to_markdown(pdf_path, write_images=False)
    except Exception as e:
        markdown_text = f"ERROR: {e}"

    # 3. CLEANED: new extract_text_from_pdf
    try:
        cleaned_text = pdf_service.extract_text_from_pdf(pdf_path)
    except Exception as e:
        cleaned_text = f"ERROR: {e}"

    print("\n" + "=" * 30 + " 1. RAW (PLAIN) " + "=" * 30)
    print(raw_text)

    print("\n" + "=" * 30 + " 2. MARKDOWN (RAW) " + "=" * 30)
    print(markdown_text)

    print("\n" + "=" * 30 + " 3. CLEANED " + "=" * 30)
    print(cleaned_text)

    # Statistics & Segmentation for RAW and CLEANED
    raw_chars = len(raw_text)
    raw_lines = len(raw_text.splitlines())
    raw_sections = list(pdf_service.segment_sections(raw_text).keys()) if not raw_text.startswith("ERROR:") else []

    clean_chars = len(cleaned_text)
    clean_lines = len(cleaned_text.splitlines())
    clean_sections = list(pdf_service.segment_sections(cleaned_text).keys()) if not cleaned_text.startswith("ERROR:") else []

    print("\n" + "=" * 30 + " 4. STATISTICS & SECTIONS " + "=" * 30)
    selected_source = "PLAIN" if cleaned_text == raw_text else "MARKDOWN (CLEANED)"
    print(f"SELECTED EXTRACTOR RESULT: {selected_source}")
    print("RAW:")
    print(f"  - Characters: {raw_chars}")
    print(f"  - Lines:      {raw_lines}")
    print(f"  - Sections:   {raw_sections}")
    print("CLEANED:")
    print(f"  - Characters: {clean_chars}")
    print(f"  - Lines:      {clean_lines}")
    print(f"  - Sections:   {clean_sections}")

    # Section-key comparison
    print("\n" + "=" * 30 + " 5. SECTION COMPARISON " + "=" * 30)
    if raw_sections == clean_sections:
        print("Section keys comparison: IDENTICAL")
        print(f"Keys: {raw_sections}")
    else:
        print("Section keys comparison: DIFFER")
        raw_set = set(raw_sections)
        clean_set = set(clean_sections)
        only_in_raw = [k for k in raw_sections if k not in clean_set]
        only_in_clean = [k for k in clean_sections if k not in raw_set]
        order_diff = (raw_set == clean_set and raw_sections != clean_sections)
        if only_in_raw:
            print(f"  - Only in RAW:     {only_in_raw}")
        if only_in_clean:
            print(f"  - Only in CLEANED: {only_in_clean}")
        if order_diff:
            print(f"  - Same keys but different ordering:")
            print(f"      RAW:     {raw_sections}")
            print(f"      CLEANED: {clean_sections}")
    print("=" * 80 + "\n")


def main():
    if len(sys.argv) < 2:
        sample_pdf = BACKEND_DIR / "tests" / "fixtures" / "SWE(2).pdf"
        if sample_pdf.exists():
            debug_file(str(sample_pdf))
        else:
            print("Usage: python debug_extraction.py <path_to_pdf>")
            sys.exit(1)
    else:
        for arg in sys.argv[1:]:
            debug_file(arg)


if __name__ == "__main__":
    main()
