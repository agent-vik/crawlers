#!/usr/bin/env python3
"""
China CPI Crawler
Fetches China Consumer Price Index data from National Bureau of Statistics
Indicator: 居民消费价格指数(1978=100) - A090201
"""

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Constants
API_URL = "https://data.stats.gov.cn/easyquery.htm"
INDICATOR_CODE = "A090201"  # 居民消费价格指数(1978=100)
START_YEAR = 2019
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "china_cpi.csv"


def get_existing_years() -> set[int]:
    """Get years already in the CSV file"""
    if not OUTPUT_FILE.exists():
        return set()

    years = set()
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            years.add(int(row['year']))
    return years


def fetch_cpi_data() -> list[dict]:
    """Fetch CPI data from National Bureau of Statistics API"""
    params = (
        f"m=QueryData"
        f"&dbcode=hgnd"
        f"&rowcode=sj"
        f"&colcode=zb"
        f"&wds=[]"
        f'&dfwds=[{{"wdcode":"zb","valuecode":"{INDICATOR_CODE}"}}]'
        f"&k1={int(time.time() * 1000)}"
    )

    url = f"{API_URL}?{params}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://data.stats.gov.cn/",
    }

    try:
        request = Request(url, headers=headers)
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
    except (URLError, HTTPError) as e:
        print(f"Error fetching data: {e}")
        return []

    if data.get('returncode') != 200:
        print(f"API error: {data.get('returndata')}")
        return []

    return data.get('returndata', {}).get('datanodes', [])


def process_data(raw_data: list[dict]) -> list[dict]:
    """Process raw API data into clean records"""
    records = []

    for item in raw_data:
        if not item.get('data', {}).get('hasdata', False):
            continue

        year = int(item['wds'][1]['valuecode'])
        if year < START_YEAR:
            continue

        value = item['data']['data']

        records.append({
            'year': year,
            'cpi_1978_base': value,
            'source': '国家统计局',
            'indicator': '居民消费价格指数(1978=100)'
        })

    # Sort by year ascending
    records.sort(key=lambda x: x['year'])
    return records


def save_to_csv(records: list[dict]) -> None:
    """Save records to CSV file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = ['year', 'cpi_1978_base', 'source', 'indicator']

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
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

    print(f"Fetching China CPI data from National Bureau of Statistics...")

    raw_data = fetch_cpi_data()
    if not raw_data:
        print("No data fetched, exiting")
        return 1

    records = process_data(raw_data)
    if not records:
        print("No valid records processed, exiting")
        return 1

    save_to_csv(records)

    # Print summary
    print("\nSummary:")
    for r in records:
        print(f"  {r['year']}: {r['cpi_1978_base']}")

    return 0


if __name__ == "__main__":
    exit(main())
