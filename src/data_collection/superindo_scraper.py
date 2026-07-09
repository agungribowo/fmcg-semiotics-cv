"""
SuperIndo Scraper
=================
Scraper untuk produk SuperIndo (superindo.co.id).
Menggunakan requests + BeautifulSoup karena sitenya server-side rendered.
"""

import re
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from src.data_collection.base_scraper import BaseScraper, HEADERS, RAW_DATA_DIR, logger


class SuperIndoScraper(BaseScraper):
    def __init__(self, headless: bool = True, download_images: bool = True):
        super().__init__("superindo", headless=False, download_images=download_images)
        self.base_url = "https://www.superindo.co.id"

    def scrape_keyword(self, keyword: str) -> List[dict]:
        logger.info(f"[SuperIndo] Mencari: {keyword}")
        results = []

        search_url = f"{self.base_url}/cari?q={keyword}"
        try:
            resp = requests.get(search_url, headers=HEADERS, timeout=30, verify=False)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"[SuperIndo] Gagal akses {search_url}: {e}")
            return results

        soup = BeautifulSoup(resp.text, "html.parser")

        # TODO: tentukan selector setelah inspeksi manual
        # Sementara placeholder
        product_cards = soup.find_all("div", class_=re.compile(r"product|produk|item|card", re.I))

        for i, card in enumerate(product_cards):
            try:
                name_el = card.find(["h3", "h4", "h5", "span", "div"], class_=re.compile(r"name|title|nama", re.I))
                product_name = name_el.get_text(strip=True) if name_el else "N/A"

                img_el = card.find("img")
                image_url = ""
                if img_el:
                    image_url = img_el.get("src") or img_el.get("data-src") or ""
                    if image_url and not image_url.startswith("http"):
                        image_url = self.base_url + image_url

                price_el = card.find(class_=re.compile(r"price|harga", re.I))
                price = price_el.get_text(strip=True) if price_el else "N/A"

                record = {
                    "source": "superindo",
                    "keyword": keyword,
                    "product_name": product_name,
                    "price": price,
                    "image_url": image_url,
                    "local_path": None,
                }

                if self.download_images and image_url:
                    kw_dir = RAW_DATA_DIR / f"superindo_{keyword}"
                    kw_dir.mkdir(parents=True, exist_ok=True)
                    safe = "".join(c for c in product_name if c.isalnum() or c in " _-").strip()[:60]
                    save_path = kw_dir / f"{keyword}_{i:04d}_{safe}"
                    local = self._download(image_url, save_path)
                    if local:
                        record["local_path"] = local

                results.append(record)

            except Exception as e:
                logger.error(f"[SuperIndo] Gagal ekstrak {i}: {e}")

        if not results:
            logger.info(f"[SuperIndo] Keyword '{keyword}': 0 hasil — coba cek selector")
        else:
            logger.info(f"[SuperIndo] {keyword}: {len(results)} produk")
        return results


if __name__ == "__main__":
    scraper = SuperIndoScraper(download_images=True)
    scraper.scrape_all(["ramen", "matcha"])
    scraper.save_metadata()
