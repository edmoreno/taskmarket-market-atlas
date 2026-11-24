# Taskmarket Market Atlas

An independent, read-only public market dashboard. Built for a paid Taskmarket bounty; not an official product. No wallet, analytics, tracking SDKs or private keys.

## Deploy in one command

Requirements: Git, GitHub CLI authenticated to an account permitted to create a public repository and enable GitHub Pages/Actions. From this checkout:

```sh
bash deploy.sh YOUR_ACCOUNT/YOUR_NEW_REPO
```

This publishes a public repository and enables Pages. The first Actions run fetches data and deploys. For a fork, enable Pages with source **GitHub Actions**, enable the scheduled workflow and dispatch it once. Update canonical repo URLs and the Open Graph image URL in `site/index.html` for your account; these links do not affect collection or display. No API secrets are required.

## Local preview

```sh
python3 -m unittest discover -s tests -v
python3 scripts/collect.py
python3 -m http.server 8080 --directory site
```

Python 3.9+ and curl are sufficient. The collector deliberately uses curl: some public API routes reject Python's default HTTP client. A collection failure fails the build instead of publishing partial or invented data. Each request retries up to three times with a 45-second timeout.

## Data and freshness

Both `chainId=4217` (Tempo/OUSD) and `chainId=8453` (Base/USDC). Endpoints: `/api/market/stats`, `/api/stats/breakdowns`, `/api/stats/platform-time-series` (7d/30d/90d/all, day), `/api/stats/activity-heatmap` (same ranges, hourOfWeek), `/api/stats/activity-feed` (40), and every cursor page of `/api/tasks` (newest, 100, no status filter). Snapshot includes exact responses and per-request capture times. Task fields retained are ID, requester, createdAt, status, mode and reward; weekly aggregation can be independently recalculated from them.

GitHub Actions collects every 20 minutes, comfortably inside the hourly target under normal scheduling. GitHub can delay scheduled runs; the UI explicitly flags data older than an hour. A successful build atomically replaces the static snapshot. Pages serves cached data (typically `max-age=600`, verify headers for your deployment). The browser checks its own hosted snapshot every five minutes, never the third-party API. No CORS proxy or client API call. No cookies or client storage.

Task list pagination is checked for complete termination and non-advancing cursors. Task IDs are deduplicated. Weekly distinct posters are lowercased requester addresses per Monday-start UTC creation week; no identity inference. Top-five and largest-poster task shares measure concentration, not sybil-adjusted human counts. API headline counts and all-time status inventory have different scopes and are labelled separately. Financial values preserve integer micro-units at source and divide by 1e6 for display. Active-agent daily counts are not summed. The current day/week is partial. API collection is not a transactional snapshot.

## Availability commitment

Keep Pages and scheduled Actions enabled for at least 30 days after any bounty payout. This repository has no expiry or teardown job. Public-repository Actions schedules may be disabled by GitHub after extended inactivity; check the Actions tab if the visible timestamp becomes stale. The owner can manually dispatch the same refresh workflow. Hosting-platform outages cannot be ruled out.

## License

Original code is MIT (LICENSE). Bundled fonts retain SIL Open Font License files in `site/assets`. Taskmarket marks belong to Taskmarket and are provided for bounty use under the [brand-kit terms](https://gist.github.com/ponderingdemocritus/05b7371bb286ab09c9f3f26bc2af9636/af55554d77b0627ff96b52a82a2f3b94b9cab387); the MIT grant does not relicense those marks. No third-party logos are used.
