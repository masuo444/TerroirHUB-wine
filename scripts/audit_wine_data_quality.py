#!/usr/bin/env python3
"""
Audit winery JSON data quality for Terroir HUB WINE.

The report is intentionally strict because the same data feeds static pages,
search, and Sakura's answer knowledge base.
"""

from __future__ import annotations

import glob
import json
import os
from collections import Counter, defaultdict


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PREF_NAMES = {
    "hokkaido": "北海道",
    "aomori": "青森県",
    "iwate": "岩手県",
    "miyagi": "宮城県",
    "akita": "秋田県",
    "yamagata": "山形県",
    "fukushima": "福島県",
    "ibaraki": "茨城県",
    "tochigi": "栃木県",
    "gunma": "群馬県",
    "saitama": "埼玉県",
    "chiba": "千葉県",
    "tokyo": "東京都",
    "kanagawa": "神奈川県",
    "niigata": "新潟県",
    "toyama": "富山県",
    "ishikawa": "石川県",
    "fukui": "福井県",
    "yamanashi": "山梨県",
    "nagano": "長野県",
    "gifu": "岐阜県",
    "shizuoka": "静岡県",
    "aichi": "愛知県",
    "mie": "三重県",
    "shiga": "滋賀県",
    "kyoto": "京都府",
    "osaka": "大阪府",
    "hyogo": "兵庫県",
    "nara": "奈良県",
    "wakayama": "和歌山県",
    "tottori": "鳥取県",
    "shimane": "島根県",
    "okayama": "岡山県",
    "hiroshima": "広島県",
    "yamaguchi": "山口県",
    "kagawa": "香川県",
    "ehime": "愛媛県",
    "kochi": "高知県",
    "fukuoka": "福岡県",
    "nagasaki": "長崎県",
    "kumamoto": "熊本県",
    "oita": "大分県",
    "miyazaki": "宮崎県",
    "kagoshima": "鹿児島県",
    "okinawa": "沖縄県",
}

CORE_FIELDS = ("id", "name", "address", "area", "desc", "grapes", "features")
TRUST_FIELDS = ("url", "source")
AIO_FIELDS = ("brands", "founded", "visit")


def has_brands(winery: dict) -> bool:
    brands = winery.get("brands") or []
    if not brands:
        return False
    for brand in brands:
        if isinstance(brand, dict) and brand.get("name"):
            return True
        if isinstance(brand, str) and brand.strip():
            return True
    return False


def is_missing(winery: dict, field: str) -> bool:
    if field == "brands":
        return not has_brands(winery)
    value = winery.get(field)
    return value in ("", None, []) or value == {}


def rank_for(winery: dict) -> tuple[str, list[str]]:
    missing = [field for field in CORE_FIELDS + TRUST_FIELDS + AIO_FIELDS if is_missing(winery, field)]
    if not missing:
        return "A", missing

    core_missing = [field for field in missing if field in CORE_FIELDS]
    aio_missing = [field for field in missing if field in AIO_FIELDS]
    trust_missing = [field for field in missing if field in TRUST_FIELDS]

    if len(missing) >= 5 or (core_missing and aio_missing and trust_missing):
        return "D", missing
    if core_missing:
        return "C", missing
    return "B", missing


def main() -> int:
    rank_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    by_pref: dict[str, Counter[str]] = defaultdict(Counter)
    worst: list[dict] = []
    b_records: list[dict] = []
    total = 0

    for path in sorted(glob.glob(os.path.join(BASE, "data", "data_*_wineries.json"))):
        pref = os.path.basename(path).replace("data_", "").replace("_wineries.json", "")
        with open(path, "r", encoding="utf-8") as f:
            wineries = json.load(f)

        for winery in wineries:
            total += 1
            rank, missing = rank_for(winery)
            rank_counts[rank] += 1
            by_pref[pref][rank] += 1
            missing_counts.update(missing)
            if rank in {"C", "D"}:
                worst.append(
                    {
                        "pref": pref,
                        "pref_name": PREF_NAMES.get(pref, pref),
                        "id": winery.get("id", ""),
                        "name": winery.get("name", ""),
                        "rank": rank,
                        "missing": missing,
                    }
                )
            elif rank == "B":
                b_records.append(
                    {
                        "pref": pref,
                        "pref_name": PREF_NAMES.get(pref, pref),
                        "id": winery.get("id", ""),
                        "name": winery.get("name", ""),
                        "missing": missing,
                    }
                )

    print("# Terroir HUB WINE data quality audit")
    print(f"total_wineries: {total}")
    print()
    print("## rank summary")
    for rank in ("A", "B", "C", "D"):
        count = rank_counts[rank]
        pct = (count / total * 100) if total else 0
        print(f"- {rank}: {count} ({pct:.1f}%)")

    print()
    print("## missing fields")
    for field, count in missing_counts.most_common():
        print(f"- {field}: {count}")

    print()
    print("## prefectures needing work")
    for pref, counts in sorted(
        by_pref.items(),
        key=lambda item: (item[1]["D"], item[1]["C"], item[1]["B"]),
        reverse=True,
    )[:15]:
        count = sum(counts.values())
        name = PREF_NAMES.get(pref, pref)
        print(f"- {name}: A={counts['A']} B={counts['B']} C={counts['C']} D={counts['D']} / {count}")

    if worst:
        print()
        print("## C/D records")
        for item in worst:
            print(f"- [{item['rank']}] {item['pref_name']} {item['name']} ({item['id']}): {', '.join(item['missing'])}")

    if b_records:
        print()
        print("## B records")
        for item in sorted(b_records, key=lambda x: (x["pref_name"], x["name"])):
            print(f"- [B] {item['pref_name']} {item['name']} ({item['id']}): {', '.join(item['missing'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
