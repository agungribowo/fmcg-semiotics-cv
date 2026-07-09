"""
YomiToku Extractor
==================
Menjalankan OCR YomiToku pada gambar produk dan mengekstrak teks
beserta bounding box. Output JSON disimpan ke data/02_interim/.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/01_raw")
INTERIM_DIR = Path("data/02_interim")


class YomiTokuExtractor:
    def __init__(self, model_name: str = "yomitoku-v1"):
        self.model_name = model_name
        # TODO: inisialisasi model YomiToku di sini

    def extract(self, image_path: Path) -> Dict:
        """
        OCR gambar dan return dictionary:
          {
            "image": "filename.jpg",
            "texts": ["teks1", "teks2"],
            "bboxes": [[x1,y1,x2,y2], ...],
            "confidences": [0.95, 0.87]
          }
        """
        # placeholder
        return {
            "image": image_path.name,
            "texts": [],
            "bboxes": [],
            "confidences": [],
        }

    def extract_all(self) -> List[Dict]:
        results = []
        for img_path in RAW_DIR.glob("*.*"):
            if img_path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            logger.info(f"Processing {img_path.name}")
            result = self.extract(img_path)
            results.append(result)
            # save individual JSON
            out_path = INTERIM_DIR / f"{img_path.stem}.json"
            with open(out_path, "w") as f:
                json.dump(result, f, indent=2)
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extractor = YomiTokuExtractor()
    data = extractor.extract_all()
    print(f"Extracted {len(data)} images")
