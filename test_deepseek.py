"""Quick test: DeepSeek API untuk filter nama produk."""
import os, json
from pathlib import Path
from openai import OpenAI

# Read API key from .env
env_path = Path(".env")
api_key = ""
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.startswith("DEEPSEEK_API_KEY="):
            api_key = line.split("=", 1)[1].strip().strip("\"'")
            break
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

test_names = [
    "Indomie Tori Kara Ramen",       # Should pass - Japanese elements
    "You C1000 Orange 500ml",         # Should pass - Japanese brand style
    "Aqua Air Mineral 600ml",         # Should NOT pass - pure Indonesian
    "Suntory Boss Coffee Rainbow",    # Should pass - Japanese brand
    "Shiseido Senka Perfect Whip",    # Should pass - Japanese brand
    "Indomie Goreng Original",        # Should NOT pass - generic
    "Pocari Sweat 500ml",             # Should pass - Japanese brand
    "Fibe Mini ファイブミニ",          # Should pass - Katakana in name
]

system_prompt = """Anda adalah ahli semiotik yang menganalisis nama produk FMCG Indonesia.
Tugas Anda: deteksi apakah nama produk mengandung ELEMEN SEMIOTIK JEPANG.

Elemen semiotik Jepang meliputi:
1. Aksara Jepang langsung: Hiragana, Katakana, Kanji
2. Kata serapan Jepang dalam Latin: ramen, matcha, miso, sushi, teriyaki, dll
3. Merek Jepang: Suntory, Shiseido, Senka, Hadalabo, Biore, Pokka, Ito En, Pocari, Soyjoy, Yobick, Oronamin
4. Istilah rasa/kualitas Jepang: matcha, sakura, hojicha, gekikara
5. Gaya bahasa Jepang atau unsur budaya Jepang dalam nama produk

Balas dengan JSON:
{"has_japanese": true/false, "confidence": 0.0-1.0, "reason": "penjelasan singkat"}"""

for name in test_names:
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Nama produk: {name}"},
        ],
        temperature=0.1, max_tokens=100,
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content or "{}")
    passed = result.get("has_japanese", False)
    conf = result.get("confidence", 0)
    reason = result.get("reason", "")[:80]
    mark = "YES" if passed else "NO"
    print(f"[{mark}] [{conf:.1f}] {name}")
    print(f"  -> {reason}")
