"""
Japanese Script Detector
========================
Mendeteksi aksara Jepang (Hiragana, Katakana, Kanji) dalam teks nama produk
dan memfilter dataset berdasarkan:
  a) Keberadaan aksara Jepang langsung (Unicode range)
  b) Keyword Jepang dalam Latin (ramen, matcha, dll)
"""

import json
import logging
import re
import shutil
from pathlib import Path
from typing import List, Optional, Set

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "01_raw"
CLEAN_DIR = PROJECT_ROOT / "data" / "02_interim" / "clean"

# Unicode ranges untuk aksara Jepang
HIRAGANA = re.compile(r'[\u3040-\u309F]')
KATAKANA = re.compile(r'[\u30A0-\u30FF]')
KANJI = re.compile(r'[\u4E00-\u9FFF]')
JP_KANA = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]')  # Hiragana + Katakana
JP_ANY = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')  # Semua aksara Jepang

# Keyword Jepang dalam Latin yang umum di produk Indonesia
JP_LATIN_KEYWORDS: Set[str] = {
    # Original food
    "ramen", "matcha", "takoyaki", "udon", "nori", "teriyaki", "miso",
    "sushi", "wasabi", "sake", "soba", "edamame", "onigiri", "okonomiyaki", "tempura",
    # Lanjutan food
    "karaage", "tori kara", "katsu", "tonkatsu", "yakitori", "gyoza", "bento",
    "yakiniku", "sukiyaki", "shabu", "kare", "teppanyaki", "shoyu",
    "geki", "gekikara", "yakisoba",
    # Beverage
    "suntory", "oolong", "pokka", "pocari",
    # Cosmetics
    "shiseido", "senka", "hadalabo", "biore", "anessa",
    # Brand-specific
    "ito en", "c1000", "yobick", "fibre mini", "soyjoy",
    # Rasa dalam bahasa Jepang
    "sakura", "matcha", "hojicha", "genmaicha",
}

# Brand yang sudah diketahui memiliki aksara Jepang
KNOWN_JP_BRANDS: Set[str] = {
    "you c1000", "ito en", "oronamin", "yobick", "fibre mini",
    "pocari sweat", "soyjoy", "pokka", "suntory", "shiseido",
    "senka", "hadalabo", "biore", "anessa",
}


def has_japanese_script(text: str) -> bool:
    """Cek apakah teks mengandung aksara Jepang (Hiragana/Katakana/Kanji)."""
    return bool(JP_ANY.search(text))


def has_kana(text: str) -> bool:
    """Cek apakah teks mengandung Kana (Hiragana atau Katakana)."""
    return bool(JP_KANA.search(text))


def has_jp_latin_keyword(text: str) -> bool:
    """Cek apakah teks mengandung keyword Jepang dalam Latin."""
    text_lower = text.lower()
    for kw in JP_LATIN_KEYWORDS:
        if kw in text_lower:
            return True
    return False


def has_jp_brand(text: str) -> bool:
    """Cek apakah teks mengandung brand Jepang yang dikenal."""
    text_lower = text.lower()
    for brand in KNOWN_JP_BRANDS:
        if brand in text_lower:
            return True
    return False


def classify_japanese_content(text: str) -> dict:
    """Klasifikasi konten Jepang dalam teks."""
    return {
        "has_hiragana": bool(HIRAGANA.search(text)),
        "has_katakana": bool(KATAKANA.search(text)),
        "has_kanji": bool(KANJI.search(text)),
        "has_kana": bool(JP_KANA.search(text)),
        "has_jp_script": bool(JP_ANY.search(text)),
        "has_jp_latin_kw": has_jp_latin_keyword(text),
        "has_jp_brand": has_jp_brand(text),
    }


def filter_dataset(
    metadata_path: Path,
    name_column: str = "product_name",
    output_prefix: str = "filtered",
    min_score: int = 1,
    copy_images: bool = True,
) -> pd.DataFrame:
    """
    Filter dataset berdasarkan deteksi konten Jepang.
    
    Scoring:
    - +2: mengandung aksara Jepang langsung (Hiragana/Katakana/Kanji)
    - +1: mengandung keyword Jepang dalam Latin
    - +1: mengandung brand Jepang yang dikenal
    
    min_score=1: setidaknya 1 indikator Jepang
    """
    logger.info(f"Memfilter: {metadata_path}")
    logger.info(f"  Kolom nama: {name_column}, min_score={min_score}")

    df = pd.read_csv(metadata_path)
    logger.info(f"  Total: {len(df)} baris")

    results = []
    for _, row in df.iterrows():
        text = str(row.get(name_column, row.get("product_name", "")))

        # Classify
        cls = classify_japanese_content(text)
        score = 0
        if cls["has_jp_script"]:
            score += 2
        if cls["has_jp_latin_kw"]:
            score += 1
        if cls["has_jp_brand"]:
            score += 1

        if score >= min_score:
            row_dict = row.to_dict()
            row_dict["jp_score"] = score
            row_dict["jp_hiragana"] = cls["has_hiragana"]
            row_dict["jp_katakana"] = cls["has_katakana"]
            row_dict["jp_kanji"] = cls["has_kanji"]
            row_dict["jp_latin_kw"] = cls["has_jp_latin_kw"]
            row_dict["jp_brand"] = cls["has_jp_brand"]
            row_dict["jp_reason"] = _get_reason(cls)
            results.append(row_dict)

    result_df = pd.DataFrame(results)
    logger.info(f"  Lolos filter: {len(result_df)} baris ({(len(result_df)/len(df)*100):.1f}%)")

    # Copy images
    if copy_images and len(result_df) > 0:
        copied = 0
        for _, row in result_df.iterrows():
            src = Path(str(row.get("local_path", "")))
            if src.exists():
                dst = CLEAN_DIR / src.name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
        logger.info(f"  Copied: {copied} images to {CLEAN_DIR}")

    # Save
    out_path = CLEAN_DIR / f"{output_prefix}_{metadata_path.stem}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(out_path, index=False)
    logger.info(f"  Saved: {out_path}")

    return result_df


def _get_reason(cls: dict) -> str:
    parts = []
    if cls["has_hiragana"]:
        parts.append("Hiragana")
    if cls["has_katakana"]:
        parts.append("Katakana")
    if cls["has_kanji"]:
        parts.append("Kanji")
    if cls["has_jp_latin_kw"]:
        parts.append("LatinJP")
    if cls["has_jp_brand"]:
        parts.append("BrandJP")
    return "+".join(parts) if parts else "unknown"


def filter_all_datasets(min_score: int = 1):
    """Filter semua metadata yang ada."""
    results = []
    for f in RAW_DIR.glob("metadata_*.csv"):
        if "filtered" in f.stem:
            continue
        try:
            df = filter_dataset(f, min_score=min_score)
            if len(df) > 0:
                results.append(df)
        except Exception as e:
            logger.warning(f"Gagal filter {f.name}: {e}")

    # Buat metadata gabungan
    if results:
        combined = pd.concat(results, ignore_index=True)
        combined.to_csv(RAW_DIR / "metadata_jp_filtered.csv", index=False)
        summary = combined.groupby("source").agg(
            total=("product_name", "count"),
            hiragana=("jp_hiragana", "sum"),
            katakana=("jp_katakana", "sum"),
            kanji=("jp_kanji", "sum"),
        ).to_string()
        logger.info(f"\n=== FILTERED SUMMARY (min_score={min_score}) ===")
        logger.info(f"\n{summary}")
        logger.info(f"\nTotal: {len(combined)} from {combined['source'].nunique()} sources")
        return combined
    return None


if __name__ == "__main__":
    filter_all_datasets()
