"""
Bulk upload CVs from a folder to the CV Matcher API.
Usage: python bulk_upload_cvs.py [folder_path] [api_url]
"""
import os
import sys
import time
import requests
from pathlib import Path

API_URL = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
FOLDER  = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Administrator\Downloads\CV SAMPLES"

UPLOAD_ENDPOINT = f"{API_URL}/candidates/upload"
ALLOWED = {".pdf", ".docx", ".doc"}


def upload_cv(path: Path) -> str:
    with open(path, "rb") as f:
        files = {"file": (path.name, f, "application/octet-stream")}
        try:
            r = requests.post(UPLOAD_ENDPOINT, files=files, timeout=120)
            if r.status_code == 201:
                data = r.json()
                return f"  OK: {data.get('full_name')} | {len(data.get('skills', []))} skills | {data.get('years_experience', 0):.1f} yrs"
            elif r.status_code == 409:
                return f"  SKIP (duplicate email): {path.name}"
            else:
                return f"  ERROR {r.status_code}: {path.name} — {r.text[:200]}"
        except Exception as e:
            return f"  EXCEPTION: {path.name} — {e}"


def main():
    folder = Path(FOLDER)
    if not folder.exists():
        print(f"Folder not found: {folder}")
        sys.exit(1)

    files = sorted([f for f in folder.iterdir() if f.suffix.lower() in ALLOWED])
    print(f"Found {len(files)} CV files in {folder}\n")

    added = skipped = failed = 0
    seen_stems = set()

    for path in files:
        # Skip obvious duplicates based on base name (e.g. "NAME (1).pdf" vs "NAME.pdf")
        clean = path.stem.replace(" (1)", "").replace(" (2)", "").strip().lower()
        if clean in seen_stems:
            print(f"  SKIP (name duplicate): {path.name}")
            skipped += 1
            continue
        seen_stems.add(clean)

        result = upload_cv(path)
        print(result)

        if result.startswith("  OK"):
            added += 1
        elif result.startswith("  SKIP"):
            skipped += 1
        else:
            failed += 1

        # Small delay to avoid Groq rate limits
        time.sleep(1.5)

    print(f"\nDone: {added} added, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
