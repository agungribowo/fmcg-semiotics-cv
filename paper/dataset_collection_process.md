# Proses Pengumpulan Dataset: Pengalaman dan Iterasi

Dokumen ini mendokumentasikan seluruh proses pengumpulan dataset untuk penelitian "Decoding Cultural Commodities: A Multimodal Deep Learning Approach for Visual Semiotics Classification on FMCG Packaging", termasuk iterasi, hambatan, dan solusi yang diterapkan.

---

## 1. Perencanaan Awal

Target awal adalah mengumpulkan gambar produk FMCG Indonesia yang mengandung elemen semiotik Jepang (Katakana, Hiragana, Kanji, nama brand Jepang, istilah Latin-romaji bertema Jepang). Dataset ini akan digunakan untuk melatih model CNN + multimodal fusion yang mengklasifikasi intensitas semiotik visual Jepang pada kemasan produk.

**Sumber data yang direncanakan:** e-commerce Indonesia (Tokopedia, Shopee, KlikIndomaret, Hypermart, Transmart, Alfamidi, SuperIndo) dan Google Images sebagai sumber tambahan.

---

## 2. Iterasi Scraping — Percobaan ke Sumber-Sumber E-Commerce

### Iterasi 1: Shopee

| Aspek | Detail |
|-------|--------|
| Tools | Playwright (system Chrome) |
| Strategi | Scraping halaman pencarian produk |
| Hasil | **Gagal total** |
| Hambatan | Shopee menampilkan halaman verifikasi traffic (captcha/bot detection) meskipun sudah menggunakan system Chrome dan anti-detection JavaScript |
| Kesimpulan | Sumber ini tidak dapat di-scrape secara otomatis tanpa captcha solving, yang di luar scope penelitian |

### Iterasi 2: SuperIndo

| Aspek | Detail |
|-------|--------|
| Tools | BeautifulSoup (server-side rendering) |
| Strategi | Request HTTP langsung ke halaman pencarian |
| Hasil | **Gagal total** |
| Hambatan | Server mengembalikan homepage yang identik untuk semua query pencarian. Tidak ada data produk yang diekstrak |
| Kesimpulan | SuperIndo kemungkinan menggunakan rendering client-side atau WAF yang memblokir request non-browser |

### Iterasi 3: Hypermart, Transmart, Alfamidi

| Sumber | Error | Interpretasi |
|--------|-------|--------------|
| Hypermart | HTTP 415 (Unsupported Media Type) | Server tidak menerima request dari Playwright |
| Transmart | HTTP 502 (Bad Gateway) | Server bermasalah atau memblokir scraping |
| Alfamidi | DNS Error | Domain tidak dapat di-resolve dari environment scraping |

**Kesimpulan dari Iterasi 1–3:** Sebagian besar e-commerce Indonesia memiliki proteksi anti-scraping yang kuat. Hanya 2 sumber yang berhasil di-scrape secara konsisten: Tokopedia dan KlikIndomaret.

---

## 3. Iterasi Scraping — Sumber yang Berhasil

### 3.1 Google Images (Sumber Utama)

| Aspek | Detail |
|-------|--------|
| Tools | Playwright (bundled Chromium) |
| Query | `{keyword} Indonesia kemasan produk` |
| Strategi | Scroll 3x untuk load lebih banyak gambar, ekstrak URL `<img>` |
| Hasil | **~1503 gambar** — sumber terbesar |
| Filter | Buang URL Google-owned dan data-URI images |
| Anti-duplikasi | Set `seen_urls` untuk mencegah download ulang |

**Hambatan:**
- Hasil pencarian Google Images tidak spesifik ke produk FMCG — banyak mengandung gambar iklan, poster, logo, dan gambar non-produk
- Beberapa URL gambar tidak valid atau sudah tidak aktif

### 3.2 Tokopedia

| Aspek | Detail |
|-------|--------|
| Tools | Playwright via `channel="chrome"` (system Chrome) |
| Strategi | JS DOM traversal dari container `divSRPContentProducts` |
| Hasil | **~194 gambar** |
| Anti-detection | Override `navigator.webdriver`, plugins, languages; locale=id-ID; timezone=Asia/Jakarta |

**Hambatan dan Solusi:**
- **HTTP/2 blocking**: Tokopedia memblokir bundled Chromium. Solusi: menggunakan system Chrome via `channel="chrome"`
- **Noise dalam DOM**: Produk nama mengandung noise harga, "terjual", "Bisa COD", "Hemat", "Official", "Kab." — diselesaikan dengan JavaScript filtering khusus
- **Anti-bot detection**: Ditangani dengan anti-detection script yang di-inject via `page.add_init_script()`

### 3.3 KlikIndomaret

| Aspek | Detail |
|-------|--------|
| Tools | Playwright (bundled Chromium) |
| Strategi | Scrape 5 halaman kategori Xpress (makanan, minuman, makanan-ringan, sembako, dapur-bahan-masakan), cache semua produk, lalu filter by keyword |
| Hasil | **~93 gambar** |
| Keyword mapping | Contoh: "ramen" → ["mie", "mi", "noodle", "ramen"] |

**Hambatan dan Solusi:**
- **WAF memblokir search API**: Tidak bisa melakukan pencarian langsung. Solusi: scrape semua produk dari 5 kategori sekaligus, lalu filter secara lokal
- **Skeleton/shimmer loading placeholder**: Gambar placeholder muncul saat loading. Solusi: filter elemen yang mengandung class `shimmers-animate`
- **Modal popup**: Popup iklan mengganggu scraping. Solusi: tekan Escape key untuk menutup modal
- **Proxy image URL**: Gambar dikirim melalui `_next/image` proxy. Solusi: deteksi URL proxy dan ekstrak URL asli dari query params

### 3.4 Curated Products

| Aspek | Detail |
|-------|--------|
| Tools | Playwright (system Chrome via Tokopedia) |
| Strategi | Target 18 brand spesifik yang diketahui memiliki elemen Jepang (You C1000, Ito En, Oronamin C, Yobick, Pristine, Nu Tea, Heavenly Blush, Pokka, Fibe Mini, Pocari Sweat, Mizone, Soyjoy, dll.) |
| Query tambahan | Katakana: オロナミンC, ヨービック, ファイブミニ, dll. |
| Hasil | **~54 gambar** |

### 3.5 Fashion Brands

| Aspek | Detail |
|-------|--------|
| Tools | Playwright (Tokopedia + Google Images) |
| Target | 15 brand fashion Indonesia yang menggunakan aksara Jepang: erigo, aerostreet, roughneck 1991, ryusei, wakai, project-n, dll. |
| Query | `{brand} kanji`, `{brand} katakana`, `ファッション インドネシア` |
| Hasil | Kumpulan gambar dari brand fashion |

---

## 4. Filtering — Iterasi Pertama: Rule-Based Japanese Detector

**File:** `src/data_collection/japanese_detector.py`

Setelah scraping selesai, filtering pertama menggunakan pendekatan rule-based tanpa API.

**Metode deteksi:**
- **Unicode regex** untuk deteksi langsung aksara Jepang: Hiragana (`\u3040-\u309F`), Katakana (`\u30A0-\u30FF`), Kanji (`\u4E00-\u9FFF`)
- **Keyword set** berisi 50+ istilah Latin-romaji Jepang (ramen, matcha, takoyaki, sushi, dll.)
- **Known brand set** berisi 14 brand FMCG Jepang (You C1000, Ito En, Biore, Anessa, dll.)

**Sistem skor:**
- +2 poin: mengandung aksara Jepang (Hiragana/Katakana/Kanji)
- +1 poin: mengandung keyword Latin-romaji Jepang
- +1 poin: mengandung nama brand Jepang yang dikenal
- Produk dengan skor >= 1 lolos filter

**Hasil:** 428 gambar lolos dan disalin ke `data/02_interim/clean/`

**Hambatan:**
- Deteksi hanya berbasis teks metadata (nama produk), bukan konten gambar — ada gambar yang lolos meskipun tidak memiliki elemen visual Jepang
- Beberapa produk Indonesian menggunakan nama Jepang sebagai brand tanpa elemen visual Jepang yang signifikan

---

## 5. Filtering — Iterasi Kedua: DeepSeek LLM Filter

**File:** `src/data_collection/deepseek_filter.py`, `run_deepseek.py`

**Alasan iterasi:** Rule-based filter hanya mendeteksi keberadaan string Jepang dalam metadata. Diperlukan pemahaman semantik yang lebih dalam — misalnya, "shabu" dalam konteks "shabu narkoba" bukan produk Jepang, dan "Tori Toraja" bukan brand Jepang.

**Metode:**
- Menggunakan DeepSeek Chat API (`deepseek-chat` model)
- System prompt: model bertindak sebagai "semiotics expert analyzing Indonesian FMCG product names"
- 5 kriteria klasifikasi: (1) aksara Jepang langsung, (2) peminjaman Latin-romaji, (3) nama brand Jepang, (4) istilah rasa/kualitas Jepang, (5) styling budaya Jepang
- Output JSON: `{"has_japanese": true/false, "confidence": 0.0-1.0, "reason": "...", "jp_elements": [...]}`

**Fitur robust:**
- **Checkpointing**: Simpan progress setiap 100 baris ke checkpoint file
- **Auto-resume**: Jika checkpoint ada saat runtime baru, lanjutkan dari baris terakhir yang selesai
- **Biaya**: ~$0.05 untuk 1844 analisis nama produk

**Hasil:** 1783/1844 lolos filter (96.7%), 61 ditolak (false positive yang valid: biore, BAMBOE, shabu narkoba, Tori Toraja, dll.)

**Hambatan:**
- **Hanya menganalisis nama produk**, bukan konten gambar — tidak ada verifikasi visual apakah gambar benar-benar mengandung tulisan Jepang
- **Rate limit**: ~1 request/detik, membutuhkan waktu untuk 1844 baris
- **DeepSeek timeout pada pipeline awal**: API timeout menengah, ditangani dengan checkpoint system

---

## 6. Filtering — Iterasi Ketiga: EasyOCR (Rencana yang Gagal)

**Status: Tidak terimplementasi**

**Rencana awal:**
EasyOCR direncanakan sebagai **Layer 1 real-time gatekeeper** saat scraping berjalan. Konsepnya:
1. Saat gambar berhasil di-download, jalankan EasyOCR pada gambar
2. Klasifikasi biner: apakah ada teks Jepang/Latin spesifik di gambar? Yes/No
3. Jika Yes → simpan gambar. Jika No → buang (drop)
4. Ini akan menyelesaikan masalah noise di pintu masuk

**Mengapa ini direncanakan:**
- Menurut `paper/methodology_draft.md:6-7`, integrasi EasyOCR real-time saat scraping dirancang untuk mengatasi noise pada pencarian e-commerce secara elegan
- EasyOCR digambarkan sebagai solusi ringan untuk sorting cepat apakah gambar memiliki elemen huruf Jepang/Latin target

**Mengapa tidak terjadi:**
- **Instalasi gagal**: `pip install easyocr` membutuhkan PyTorch (~2GB) yang timeout saat download di environment penelitian
- **DeepSeek sudah cukup memadai**: DeepSeek filter berbasis nama produk sudah memberikan akurasi 96.7%, sehingga EasyOCR tidak lagi menjadi prerequisite
- **Tujuan akhir adalah CNN visual**: Model akan belajar dari fitur visual kemasan (warna, layout, typography, logo) — bukan dari teks OCR. EasyOCR hanya berguna sebagai verifikasi post-processing

**Rekomendasi saat itu (log.md:67-68):** Lanjutkan preprocessing dulu dengan 1783 gambar yang sudah terfilter. Jika hasil training kurang memuaskan, baru install EasyOCR untuk verifikasi tambahan.

---

## 7. Ringkasan Noise dan Cara Penanganannya

| Masalah Noise | Cara Penanganan | Status |
|---------------|-----------------|--------|
| Gambar non-produk dari Google (iklan, poster, logo) | DeepSeek filter + rule-based filter | Sebagian ditangani, sebagian masih lolos |
| Brand false positive (biore, BAMBOE, shabu) | DeepSeek menangkap 61 kasus | Selesai |
| Scraping diblokir (Shopee, SuperIndo, dll.) | Beralih ke sumber lain | Selesai |
| Bot detection/e-commerce anti-scraping | Anti-detection JS, system Chrome, delays | Selesai |
| KlikIndomaret WAF | Strategi category-page scraping | Selesai |
| Skeleton loading placeholder | Filter class `shimmers-animate` | Selesai |
| Proxy image URL | Ekstrak URL asli dari query params | Selesai |
| Nama produk mengandung noise DOM | JavaScript filtering khusus | Selesai |
| Download duplikat | Set `seen_urls` + `drop_duplicates()` | Selesai |
| API timeout mid-filter | Checkpoint system setiap 100 baris | Selesai |
| Gambar corrupt/gagal download | Try-except, log error, skip | Selesai |
| EasyOCR tidak bisa diinstal | Dihentikan, gunakan DeepSeek sebagai gantinya | Dihentikan |

---

## 8. Status Akhir Dataset

| Metrik | Jumlah |
|--------|--------|
| Total gambar di-scrape | ~1844 |
| Lolos DeepSeek filter | 1783 (96.7%) |
| Lolos rule-based filter (ke `data/02_interim/clean/`) | 428 |
| Sumber scraper yang berhasil | 4 dari 6 yang dicoba |
| E-commerce yang diblokir | 5 (Shopee, SuperIndo, Hypermart, Transmart, Alfamidi) |
| Biaya API DeepSeek | ~$0.05 |

---

## 9. Langkah Selanjutnya yang Direncanakan

1. **Cleaning image-level**: Hapus corrupt, deduplikasi (perceptual hash), validasi resolusi minimum, hapus non-product images
2. **Preprocessing**: Rename sesuai label, resize 224x224, split train/val/test
3. **OCR Verification (opsional)**: Install EasyOCR atau YomiToku di environment yang sesuai untuk verifikasi visual apakah gambar benar mengandung tulisan Jepang
4. **Modeling**: CNN classification (ResNet18) dan multimodal fusion (CNN + LSTM)
