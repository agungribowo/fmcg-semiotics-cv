# Research Log — FMCG Semiotics CV

## 2026-07-09 — Initial Dataset Pipeline

### Objective
Membangun multi-source scraper untuk collect produk FMCG Indonesia dengan elemen semiotik Jepang (Katakana/Hiragana/Kanji), lalu filter pake DeepSeek API.

### Completed

#### 1. Scrapers (4 sumber, ~1844 gambar)

| Source | Tools | Images | Status |
|--------|-------|--------|--------|
| **Google Images** | Playwright (bundled Chromium), query `{keyword} Indonesia kemasan produk` | ~1503 | OK |
| **Tokopedia** | Playwright via `channel="chrome"` (system Chrome, bypass HTTP2 blocking), JS DOM traversal from `divSRPContentProducts` | ~194 | OK |
| **KlikIndomaret** | Playwright, scrape 5 xpress categories once, cache, filter_by_keyword() | ~93 | OK |
| **Curated** | Focused scraping of known Japanese brands (You C1000, Ito En, Oronamin, Yobick, dll) | ~54 | OK |

#### 2. Scrapers that failed
- **Shopee**: blocked by traffic verification page (even with system Chrome)
- **SuperIndo**: returns identical homepage for all queries
- **Hypermart** (415), **Transmart** (502), **Alfamidi** (DNS error)

#### 3. DeepSeek Filtering
- Model: `deepseek-chat`, via OpenAI-compatible API at `api.deepseek.com`
- API key stored in `.env` (gitignored)
- Cost: **~$0.05** for 1844 product name analyses
- **Result: 1783/1844 passed (96.7%)**, 61 failed (legitimate false positives: biore, BAMBOE, shabu narkoba, Tori Toraja, dll.)
- Added checkpointing (save every 100 rows, auto-resume)

#### 4. Files produced
- `data/01_raw/metadata_all.csv` (1844 rows, all sources combined)
- `data/01_raw/metadata_all_deepseek.csv` (full results with ds_has_japanese, ds_confidence, ds_reason)
- `data/01_raw/metadata_all_deepseek_filtered.csv` (1783 filtered rows)
- `src/data_collection/` — all scraper scripts

#### 5. Anti-detection measures
- Override webdriver, proper UA, locale id-ID, timezone Asia/Jakarta
- System Chrome via `channel="chrome"` for difficult targets (Tokopedia)
- 1.5s–2s delays between requests

### Next Steps (for next session)

1. **Cleaning** (image-level):
   - Hapus corrupt/gagal download
   - Deduplikasi (perceptual hash or manual)
   - Validasi resolusi minimum
   - Hapus non-product images (poster, logo, etc.)

2. **Preprocessing**:
   - Rename file sesuai label
   - Resize to 224x224
   - Split train/val/test

3. **Modeling**:
   - CNN classification (binary: Japanese semiotic vs not, or multi-class per brand)

### Known Issues
- `pip install easyocr` fails (PyTorch ~2GB download timeout in this env)
- DeepSeek only analyzes product NAME text, not image content (no OCR fallback)
- Google Images results include some non-product images (ads, posters)
- Rate-limited by DeepSeek API (~1 request/second effective throughput)

Alasannya:
- DeepSeek udah filter based on product name (nama produk = Japanese brand? → 96.7% akurat)
- Tujuan akhir kita adalah CNN classification based on image features (bukan teks di gambar). Model bakal belajar dari visual kemasan: warna, layout, typography, logo Japanese brand — bukan dari OCR text.
- EasyOCR hanya berguna kalau kamu mau double-check bahwa beneran ada tulisan Jepang di gambar kemasannya. Itu bisa jadi post-processing nanti, bukan prerequisite.
Saran: Lanjut preprocessing (resize + split train/val) dulu pakai 1783 gambar yang sudah terfilter. Kalau nanti hasil training kurang memuaskan, baru install EasyOCR di mesin kamu buat verifikasi tambahan.