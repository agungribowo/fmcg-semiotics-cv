"""
DeepSeek Japanese Filter
========================
Menggunakan DeepSeek API untuk mendeteksi elemen semiotik Jepang
dalam nama produk/deskripsi, lalu memfilter dataset.

Cara pakai:
    set DEEPSEEK_API_KEY=sk-xxx
    python deepseek_filter.py
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import pandas as pd
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/01_raw")

SYSTEM_PROMPT = """Anda adalah ahli semiotik yang menganalisis nama produk FMCG Indonesia.
Tugas Anda: deteksi apakah nama produk mengandung ELEMEN SEMIOTIK JEPANG.

Elemen semiotik Jepang meliputi:
1. Aksara Jepang langsung: Hiragana (\\u3040-\\u309F), Katakana (\\u30A0-\\u30FF), Kanji (\\u4E00-\\u9FFF)
2. Kata serapan Jepang dalam Latin: ramen, matcha, takoyaki, miso, sushi, wasabi, sake, teriyaki, udon, nori, edamame, onigiri, tempura, karaage, shoyu, yakisoba, bento, dll
3. Merek Jepang: Suntory, Shiseido, Senka, Hadalabo, Biore, Anessa, Pokka, Ito En, Pocari, Soyjoy, Yobick, Oronamin, Fibe Mini, C1000, You C1000
4. Istilah rasa/kualitas Jepang: matcha, sakura, hojicha, genmaicha, gekikara (super pedas)
5. Nama produk yang menggunakan gaya bahasa Jepang atau mengandung unsur budaya Jepang

Balas dengan JSON:
{"has_japanese": true/false, "confidence": 0.0-1.0, "reason": "penjelasan singkat", "jp_elements": ["elemen1", "elemen2"]}"""


class DeepSeekFilter:
    def __init__(self, api_key: str, model: str = "deepseek-chat", batch_size: int = 20):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = model
        self.batch_size = batch_size
        self.stats = {"total": 0, "passed": 0, "failed": 0, "cost_est": 0.0}

    def analyze_product_name(self, name: str) -> dict:
        """Analisis 1 nama produk via DeepSeek."""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Nama produk: {name}"},
                ],
                temperature=0.1,
                max_tokens=150,
                response_format={"type": "json_object"},
            )
            text = resp.choices[0].message.content or "{}"
            # Estimate cost: ~100 input + 50 output tokens
            self.stats["cost_est"] += (100 * 0.14 + 50 * 0.28) / 1_000_000
            return json.loads(text)
        except Exception as e:
            logger.warning(f"API error for '{name[:30]}': {e}")
            return {"has_japanese": False, "confidence": 0.0, "reason": f"API error: {e}"}

    def filter_dataset(
        self,
        metadata_path: Path,
        name_column: str = "product_name",
        min_confidence: float = 0.5,
        output_suffix: str = "_deepseek",
        max_rows: Optional[int] = None,
        checkpoint_interval: int = 100,
    ) -> pd.DataFrame:
        logger.info(f"DeepSeek filtering: {metadata_path}")
        logger.info(f"  Model: {self.model}, min_confidence={min_confidence}")

        out_name = f"{metadata_path.stem}{output_suffix}.csv"
        out_path = RAW_DIR / out_name
        checkpoint_name = f"{metadata_path.stem}{output_suffix}_checkpoint.csv"
        checkpoint_path = RAW_DIR / checkpoint_name

        results = []
        start_idx = 0

        if checkpoint_path.exists():
            existing = pd.read_csv(checkpoint_path)
            results = existing.to_dict("records")
            start_idx = len(results)
            logger.info(f"  Resuming from checkpoint: {start_idx} rows already done")

        df = pd.read_csv(metadata_path)
        if max_rows:
            df = df.head(max_rows)
        logger.info(f"  Total: {len(df)} rows")

        for idx, row in df.iterrows():
            if idx < start_idx:
                continue

            name = str(row.get(name_column, ""))
            if not name:
                continue

            analysis = self.analyze_product_name(name)
            passed = analysis.get("has_japanese", False) and analysis.get("confidence", 0) >= min_confidence

            row_dict = row.to_dict()
            row_dict["ds_has_japanese"] = analysis.get("has_japanese", False)
            row_dict["ds_confidence"] = analysis.get("confidence", 0.0)
            row_dict["ds_reason"] = analysis.get("reason", "")
            row_dict["ds_jp_elements"] = json.dumps(analysis.get("jp_elements", []))
            results.append(row_dict)

            self.stats["total"] += 1
            if passed:
                self.stats["passed"] += 1
            else:
                self.stats["failed"] += 1

            if (idx + 1) % 10 == 0:
                pct = (idx + 1) / len(df) * 100
                logger.info(f"  Progress: {idx+1}/{len(df)} ({pct:.0f}%) | Passed: {self.stats['passed']}")

            if (idx + 1) % checkpoint_interval == 0:
                pd.DataFrame(results).to_csv(checkpoint_path, index=False)
                logger.info(f"  Checkpoint saved: {idx+1} rows")

            # Rate limit removed async calls are self-throttling

        result_df = pd.DataFrame(results)
        passed_df = result_df[result_df["ds_has_japanese"] & (result_df["ds_confidence"] >= min_confidence)]

        logger.info(f"  Results: {self.stats['passed']}/{self.stats['total']} passed ({self.stats['passed']/self.stats['total']*100:.1f}%)")
        logger.info(f"  Est. cost: ${self.stats['cost_est']:.4f}")

        # Save
        result_df.to_csv(out_path, index=False)
        logger.info(f"  Full results: {out_path}")

        # Remove checkpoint
        if checkpoint_path.exists():
            checkpoint_path.unlink()

        # Save filtered only
        filtered_name = f"{metadata_path.stem}{output_suffix}_filtered.csv"
        filtered_path = RAW_DIR / filtered_name
        passed_df.to_csv(filtered_path, index=False)
        logger.info(f"  Filtered ({len(passed_df)}): {filtered_path}")

        return result_df


def main():
    api_key = ""
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("DEEPSEEK_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip("\"'")
                break
    if not api_key:
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        logger.error("DEEPSEEK_API_KEY not found! Buat file .env dulu.")
        return

    flt = DeepSeekFilter(api_key=api_key, batch_size=20)

    exclude = ["_deepseek", "filtered", "all", "curated", "_new", "_id_lanjutan", "metadata_google_id"]
    for f in sorted(RAW_DIR.glob("metadata_*.csv")):
        if any(p in f.stem for p in exclude):
            continue
        logger.info(f"\n{'='*50}")
        flt.filter_dataset(f)

    logger.info(f"\n=== FINAL ===")
    logger.info(f"Total: {flt.stats['total']}, Passed: {flt.stats['passed']}, Failed: {flt.stats['failed']}")
    logger.info(f"Est cost: ${flt.stats['cost_est']:.4f}")


if __name__ == "__main__":
    main()
