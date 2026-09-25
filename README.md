# Capitol Ledger

A responsive dashboard for publicly disclosed U.S. congressional securities transactions. The published version is a static GitHub Pages site, refreshed every six hours from a public JSON feed. It requires no private key in the browser or deployment secrets.

## Data source

The live feed is the anonymous `/api/trades` and `/api/politicians` JSON service used by [Disclosed Capitol’s public trades website](https://www.disclosedcapitol.com/trades). I verified both endpoints return real trade/member records without an API key; the feed includes transaction and disclosure dates, politician, chamber, party, state, and the disclosed amount range. Trades are sorted by disclosure date and requested with a bounded page size. The ingestion snapshot includes at most 5,000 recent trades (up to the provider’s 10-year window) and all returned politician pages.

This is a third-party aggregator of public filings, not a direct government API. The aggregator can change its website endpoint or data coverage. Entries link back to its public disclosure pages. The optional local Next.js app calls the public endpoint server-side; the published static site refreshes JSON snapshots through GitHub Actions.

## Run locally

Requirements: Node.js 20 or newer.

```bash
npm install
npm run dev
```

Open http://localhost:3000. To create a fresh static data snapshot for the published site:

```bash
npm run ingest
python3 -m http.server 8000 --directory site
```

Open http://localhost:8000. The ingestion is idempotent by provider transaction ID and refreshes `site/data/`.

## Deployment

The site is configured to publish from the `codex/capitol-ledger-live` branch with GitHub Actions. The workflow refreshes public data, enables Pages for the repository, and deploys the `site/` directory. It also runs every six hours.

The hosting workflow does not require an API key or a user password. It does require a writable GitHub repository and GitHub Pages/Actions enabled for that repository. The Codex GitHub connection can write to the user’s existing repositories, but there is no dedicated Capitol Ledger repository in the connected account, and the available publishing tools cannot create a new repository. I have kept the publishing branch isolated from the existing default branch. The Pages URL uses that repository’s project path.

## Site features

- Recent disclosure feed with transaction date, disclosure date, disclosed amount range, buy/sell text, and over-45-day filing flags
- Search and filters for member/ticker, chamber, party, direction, date, and disclosed range
- Member directory with state, chamber, party, counts, and Bioguide portraits when available
- Member history, activity-by-month chart, and top ticker list
- Ticker lookup and leaderboards
- Responsive layout and paginated long lists
- Visible delay, public-data, range, and no-investment-advice disclosures

## Data limitations

- Disclosures are delayed; the feed does not represent real-time trading.
- The public snapshot is capped at 5,000 recent trade records; older history may be absent.
- Politician totals come from the data provider, while snapshot charts and rankings only count trades in the refreshed archive.
- A missing ticker in a filing is represented as `N/A`; it is not guessed from the asset description.
- Provider fields can be corrected or amended. The refresh process deduplicates stable IDs, but provider history remains authoritative.
- This tracker presents public records for informational purposes only and is not financial advice.
