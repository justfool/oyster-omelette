"""從烏嘎嘎卡牌中心抓 A／B 牌庫文字與單張卡圖。"""

from __future__ import annotations

import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

CARDS_URL = "https://agricola-viewer.vercel.app/cards.json"
MANIFEST_URL = "https://agricola-viewer.vercel.app/card-images.json"
CDN = "https://agricola-cards.pages.dev/"
DECKS = {"A", "B"}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://agricola-viewer.vercel.app/",
}
LAYOUT_KEYS = {
    "source_image",
    "position",
    "grid_col",
    "grid_row",
    "grid_cols",
    "grid_rows",
    "crop_top",
    "crop_bottom",
    "crop_left",
    "crop_right",
    "tags",
}

ROOT = Path(__file__).resolve().parent
TEXT_DIR = ROOT / "text"
IMAGE_DIR = ROOT / "images"


def file_id(card_id: str) -> str:
    return card_id.replace("*", "")


def text_record(card: dict) -> dict:
    record = {k: v for k, v in card.items() if k not in LAYOUT_KEYS}
    if "類型" not in record and record.get("類別"):
        record["類型"] = record["類別"]
    return record


def image_url(card: dict, manifest: dict) -> str | None:
    cid = file_id(card["卡片ID"])
    deck = card.get("牌組", "")
    rel = manifest.get("byDeckId", {}).get(f"{deck}/{cid}") or manifest.get("byId", {}).get(cid)
    if rel:
        return CDN + rel
    src = card.get("source_image")
    if src and src.endswith((".jpg", ".jpeg", ".png", ".webp")):
        return CDN + "images/" + src
    return None


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(fetch_bytes(url))


def main() -> None:
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    cards = json.loads(fetch_bytes(CARDS_URL).decode("utf-8"))
    manifest = json.loads(fetch_bytes(MANIFEST_URL).decode("utf-8"))

    deck_cards = [c for c in cards if c.get("牌組") in DECKS]
    jobs: list[tuple[str, str, Path]] = []
    for card in deck_cards:
        cid = file_id(card["卡片ID"])
        (TEXT_DIR / f"{cid}.json").write_text(
            json.dumps(text_record(card), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        url = image_url(card, manifest)
        if url is None:
            print(f"no image url: {card['卡片ID']}")
            continue
        ext = Path(urlparse(url).path).suffix.lower() or ".webp"
        dest = IMAGE_DIR / f"{cid}{ext}"
        if dest.exists() and dest.stat().st_size > 0:
            continue
        jobs.append((card["卡片ID"], url, dest))

    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(download, url, dest): cid for cid, url, dest in jobs}
        for future in as_completed(futures):
            cid = futures[future]
            try:
                future.result()
            except Exception as exc:
                failed.append(f"{cid}: {exc}")

    print(f"text {len(deck_cards)}  images {len(jobs) - len(failed)}  failed {len(failed)}")
    for line in failed:
        print(line)


if __name__ == "__main__":
    main()
