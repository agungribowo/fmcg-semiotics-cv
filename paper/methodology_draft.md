# Methodology & System Architecture

## 1. Pengumpulan Data (Automated Content-Based Filtering)
Karena tingginya tingkat *noise* pada pencarian e-commerce, pengumpulan data dilakukan dengan skema penyaringan berlapis:
* [cite_start]**Scraping Target:** Menggunakan Python Playwright menargetkan KlikIndomaret untuk menjaring representasi fisik produk Fast-Moving Consumer Goods (FMCG)[cite: 402]. 
* [cite_start]**Layer 1 (Data Collection Filter):** Integrasi EasyOCR yang berjalan secara real-time saat scraping[cite: 62]. [cite_start]Tugasnya adalah melakukan klasifikasi biner (Apakah ada teks Jepang/Latin spesifik di gambar ini? Yes/No)[cite: 63].
* [cite_start]Jika *Yes*, simpan gambar[cite: 64]. [cite_start]Jika *No*, buang (drop)[cite: 64]. [cite_start]Ini menyelesaikan masalah *noise* data secara elegan di pintu awal[cite: 65].

## 2. Arsitektur Multimodal Fusion
[cite_start]Model dibangun menggunakan pendekatan *Transfer Learning* yang memproses dua aliran data sekaligus[cite: 201]:

* [cite_start]**Aliran Semantik (Layer 2 - Feature Extractor):** Gambar kemasan dimasukkan ke YomiToku untuk membaca tata letak dan menghasilkan output teks Jepang beserta koordinat layout (JSON)[cite: 319].
* [cite_start]**Aliran Visual:** Gambar kemasan dimasukkan ke Transfer Learning CNN (seperti ResNet atau EfficientNet) untuk mengeluarkan fitur visual/grafis[cite: 320].
* [cite_start]**Multimodal Fusion:** Menggabungkan representasi output teks, koordinat layout, dan fitur visual CNN[cite: 321]. [cite_start]Fitur ini dilatih menjadi *classifier* baru berdasarkan anotasi semiotik[cite: 322].


## 3. Tech Stack & Environment (Spesifikasi Alat)
Untuk menjaga agar eksperimen ini dapat direproduksi (Reproducible Research), berikut adalah daftar pustaka dan alat utama yang digunakan dalam pipeline:

* **Scraping Engine:** `Python Playwright`. Dipilih karena kemampuannya me-render JavaScript secara dinamis, sangat cocok untuk e-commerce modern seperti KlikIndomaret yang menggunakan sistem *client-side rendering*.
* **Layer 1 (Data Collection Filter):** `EasyOCR`. Bertindak sebagai *gatekeeper* awal saat scraping berjalan. Karena sangat ringan, model ini dipakai untuk menyortir secara cepat apakah gambar memiliki elemen huruf Jepang/Latin target.
* **Layer 2 (Semantic & Layout Extractor):** `YomiToku`. Model OCR khusus bahasa Jepang yang digunakan untuk melakukan *layout analysis*, mendeteksi tata letak vertikal, dan mengekstrak aksara Kanji/Katakana/Hiragana beserta koordinat *bounding box*-nya menjadi file JSON.
* **Computer Vision (Feature Extractor):** `Transfer Learning CNN` (Misal: ResNet50 / EfficientNet) yang berjalan di framework PyTorch/TensorFlow untuk mengekstrak fitur grafis visual dari kemasan.