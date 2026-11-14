"""Fetcher settings for EODHD fundamental & market data pipeline."""
SEC_USER_AGENT = "Quality-Moat-Screener research schultz.janis@gmail.com"
SEC_MAX_RPS = 8                 # SEC fair-access limit is 10 requests/second
EODHD_MAX_RPS = 12              # EODHD rate limit is 1,000 req/min (~16.6 req/s); stay safely at 12 req/s
EODHD_WORKERS = 8               # Concurrent workers for EODHD fetches
EODHD_MIN_QUOTA_RESERVE = 1000  # Keep at least 1,000 daily API calls in reserve
FUND_CACHE_DAYS = 30            # Reuse cached full EODHD fundamentals JSON for 30 days unless refreshed
EOD_CACHE_DAYS = 1              # Reuse EOD price history within the same trading day
CACHE_DAYS = 7                  # Default cache TTL for auxiliary endpoints
YAHOO_PAUSE_S = 0.25            # Legacy Yahoo pause
OFFLINE = False                 # Set by fetch_market_data.py --offline: use cached responses only
REFRESH_FUNDAMENTALS = False    # Set by fetch_market_data.py --refresh-fundamentals: force re-download
