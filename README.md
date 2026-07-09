# fmcg-semiotics-cv
A Multimodal Deep Learning approach (CNN + OCR) for visual semiotics and cultural meaning classification on product packaging.

Topic (Tags) : computer-vision, ocr, multimodal-learning, semiotics, digital-humanities, transfer-learning

Kandidat Judul Paper (Jurnal Internasional/Nasional)
Sebelumnya kita sudah memiliki draf judul kasar mengenai integrasi OCR dan CNN. Untuk menembus jurnal Q1/Q2 (baik di bidang Ilmu Komputer terapan maupun Linguistik Komputasional), judul harus menonjolkan novelty fusi lintas disiplinnya. Berikut adalah beberapa opsi judul yang bisa Anda diskusikan dengan rekan dosen:

Opsi 1: Fokus pada Computer Vision & Metodologi (Cocok untuk Jurnal AI Terapan)

English: "Decoding Cultural Commodities: A Multimodal Deep Learning Approach for Visual Semiotics Classification on FMCG Packaging"

Indonesia: "Pendekatan Deep Learning Multimodal untuk Klasifikasi Semiotika Visual dan Komodifikasi Budaya pada Kemasan FMCG"

Opsi 2: Fokus pada Linguistik Komputasional & Semiotika (Cocok untuk Jurnal Digital Humanities)

English: "Bridging Semiotics and AI: Supervised Multimodal Fusion of OCR and CNN to Analyze Japanese Branding Intent in Indonesian Markets"

Indonesia: "Menjembatani Semiotika dan AI: Fusi Multimodal OCR dan CNN dalam Analisis Makna Konotatif Kemasan Bergaya Jepang di Indonesia"

Opsi 3: Keseimbangan Teknis & Bisnis (Lebih ringkas dan memukul)

English: "The Semiotics of Packaging: Automated Cultural Meaning Extraction using Transfer Learning and Optical Character Recognition"

Indonesia: "Semiotika Kemasan: Ekstraksi Makna Budaya Otomatis Menggunakan Transfer Learning dan Optical Character Recognition"

fmcg-semiotics-cv/
│
├── data/                  <- Folder ini WAJIB di-track menggunakan DVC (DagsHub), bukan Git biasa.
│   ├── 01_raw/            <- Gambar mentah hasil scraping KlikIndomaret.
│   ├── 02_interim/        <- Hasil OCR YomiToku (format JSON) sebelum dianotasi.
│   └── 03_processed/      <- Data final yang sudah dianotasi dosen via Label Studio (siap untuk training CNN).
│
├── notebooks/             <- Tempat coretan eksperimen atau file .ipynb.
│   ├── 01_exploratory_scraping.ipynb   <- Uji coba scraping skala kecil.
│   └── 02_yomitoku_colab_test.ipynb    <- Script untuk dijalankan di Google Colab.
│
├── src/                   <- Source code utama yang sudah rapi (bukan coretan).
│   ├── data_collection/
│   │   └── klikindomaret_scraper.py    <- Script Playwright yang baru kita diskusikan.
│   ├── features/
│   │   └── yomitoku_extractor.py       <- Script untuk menjalankan YomiToku dan mengekstrak teks/bounding box.
│   └── models/
│       ├── cnn_visual.py               <- Arsitektur model CNN untuk ekstraksi fitur visual.
│       └── multimodal_fusion.py        <- Arsitektur fusi (gabungan teks dan gambar).
│
├── paper/                 <- Semua hal terkait penulisan naskah jurnal.
│   ├── figures/           <- Gambar grafik, diagram arsitektur, atau heatmap Grad-CAM untuk paper.
│   ├── references/        <- File sitasi (.bib atau referensi PDF dari dosen).
│   └── manuscript.md      <- (Atau file .tex / .docx) Draft tulisan Anda dan dosen.
│
├── .dvc/                  <- Konfigurasi DVC (otomatis terbuat saat inisialisasi DVC).
├── .gitignore             <- File krusial agar gambar mentah atau file rahasia tidak ter-push ke GitHub.
├── requirements.txt       <- Daftar library (playwright, pandas, dll) agar environment mudah direplikasi.
└── README.md              <- Wajah dari repo Anda (Penjelasan proyek, arsitektur, dan cara menjalankan script).
