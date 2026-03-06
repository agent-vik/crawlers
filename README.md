# Crawlers

Data crawlers for public data sources, maintained by [Agent Vik](https://github.com/agent-vik).

## Crawlers

| Crawler | Source | Data | Schedule |
|---------|--------|------|----------|
| [world-gdp](crawlers/world-gdp/) | World Bank | Global GDP (2019+) | Monthly (1st) |

## Structure

```
crawlers/
├── crawlers/           # Individual crawler modules
│   └── world-gdp/
│       └── main.py
├── data/               # Output data (CSV)
├── .github/workflows/  # Schedules (one yml per crawler)
├── requirements.txt    # Shared dependencies
└── README.md
```

## Scheduling

Each crawler has its own workflow file:

```
.github/workflows/world-gdp.yml
```

Edit the `cron` expression to change schedule:

```yaml
on:
  schedule:
    - cron: '0 0 1 * *'  # minute hour day month weekday
```

## Data

All output data is stored in `data/` directory as CSV files.

## Adding a New Crawler

1. Create: `crawlers/<name>/main.py`
2. Create: `.github/workflows/<name>.yml`
3. Update `requirements.txt` if needed
4. Update this README
