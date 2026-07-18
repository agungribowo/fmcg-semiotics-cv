"""
Fashion Scraper
===============
Scraper khusus produk fashion (kaos, jaket, dll) dari brand Indonesia
yang menggunakan elemen semiotik Jepang (Katakana, Hiragana, Kanji)
di desain produk mereka.
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
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

ANTI_DETECT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => false });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en'] });
"""

# ─── Brand + Keyword Lists ───────────────────────────────────────────────
# Brand Indonesia yang sering pakai elemen Jepang di desain
FASHION_BRANDS = [
    "erigo",
    "aerostreet",
    "roughneck 1991",
    "ryusei",
    "wakai",
    "project-n",
    "ambon clothing",
    "skaters",
    "greenlight",
    "cotton ink",
    "maternal disaster",
    "threedayss",
    "saturdaysinco",
    "palmers",
    "jroh",
]

# Keyword kategori fashion + elemen Jepang
FASHION_KEYWORDS = [
    # Kombinasi brand + elemen Jepang
    "erigo kaos jepang",
    "erigo katakana",
    "erigo kanji",
    "erigo hiragana",
    "erigo japanese",
    "aerostreet kaos jepang",
    "aerostreet katakana",
    "aerostreet kanji",
    "aerostreet japanese",
    # Umum: kaos dengan elemen Jepang
    "kaos katakana",
    "kaos hiragana",
    "kaos kanji jepang",
    "kaos japanese",
    "kaos tulisan jepang",
    "kaos karakter jepang",
    "kaos anime indonesia",
    "kaos desain jepang",
    # Jaket / outerwear
    "jaket katakana",
    "jaket kanji",
    "jaket japanese",
    # Searching by Japanese characters directly
    "ファッション インドネシア",  # Fashion Indonesia (JP)
    "アパレル インドネシア",      # Apparel Indonesia (JP)
    # Brand-specific: Ryusei (Bandung, streetwear Jepang)
    "ryusei jaket jepang",
    "ryusei kanji",
    "ryusei japanese",
    "ryusei jaket varsity",
    # Brand-specific: Roughneck 1991 (jaket varsity, edisi Jepang)
    "roughneck 1991 jaket jepang",
    "roughneck 1991 kanji",
    "roughneck 1991 japanese",
    "roughneck 1991 varsity kanji",
    # Brand-specific: Wakai (sepatu kasual, tulisan kanji)
    "wakai kanji",
    "wakai sepatu jepang",
    "wakai japanese",
    "wakai tulisan jepang",
    # Brand-specific: Project-N (Japvanese, gabung Jepang + Jawa)
    "project-n japvanese",
    "project-n kanji jawa",
    "project-n japanese jawa",
    "project-n kaos jepang",
]

# Keywords brand saja (untuk cari produk brand yang punya koleksi JP)
BRAND_SEARCH_QUERIES = (
    [f"{b} kaos" for b in FASHION_BRANDS]
    + [f"{b} jaket" for b in FASHION_BRANDS]
    + [f"{b} sepatu" for b in ["wakai"]]
)


class FashionScraper:
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

    def _scrape_tokopedia(self, keyword: str) -> List[dict]:
        """Scrape produk fashion dari Tokopedia berdasarkan keyword."""
        logger.info(f"[Tokopedia-Fashion] Mencari: {keyword}")
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
                logger.warning(f"[Tokopedia-Fashion] Timeout load: {e}")

            if page.url == "about:blank":
                logger.warning(f"[Tokopedia-Fashion] BLOCKED for '{keyword}'")
                browser.close()
                return results

            page.wait_for_timeout(5000)

            for _ in range(4):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

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

                        const priceEl = Array.from(link.querySelectorAll('*'))
                            .find(el => (el.textContent || '').trim().startsWith('Rp') && el.children.length === 0);
                        const price = priceEl ? (priceEl.textContent || '').trim() : '';

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

                        let shopName = '';
                        for (const el of allLeafEls) {
                            const txt = (el.textContent || '').trim();
                            if (txt === productName || txt === price || txt.startsWith('Rp')
                                || txt.match(/^\\d+\\.\\d+$/) || txt.match(/^\\d+ terjual$/)
                                || txt === 'Bisa COD' || txt.includes('Hemat') || txt.includes('Pakai')
                                || txt.startsWith('Kab.') || txt.includes('rating')) continue;
                            if (txt.length > 3 && txt !== productName && !shopName) {
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

            logger.info(f"[Tokopedia-Fashion] '{keyword}': {len(products_data)} produk ditemukan")

            for prod in products_data:
                if len(results) >= self.max_products:
                    break
                record = {
                    "source": "tokopedia_fashion",
                    "keyword": keyword,
                    "product_name": prod["name"][:100],
                    "shop_name": prod["shop"][:50],
                    "price": prod["price"],
                    "image_url": prod["image"],
                    "local_path": None,
                }

                if self.download_images:
                    kw_dir = RAW_DATA_DIR / f"fashion_{keyword.replace(' ', '_')}"
                    kw_dir.mkdir(parents=True, exist_ok=True)
                    safe = re.sub(r'[^\w\s-]', '', prod["name"])[:40].strip() or keyword.replace(" ", "_")
                    save_path = kw_dir / f"{keyword.replace(' ', '_')}_{len(results):04d}_{safe}"
                    local = self._download(prod["image"], save_path)
                    if local:
                        record["local_path"] = local
                        results.append(record)
                else:
                    results.append(record)

            browser.close()

        logger.info(f"[Tokopedia-Fashion] '{keyword}': {len(results)} produk")
        return results

    def _scrape_google_images(self, keyword: str) -> List[dict]:
        """Scrape gambar produk fashion dari Google Images."""
        logger.info(f"[Google-Fashion] Mencari: {keyword}")
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

            q = f"{keyword} fashion indonesia"
            search_url = f"https://www.google.com/search?tbm=isch&q={q}"
            page.goto(search_url, timeout=30000)
            page.wait_for_timeout(3000)

            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            imgs = page.locator("img").all()
            seen_urls = set()
            for img in imgs:
                if len(results) >= self.max_products:
                    break
                src = img.get_attribute("src") or ""
                if not src or "google" in src or "data:image" in src:
                    continue
                if src in seen_urls:
                    continue
                seen_urls.add(src)

                alt = img.get_attribute("alt") or keyword
                record = {
                    "source": "google_fashion",
                    "keyword": keyword,
                    "product_name": alt[:100],
                    "image_url": src,
                    "local_path": None,
                }
                if self.download_images:
                    kw_dir = RAW_DATA_DIR / f"fashion_{keyword.replace(' ', '_')}"
                    kw_dir.mkdir(parents=True, exist_ok=True)
                    safe = re.sub(r'[^\w\s-]', '', alt)[:40].strip() or keyword.replace(" ", "_")
                    save_path = kw_dir / f"{keyword.replace(' ', '_')}_{len(results):04d}_{safe}"
                    local = self._download(src, save_path)
                    if local:
                        record["local_path"] = local
                        results.append(record)
                else:
                    results.append(record)

            browser.close()

        logger.info(f"[Google-Fashion] '{keyword}': {len(results)} gambar")
        return results

    def scrape_all(
        self,
        keywords: List[str] = None,
        brands: List[str] = None,
        sources: str = "all",
    ):
        """
        Run scraping untuk semua keyword fashion.

        Args:
            keywords: custom keyword list (default: FASHION_KEYWORDS)
            brands: custom brand list (default: FASHION_BRANDS)
            sources: "all", "tokopedia", atau "google"
        """
        if keywords is None:
            keywords = FASHION_KEYWORDS
        if brands is None:
            brands = FASHION_BRANDS

        all_data = []

        # Scrape by keyword
        for kw in keywords:
            if sources in ("all", "tokopedia"):
                data = self._scrape_tokopedia(kw)
                all_data.extend(data)
            if sources in ("all", "google"):
                data = self._scrape_google_images(kw)
                all_data.extend(data)

        # Scrape by brand name (carari semua produk brand tsb)
        for brand in brands:
            brand_kws = [
                f"{brand} kaos",
                f"{brand} kanji",
                f"{brand} japanese",
            ]
            for kw in brand_kws:
                if sources in ("all", "tokopedia"):
                    data = self._scrape_tokopedia(kw)
                    all_data.extend(data)

        self.scraped_data = all_data
        return all_data

    def save_metadata(self):
        if not self.scraped_data:
            logger.warning("[Fashion] Tidak ada data.")
            return
        df = pd.DataFrame(self.scraped_data)
        df = df.drop_duplicates(subset=["product_name", "image_url"])

        csv_path = RAW_DATA_DIR / "metadata_fashion.csv"
        df.to_csv(csv_path, index=False)

        json_path = RAW_DATA_DIR / "metadata_fashion.json"
        with open(json_path, "w") as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)

        logger.info(f"[Fashion] {len(df)} produk -> {csv_path}")
        print(df.groupby("keyword").agg(
            total=("product_name", "count"),
            images=("local_path", lambda x: x.notna().sum()),
        ).to_string())


if __name__ == "__main__":
    scraper = FashionScraper(headless=True, download_images=True, max_products=15)
    scraper.scrape_all()
    scraper.save_metadata()
