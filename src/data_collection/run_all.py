"""
Run All Scrapers
================
Menjalankan semua scraper secara berurutan untuk mengumpulkan gambar produk FMCG
dengan elemen semiotik Jepang dari berbagai sumber.
"""

import logging
import sys
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path("data/01_raw")

KEYWORDS = [
    "ramen", "matcha", "takoyaki", "udon",
    "nori", "teriyaki", "miso", "sushi",
    "wasabi", "sake", "soba", "edamame",
    "onigiri", "okonomiyaki", "tempura",
]

KEYWORDS_LANJUTAN = [
    # Food—Jepang yang muncul di produk Indonesia
    "karaage", "tori", "katsu", "yakitori", "gyoza",
    "bento", "yakiniku", "sukiyaki", "shabu", "kare",
    "tonkatsu", "teppanyaki",
    # Geki / pedas
    "geki", "gekikara",
    # Tea / beverage
    "kyusu", "suntory", "oolong",
    # Cosmetics
    "shiseido", "senka", "hadalabo", "biore", "anessa",
]

# Mapping keyword → istilah Jepang (Katakana/Hiragana/Kanji)
KEYWORD_JP = {
    "ramen": "ラーメン", "matcha": "抹茶", "takoyaki": "たこ焼き",
    "udon": "うどん", "nori": "のり", "teriyaki": "照り焼き",
    "miso": "味噌", "sushi": "寿司", "wasabi": "わさび",
    "sake": "酒", "soba": "そば", "edamame": "枝豆",
    "onigiri": "おにぎり", "okonomiyaki": "お好み焼き", "tempura": "天ぷら",
    "karaage": "唐揚げ", "tori": "鶏", "katsu": "カツ",
    "yakitori": "焼き鳥", "gyoza": "餃子", "bento": "弁当",
    "yakiniku": "焼肉", "sukiyaki": "すき焼き", "kare": "カレー",
    "tonkatsu": "豚カツ", "teppanyaki": "鉄板焼き",
    "geki": "激", "gekikara": "激辛",
    "kyusu": "急須", "oolong": "烏龍茶",
    # Cosmetics in JP
    "shiseido": "資生堂", "senka": "洗顔", "hadalabo": "肌ラボ",
}


def run_klikindomaret(keywords: List[str]):
    logger.info("=" * 50)
    logger.info("MEMULAI SCRAPER: KlikIndomaret")
    logger.info("=" * 50)
    from src.data_collection.klikindomaret_scraper import KlikIndomaretScraper
    scraper = KlikIndomaretScraper(headless=True, download_images=True)
    scraper.scrape_all(keywords)
    scraper.save_metadata()


def run_tokopedia(keywords: List[str], suffix: str = ""):
    logger.info("=" * 50)
    logger.info("MEMULAI SCRAPER: Tokopedia")
    logger.info("=" * 50)
    from src.data_collection.tokopedia_scraper import TokopediaScraper
    search_kws = []
    for kw in keywords:
        search_kws.append(kw)
        jp = KEYWORD_JP.get(kw)
        if jp:
            search_kws.append(jp)
    scraper = TokopediaScraper(headless=True, download_images=True, max_products=15)
    scraper.scrape_all(search_kws, with_jp=False)
    scraper.save_metadata(suffix)


def run_google_images(keywords: List[str], suffix: str = ""):
    logger.info("=" * 50)
    logger.info("MEMULAI SCRAPER: Google Images" + (f" ({suffix})" if suffix else ""))
    logger.info("=" * 50)
    from src.data_collection.google_images_scraper import GoogleImagesScraper
    # Build list Latin + versi Jepang
    search_kws = []
    for kw in keywords:
        search_kws.append(kw)
        jp = KEYWORD_JP.get(kw)
        if jp:
            search_kws.append(jp)
    scraper = GoogleImagesScraper(headless=True, download_images=True, max_images=20)
    scraper.scrape_all(search_kws)
    out = f"metadata_google{suffix}.csv" if suffix else "metadata_google.csv"
    scraper.save_metadata()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    kw_list = KEYWORDS + KEYWORDS_LANJUTAN

    if mode == "klik":
        run_klikindomaret(kw_list)
    elif mode == "google":
        run_google_images(kw_list, "_id")
    elif mode == "google_lanjutan":
        run_google_images(KEYWORDS_LANJUTAN, "_id_lanjutan")
    elif mode == "tokopedia":
        run_tokopedia(kw_list, "_id")
    elif mode == "all":
        run_klikindomaret(kw_list)
        run_google_images(kw_list, "_id")
        run_tokopedia(kw_list, "_id")
    else:
        print("Usage: python run_all.py [klik|google|google_lanjutan|tokopedia|all]")
