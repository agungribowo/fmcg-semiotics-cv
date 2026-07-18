"""
Google Images Scraper
=====================
Scraper gambar produk dari Google Images untuk keyword Jepang.
Digunakan sebagai fallback untuk keyword yang tidak ditemukan di e-commerce.
"""

import json
import logging
import re
import time
import urllib3
from pathlib import Path
from typing import List, Optional

import pandas as pd
import requests
from playwright.sync_api import sync_playwright

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "01_raw"

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
"""


class GoogleImagesScraper:
    def __init__(self, headless: bool = True, download_images: bool = True, max_images: int = 30):
        self.headless = headless
        self.download_images = download_images
        self.max_images = max_images
        self.scraped_data: List[dict] = []

    def _download(self, url: str, save_path: Path) -> Optional[str]:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
            resp.raise_for_status()
            ct = resp.headers.get("content-type", "")
            ext = ".png" if "png" in ct else ".webp" if "webp" in ct else ".jpg"
            full_path = save_path.parent / f"{save_path.stem}{ext}"
            with open(full_path, "wb") as f:
                f.write(resp.content)
            return str(full_path)
        except Exception as e:
            logger.warning(f"Gagal download: {e}")
            return None

    def scrape_keyword(self, keyword: str, country_filter: str = "Indonesia") -> List[dict]:
        logger.info(f"[GoogleImages] Mencari: {keyword} ({country_filter})")
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            ctx = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 720},
                locale="id-ID",
            )
            page = ctx.new_page()
            page.add_init_script(ANTI_DETECT_SCRIPT)

            q = f"{keyword} {country_filter} kemasan produk"
            search_url = f"https://www.google.com/search?tbm=isch&q={q}"
            page.goto(search_url, timeout=30000)
            page.wait_for_timeout(3000)

            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            # Extract image URLs from Google's structured data
            imgs = page.locator("img").all()
            seen_urls = set()
            for img in imgs:
                if len(results) >= self.max_images:
                    break
                src = img.get_attribute("src") or ""
                if not src or "google" in src or "data:image" in src:
                    continue
                if src in seen_urls:
                    continue
                seen_urls.add(src)

                alt = img.get_attribute("alt") or keyword
                record = {
                    "source": "google_images",
                    "keyword": keyword,
                    "product_name": alt[:100],
                    "image_url": src,
                    "local_path": None,
                }
                if self.download_images:
                    kw_dir = RAW_DATA_DIR / f"google_{keyword}"
                    kw_dir.mkdir(parents=True, exist_ok=True)
                    safe = re.sub(r'[^\w\s-]', '', alt)[:40].strip() or keyword
                    save_path = kw_dir / f"{keyword}_{len(results):04d}_{safe}"
                    local = self._download(src, save_path)
                    if local:
                        record["local_path"] = local
                        results.append(record)
                else:
                    results.append(record)

            browser.close()

        logger.info(f"[GoogleImages] '{keyword}': {len(results)} gambar")
        return results

    def scrape_all(self, keywords: List[str]) -> List[dict]:
        all_data = []
        for kw in keywords:
            data = self.scrape_keyword(kw)
            all_data.extend(data)
        self.scraped_data = all_data
        return all_data

    def save_metadata(self, suffix: str = ""):
        if not self.scraped_data:
            return
        df = pd.DataFrame(self.scraped_data)
        name = f"metadata_google{suffix}"
        csv_path = RAW_DATA_DIR / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        json_path = RAW_DATA_DIR / f"{name}.json"
        with open(json_path, "w") as f:
            json.dump(self.scraped_data, f, indent=2)
        logger.info(f"[GoogleImages] {len(df)} gambar -> {csv_path}")
        print(df.groupby("keyword").agg(
            total=("product_name", "count"),
            images=("local_path", lambda x: x.notna().sum()),
        ).to_string())
