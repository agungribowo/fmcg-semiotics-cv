"""
Merge Blibli Metadata to All
=============================
Jalankan setelah blibli_semi_auto.py selesai.
Gabungkan metadata_blibli_manual.csv ke metadata_all.csv.
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/01_raw")
ALL_CSV = RAW_DIR / "metadata_all.csv"
BLIBLI_CSV = RAW_DIR / "metadata_blibli_manual.csv"


def main():
    if not BLIBLI_CSV.exists():
        print(f"File tidak ditemukan: {BLIBLI_CSV}")
        print("Jalankan blibli_semi_auto.py terlebih dahulu.")
        return

    blibli = pd.read_csv(BLIBLI_CSV)
    print(f"Blibli metadata: {len(blibli)} rows")

    if ALL_CSV.exists():
        all_df = pd.read_csv(ALL_CSV)
        before = len(all_df)

        # Cek duplikat berdasarkan local_path
        existing_paths = set(all_df["local_path"].dropna())
        new_rows = blibli[~blibli["local_path"].isin(existing_paths)]

        if len(new_rows) == 0:
            print("Tidak ada data baru untuk ditambahkan.")
            return

        all_df = pd.concat([all_df, new_rows[["source", "keyword", "product_name", "local_path"]]], ignore_index=True)
        all_df.to_csv(ALL_CSV, index=False)
        print(f"metadata_all.csv: {before} -> {len(all_df)} rows (+{len(new_rows)})")
    else:
        blibli[["source", "keyword", "product_name", "local_path"]].to_csv(ALL_CSV, index=False)
        print(f"metadata_all.csv created: {len(blibli)} rows")


if __name__ == "__main__":
    main()
