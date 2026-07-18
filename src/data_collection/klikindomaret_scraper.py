"""
KlikIndomaret Scraper
=====================
Scraper produk dari KlikIndomaret via Xpress category pages.
Karena search API diblokir WAF, strategi:
  1. Scrape produk dari halaman kategori Xpress (makanan, minuman, dll)
  2. Filter produk yang namanya mengandung keyword target
  3. Download gambar ke data/01_raw/
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

KEYWORDS = [
    "ramen", "matcha", "takoyaki", "udon",
    "nori", "teriyaki", "miso", "sushi",
    "wasabi", "sake", "soba", "edamame",
    "onigiri", "okonomiyaki", "tempura",
]

# Keyword Indonesia -> Jepang mapping (produk di Indo pakai istilah lokal)
KEYWORD_MAP = {
    "ramen": ["mie", "mi", "noodle", "ramen"],
    "matcha": ["matcha", "green tea", "teh hijau"],
    "takoyaki": ["takoyaki"],
    "udon": ["udon", "mie"],
    "nori": ["nori", "rumput laut"],
    "teriyaki": ["teriyaki"],
    "miso": ["miso"],
    "sushi": ["sushi", "sushi rice"],
    "wasabi": ["wasabi"],
    "sake": ["sake"],
    "soba": ["soba"],
    "edamame": ["edamame", "kedelai"],
    "onigiri": ["onigiri"],
    "okonomiyaki": ["okonomiyaki"],
    "tempura": ["tempura"],
}

XPRESS_CATEGORIES = [
    "makanan",
    "minuman",
    "makanan-ringan",
    "sembako",
    "dapur-bahan-masakan",
]

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


class KlikIndomaretScraper:
    def __init__(self, headless: bool = True, download_images: bool = True):
        self.headless = headless
        self.download_images = download_images
        self.scraped_data: List[dict] = []
        self._category_cache: List[dict] = []

    def _download(self, url: str, save_path: Path) -> Optional[str]:
        try:
            real_url = url
            if "_next/image" in url or "assets-klikidmcore" in url:
                from urllib.parse import parse_qs, unquote, urlparse
                qs = parse_qs(urlparse(url).query)
                raw = qs.get("url", [None])[0]
                if raw:
                    real_url = unquote(raw)

            resp = requests.get(real_url, headers=HEADERS, timeout=30, verify=False)
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

    def _dismiss_modal(self, page):
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

    def scrape_category(self, category: str) -> List[dict]:
        logger.info(f"[KlikIndomaret] Scrape kategori: {category}")
        url = f"https://www.klikindomaret.com/xpress/category/{category}"
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
                timezone_id="Asia/Jakarta",
            )
            page = ctx.new_page()
            page.add_init_script(ANTI_DETECT_SCRIPT)

            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)
            self._dismiss_modal(page)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)
            self._dismiss_modal(page)

            cards = page.locator(".card-product")
            total = cards.count()
            real = sum(
                1 for i in range(total)
                if "shimmers-animate" not in cards.nth(i).inner_html()
            )
            logger.info(f"  {category}: {real}/{total} produk real")

            for i in range(total):
                try:
                    c = cards.nth(i)
                    if "shimmers-animate" in c.inner_html():
                        continue

                    text = c.inner_text().strip()
                    product_name = re.sub(r"^Tambah\s*", "", text)
                    img_el = c.locator("img").first
                    image_url = img_el.get_attribute("src") or ""

                    results.append({
                        "source": "klikindomaret",
                        "category": category,
                        "product_name": product_name,
                        "image_url": image_url,
                        "local_path": None,
                    })
                except Exception as e:
                    logger.error(f"  Gagal ekstrak card {i}: {e}")

            browser.close()

        return results

    def scrape_all_categories(self) -> List[dict]:
        """Scrape SEMUA kategori SEKALI, return gabungan semua produk."""
        all_products = []
        for cat in XPRESS_CATEGORIES:
            products = self.scrape_category(cat)
            all_products.extend(products)
        self._category_cache = all_products
        logger.info(f"[KlikIndomaret] Total {len(all_products)} produk dari {len(XPRESS_CATEGORIES)} kategori")
        return all_products

    def filter_by_keyword(self, keyword: str, all_products: List[dict]) -> List[dict]:
        """Filter produk dari cache berdasarkan keyword."""
        variants = KEYWORD_MAP.get(keyword, [keyword])
        matched = []
        for p in all_products:
            name_lower = p["product_name"].lower()
            if any(v in name_lower for v in variants):
                if self.download_images:
                    kw_dir = RAW_DATA_DIR / f"klikindomaret_{keyword}"
                    kw_dir.mkdir(parents=True, exist_ok=True)
                    safe = "".join(c for c in p["product_name"] if c.isalnum() or c in " _-").strip()[:60]
                    save_path = kw_dir / f"{keyword}_{len(matched):04d}_{safe}"
                    local = self._download(p["image_url"], save_path)
                    if local:
                        p["local_path"] = local
                p["keyword"] = keyword
                matched.append(p)

        logger.info(f"[KlikIndomaret] '{keyword}': {len(matched)} cocok dari {len(all_products)}")
        return matched

    def scrape_all(self, keywords: Optional[List[str]] = None) -> List[dict]:
        kw_list = keywords or KEYWORDS
        all_products = self.scrape_all_categories()
        all_data = []
        for kw in kw_list:
            results = self.filter_by_keyword(kw, all_products)
            all_data.extend(results)
        self.scraped_data = all_data
        return all_data

    def save_metadata(self):
        if not self.scraped_data:
            logger.warning("[KlikIndomaret] Tidak ada data.")
            return
        df = pd.DataFrame(self.scraped_data)
        df = df.drop_duplicates(subset=["product_name", "image_url"])
        csv_path = RAW_DATA_DIR / "metadata_klikindomaret.csv"
        df.to_csv(csv_path, index=False)
        json_path = RAW_DATA_DIR / "metadata_klikindomaret.json"
        with open(json_path, "w") as f:
            json.dump(self.scraped_data, f, indent=2)
        logger.info(f"[KlikIndomaret] {len(df)} produk -> {csv_path}")
        print(df.groupby("keyword").agg(
            total=("product_name", "count"),
            images=("local_path", lambda x: x.notna().sum()),
        ).to_string())


if __name__ == "__main__":
    scraper = KlikIndomaretScraper(headless=True, download_images=True)
    scraper.scrape_all()
    scraper.save_metadata()
