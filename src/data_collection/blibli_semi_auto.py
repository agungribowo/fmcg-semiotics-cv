"""
Blibli Semi-Automated Image Downloader
======================================
Cara pakai:
  python blibli_semi_auto.py

  1. Paste link gambar Blibli (bisa banyak, satu per baris atau koma)
  2. Ketik 'done' atau enter kosong selesai
  3. Script download, rename, buat metadata otomatis
"""

import os
import re
import sys
import time
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime

RAW_DIR = Path("data/01_raw/blibli_manual")
METADATA_PATH = Path("data/01_raw/metadata_blibli_manual.csv")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://www.blibli.com/",
}


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[^\w\.\-]', '_', name)
    return name[:80]


def detect_ext(content_type: str, url: str) -> str:
    if "webp" in content_type:
        return ".webp"
    elif "png" in content_type:
        return ".png"
    elif "gif" in content_type:
        return ".gif"
    elif "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    # fallback dari URL
    for ext in [".webp", ".png", ".jpg", ".jpeg", ".gif"]:
        if ext in url.lower():
            return ext
    return ".jpg"


def download_image(url: str, save_path: Path) -> dict:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        ct = resp.headers.get("content-type", "")
        ext = detect_ext(ct, url)
        full_path = save_path.with_suffix(ext)
        with open(full_path, "wb") as f:
            f.write(resp.content)
        size_kb = os.path.getsize(full_path) / 1024
        return {"ok": True, "path": str(full_path), "size_kb": round(size_kb, 1), "ext": ext}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def extract_product_name(url: str) -> str:
    """Coba extract nama produk dari URL Blibli."""
    # Pattern: /produk/nama-produk/...
    match = re.search(r'/produk/([^/]+)', url)
    if match:
        return sanitize_filename(match.group(1))
    # Pattern dari filename URL
    name = url.split("/")[-1].split("?")[0]
    return sanitize_filename(name)


def load_existing_metadata() -> list:
    if METADATA_PATH.exists():
        import pandas as pd
        df = pd.read_csv(METADATA_PATH)
        return df.to_dict('records')
    return []


def save_metadata(records: list):
    import pandas as pd
    df = pd.DataFrame(records)
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(METADATA_PATH, index=False)
    print(f"\nMetadata saved: {METADATA_PATH} ({len(df)} rows)")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing metadata untuk counter
    existing = load_existing_metadata()
    counter = len(existing) + 1

    print("=" * 60)
    print("  BLIBLI SEMI-AUTOMATED IMAGE DOWNLOADER")
    print("=" * 60)
    print(f"  Target folder: {RAW_DIR}")
    print(f"  Existing images: {counter - 1}")
    print()
    print("  Paste link gambar Blibli (banyak sekaligus boleh).")
    print("  Ketik 'done' atau enter kosong untuk selesai.")
    print("  Format: bisa URL tunggal, banyak per baris, atau koma-separated.")
    print("=" * 60)
    print()

    results = []
    batch_num = 1

    while True:
        print(f"--- Batch {batch_num} ---")
        lines = []
        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if line.lower() in ("done", "exit", "quit", ""):
                break
            lines.append(line)
        if not lines:
            break

        # Parse all URLs
        urls = []
        for line in lines:
            # Split by comma or newline
            parts = re.split(r'[,\n]+', line)
            for part in parts:
                url = part.strip()
                if url.startswith("http"):
                    urls.append(url)

        if not urls:
            print("  Tidak ada URL valid.")
            continue

        print(f"  Downloading {len(urls)} gambar...")
        for url in urls:
            product_name = extract_product_name(url)
            filename = f"blibli_{counter:04d}_{product_name}"
            save_path = RAW_DIR / filename

            result = download_image(url, save_path)
            if result["ok"]:
                record = {
                    "source": "blibli_manual",
                    "keyword": "manual",
                    "product_name": product_name,
                    "image_url": url,
                    "local_path": str(RAW_DIR / Path(result["path"]).name),
                    "file_size_kb": result["size_kb"],
                    "collection_date": datetime.now().strftime("%Y-%m-%d"),
                }
                results.append(record)
                existing.append(record)
                print(f"  [{counter}] OK  {filename}{result['ext']} ({result['size_kb']}KB)")
            else:
                print(f"  [{counter}] FAIL {product_name}: {result['error']}")
            counter += 1

        # Auto-save metadata setiap batch
        save_metadata(existing)
        batch_num += 1
        print()

    # Final summary
    print("=" * 60)
    print(f"  SELESAI!")
    print(f"  Total download: {len(results)} gambar")
    print(f"  Total di folder: {counter - 1} gambar")
    print(f"  Metadata: {METADATA_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
