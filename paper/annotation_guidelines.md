# Panduan Anotasi Dataset Semiotika Kemasan FMCG

Dokumen ini berisi petunjuk operasional anotasi gambar kemasan produk FMCG Indonesia untuk penelitian:
**"Large-Scale Multimodal Analysis of Product Packaging: Visual Semiotic Classification"**

---

## 1. Tujuan Pelabelan
Anotasi ini bertujuan membentuk *Ground Truth* (data acuan) yang menggabungkan:
1. **Fitur Kebahasaan (Denotasi):** Jenis aksara/teks Jepang yang teridentifikasi.
2. **Fitur Semiotika Visual (Konotasi):** Citra atau pesan budaya Jepang yang dibangun oleh kemasan.

---

## 2. Petunjuk Akses
1. Buka antarmuka Label Studio melalui tautan DagsHub Project.
2. Login menggunakan akun yang ditunjuk.
3. Gambar akan ditampilkan satu per satu di layar utama.

---

## 3. Rubrik Pelabelan

### Bagian 1: Jenis Aksara (Multi-Select / Boleh Pilih Lebih dari Satu)
* **Kanji (漢字):** Terdapat karakter Kanji (contoh: 味, 新, 辛).
* **Katakana (カタカナ):** Terdapat aksara Katakana (contoh: ラーメン, マッチャ).
* **Hiragana (ひらがな):** Terdapat aksara Hiragana (contoh: おいしい, ほんもの).
* **Romaji / Istilah Latin:** Menggunakan kosakata bahasa Jepang yang ditulis dengan huruf Latin/Romawi (contoh: *Takoyaki*, *Gekikara*, *Oishii*).
* **Pseudo-Japanese:** Teks yang sekilas tampak seperti aksara Jepang, tetapi tidak memiliki makna linguistik yang valid (huruf hiasan/rekaan).

---

### Bagian 2: Klasifikasi Semiotika Visual (Single Choice / Pilih 1 Terbaik)
* **Otentik & Premium Tradisional:** Kemasan menggunakan warna tenang/gelap, kaligrafi (*shodo*), Kanji dominan, serta menekankan keaslian resep atau tradisi Jepang.
* **Pop Culture & Modern Casual:** Kemasan menggunakan warna cerah, memuat makanan populer (Ramen, Gyoza), serta menargetkan segmen konsumen muda/kasual.
* **Kawaii & Character Branding:** Kemasan didominasi oleh ilustrasi karakter/maskot imut berestetika Jepang.
* **Pseudo-Japanese / Minimal Gimmick:** Aksara Jepang hanya berupa tempelan kecil tanpa mendukung tema estetika kemasan secara keseluruhan.
* **Bukan Kemasan / Data Noise:** Gambar tidak menampilkan kemasan produk secara utuh (contoh: poster, logo, atau gambar buram/rusak).

---

### Bagian 3: Catatan Linguistik (Opsional)
Berisi catatan dari pakar bahasa jika ditemukan anomali tata bahasa, kesalahan ejaan Romaji/Kanji, atau pergeseran makna semantik pada produk lokal.