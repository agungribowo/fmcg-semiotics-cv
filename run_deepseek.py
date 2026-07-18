"""Run DeepSeek filter - detect Japanese elements in product names."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from src.data_collection.deepseek_filter import DeepSeekFilter

PROJECT_ROOT = Path(__file__).resolve().parent

# Read key
api_key = ""
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.startswith("DEEPSEEK_API_KEY="):
            api_key = line.split("=", 1)[1].strip().strip("\"'")
            break
if not api_key:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")

if not api_key:
    print("ERROR: No API key found!")
    sys.exit(1)

flt = DeepSeekFilter(api_key=api_key, batch_size=20)

raw = PROJECT_ROOT / "data" / "01_raw"

# Process specific metadata files
targets = [
    raw / "metadata_all.csv",  # 1844 rows - all sources
]

for f in targets:
    if f.exists():
        print(f"\n{'='*60}")
        flt.filter_dataset(f)

print(f"\n=== FINAL ===")
print(f"Total: {flt.stats['total']}, Passed: {flt.stats['passed']}, Failed: {flt.stats['failed']}")
print(f"Est cost: ${flt.stats['cost_est']:.4f}")
