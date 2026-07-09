# Kamus Semiotik Visual & Rubrik Anotasi (Ground Truth)

Dokumen ini merupakan pedoman *Ground Truth* bagi model Supervised Learning, dirumuskan oleh Pakar Domain (Dosen Bahasa Jepang) untuk memetakan elemen linguistik/visual ke dalam kelas klasifikasi semiotik.

## Landasan Teori Semiotika
[cite_start]Penelitian ini menggunakan kerangka teori dua tingkat signifikasi Roland Barthes[cite: 479]:
1.  [cite_start]**Denotasi (Tingkat I):** Makna harfiah dan langsung dari tanda (baik teks maupun visual pada kemasan)[cite: 480].
2.  [cite_start]**Konotasi (Tingkat II):** Makna kultural atau ideologis yang dibangun dari tanda denotatif tersebut[cite: 481]. [cite_start]Pada tingkat ini, tanda denotatif menjadi penanda baru yang memperoleh petanda yang lebih luas dan kaya secara kultural[cite: 595].

## Parameter Multi-Class Classification (Draft Awal)
Berikut adalah rancangan label kelas konotasi yang akan dianut oleh model AI:

* **Kelas 1: Premium Tradisional**
    * [cite_start]*Indikator Visual & Linguistik:* Sering dikonotasikan dengan warna gelap/emas dan tipografi Kanji kaligrafi[cite: 193].
* **Kelas 2: Pop & Kasual Modern**
    * [cite_start]*Indikator Visual & Linguistik:* Dikonotasikan dengan warna cerah, maskot, dan banyak kata serapan Katakana[cite: 194].
* **Kelas 3: Intensitas Ekstrem**
    * [cite_start]*Indikator Visual & Linguistik:* Sering dikaitkan dengan warna merah menyala dan kata Kanji seperti "Gekikara"[cite: 195].

> **Catatan untuk Kolaborator (Dosen Bahasa Jepang):** > *Mohon sesuaikan atau tambahkan definisi kelas-kelas di atas berdasarkan hasil temuan dari fase Exploratory Scraping agar selaras dengan fenomena Japanization aktual di pasaran.*