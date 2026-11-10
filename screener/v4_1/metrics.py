"""Phase 4.1 audit metrics from annual series ({fiscal_year: value}, money in units, not millions).

Shared by the SEC (US) and Yahoo (EU / gaps) fetchers so both produce identical definitions.
"""
from __future__ import annotations

from statistics import median

DEFAULT_TAX = 0.21


def _last_years(series: dict, n: int) -> list[int]:
    return sorted(series)[-n:]


def cagr(series: dict, years: int):
    """CAGR between the latest year and `years` earlier; None if either end missing or non-positive."""
    if not series:
        return None
    end = max(series)
    start = end - years
    a, b = series.get(start), series.get(end)
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return (b / a) ** (1 / years) - 1


def true_fcf(ocf: dict, capex: dict, sbc: dict) -> dict:
    """True FCF = OCF − CapEx − SBC (CapEx/SBC taken as positive outflows; missing SBC = 0)."""
    out = {}
    for y, o in ocf.items():
        if o is None or y not in capex or capex[y] is None:
            continue
        out[y] = o - abs(capex[y]) - abs(sbc.get(y) or 0)
    return out


def roic_series(ebit: dict, tax_rate: dict, equity: dict, debt: dict, cash: dict, goodwill: dict, intang: dict):
    """Per-year ROIC = EBIT × (1 − t) / average invested capital (equity + debt − cash).
    Tangible ROIC deducts goodwill and other intangibles from invested capital."""
    def ic(y, tangible):
        if y not in equity or equity[y] is None:
            return None
        v = equity[y] + (debt.get(y) or 0) - (cash.get(y) or 0)
        if tangible:
            v -= (goodwill.get(y) or 0) + (intang.get(y) or 0)
        return v

    gaap, tang = {}, {}
    for y, e in ebit.items():
        if e is None:
            continue
        t = tax_rate.get(y)
        t = DEFAULT_TAX if t is None or not (0 <= t <= 0.40) else t
        nopat = e * (1 - t)
        for tangible, out in ((False, gaap), (True, tang)):
            cur, prev = ic(y, tangible), ic(y - 1, tangible)
            base = (cur + prev) / 2 if cur is not None and prev is not None else cur
            if base is not None and base > 0:
                out[y] = nopat / base
    return gaap, tang


def summarize(s: dict, price_at_year_end: dict | None = None) -> dict:
    """s: dict of annual series. Keys used: sales, ni, eps, ocf, capex, sbc, dividends, equity, debt, cash,
    goodwill, intang, ebit, pretax, tax, interest, assets, shares. Returns financials.csv fields."""
    g = lambda k: s.get(k) or {}
    fcf = true_fcf(g("ocf"), g("capex"), g("sbc"))
    tax_rate = {y: (g("tax")[y] / g("pretax")[y]) for y in g("tax") if g("pretax").get(y)}
    roic, roic_t = roic_series(g("ebit"), tax_rate, g("equity"), g("debt"), g("cash"), g("goodwill"), g("intang"))
    out = {}

    def latest(k):
        ser = g(k)
        return ser[max(ser)] if ser else None

    last = max(g("ni")) if g("ni") else None
    for key, src in (("ni_ttm_m", "ni"), ("ocf_ttm_m", "ocf"), ("sbc_ttm_m", "sbc"), ("lt_debt_m", "debt"),
                     ("interest_m", "interest"), ("ebit_ttm_m", "ebit"), ("total_assets_m", "assets"),
                     ("sales_ttm_m", "sales")):
        v = latest(src)
        out[key] = None if v is None else abs(v) / 1e6 if src in ("interest",) else v / 1e6
    cx, dv = latest("capex"), latest("dividends")
    out["capex_ttm_m"] = None if cx is None else abs(cx) / 1e6
    out["dividends_ttm_m"] = None if dv is None else abs(dv) / 1e6

    yrs = _last_years(roic, 10)
    if yrs:
        out["roic_median"] = median(roic[y] for y in yrs)
        out["roic_years"] = len(yrs)
    yt = _last_years(roic_t, 10)
    if yt:
        out["roic_tangible_median"] = median(roic_t[y] for y in yt)

    conv_years = [y for y in _last_years(fcf, 5) if g("ni").get(y) is not None]
    ni_sum = sum(g("ni")[y] for y in conv_years)
    if conv_years and ni_sum > 0:
        out["fcf_conv"] = sum(fcf[y] for y in conv_years) / ni_sum
        out["fcf_conv_years"] = len(conv_years)

    # v4.1 normalised earnings: mid-cycle margins and cycle-average NI (up to 10 years)
    sales = g("sales")
    ni_m = {y: g("ni")[y] / sales[y] for y in g("ni") if g("ni")[y] is not None and (sales.get(y) or 0) > 0}
    fcf_m = {y: fcf[y] / sales[y] for y in fcf if (sales.get(y) or 0) > 0}
    ym = _last_years(ni_m, 10)
    if ym:
        out["ni_margin_med"] = median(ni_m[y] for y in ym)
        out["margin_years"] = len(ym)
    yf = _last_years(fcf_m, 10)
    if yf:
        out["fcf_margin_med"] = median(fcf_m[y] for y in yf)
    yn = _last_years({y: v for y, v in g("ni").items() if v is not None}, 10)
    if yn:
        out["ni_avg_m"] = sum(g("ni")[y] for y in yn) / len(yn) / 1e6

    # v4.1 banks / insurers: return on (tangible) equity on average equity
    def eq(y, tangible):
        e = g("equity").get(y)
        if e is None:
            return None
        return e - ((g("goodwill").get(y) or 0) + (g("intang").get(y) or 0) if tangible else 0)

    for key, tangible in (("roe_median", False), ("rote_median", True)):
        ser = {}
        for y, n in g("ni").items():
            cur, prev = eq(y, tangible), eq(y - 1, tangible)
            base = (cur + prev) / 2 if cur is not None and prev is not None else cur
            if n is not None and base and base > 0:
                ser[y] = n / base
        yrs_e = _last_years(ser, 10)
        if yrs_e:
            out[key] = median(ser[y] for y in yrs_e)
    if g("equity"):
        ly = max(g("equity"))
        out["equity_m"] = g("equity")[ly] / 1e6
        out["tbv_m"] = eq(ly, True) / 1e6

    for name, ser in (("bv", g("equity")), ("eps", g("eps")), ("sales", g("sales")), ("fcf", fcf)):
        for n in (10, 5, 3):
            out[f"cagr_{name}_{n}"] = cagr(ser, n)

    # Buffett $1 test over the longest window up to 10 years (min 5) with prices and shares at both ends
    if price_at_year_end and g("shares") and last:
        for window in range(10, 4, -1):
            y0 = last - window
            p0, p1 = price_at_year_end.get(y0), price_at_year_end.get(last)
            sh0, sh1 = g("shares").get(y0), g("shares").get(last)
            if None in (p0, p1, sh0, sh1):
                continue
            retained = sum((g("ni").get(y) or 0) - abs(g("dividends").get(y) or 0) for y in range(y0 + 1, last + 1))
            if retained <= 0:
                break
            out["mcap_delta_m"] = (p1 * sh1 - p0 * sh0) / 1e6
            out["retained_m"] = retained / 1e6
            out["dollar_years"] = window
            break
    out["fiscal_year"] = last
    return out
