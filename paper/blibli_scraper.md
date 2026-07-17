# Blibli Semi-Automated Scraper — Dokumentasi

## 1. Ringkasan

Tool semi-otomatis untuk mengumpulkan gambar produk FMCG dari marketplace **Blibli**. User mem paste link gambar ke terminal, script mendownload, rename, dan membuat metadata otomatis.

**Mengapa semi-otomatis:**
- Blibli memiliki proteksi anti-bot (Cloudflare)
- Selenium/Playwright rawan IP blokir jika request berulang
- Pendekatan manual lebih aman untuk jumlah data 50-200 gambar
- User bisa verifikasi visual apakah produk mengandung elemen Jepang sebelum download

---

## 2. Cara Penggunaan

### Step 1: Jalankan script

```bash
python src/data_collection/blibli_semi_auto.py
```

### Step 2: Paste link gambar

```
> https://www.blibli.com/gambar/produk1.webp, https://www.blibli.com/gambar/produk2.jpg
> https://www.blibli.com/gambar/produk3.webp
> done
```

- Bisa banyak URL sekaligus (koma-separated atau per baris)
- Ketik `done` atau enter kosong untuk selesai

### Step 3: Gabungkan metadata

```bash
python src/data_collection/merge_blibli_metadata.py
```

### Output

| File | Lokasi |
|------|--------|
| Gambar | `data/01_raw/blibli_manual/` |
| Metadata batch | `data/01_raw/metadata_blibli_manual.csv` |
| Metadata gabungan | `data/01_raw/metadata_all.csv` |

### Format penamaan file

```
blibli_0001_nama_produk.webp
blibli_0002_nama_produk.jpg
blibli_0003_nama_produk.png
```

---

## 3. Keyword yang Telah Digunakan (Scraping Sebelumnya)

Keyword berikut sudah di-scrape ke Google Images, Tokopedia, dan KlikIndomaret. **Dapat diterapkan juga pada pencarian Blibli** untuk memperluas dataset.

### 3.1 Makanan Jepang (Food)

| Keyword | Latin | Katakana/Kanji | Jumlah gambar terkumpul |
|---------|-------|----------------|------------------------|
| Ramen | ramen | ラーメン | ~139 |
| Sushi | sushi | 寿司 | ~21 |
| Takoyaki | takoyaki | たこ焼き | ~46 |
| Gyoza | gyoza | 餃子 | ~21 |
| Udon | udon | うどん | ~13 |
| Soba | soba | そば | ~14 |
| Tempura | tempura | テンプラ | ~15 |
| Teriyaki | teriyaki | 照り焼き | ~14 |
| Karaage | karaage | 唐揚げ | ~17 |
| Tonkatsu | tonkatsu | 豚カツ | ~14 |
| Katsu | katsu | カツ | ~17 |
| Kare | kare | カレー | ~21 |
| Bento | bento | 弁当 | ~23 |
| Onigiri | onigiri | おにぎり | ~19 |
| Okonomiyaki | okonomiyaki | お好み焼き | ~18 |
| Sukiyaki | sukiyaki | すき焼き | ~19 |
| Yakiniku | yakiniku | 焼肉 | ~19 |
| Yakisoba | yakisoba | 焼きそば | ~28 |
| Yakitori | yakitori | 焼き鳥 | ~21 |
| Shabu | shabu | しゃぶしゃぶ | ~17 |
| Teppanyaki | teppanyaki | 鉄板焼き | ~19 |
| Nori | nori | のり | ~20 |
| Edamame | edamame | 枝豆 | ~18 |
| Wasabi | wasabi | ワサビ | ~18 |
| Miso | miso | 味噌 | ~42 |
| Shoyu | shoyu | 醤油 | ~22 |

### 3.2 Minuman (Beverages)

| Keyword | Latin | Katakana/Kanji | Jumlah gambar terkumpul |
|---------|-------|----------------|------------------------|
| Matcha | matcha | 抹茶 | ~22 |
| Oolong | oolong | 烏龍茶 | ~15 |
| Sake | sake | 酒 | ~15 |
| Suntory | suntory | サントリー | ~19 |

### 3.3 Brand FMCG Jepang di Indonesia

| Keyword | Brand | Kategori |
|---------|-------|----------|
| Anessa | Anessa (Shiseido) | Skincare/Sunscreen |
| Biore | Biore (Kao) | Skincare/Sabun |
| Hada Labo | Hada Labo (Rohto) | Skincare/Lotion |
| Senka | Senka (Shiseido) | Skincare/Face Wash |
| Shiseido | Shiseido | Skincare |
| You C1000 | You C1000 (Tempo) | Minuman |
| Ito En | Ito En | Minuman Teh |
| Oronamin C | Oronamin C (Oronamin) | Minuman |
| Pokka | Pokka (Sapporo) | Minuman |
| Pocari Sweat | Pocari Sweat (Otsuka) | Minuman |

### 3.4 Keyword Tambahan (Blibli-specific)

Keyword berikut **belum di-scrape** dan bisa dicoba di Blibli:

| Keyword | Kategori | Alasan |
|---------|----------|--------|
| **Kirin** | Minuman | Brand minuman Jepang populer di Indonesia |
| **Mirin** | Bumbu | Mirin (味醂), bumbu masak Jepang |
| **Panko** | Tepung | Tepung roti Jepang |
| **Shichimi** | Bumbu | Shichimi togarashi (七味唐辛о) |
| **Furikake** | Topping | Furikake (ふりかけ) taburan nasi |
| **Natto** | Makanan | Natto (納豆), kedelai fermentasi |
| **Unagi** | Makanan | Unagi (うなぎ), belut |
| **Wagyu** | Daging | Wagyu (和牛) |
| **Matcha latte** | Minuman | Varian matcha |
| **Hojicha** | Minuman Teh | Teh bakar Jepang |
| **Genmaicha** | Minuman Teh | Teh beras Jepang |
| **Dashi** | Bumbu | Kaldu dasar Jepang |
| **Tsuyu** | Bumbu | Saus celup Jepang |
| **Tonkotsu** | Mie | Kuah tonkotsu |
| **Miso soup** | Makanan | Sup miso instan |
| **Rice cracker** | Snack | Crackers Jepang (senbei) |
| **Seaweed snack** | Snack | Cemaran rumput laut |
| **Japanese green tea** | Minuman | Teh hijau Jepang |
| **Matcha powder** | Bahan | Bubuk matcha |
| **Wasabi sauce** | Bumbu | Saus wasabi |
| **Gyoza sauce** | Bumbu | Saus gyoza |
| **Takoyaki sauce** | Bumbu | Saus takoyaki |

---

## 4. Tips Pencarian di Blibli

### Format URL Blibli

```
https://www.blibli.com/cari/{keyword}
```

Contoh:
```
https://www.blibli.com/cari/kirin
https://www.blibli.com/cari/mirin
https://www.blibli.com/cari/takoyaki
```

### Cara mendapatkan link gambar

1. Buka hasil pencarian di Blibli
2. Klik produk yang ingin diambil gambarnya
3. Klik kanan pada gambar produk → **Copy image address**
4. Paste ke terminal script

### Tips agar lebih cepat

- Buka beberapa tab produk sekaligus
- Copy semua link gambar, paste sekaligus ke terminal
- Script akan download semua sekaligus
- Metadata dibuat otomatis

---

## 5. Struktur Metadata

### metadata_blibli_manual.csv

| Kolom | Deskripsi |
|-------|-----------|
| `source` | `blibli_manual` |
| `keyword` | `manual` |
| `product_name` | Nama produk dari URL |
| `image_url` | URL asli gambar |
| `local_path` | Path lokal file gambar |
| `file_size_kb` | Ukuran file dalam KB |
| `collection_date` | Tanggal pengumpulan |

### metadata_all.csv (gabungan)

Kolom yang sama dengan metadata_blibli, hanya kolom tambahan dari source lain digabungkan.

---

## 6. Monitoring dan Logging

Script mencetak log ke terminal:

```
--- Batch 1 ---
  Downloading 5 gambar...
  [1] OK  blibli_0001_kirin_ryusei.webp (45.2KB)
  [2] OK  blibli_0002_mirin_honda.webp (38.7KB)
  [3] FAIL gyoza_sauce: Connection timeout
  [4] OK  blibli_0004_takoyaki_sauce.jpg (52.1KB)
  [5] OK  blibli_0005_nori_snack.webp (41.3KB)

Metadata saved: data/01_raw/metadata_blibli_manual.csv (4 rows)
```

---

## 7. Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `Connection timeout` | Coba lagi beberapa saat, Blibli mungkin rate limit |
| `403 Forbidden` | URL gambar mungkin sudah expired, copy ulang dari browser |
| Gambar tidak terdownload | Cek apakah URL valid (dimulai `https://`) |
| Metadata tidak terupdate | Jalankan `merge_blibli_metadata.py` manual |
| Ingesti rename | Edit `metadata_blibli_manual.csv` langsung |
