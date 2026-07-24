# Status & Pelacakan Anotasi Dataset

Dokumen ini mencatat perkembangan proses anotasi dataset kemasan FMCG.

---

## 1. Ringkasan Dataset Anotasi

| Metrik | Nilai |
| :--- | :--- |
| **Target Dataset (Primary High-Res)** | 401 Gambar |
| **Lokasi Storage** | `data/03_processed/high_res_annotation/` |
| **Platform Anotasi** | Label Studio via DagsHub |
| **Anotator Utama** | Pakar Bahasa & Semiotika Jepang |
| **Status Pekerjaan** | **In Progress** |

---

## 2. Tabel Pelacakan Progres Batch

| Batch | Jumlah Gambar | Sumber Data | Status Anotasi | Tanggal Selesai | Catatan |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Batch 1 (Shopee Mall)** | 148 | Shopee Mall (Manual High-Res) | Belum Mulai | - | Target awal anotasi |
| **Batch 2 (Blibli)** | 253 | Blibli (Semi-Auto High-Res) | Belum Mulai | - | Target tahap kedua |

---

## 3. Log Perubahan & Diskusi Rubrik

* **2026-07-24:** Proyek Label Studio berhasil dibuat di DagsHub. XML disesuaikan untuk mendukung analisis Multi-label Aksara (Denotasi) dan Klasifikasi Semiotika (Konotasi).