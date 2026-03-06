#!/usr/bin/env python3
"""
World GDP Crawler
Fetches global GDP data from World Bank API
Indicator: GDP (current US$) - NY.GDP.MKTP.CD
"""

import csv
import json
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# Constants
API_URL = "https://api.worldbank.org/v2/country/WLD/indicator/NY.GDP.MKTP.CD"
START_YEAR = 2019
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "world_gdp.csv"


def fetch_gdp_data() -> list[dict]:
    """Fetch GDP data from World Bank API"""
    url = f"{API_URL}?format=json&date={START_YEAR}:2025&per_page=50"

    try:
        with urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
    except (URLError, HTTPError) as e:
        print(f"Error fetching data: {e}")
        return []

    # API returns [metadata, data_array]
    if len(data) < 2:
        print("Invalid API response")
        return []

    return data[1]


def process_data(raw_data: list[dict]) -> list[dict]:
    """Process raw API data into clean records"""
    records = []

    for item in raw_data:
        if item.get('value') is None:
            continue

        year = int(item['date'])
        gdp_usd = float(item['value'])
        gdp_trillion = round(gdp_usd / 1e12, 3)  # Convert to Trillion $

        records.append({
            'year': year,
            'gdp_trillion_usd': gdp_trillion,
            'source': 'World Bank',
            'indicator': 'GDP (current US$)'
        })

    # Sort by year descending
    records.sort(key=lambda x: x['year'], reverse=True)
    return records


def save_to_csv(records: list[dict]) -> None:
    """Save records to CSV file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = ['year', 'gdp_trillion_usd', 'source', 'indicator']

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Saved {len(records)} records to {OUTPUT_FILE}")


def main():
    print("Fetching World GDP data from World Bank API...")

    raw_data = fetch_gdp_data()
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
        print(f"  {r['year']}: {r['gdp_trillion_usd']} Trillion USD")

    return 0


if __name__ == "__main__":
    exit(main())
