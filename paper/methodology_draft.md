# Methodology & System Architecture

## 1. Pengumpulan Data (Automated Content-Based Filtering)
Karena tingginya tingkat *noise* pada pencarian e-commerce, pengumpulan data dilakukan dengan skema penyaringan berlapis:
* [cite_start]**Scraping Target:** Menggunakan Python Playwright menargetkan KlikIndomaret untuk menjaring representasi fisik produk Fast-Moving Consumer Goods (FMCG)[cite: 402]. 
* [cite_start]**Layer 1 (Data Collection Filter):** Integrasi EasyOCR yang berjalan secara real-time saat scraping[cite: 62]. [cite_start]Tugasnya adalah melakukan klasifikasi biner (Apakah ada teks Jepang/Latin spesifik di gambar ini? Yes/No)[cite: 63].
* [cite_start]Jika *Yes*, simpan gambar[cite: 64]. [cite_start]Jika *No*, buang (drop)[cite: 64]. [cite_start]Ini menyelesaikan masalah *noise* data secara elegan di pintu awal[cite: 65].

## 2. Arsitektur Multimodal Fusion
[cite_start]Model dibangun menggunakan pendekatan *Transfer Learning* yang memproses dua aliran data sekaligus[cite: 201]:

* [cite_start]**Aliran Semantik (Layer 2 - Feature Extractor):** Gambar kemasan dimasukkan ke YomiToku untuk membaca tata letak dan menghasilkan output teks Jepang beserta koordinat layout (JSON)[cite: 319].
* [cite_start]**Aliran Visual:** Gambar kemasan dimasukkan ke Transfer Learning CNN (EfficientNetB0) untuk mengeluarkan fitur visual/grafis[cite: 320].
* [cite_start]**Multimodal Fusion:** Menggabungkan representasi output teks, koordinat layout, dan fitur visual CNN[cite: 321]. [cite_start]Fitur ini dilatih menjadi *classifier* baru berdasarkan anotasi semiotik[cite: 322].


## 3. Tech Stack & Environment (Spesifikasi Alat)
Untuk menjaga agar eksperimen ini dapat direproduksi (Reproducible Research), berikut adalah daftar pustaka dan alat utama yang digunakan dalam pipeline:

* **Scraping Engine:** `Python Playwright`. Dipilih karena kemampuannya me-render JavaScript secara dinamis, sangat cocok untuk e-commerce modern seperti KlikIndomaret yang menggunakan sistem *client-side rendering*.
* **Layer 1 (Data Collection Filter):** `EasyOCR`. Bertindak sebagai *gatekeeper* awal saat scraping berjalan. Karena sangat ringan, model ini dipakai untuk menyortir secara cepat apakah gambar memiliki elemen huruf Jepang/Latin target.
* **Layer 2 (Semantic & Layout Extractor):** `YomiToku`. Model OCR khusus bahasa Jepang yang digunakan untuk melakukan *layout analysis*, mendeteksi tata letak vertikal, dan mengekstrak aksara Kanji/Katakana/Hiragana beserta koordinat *bounding box*-nya menjadi file JSON.
* **Computer Vision (Feature Extractor):** `Transfer Learning CNN` (`EfficientNetB0`) yang berjalan di framework PyTorch untuk mengekstrak fitur grafis visual dari kemasan.

---

## 4. Update Implementasi (vs Rencana Awal)

> Dokumen ini mencatat perubahan antara metodologi yang direncanakan dengan implementasi aktual berdasarkan kendala teknis dan hasil eksperimen.

### 4.1 Pengumpulan Data — Multi-Source Scraping

Rencana awal hanya menargetkan KlikIndomaret. Implementasi aktual menggunakan **7 sumber** untuk memperluas cakupan dataset:

| Sumber | Tools | Hasil | Status |
|--------|-------|-------|--------|
| Google Images | Playwright (bundled Chromium) | ~1200 gambar | Berhasil |
| Tokopedia | Playwright (system Chrome, bypass HTTP/2) | ~178 gambar | Berhasil |
| KlikIndomaret | Playwright, category-page scraping | ~89 gambar | Berhasil |
| Curated Brands | Tokopedia, 18 brand spesifik | 17 gambar | Berhasil |
| Fashion Brands | Tokopedia + Google, 15 brand | ~19 gambar | Berhasil |
| Shopee Mall (Manual) | Manual download | 148 gambar | Berhasil |
| **Blibli (Manual)** | **Semi-automated scraper** | **253 gambar** | **Berhasil** |

**Sumber yang gagal:** Shopee (captcha blocking), SuperIndo (identical homepage), Hypermart (HTTP 415), Transmart (HTTP 502), Alfamidi (DNS error).

### 4.2 Filtering — EasyOCR Digantikan DeepSeek LLM

**Rencana awal (tidak terimplementasi):**
- Layer 1: EasyOCR sebagai *gatekeeper* real-time saat scraping
- Klasifikasi biner: ada teks Jepang di gambar? Yes/No
- Alasan gagal: `pip install easyocr` membutuhkan PyTorch (~2GB) yang timeout saat download

**Implementasi aktual (2 lapis filtering):**

**Layer 1 — Rule-Based Japanese Detector** (`japanese_detector.py`):
- Deteksi aksara Jepang via Unicode regex (Hiragana `\u3040-\u309F`, Katakana `\u30A0-\u30FF`, Kanji `\u4E00-\u9FFF`)
- Keyword set 50+ istilah Latin-romaji Jepang (ramen, matcha, takoyaki, dll.)
- Known brand set 14 brand FMCG Jepang
- Skoring: +2 (aksara Jepang langsung) +1 (keyword Latin) +1 (brand Jepang)
- Threshold: skor >= 1 → lolos filter
- Hasil: 428 gambar lolos ke `data/02_interim/clean/`

**Layer 2 — DeepSeek LLM Filter** (`deepseek_filter.py`):
- Model: `deepseek-chat` via OpenAI-compatible API (`api.deepseek.com`)
- System prompt: "semiotics expert analyzing Indonesian FMCG product names"
- 5 kriteria klasifikasi: (1) aksara Jepang langsung, (2) peminjaman Latin-romaji, (3) nama brand Jepang, (4) istilah rasa/kualitas Jepang, (5) styling budaya Jepang
- Output JSON: `{has_japanese, confidence, reason, jp_elements}`
- Checkpoint system: simpan setiap 100 baris, auto-resume
- Biaya: ~$0.05 untuk 1844 analisis
- Hasil: 1783/1844 lolos (96.7%), 61 ditolak (false positive valid: biore, BAMBOE, shabu narkoba, Tori Toraja)

### 4.3 Dataset Aktual

#### Metrik Pemrosesan Data

| Metrik | Jumlah / Hasil |
|--------|----------------|
| Total Gambar Mentah Terkumpul | 1919 Gambar |
| Metadata Terdaftar (`metadata_all.csv`) | 1886 baris |
| Lolos DeepSeek LLM Filter | 1438 Gambar |
| Lolos Rule-Based Filter (Clean) | 322 Gambar |
| Dataset Semi-Auto High-Res (Shopee Mall + Blibli) | 401 Gambar |

#### Sumber Per Sumber

| Sumber | Jumlah | Keterangan |
|--------|--------|------------|
| Google Images | ~1200 | Playwright (bundled Chromium) |
| Tokopedia | ~178 | Playwright (system Chrome) |
| KlikIndomaret | ~89 | Playwright, category-page scraping |
| Curated Brands | 17 | Tokopedia, 18 brand spesifik |
| Fashion Brands | ~19 | Tokopedia + Google, 15 brand |
| Shopee Mall (Manual) | 148 | Manual download, resolusi tinggi |
| Blibli (Semi-Auto) | 253 | Semi-automated scraper, resolusi menengah-tinggi |

**Karakteristik kualitas data:**
- Dataset scraped (Google/Tokopedia/KlikIndomaret): resolusi rendah (46-200px), thumbnail, tidak layak OCR
- Dataset semi-auto high-res (Shopee Mall + Blibli): resolusi menengah-tinggi (300-1000px), layak OCR, sudah dikonfirmasi mengandung elemen Jepang

### 4.4 Tech Stack Aktual

| Komponen | Rencana | Aktual |
|----------|---------|--------|
| Scraping | Playwright (KlikIndomaret saja) | Playwright (4 sumber) + manual (Shopee Mall & Blibli) |
| Layer 1 Filter | EasyOCR (real-time gatekeeper) | Rule-based Unicode regex + DeepSeek LLM |
| Layer 2 OCR | YomiToku | YomiToku (belum terimplementasi) |
| CV Model | ResNet/EfficientNet | EfficientNetB0 (belum terimplementasi) |
| Fusion | CNN + LSTM | CNN + LSTM (belum terimplementasi) |

### 4.5 Hambatan Utama

1. **Anti-bot detection**: Shopee, Hypermart, Transmart memblokir scraping — beralih ke sumber lain
2. **EasyOCR installation**: PyTorch dependency timeout — digantikan DeepSeek LLM filter
3. **Thumbnail scraping**: Google/Tokopedia hanya menyediakan gambar resolusi rendah — ditambah manual collection dari Shopee Mall dan Blibli
4. **Noise data**: 61 false positive berhasil ditangkap oleh DeepSeek (brand seperti biore, BAMBOE yang menggunakan nama Jepang tanpa elemen visual Jepang signifikan)