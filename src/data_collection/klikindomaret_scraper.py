"""
KlikIndomaret Scraper
=====================
Playwright-based scraper untuk mengunduh gambar produk dari KlikIndomaret.
Output:
  - Gambar .jpg/.png disimpan ke data/01_raw/{keyword}/
  - Metadata CSV + JSON disimpan ke data/01_raw/
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import List, Optional

import pandas as pd
import requests
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path("data/01_raw")

KEYWORDS = [
    "ramen", "matcha", "takoyaki", "udon",
    "nori", "teriyaki", "miso", "sushi",
    "wasabi", "sake", "soba", "edamame",
    "onigiri", "okonomiyaki", "tempura",
]

BASE_URL = "https://www.klikindomaret.com/search/?searchkey="

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


class KlikIndomaretScraper:
    def __init__(self, headless: bool = True, download_images: bool = True):
        self.headless = headless
        self.download_images = download_images
        self.scraped_data: List[dict] = []

    def _download_image(self, url: str, save_path: Path) -> Optional[str]:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            ext = Path(url).suffix
            if ext.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                ext = ".jpg"
            filename = f"{save_path.stem}{ext}"
            full_path = save_path.parent / filename
            with open(full_path, "wb") as f:
                f.write(resp.content)
            return str(full_path)
        except Exception as e:
            logger.warning(f"Gagal download gambar {url}: {e}")
            return None

    def scrape_keyword(self, keyword: str) -> List[dict]:
        logger.info(f"Memulai scraping untuk kata kunci: {keyword}")
        target_url = f"{BASE_URL}{keyword}"
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.goto(target_url)
            time.sleep(3)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            product_elements = page.locator("div.item")
            count = product_elements.count()
            logger.info(f"Ditemukan {count} produk untuk '{keyword}'")

            for i in range(count):
                item = product_elements.nth(i)
                try:
                    name_el = item.locator("div.title").first
                    product_name = name_el.inner_text().strip() if name_el.count() > 0 else "N/A"

                    price_el = item.locator("span.price-value").first
                    product_price = price_el.inner_text().strip() if price_el.count() > 0 else "N/A"

                    image_el = item.locator("img").first
                    image_url = image_el.get_attribute("src")
                    if not image_url or "placeholder" in image_url:
                        image_url = image_el.get_attribute("data-src")

                    if not image_url:
                        continue

                    record = {
                        "keyword": keyword,
                        "product_name": product_name,
                        "price": product_price,
                        "image_url": image_url,
                        "local_path": None,
                    }

                    if self.download_images:
                        kw_dir = RAW_DATA_DIR / keyword
                        kw_dir.mkdir(parents=True, exist_ok=True)
                        safe_name = "".join(c for c in product_name if c.isalnum() or c in " _-").strip()
                        save_path = kw_dir / f"{keyword}_{i:04d}_{safe_name[:60]}"
                        local = self._download_image(image_url, save_path)
                        if local:
                            record["local_path"] = local
                            logger.info(f"  [{i+1}/{count}] {product_name} -> {local}")
                        else:
                            logger.warning(f"  [{i+1}/{count}] {product_name}: gambar gagal diunduh")
                    else:
                        logger.info(f"  [{i+1}/{count}] {product_name}")

                    results.append(record)

                except Exception as e:
                    logger.error(f"Gagal mengekstrak item ke-{i}: {e}")

            browser.close()

        return results

    def scrape_all(self, keywords: Optional[List[str]] = None) -> List[dict]:
        kw_list = keywords or KEYWORDS
        all_data = []
        for kw in kw_list:
            results = self.scrape_keyword(kw)
            all_data.extend(results)
        self.scraped_data = all_data
        return all_data

    def save_metadata(self):
        if not self.scraped_data:
            logger.warning("Tidak ada data untuk disimpan.")
            return

        df = pd.DataFrame(self.scraped_data)
        df = df.drop_duplicates(subset=["product_name", "image_url"])

        csv_path = RAW_DATA_DIR / "metadata.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Metadata CSV disimpan: {csv_path} ({len(df)} baris)")

        json_path = RAW_DATA_DIR / "metadata.json"
        with open(json_path, "w") as f:
            json.dump(self.scraped_data, f, indent=2)
        logger.info(f"Metadata JSON disimpan: {json_path}")

        summary = df.groupby("keyword").agg(
            total=("product_name", "count"),
            with_images=("local_path", lambda x: x.notna().sum()),
        )
        print(f"\n{'='*50}")
        print("RINGKASAN SCRAPING")
        print(f"{'='*50}")
        print(summary.to_string())
        print(f"{'='*50}")
        print(f"Total produk unik: {len(df)}")


if __name__ == "__main__":
    scraper = KlikIndomaretScraper(headless=True, download_images=True)
    scraper.scrape_all()
    scraper.save_metadata()
