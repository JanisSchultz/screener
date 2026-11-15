"""Quantitative PAR inputs computed from annual series and monthly prices (no network).

Owner EPS (per fiscal year, reporting currency) = (Net income + MAX(0, D&A − CapEx − IFRS-16 lease depreciation)) ÷
period-end shares outstanding (scaled to reported diluted EPS when net income clearly includes minority interests). D&A is taken
deterministically (cash-flow depreciation → income-statement D&A → reconciled depreciation) and capped at 1.5× its
prior-3y median (impairment guard); lease depreciation ≈ 20% of average lease liabilities for IFRS reporters only.
- Last peak Owner EPS = highest Owner EPS of the latest 5 fiscal years (converted to the quote currency).
- Cycle low / high multiple: for each of the last 60 monthly closes, price ÷ the peak Owner EPS known at that
  month (a fiscal year counts from its period end + 3 months filing lag; peak over the 5 fiscal years up to
  then; months where that peak is <= 0 are skipped). Low / high = MIN / MAX of the calendar-year medians
  (years with >= 3 months), so single bubble or crash months do not set the range. Current FX for all months.
- Cycle Owner EPS growth g = peak-to-peak growth: latest peak vs the peak of the prior 5 fiscal years
  (years last−9 … last−5), annualised over the actual gap between the two peak years. With a short history (Yahoo, ~4 years)
  g = growth from the first positive year in the window to the latest peak, annualised over >= 3 years.
- Years whose net income is more than 10% above operating cash flow and 30% above the prior year and (if
  reported) the following year — for the latest year +50% vs prior and 30% above cash flow — (one-off gains: tax-allowance releases, disposal / spin-off gains, hedge marks) are left out
  of the Owner EPS series.
- With an analyst 'My Peak EPS', each year's Owner EPS is capped at it before the cycle multiples are measured.
- v7.2: fiscal years ending before the first trading day (listing_date, primary listing only) are left out of the
  Owner EPS series — pre-IPO / carve-out years sit on a different share and capital basis (CVC FY2021).
- p2p_ok (peak-to-peak test, feeds the Gate 6 rule check): "Y" latest peak above the prior-cycle peak,
  "N" not above it — or, with a short history, the peak is the first year available and the latest year is
  more than 10% below it (earnings falling since the start of the data); blank = cannot tell.
"""
from __future__ import annotations

import datetime as dt
from statistics import median

from .metrics import implied_shares, owner_addback

PEAK_YEARS = 5
MULT_MONTHS = 60
SPIKE = 1.3                     # net income > 30% above each neighbouring year …
SPIKE_OCF = 1.1                 # … and > 10% above operating cash flow = one-off (non-cash) gain
SPIKE_LAST, SPIKE_LAST_OCF = 1.5, 1.3   # latest year (no following year yet): +50% vs prior and 30% above OCF


def spike_years(s: dict) -> list[int]:
    """Non-cash earnings spikes (tax-allowance releases, disposal / spin-off gains, hedge marks): net income
    more than 10% above operating cash flow and 30% above each reported neighbouring year (prior and following), with
    a positive prior year when it is reported (a spike reverts; a lasting step-up is real growth)."""
    ni, ocf = s.get("ni") or {}, s.get("ocf") or {}

    def spike(y, n):
        if not n or n <= 0 or not ocf.get(y) or n <= SPIKE_OCF * ocf[y]:
            return False
        prev, nxt = ni.get(y - 1), ni.get(y + 1)
        if prev is None and nxt is None:
            return False
        if prev is not None and (prev <= 0 or n <= SPIKE * prev):
            return False
        if nxt is None:                 # latest year: no reversal visible yet -> stricter test
            return prev is not None and n > SPIKE_LAST * prev and n > SPIKE_LAST_OCF * ocf[y]
        return n > SPIKE * max(nxt, 0)
    return sorted(y for y, n in ni.items() if spike(y, n))


def owner_eps_series(s: dict) -> dict:
    """{fiscal year: Owner EPS in reporting currency} for years with net income and shares (spike years left out).
    Add-back = MAX(0, D&A − CapEx − IFRS-16 lease depreciation proxy), see metrics.owner_addback."""
    g = lambda k: s.get(k) or {}
    ni, eps = g("ni"), g("eps")
    shares = implied_shares(ni, eps, g("shares"))
    skip = set(spike_years(s))
    out = {}
    for y, n in ni.items():
        sh = shares.get(y)
        if n is None or not sh or sh <= 0 or y in skip:
            continue
        add = owner_addback(s, y)
        e = eps.get(y)
        if e and n > 0 and e > 0 and not 0.67 <= (n / sh) / e <= 1.5:
            # net income includes minority interests (e.g. IBKR: holding-company NI vs Class A shares):
            # scale to the owners' share implied by reported diluted EPS
            out[y] = e * (1 + add / n)
        else:
            out[y] = (n + add) / sh
    return out


def _peak(eps: dict, last: int):
    yrs = [y for y in eps if last - PEAK_YEARS < y <= last]
    if not yrs:
        return None, None
    y = max(yrs, key=lambda k: eps[k])
    return eps[y], y


FILING_LAG_DAYS = 92
PRICE_HISTORY_START = "2014-02-01"   # EOD cache starts 2014-01-01: an earlier first bar says nothing about listing


def _available(fy: int, period_end: dict | None = None) -> dt.date:
    """Point-in-time availability of a fiscal year: period end + ~3 months filing lag (no look-ahead for
    January–June year-ends); 1 April of the following year when the period end is unknown."""
    pe = (period_end or {}).get(fy)
    if pe:
        try:
            return dt.date.fromisoformat(str(pe)[:10]) + dt.timedelta(days=FILING_LAG_DAYS)
        except ValueError:
            pass
    return dt.date(fy + 1, 4, 1)


def pre_listing_years(series: dict, listing_date: str | None) -> list[int]:
    """Fiscal years whose period end precedes the first trading day (None when listed before the price history)."""
    if not listing_date or str(listing_date) <= PRICE_HISTORY_START:
        return []
    pe = series.get("period_end") or {}
    return sorted(y for y, d in pe.items() if d and str(d)[:10] < str(listing_date)[:10])


def compute(series: dict, monthly_prices: dict | None, fx_rep_to_quote: float | None,
            peak_override: float | None = None, listing_date: str | None = None) -> dict:
    """financials.csv fields peak_oe_year, peak_oe_eps, cur_oe_eps, cur_oe_year, mult_low_5y, mult_high_5y,
    cagr_oe_eps, p2p_ok (+ notes). peak_override ('My Peak EPS', quote currency): each year's Owner EPS is capped at it
    for the cycle multiples, so the windfall / one-off years the override excludes cannot depress the multiples.
    listing_date: first trading day of the primary listing; earlier fiscal years are left out of the Owner EPS series."""
    eps = owner_eps_series(series)
    out, notes = {}, []
    pre = [y for y in pre_listing_years(series, listing_date) if y in eps]
    if pre and len(pre) < len(eps):
        eps = {y: v for y, v in eps.items() if y not in pre}
        notes.append(f"pre-listing FY{pre[0]}" + (f"–FY{pre[-1]}" if len(pre) > 1 else "") + " left out of Owner EPS")
    all_ni_yrs = series.get("ni") or {}
    ref_last = max(eps) if eps else (max(all_ni_yrs) if all_ni_yrs else None)
    spikes = [y for y in spike_years(series) if ref_last is None or y > ref_last - 2 * PEAK_YEARS]
    if spikes:
        notes.append("non-cash earnings spike left out of peak: FY" + ", FY".join(map(str, spikes)))
    if not eps or not fx_rep_to_quote:
        return {"_notes": ["PAR inputs n/a (no Owner EPS or FX)"]}
    last = max(eps)
    peak, py = _peak(eps, last)
    if peak is None:
        return {"_notes": ["PAR inputs n/a"]}
    out["peak_oe_year"], out["peak_oe_eps"] = py, round(peak * fx_rep_to_quote, 4)
    out["cur_oe_eps"] = round(eps[last] * fx_rep_to_quote, 4)
    out["cur_oe_year"] = last

    # peak-to-peak growth and test
    prior = {y: v for y, v in eps.items() if last - 2 * PEAK_YEARS < y <= last - PEAK_YEARS}
    if prior:
        ppy = max(prior, key=lambda k: prior[k])
        pp = prior[ppy]
        out["p2p_ok"] = "Y" if peak > pp else "N"
        if pp > 0 and peak > 0:
            out["cagr_oe_eps"] = round((peak / pp) ** (1 / max(1, py - ppy)) - 1, 4)
    else:
        notes.append("short history")
        window = sorted(y for y in eps if last - PEAK_YEARS < y <= last)
        first = next((y for y in window if eps[y] > 0), None)
        if first is not None and py > first and peak > 0:
            out["cagr_oe_eps"] = round((peak / eps[first]) ** (1 / max(py - first, 3)) - 1, 4)
        if window and py == window[0] and len(window) >= 3 and eps[last] < 0.9 * peak:
            out["p2p_ok"] = "N"

    # cycle multiples on monthly closes
    m_eps = eps
    if peak_override and peak_override > 0:
        cap = peak_override / fx_rep_to_quote
        m_eps = {y: min(v, cap) for y, v in eps.items()}
        if any(v > cap for v in eps.values()):
            notes.append("cycle multiples on Owner EPS capped at My Peak EPS")
    if monthly_prices:
        months = sorted(monthly_prices)[-MULT_MONTHS:]
        mults, by_year = [], {}
        for d in months:
            day = dt.date.fromisoformat(d)
            known = [y for y in m_eps if _available(y, series.get("period_end")) <= day]
            if not known:
                continue
            pk, _ = _peak({y: m_eps[y] for y in known}, max(known))
            if pk and pk > 0:
                mults.append(monthly_prices[d] / (pk * fx_rep_to_quote))
                by_year.setdefault(day.year, []).append(mults[-1])
        yearly = [median(v) for v in by_year.values() if len(v) >= 3]
        if len(mults) >= 12 and len(yearly) >= 2:
            out["mult_low_5y"], out["mult_high_5y"] = round(min(yearly), 2), round(max(yearly), 2)
            if len(mults) < MULT_MONTHS - 6:
                notes.append(f"multiples over {len(mults)} months")
        else:
            notes.append("too few months for cycle multiples")
    out["_notes"] = notes
    return out
