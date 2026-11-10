"""Fetcher settings. SEC asks every client to identify itself with a contact address."""
SEC_USER_AGENT = "Quality-Moat-Screener research schultz.janis@gmail.com"
SEC_MAX_RPS = 8                 # SEC fair-access limit is 10 requests/second
CACHE_DAYS = 7                  # reuse downloaded statements for this many days
YAHOO_PAUSE_S = 0.25            # pause between Yahoo per-ticker calls
OFFLINE = False                 # set by fetch_market_data.py --offline: use cached responses only
