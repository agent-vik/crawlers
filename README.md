# Crawlers

Data crawlers for public data sources, maintained by [Agent Vik](https://github.com/agent-vik).

## Crawlers

| Crawler | Source | Data | Schedule |
|---------|--------|------|----------|
| [world-gdp](crawlers/world-gdp/) | World Bank | Global GDP (2019+) | Monthly |

## Structure

```
crawlers/
├── crawlers/           # Individual crawler modules
│   └── world-gdp/
│       └── main.py
├── utils/              # Shared utilities
├── data/               # Output data (CSV)
├── .github/workflows/  # GitHub Actions schedules
└── README.md
```

## Data

All output data is stored in `data/` directory as CSV files.

## Adding a New Crawler

1. Create directory: `crawlers/<name>/`
2. Write script: `main.py`
3. Add workflow: `.github/workflows/<name>.yml`
4. Update this README

## License

MIT
