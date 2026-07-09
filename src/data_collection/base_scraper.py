"""
Base Scraper
============
Abstract base class untuk semua scraper produk FMCG.
"""

import json
import logging
import re
import time
import urllib3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

import pandas as pd
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path("data/01_raw")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

ANTI_DETECT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => false });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en'] });
"""


def extract_filename(url: str) -> str:
    name = url.split("/")[-1].split("?")[0]
    name = re.sub(r'[^\w\.\-]', '_', name)
    return name[:100]


class BaseScraper(ABC):
    def __init__(self, name: str, headless: bool = True, download_images: bool = True):
        self.name = name
        self.headless = headless
        self.download_images = download_images
        self.scraped_data: List[dict] = []

    @abstractmethod
    def scrape_keyword(self, keyword: str) -> List[dict]:
        ...

    def scrape_all(self, keywords: List[str]) -> List[dict]:
        all_data = []
        for kw in keywords:
            results = self.scrape_keyword(kw)
            all_data.extend(results)
        self.scraped_data = all_data
        return all_data

    def _download(self, url: str, save_path: Path) -> Optional[str]:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30, verify=False)
            resp.raise_for_status()
            ct = resp.headers.get("content-type", "")
            if "png" in ct:
                ext = ".png"
            elif "webp" in ct:
                ext = ".webp"
            elif "gif" in ct:
                ext = ".gif"
            else:
                ext = ".jpg"
            full_path = save_path.parent / f"{save_path.stem}{ext}"
            with open(full_path, "wb") as f:
                f.write(resp.content)
            return str(full_path)
        except Exception as e:
            logger.warning(f"[{self.name}] Gagal download {url[:80]}: {e}")
            return None

    def save_metadata(self):
        if not self.scraped_data:
            logger.warning(f"[{self.name}] Tidak ada data.")
            return
        df = pd.DataFrame(self.scraped_data)
        df = df.drop_duplicates(subset=["product_name", "image_url"])

        csv_path = RAW_DATA_DIR / f"metadata_{self.name}.csv"
        df.to_csv(csv_path, index=False)

        json_path = RAW_DATA_DIR / f"metadata_{self.name}.json"
        with open(json_path, "w") as f:
            json.dump(self.scraped_data, f, indent=2)

        logger.info(f"[{self.name}] {len(df)} produk -> {csv_path}")

        summary = df.groupby("keyword").agg(
            total=("product_name", "count"),
            with_images=("local_path", lambda x: x.notna().sum()),
        )
        print(f"\n=== {self.name.upper()} ===")
        print(summary.to_string())
