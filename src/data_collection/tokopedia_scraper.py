"""
Tokopedia Scraper
=================
Scraper produk dari Tokopedia untuk mencari produk dengan keyword Jepang
yang beredar di Indonesia.
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

RAW_DATA_DIR = Path("data/01_raw")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

ANTI_DETECT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => false });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en'] });
"""

# Mapping keyword Latin → Jepang (sama seperti run_all.py)
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
    "suntory": "サントリー",
    "shiseido": "資生堂", "senka": "洗顔", "hadalabo": "肌ラボ", "biore": "ビオレ", "anessa": "アネッサ",
}


class TokopediaScraper:
    def __init__(self, headless: bool = True, download_images: bool = True, max_products: int = 20):
        self.headless = headless
        self.download_images = download_images
        self.max_products = max_products
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

    def scrape_keyword(self, keyword: str) -> List[dict]:
        logger.info(f"[Tokopedia] Mencari: {keyword}")
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel="chrome",
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            ctx = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1366, "height": 768},
                locale="id-ID",
                timezone_id="Asia/Jakarta",
            )
            page = ctx.new_page()
            page.add_init_script(ANTI_DETECT_SCRIPT)

            search_url = f"https://www.tokopedia.com/search?q={keyword}&ob=5&st=product"
            try:
                page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                logger.warning(f"[Tokopedia] Timeout load: {e}")

            if page.url == "about:blank":
                logger.warning(f"[Tokopedia] BLOCKED (blank page) for '{keyword}'")
                browser.close()
                return results

            page.wait_for_timeout(5000)

            # Scroll to load more products
            for _ in range(4):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            # Extract products via JavaScript structural DOM traversal
            max_n = self.max_products
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

                        // Get price: any element starting with Rp
                        const priceEl = Array.from(link.querySelectorAll('*'))
                            .find(el => (el.textContent || '').trim().startsWith('Rp') && el.children.length === 0);
                        const price = priceEl ? (priceEl.textContent || '').trim() : '';

                        // Get product name: first long text found in leaf elements
                        let productName = '';
                        const allLeafEls = Array.from(link.querySelectorAll('*'))
                            .filter(el => el.children.length === 0 && (el.textContent || '').trim().length > 5);
                        for (const el of allLeafEls) {
                            const txt = (el.textContent || '').trim();
                            if (!txt.startsWith('Rp') && !txt.match(/^\\d+\\.\\d+$/) && !txt.match(/^\\d+ terjual$/)
                                && txt !== 'Bisa COD' && !txt.includes('Hemat') && !txt.includes('Pakai')
                                && !txt.includes('Official') && !txt.startsWith('Kab.')) {
                                productName = txt;
                                break;
                            }
                        }

                        // Get shop name: leaf element with city-like pattern or before/after price
                        let shopName = '';
                        for (const el of allLeafEls) {
                            const txt = (el.textContent || '').trim();
                            if (txt === productName || txt === price || txt.startsWith('Rp')
                                || txt.match(/^\\d+\\.\\d+$/) || txt.match(/^\\d+ terjual$/)
                                || txt === 'Bisa COD' || txt.includes('Hemat') || txt.includes('Pakai')
                                || txt.startsWith('Kab.') || txt.includes('rating')) continue;
                            if (txt.length > 3 && txt !== productName && !shopName) {
                                // Check if it looks like a shop name (not a rating count)
                                if (!txt.match(/^\\d+/)) {
                                    shopName = txt;
                                }
                            }
                        }

                        if (productName) {
                            results.push({ name: productName, image: imageUrl, price: price, shop: shopName });
                        }
                    }
                    return results;
                }
            """, max_n)

            logger.info(f"[Tokopedia] '{keyword}': {len(products_data)} produk ditemukan")

            for p in products_data:
                if len(results) >= self.max_products:
                    break
                record = {
                    "source": "tokopedia",
                    "keyword": keyword,
                    "product_name": p["name"][:100],
                    "shop_name": p["shop"][:50],
                    "price": p["price"],
                    "image_url": p["image"],
                    "local_path": None,
                }

                if self.download_images:
                    kw_dir = RAW_DATA_DIR / f"tokopedia_{keyword}"
                    kw_dir.mkdir(parents=True, exist_ok=True)
                    safe = re.sub(r'[^\w\s-]', '', p["name"])[:40].strip() or keyword
                    save_path = kw_dir / f"{keyword}_{len(results):04d}_{safe}"
                    local = self._download(p["image"], save_path)
                    if local:
                        record["local_path"] = local
                        results.append(record)
                else:
                    results.append(record)

            browser.close()

        logger.info(f"[Tokopedia] '{keyword}': {len(results)} produk")
        return results

    def scrape_all(self, keywords: List[str], with_jp: bool = True) -> List[dict]:
        all_data = []
        for kw in keywords:
            data = self.scrape_keyword(kw)
            all_data.extend(data)
            if with_jp:
                jp = KEYWORD_JP.get(kw)
                if jp:
                    data_jp = self.scrape_keyword(jp)
                    all_data.extend(data_jp)
        self.scraped_data = all_data
        return all_data

    def save_metadata(self, suffix: str = ""):
        if not self.scraped_data:
            return
        df = pd.DataFrame(self.scraped_data)
        name = f"metadata_tokopedia{suffix}"
        csv_path = RAW_DATA_DIR / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        json_path = RAW_DATA_DIR / f"{name}.json"
        with open(json_path, "w") as f:
            json.dump(self.scraped_data, f, indent=2)
        logger.info(f"[Tokopedia] {len(df)} produk -> {csv_path}")
        print(df.groupby("keyword").agg(
            total=("product_name", "count"),
            images=("local_path", lambda x: x.notna().sum()),
        ).to_string())
