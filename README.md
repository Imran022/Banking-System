# Capitol Ledger

A responsive dashboard of public U.S. congressional securities disclosures. The standalone static website is in `site/`; a scheduled GitHub Action refreshes its JSON data every six hours without an API key.

## Data source

The refresh uses the anonymous `/api/trades` and `/api/politicians` JSON endpoints used by [Disclosed Capitol’s public trades website](https://www.disclosedcapitol.com/trades). Direct requests return current public trades without authentication. Records include transaction/disclosure dates, politician, chamber, party, state, and disclosed amount ranges.

The ingestion job stores up to 5,000 recent transactions (within the provider’s 10-year request window), with all politician profiles, and deduplicates by provider trade ID. This is a third-party aggregator of public filings; its endpoint and coverage may change. Amounts remain the ranges reported in disclosures.

## Publishing

The `codex/capitol-ledger-live` branch isolates this site and refresh workflow from the repository default branch. GitHub Actions refreshes the data every six hours and commits changed snapshots only to that branch. The connected GitHub integration could push the branch but could not enable Pages for this repository. The static files and refreshed data are publicly available from the branch; publish them through a Pages-enabled repository or compatible static CDN if desired. No API key, Vercel token, or third-party account credentials are used. The first live data refresh succeeded.

## Run locally

Requirements: Node.js 20 or newer.

```bash
npm install
npm run dev
```

For the standalone version:

```bash
npm run ingest
python3 -m http.server 8000 --directory site
```

Open http://localhost:8000.

## Features

- Recent disclosures, amount ranges, transaction and disclosure dates, and over-45-day filing flags
- Search and filters for member/ticker, chamber, party, direction, date, and amount bracket
- Politician directory and profiles with Bioguide portraits when available
- Member/ticker drilldown, monthly activity chart, and leaderboards
- 25-row pagination, responsive mobile layout, and visible public-data/no-advice disclaimer

## Limitations

- Filing data is delayed and may be incomplete, corrected, or amended.
- The static archive is capped at 5,000 recent trades; older histories may be missing.
- Politician totals come from the provider; charts and rankings count records in this bounded snapshot.
- The app does not guess a ticker when the provider marks it `N/A`.
- Informational use only, not financial advice.
