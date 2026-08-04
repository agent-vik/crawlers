#!/usr/bin/env python3
"""
China CPI Crawler
Fetches China Consumer Price Index data from Eastmoney datacenter API.

Indicator: 居民消费价格指数(1978=100)
Data: Eastmoney returns monthly cumulative YoY index (NATIONAL_ACCUMULATE).
The 1978=100 base index is derived by chaining:
    base[y] = base[y-1] * (accumulate[y] / 100)
where accumulate[y] is the December cumulative index for year y
(equivalent to the full-year YoY change).
"""

import csv
from datetime import datetime
from pathlib import Path

import requests

# Eastmoney datacenter API
API_URL = (
    "https://datacenter-web.eastmoney.com/api/data/v1/get"
    "?reportName=RPT_ECONOMY_CPI"
    "&columns=ALL"
    "&pageNumber=1&pageSize=500"
    "&sortColumns=REPORT_DATE&sortTypes=1"
)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

START_YEAR = 2019
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "china_cpi.csv"


def fetch_cpi_accumulate() -> dict[int, float]:
    """Fetch monthly CPI data from Eastmoney, return {year: full-year YoY index}."""
    resp = requests.get(API_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("result") or not data["result"].get("data"):
        raise RuntimeError("Eastmoney returned no CPI data")

    # Accumulate per-year December cumulative index (full-year YoY, prev-year=100)
    by_year: dict[int, float] = {}
    for row in data["result"]["data"]:
        time_label = row.get("TIME", "")
        acc = row.get("NATIONAL_ACCUMULATE")
        if acc is None or "12月份" not in time_label:
            continue
        try:
            year = int(time_label[:4])
            by_year[year] = float(acc)
        except (ValueError, TypeError):
            continue

    return by_year


def read_existing() -> dict[int, float]:
    """Read existing base-index rows from CSV."""
    if not OUTPUT_FILE.exists():
        return {}
    existing: dict[int, float] = {}
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                existing[int(row["year"])] = float(row["cpi_1978_base"])
            except (ValueError, TypeError):
                continue
    return existing


def main() -> int:
    current_year = datetime.now().year
    print(f"Checking China CPI data (Eastmoney) up to {current_year}...")

    existing = read_existing()

    print("Fetching China CPI data from Eastmoney datacenter API...")
    try:
        accumulate = fetch_cpi_accumulate()
    except (requests.exceptions.RequestException, RuntimeError) as e:
        print(f"API request failed: {type(e).__name__}: {e}")
        return 0

    if not accumulate:
        print("No CPI data fetched")
        return 0

    # Build the base-index chain
    # Start point: use existing CSV values where available, else seed from 2019
    base = dict(existing)
    if not base:
        # Seed from the first available year using the provided reference
        # (2019 value is a known public constant; fall back to 2019=669.8)
        if 2019 in accumulate:
            base[2019] = 669.8
        else:
            print("No baseline year available to seed the chain")
            return 0

    # Chain forward using cumulative YoY
    for year in sorted(accumulate):
        if year in base:
            continue
        prev = year - 1
        if prev in base:
            base[year] = base[prev] * accumulate[year] / 100.0

    # Keep only years >= START_YEAR
    records = [
        {
            "year": y,
            "cpi_1978_base": round(v, 1),
            "source": "东方财富",
            "indicator": "居民消费价格指数(1978=100)",
        }
        for y, v in sorted(base.items())
        if y >= START_YEAR
    ]

    if not records:
        print("No complete records to save")
        return 0

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = ["year", "cpi_1978_base", "source", "indicator"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print("\nSummary:")
    for r in records:
        print(f"  {r['year']}: {r['cpi_1978_base']}")

    return 0


if __name__ == "__main__":
    exit(main())