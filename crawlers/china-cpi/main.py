#!/usr/bin/env python3
"""
China CPI Crawler
Fetches China Consumer Price Index data from National Bureau of Statistics
via cn-stats (cnstats) PyPI package.

Indicator: 居民消费价格指数(1978=100) - A090201
Database: hgnd (宏观年度数据)
"""

import csv
from datetime import datetime
from pathlib import Path

import requests
from cnstats.stats import stats

# Constants
INDICATOR_CODE = "A090201"  # 居民消费价格指数(1978=100)
DBCODE = "hgnd"  # 宏观年度
START_YEAR = 2019
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "china_cpi.csv"


def get_existing_years() -> set[int]:
    """Get years already in the CSV file"""
    if not OUTPUT_FILE.exists():
        return set()

    years = set()
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            years.add(int(row["year"]))
    return years


def fetch_cpi_data(current_year: int) -> list[dict]:
    """Fetch CPI data from National Bureau of Statistics via cn-stats"""
    # Build date range string: "2019,2020,...,current_year"
    years = list(range(START_YEAR, current_year + 1))
    datestr = ",".join(str(y) for y in years)

    print(f"Querying cn-stats: zbcode={INDICATOR_CODE}, dbcode={DBCODE}, dates={datestr}")

    try:
        raw = stats(zbcode=INDICATOR_CODE, datestr=datestr, dbcode=DBCODE)
    except (requests.exceptions.JSONDecodeError, requests.exceptions.ConnectionError,
            requests.exceptions.Timeout, requests.exceptions.RequestException,
            KeyError, TypeError) as e:
        print(f"API request failed: {type(e).__name__}: {e}")
        print("This is likely due to NBS WAF blocking (403 UrlACL). Retry later.")
        return []

    if not raw:
        print("cn-stats returned empty result")
        return []

    # raw format: [[指标名称, 指标代码, 查询日期, 数值], ...]
    records = []
    for item in raw:
        if len(item) < 4:
            continue

        indicator_name = item[0]
        indicator_code = item[1]
        date_val = item[2]
        data_val = item[3]

        # Skip if data value is empty or not a valid number
        try:
            value = float(data_val)
        except (ValueError, TypeError):
            continue

        # date_val should be a year string for annual data
        try:
            year = int(date_val)
        except (ValueError, TypeError):
            continue

        if year < START_YEAR:
            continue

        records.append(
            {
                "year": year,
                "cpi_1978_base": value,
                "source": "国家统计局",
                "indicator": indicator_name,
            }
        )

    # Sort by year ascending
    records.sort(key=lambda x: x["year"])
    return records


def save_to_csv(records: list[dict]) -> None:
    """Save records to CSV file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = ["year", "cpi_1978_base", "source", "indicator"]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Saved {len(records)} records to {OUTPUT_FILE}")


def main():
    current_year = datetime.now().year
    print(f"Checking China CPI data for {current_year}...")

    # Check if current year data already exists
    existing_years = get_existing_years()
    if current_year in existing_years:
        print(f"Data for {current_year} already exists, skipping crawl")
        return 0

    print(f"Fetching China CPI data from National Bureau of Statistics (via cn-stats)...")

    records = fetch_cpi_data(current_year)
    if not records:
        print(f"No data fetched for {current_year}, may not be published yet")
        return 0

    save_to_csv(records)

    # Print summary
    print("\nSummary:")
    for r in records:
        print(f"  {r['year']}: {r['cpi_1978_base']}")

    return 0


if __name__ == "__main__":
    exit(main())
