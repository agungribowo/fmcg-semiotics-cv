"""
Curated Product Scraper
=======================
Scraping produk-produk spesifik yang sudah diketahui memiliki elemen
semiotik Jepang (Katakana/Hiragana/Kanji) pada kemasannya.
Menggunakan Tokopedia sebagai sumber (produk Indonesia asli).
"""

import json
import logging
import re
import urllib3
from pathlib import Path
from typing import List, Optional

import pandas as pd
import requests
from playwright.sync_api import sync_playwright

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path("data/02_interim/curated")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
}

ANTI_DETECT = """
Object.defineProperty(navigator, 'webdriver', { get: () => false });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
"""

# Produk yang sudah teridentifikasi memiliki elemen semiotik Jepang
CURATED_PRODUCTS = [
    # Minuman
    {"brand": "You C1000",       "query": "You C1000",       "jp_elements": "Vitamin"},
    {"brand": "You C1000",       "query": "C1000",           "jp_elements": "Vitamin"},
    {"brand": "Teh Ito En",      "query": "Ito En Teh",       "jp_elements": "ジャスミン (Jasmine)"},
    {"brand": "Oronamin C",      "query": "Oronamin C Drink", "jp_elements": "オロナミンC"},
    {"brand": "Yobick",          "query": "Yobick",           "jp_elements": "ヨービック"},
    {"brand": "Pristine",        "query": "Pristine Air",     "jp_elements": ""},
    {"brand": "Nu Tea",          "query": "Nu Tea",           "jp_elements": ""},
    {"brand": "Heavenly Blush",  "query": "Heavenly Blush",   "jp_elements": ""},
    {"brand": "Pokka",           "query": "Pokka",            "jp_elements": "The Pokka"},
    {"brand": "Perfect Alkaline","query": "Perfect Alkaline Water", "jp_elements": ""},
    {"brand": "Fibe Mini",       "query": "Fibe Mini",        "jp_elements": "ファイブミニ"},
    # Rasa dalam Katakana
    {"brand": "Vitamin Apple",   "query": "ビタミンアップル",   "jp_elements": "ビタミンアップル"},
    {"brand": "Vitamin Orange",  "query": "ビタミンオレンジ",   "jp_elements": "ビタミンオレンジ"},
    {"brand": "Jasmine Tea",     "query": "ジャスミン tea",    "jp_elements": "ジャスミン"},
    # Tambahan produk FMCG Indonesia dengan aksara Jepang
    {"brand": "Pocari Sweat",    "query": "Pocari Sweat",     "jp_elements": "Pocari Sweat (nama Jepang)"},
    {"brand": "Mizone",          "query": "Mizone",           "jp_elements": ""},
    {"brand": "Soyjoy",          "query": "Soyjoy",           "jp_elements": "SOYJOY (Katakana)"},
]

# Query versi Katakana untuk produk-produk ini
CURATED_JP_QUERIES = [
    "オロナミンC", "ヨービック", "ファイブミニ", "ビタミンアップル",
    "ビタミンオレンジ", "ジャスミン", "ポカリスエット", "ポッカ",
]


class CuratedScraper:
    def __init__(self, headless: bool = True, download_images: bool = True, max_per_product: int = 10):
        self.headless = headless
        self.download_images = download_images
        self.max_per_product = max_per_product
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
            logger.warning(f"Download fail: {e}")
            return None

    def scrape_product(self, brand: str, query: str, jp_elements: str = "") -> List[dict]:
        logger.info(f"[Curated] Mencari: {brand} (query='{query}')")
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel="chrome", headless=self.headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            ctx = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1366, "height": 768},
                locale="id-ID", timezone_id="Asia/Jakarta",
            )
            page = ctx.new_page()
            page.add_init_script(ANTI_DETECT)

            url = f"https://www.tokopedia.com/search?q={query}&ob=5&st=product"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except:
                pass
            if page.url == "about:blank":
                browser.close()
                return results
            page.wait_for_timeout(5000)

            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            max_n = self.max_per_product
            products_data = page.evaluate("""
                (maxP) => {
                    const container = document.querySelector('[data-testid="divSRPContentProducts"]');
                    if (!container) return [];
                    const cards = container.querySelectorAll(':scope > div');
                    const results = [];
                    for (const card of cards) {
                        if (results.length >= maxP) break;
                        const link = card.querySelector('a[href*="tokopedia.com"]');
                        if (!link) continue;
                        const img = link.querySelector('img[alt="product-image"]');
                        const imageUrl = img ? (img.getAttribute('src') || '') : '';
                        if (!imageUrl) continue;
                        const priceEl = Array.from(link.querySelectorAll('*'))
                            .find(el => (el.textContent || '').trim().startsWith('Rp') && el.children.length === 0);
                        const price = priceEl ? (priceEl.textContent || '').trim() : '';
                        const allLeafEls = Array.from(link.querySelectorAll('*'))
                            .filter(el => el.children.length === 0 && (el.textContent || '').trim().length > 5);
                        let productName = '';
                        for (const el of allLeafEls) {
                            const txt = (el.textContent || '').trim();
                            if (!txt.startsWith('Rp') && !txt.match(/^\d+\.\d+$/) && !txt.match(/^\d+ terjual$/)
                                && txt !== 'Bisa COD' && !txt.includes('Hemat') && !txt.includes('Pakai')
                                && !txt.includes('Official') && !txt.startsWith('Kab.')) {
                                productName = txt; break;
                            }
                        }
                        if (productName) results.push({ name: productName, image: imageUrl, price: price });
                    }
                    return results;
                }
            """, max_n)

            logger.info(f"[Curated] '{brand}': {len(products_data)} produk")

            for p_data in products_data:
                if len(results) >= self.max_per_product:
                    break
                record = {
                    "source": "curated_tokopedia",
                    "brand": brand,
                    "query": query,
                    "jp_elements": jp_elements,
                    "product_name": p_data["name"][:100],
                    "price": p_data["price"],
                    "image_url": p_data["image"],
                    "local_path": None,
                }
                if self.download_images:
                    kw_dir = RAW_DATA_DIR / brand.replace(" ", "_").lower()
                    kw_dir.mkdir(parents=True, exist_ok=True)
                    safe = re.sub(r'[^\w\s-]', '', p_data["name"])[:40].strip() or brand
                    save_path = kw_dir / f"{brand.replace(' ', '_')}_{len(results):04d}_{safe}"
                    local = self._download(p_data["image"], save_path)
                    if local:
                        record["local_path"] = local
                        results.append(record)
                else:
                    results.append(record)

            browser.close()

        return results

    def scrape_all(self):
        all_data = []
        for prod in CURATED_PRODUCTS:
            data = self.scrape_product(prod["brand"], prod["query"], prod["jp_elements"])
            all_data.extend(data)
        for q in CURATED_JP_QUERIES:
            data = self.scrape_product(q, q, f"Aksara Jepang: {q}")
            all_data.extend(data)
        self.scraped_data = all_data
        return all_data

    def save_metadata(self):
        if not self.scraped_data:
            return
        df = pd.DataFrame(self.scraped_data)
        csv_path = RAW_DATA_DIR / "metadata_curated.csv"
        df.to_csv(csv_path, index=False)
        json_path = RAW_DATA_DIR / "metadata_curated.json"
        with open(json_path, "w") as f:
            json.dump(self.scraped_data, f, indent=2)
        logger.info(f"[Curated] {len(df)} gambar -> {csv_path}")
        print(df.groupby("brand").agg(
            total=("product_name", "count"),
            images=("local_path", lambda x: x.notna().sum()),
        ).to_string())
