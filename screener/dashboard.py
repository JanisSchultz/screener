"""Standalone Interactive HTML Cockpit Generator for Quality & Moat Screener.

Compiles all universes (US, EU, CA) from data/ into a unified, high-performance,
zero-dependency standalone HTML application (output/screener.html).
"""
from __future__ import annotations

import csv
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from . import config as C
from .data import DATA_DIR, DOCS_DIR, OUTPUT_DIR, load_universe, universe_keys
from .fetch.metrics import cagr
from .gates import (
    G_FLAG_OK,
    G_FLAG_SAT_LO,
    active_roic,
    cap_audit,
    g6_checks,
    params,
    par_valuation,
    results,
    uses_gaap_roic,
)


def _load_sales_cagrs(u_key: str) -> dict[str, tuple[float | None, float | None]]:
    """Compute trailing 3y and 5y revenue CAGRs per company id from fundamentals_panel.csv."""
    panel_path = DATA_DIR / u_key / "fundamentals_panel.csv"
    if not panel_path.exists():
        return {}
    series: dict[str, dict[int, float]] = {}
    with panel_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cid, fy_s, rev_s = r.get("id"), r.get("fy"), r.get("revenue_m")
            if cid and fy_s and rev_s:
                try:
                    series.setdefault(cid, {})[int(fy_s)] = float(rev_s)
                except ValueError:
                    pass
    out: dict[str, tuple[float | None, float | None]] = {}
    for cid, ser in series.items():
        s3 = cagr(ser, 3)
        s5 = cagr(ser, 5)
        out[cid] = (round(s3, 4) if s3 is not None else None, round(s5, 4) if s5 is not None else None)
    return out


def collect_screener_data(keys: list[str] | None = None) -> dict[str, Any]:
    """Collect and compute all gate results and valuations across universes."""
    universe_list = keys or universe_keys()
    all_companies = []
    universes_meta = {}
    latest_price_date: str | None = None

    for u_key in universe_list:
        meta = load_universe(u_key)
        for tech in (meta.get("technicals") or {}).values():
            as_of = tech.get("as_of")
            if as_of and (latest_price_date is None or as_of > latest_price_date):
                latest_price_date = as_of
        universes_meta[u_key] = {
            "key": u_key,
            "title": meta.get("title", u_key.upper()),
            "index_name": meta.get("index_name", u_key.upper()),
            "currency": meta.get("currency", "USD"),
            "as_of": meta.get("as_of", "2026-10-31"),
            "parameters": meta.get("parameters", {}),
        }
        p = params(meta)
        # Full PAR parameter set (defaults + universe.json overrides) so the JS sandbox uses exactly the Python constants
        universes_meta[u_key]["par_params"] = {
            "k": p.get("par_cost_of_equity", 0.085),
            "k_fin": p.get("par_cost_of_equity_fin", 0.1025),
            "g_anchor_max": p.get("par_g_anchor_max", 0.130),
            "roic_cap": p.get("par_roic_cap", 0.50),
            "roic_term_max": p.get("par_roic_term_max", 0.20),
            "g_base": p.get("par_g_base", 0.030),
        }
        res_map = results(meta)
        sales_cagr_map = _load_sales_cagrs(u_key)

        for c in meta["companies"]:
            cid = c["id"]
            fin = meta["financials"].get(cid, {})
            s3_panel, s5_panel = sales_cagr_map.get(cid, (None, None))
            pres = res_map.get(cid, {})
            audit = cap_audit(c)
            cap_val = audit["cap_final"]
            moat_arch_val = audit["primary_moat"]
            sub_ind = c.get("sub_industry", "")
            val = par_valuation(fin, p, cap=cap_val, moat=moat_arch_val, sub_industry=sub_ind)

            # Active capital-return input (same helper as par_valuation): ROE for Balance-Sheet Financials,
            # GAAP ROIC for IFRIC-12 Concessions, Tangible Operating ROIC otherwise (no analyst overrides since v7.6).
            r_op = fin.get("roic_operating")
            r_med = fin.get("roic_median")
            roic_used, roic_source = active_roic(fin, sub_ind)

            st_map = pres.get("status", {})
            passes_g123a = bool(
                st_map.get("1") == "pass"
                and st_map.get("2") == "pass"
                and moat_arch_val not in (None, "", "None")
                and not audit["moat_partial"]
            )
            g6_chk = g6_checks(fin, sub_ind, p)
            g6_flags = sum(1 for v_ in g6_chk.values() if v_ == "flag")
            passes_quality_grade = bool(
                passes_g123a
                and st_map.get("3b") == "pass"
                and g6_flags < 3
            )
            passes_prime_grade = bool(
                pres.get("result") == C.RES_QPASS
                and g6_flags < 3
            )
            passes_growth_0g = bool(
                passes_quality_grade
                and val.get("status") == C.V_VALUED
                and val.get("g_market_flag") in (G_FLAG_OK, G_FLAG_SAT_LO)
                and val.get("g_market") is not None
                and val.get("g_market") < 0.05
                and val.get("g_org_exp") is not None
                and val.get("g_org_exp") >= 0.05
            )

            company_record = {
                "id": cid,
                "ticker": c.get("ticker") or cid,
                "company": c.get("company", cid),
                "country": c.get("country", ""),
                "sector": c.get("sector", ""),
                "sub_industry": c.get("sub_industry", ""),
                "universe": u_key,
                # Qualitative inputs
                "g1": c.get("1"),
                "g2": c.get("2"),
                "g2_reason": c.get("2r"),
                "g3a_moat_archetype": moat_arch_val,
                "g3_moat_scores": audit["moat_scores"],
                "moat_complete": audit["moat_complete"],
                "g3b_pricing": c.get("3b"),
                "g3m_moat_note": c.get("3m"),
                "g4_cap": cap_val,
                "g4_force_scores": audit["force_scores"],
                "g4n_note": c.get("4n"),
                "cap_init": audit["cap_init"],
                "cap_haircut": audit["mod_haircut"],
                "cap_fatal": audit["fatal_flaw"],
                "cap_audited": audit["audited"],
                "g5_mgmt": c.get("5"),
                "g6_cash": c.get("6"),
                "note": c.get("note"),
                "evidence": c.get("evidence"),
                "passes_g123a": passes_g123a,
                "passes_quality_grade": passes_quality_grade,
                "passes_prime_grade": passes_prime_grade,
                "passes_growth_0g": passes_growth_0g,
                # Gate Waterfall status
                "result": pres.get("result", C.RES_REVIEW),
                "rejected_at": pres.get("rejected_at", ""),
                "review_at": pres.get("review_at", ""),
                "gate_status": pres.get("status", {}),
                "failed_gates": [lbl for _, lbl, _ in pres.get("failed", [])],
                # Financial inputs
                "price": fin.get("price"),
                "quote_currency": fin.get("quote_currency") or universes_meta[u_key]["currency"],
                "market_cap_m": fin.get("market_cap_m"),
                "sales_ttm_m": fin.get("sales_ttm_m"),
                "ni_ttm_m": fin.get("ni_ttm_m"),
                "ebit_ttm_m": fin.get("ebit_ttm_m"),
                "capex_ttm_m": fin.get("capex_ttm_m"),
                "da_ttm_m": fin.get("da_ttm_m"),
                "dividends_ttm_m": fin.get("dividends_ttm_m"),
                "lt_debt_m": fin.get("lt_debt_m"),
                "cash_m": fin.get("cash_m"),
                "interest_m": fin.get("interest_m"),
                "roic_median": r_med,
                "roic_operating": r_op,
                "roic_used": roic_used,
                "roic_source": roic_source,
                "roe_median": fin.get("roe_median"),
                "equity_m": fin.get("equity_m"),
                "ocf_ni_2y": fin.get("ocf_ni_2y"),
                "owner_add_m": fin.get("owner_add_m"),
                "uses_gaap_roic": val.get("roic_basis_gaap", uses_gaap_roic(sub_ind)),
                "fcf_conv": fin.get("fcf_conv"),
                "peak_oe_year": fin.get("peak_oe_year"),
                "peak_oe_eps": fin.get("peak_oe_eps"),
                "cur_oe_eps": fin.get("cur_oe_eps"),
                "mult_low_5y": fin.get("mult_low_5y"),
                "mult_high_5y": fin.get("mult_high_5y"),
                "cagr_oe_eps": fin.get("cagr_oe_eps"),
                "sales_1y": fin.get("sales_1y"),
                "sales_3y": fin.get("sales_3y") if fin.get("sales_3y") is not None else s3_panel,
                "sales_5y": fin.get("sales_5y") if fin.get("sales_5y") is not None else s5_panel,
                "sales_cagr": fin.get("sales_cagr"),
                "sales_cagr_yrs": fin.get("sales_cagr_yrs"),
                "opcost_1y": fin.get("opcost_1y"),
                "opcost_cagr": fin.get("opcost_cagr"),
                "cap_growth": fin.get("cap_growth"),
                "buyback_yield": fin.get("buyback_yield"),
                "retention_rate": fin.get("retention_rate"),
                "roiic": fin.get("roiic"),
                "p2p_ok": fin.get("p2p_ok"),
                # Gate 6 rule check (review flags only; the qualitative Gate 6 decides)
                "g6_checks": g6_chk,
                "g6_flags": g6_flags,
                "g6_answer": c.get("6"),
                "g6_netdebt_yrs": fin.get("g6_netdebt_yrs"),
                "g6_intcov": fin.get("g6_intcov"),
                "fin_note": fin.get("fin_note"),
                # Quantitative Valuation (screener/gates.py par_valuation)
                "val_status": val.get("status", C.V_NODATA),
                "peak_eps": val.get("peak_eps"),
                "peak_weight": val.get("peak_weight"),
                "cur_oe_year": fin.get("cur_oe_year"),
                "cur_mult": val.get("cur_mult"),
                "par_mult": val.get("par_mult"),
                "par_val": val.get("par_val"),
                "vs_par": val.get("vs_par"),
                "term_mult": val.get("term_mult"),
                "term_val": val.get("term_val"),
                "vs_term": val.get("vs_term"),
                "irr_5y": val.get("irr_5y"),
                "dy": val.get("dy"),
                "g_start": val.get("g_start"),
                "g_org_start": val.get("g_org_start"),
                "g_exp": val.get("g_exp"),
                "g_org_exp": val.get("g_org_exp"),
                "cap_implied": val.get("cap_implied"),
                "cap_gap": val.get("cap_gap"),
                "g_market": val.get("g_market"),
                "g_market_flag": val.get("g_market_flag"),
                "g_gap": val.get("g_gap"),
                "bvps": val.get("bvps"),
                "nav_anchor": val.get("nav_anchor"),
                "mtm_holdco": val.get("mtm_holdco"),
                "finite_conc": val.get("finite_conc"),
                "bs_fin": val.get("bs_fin"),
                "disc_rate": val.get("k"),
                "reinv_eff": val.get("reinv_eff"),
                "pe_mm": val.get("pe_mm"),
                "pe_mck": val.get("pe_mck"),
                "pe_vd": val.get("pe_vd"),
                "roic_exp": val.get("roic_exp"),
                "ma_reinvest": val.get("ma_reinvest"),
                "ma_alpha": val.get("ma_alpha"),
                "ronic_le_r": val.get("ronic_le_r"),
                "bb_eff": val.get("bb_eff"),
            }
            all_companies.append(company_record)

    # Global KPI Aggregates
    qpass_count = sum(1 for c in all_companies if c["passes_prime_grade"])
    growth_0g_count = sum(1 for c in all_companies if c["passes_growth_0g"])
    valued_list = [c for c in all_companies if c["passes_prime_grade"] and c["val_status"] == C.V_VALUED]
    # v7.7: IRR in excess of each company's own hurdle r, so 8.50% and 10.25% names are comparable
    excess = [c["irr_5y"] - c["disc_rate"] for c in valued_list if c["irr_5y"] is not None and c["disc_rate"] is not None]
    median_excess_irr = statistics.median(excess) if excess else None

    stockholm_now = datetime.now(ZoneInfo("Europe/Stockholm"))

    return {
        "version": C.SCREENER_VERSION,
        "generated_at": stockholm_now.strftime("%Y-%m-%d %H:%M %Z"),
        "price_updated_at": latest_price_date,
        "summary": {
            "total_companies": len(all_companies),
            "quality_pass": qpass_count,
            "growth_0g": growth_0g_count,
            "valued": len(valued_list),
            "median_excess_irr": median_excess_irr,
        },
        "universes": universes_meta,
        "companies": all_companies,
        "fx_rates": C.FX_TO_USD,
        "changelog": C.CHANGELOG,
    }


def build_dashboard_html(data: dict[str, Any]) -> str:
    """Generate the complete, self-contained standalone HTML application."""
    json_payload = json.dumps(data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="theme-color" content="#090d16">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <title>Quality & Moat Screener — Global Dashboard (v{data['version']})</title>
  <style>
    /* CSS Reset & Dark Modern Financial Terminal Palette */
    :root {{
      --bg-base: #090d16;
      --bg-surface: #111827;
      --bg-card: #182234;
      --bg-card-hover: #1f2c42;
      --border: #26354a;
      --border-subtle: #1e293b;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --accent: #38bdf8;
      --accent-hover: #0ea5e9;
      --green: #10b981;
      --green-bg: rgba(16, 185, 129, 0.15);
      --green-border: rgba(16, 185, 129, 0.35);
      --red: #f43f5e;
      --red-bg: rgba(244, 63, 94, 0.15);
      --red-border: rgba(244, 63, 94, 0.35);
      --amber: #f59e0b;
      --amber-bg: rgba(245, 158, 11, 0.15);
      --amber-border: rgba(245, 158, 11, 0.35);
      --blue: #3b82f6;
      --blue-bg: rgba(59, 130, 246, 0.15);
      --purple: #a855f7;
      --purple-bg: rgba(168, 85, 247, 0.15);
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: rgba(56, 189, 248, 0.15);
    }}
    html, body {{
      width: 100%;
      max-width: 100vw;
      height: 100%;
      height: 100dvh;
      margin: 0;
      padding: 0;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg-base);
      color: var(--text-main);
      line-height: 1.45;
      font-size: 13px;
      display: flex;
      flex-direction: column;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}

    /* Layout & Header */
    .app-header {{
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-shrink: 0;
      z-index: 40;
      gap: 16px;
    }}
    .brand-title {{
      font-size: 16px;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      min-width: 0;
    }}
    .brand-subtitle {{
      color: var(--text-dim);
      font-size: 12px;
      font-weight: normal;
      margin-left: 6px;
    }}
    .badge-version {{
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 2px 7px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 600;
    }}
    .badge-updated {{
      background: rgba(148, 163, 184, 0.1);
      color: var(--text-muted);
      border: 1px solid var(--border);
      padding: 2px 8px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 500;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}
    .kpi-bar {{
      display: flex;
      gap: 20px;
      align-items: center;
      flex-shrink: 0;
    }}
    .kpi-chip {{
      display: flex;
      flex-direction: column;
      align-items: flex-end;
    }}
    .kpi-label {{
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      font-weight: 600;
      white-space: nowrap;
    }}
    .kpi-value {{
      font-size: 15px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}
    .kpi-value.green {{ color: var(--green); }}
    .kpi-value.accent {{ color: var(--accent); }}
    .kpi-value.amber {{ color: var(--amber); }}

    .kpi-label[title],
    .metric-box .label[title],
    .audit-stat .lbl[title],
    .card-metric-label[title],
    .sandbox-group label[title],
    .dcf-schedule-table th[title],
    .delta-table td:first-child[title],
    .filter-step-box strong[title],
    .filter-step-box span[title] {{
      cursor: help;
    }}

    /* Header Responsiveness */
    @media (max-width: 1024px) {{
      .app-header {{
        padding: 10px 16px;
      }}
      .brand-subtitle {{
        display: none;
      }}
      .kpi-bar {{
        gap: 14px;
      }}
      .kpi-value {{
        font-size: 14px;
      }}
    }}
    @media (max-width: 768px) {{
      .app-header {{
        padding: 8px 12px;
        flex-direction: column;
        align-items: stretch;
        gap: 8px;
        min-width: 0;
        max-width: 100%;
      }}
      .brand-title {{
        font-size: 15px;
        justify-content: space-between;
      }}
      .kpi-bar {{
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 5px;
        width: 100%;
        min-width: 0;
      }}
      .kpi-chip {{
        align-items: center;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 5px 4px;
        text-align: center;
        min-width: 0;
        overflow: hidden;
      }}
      .kpi-label {{
        font-size: 9px;
        letter-spacing: 0.01em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
      }}
      .kpi-value {{
        font-size: 13px;
        margin-top: 1px;
        white-space: nowrap;
      }}
    }}

    /* Navigation Tabs */
    .tab-bar {{
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border);
      padding: 0 24px;
      display: flex;
      gap: 4px;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      flex-shrink: 0;
      scrollbar-width: none;
    }}
    .tab-bar::-webkit-scrollbar {{
      display: none;
    }}
    .tab-btn {{
      padding: 11px 16px;
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      color: var(--text-muted);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.15s ease;
      white-space: nowrap;
      min-height: 44px;
    }}
    .tab-btn:hover {{
      color: var(--text-main);
      background: rgba(255,255,255,0.02);
    }}
    .tab-btn.active {{
      color: var(--accent);
      border-bottom-color: var(--accent);
    }}
    .pill-count {{
      background: var(--border);
      color: var(--text-muted);
      border-radius: 9999px;
      padding: 1px 6px;
      font-size: 11px;
      font-weight: 700;
    }}
    .tab-btn.active .pill-count {{
      background: rgba(56, 189, 248, 0.2);
      color: var(--accent);
    }}
    .tab-label-short {{
      display: none;
    }}
    @media (max-width: 768px) {{
      .tab-bar {{
        padding: 0 10px;
        gap: 2px;
      }}
      .tab-btn {{
        padding: 10px 10px;
        font-size: 12px;
        gap: 6px;
      }}
      .tab-label-full {{
        display: none;
      }}
      .tab-label-short {{
        display: inline;
      }}
    }}
    @media (max-width: 440px) {{
      .tab-bar {{
        padding: 0 6px;
        gap: 2px;
      }}
      .tab-btn {{
        padding: 8px 6px;
        font-size: 11px;
        gap: 4px;
        min-height: 40px;
      }}
      .pill-count {{
        padding: 1px 4px;
        font-size: 10px;
      }}
    }}

    /* Controls & Filter Bar */
    .controls-bar {{
      padding: 10px 24px;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }}
    .filters-left {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      flex: 1;
    }}
    .filters-right {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .search-box {{
      position: relative;
      width: 210px;
    }}
    .search-input {{
      width: 100%;
      background: var(--bg-base);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 7px 30px 7px 30px;
      color: var(--text-main);
      font-size: 13px;
      outline: none;
      transition: border-color 0.15s ease;
      height: 36px;
    }}
    .search-input:focus {{
      border-color: var(--accent);
    }}
    .search-icon {{
      position: absolute;
      left: 10px;
      top: 9px;
      color: var(--text-dim);
      font-size: 13px;
      pointer-events: none;
    }}
    .search-clear {{
      position: absolute;
      right: 8px;
      top: 7px;
      background: none;
      border: none;
      color: var(--text-dim);
      font-size: 16px;
      cursor: pointer;
      padding: 2px 6px;
      border-radius: 4px;
      display: none;
      line-height: 1;
    }}
    .search-clear:hover {{
      color: var(--text-main);
    }}
    .select-filter {{
      background: var(--bg-base);
      border: 1px solid var(--border);
      color: var(--text-main);
      border-radius: 6px;
      padding: 0 10px;
      font-size: 12px;
      outline: none;
      cursor: pointer;
      height: 36px;
      max-width: 170px;
      text-overflow: ellipsis;
    }}
    .market-pills {{
      display: flex;
      background: var(--bg-base);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 2px;
      height: 36px;
      align-items: center;
    }}
    .market-btn {{
      background: none;
      border: none;
      color: var(--text-muted);
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      height: 30px;
      display: inline-flex;
      align-items: center;
      white-space: nowrap;
    }}
    .market-btn.active {{
      background: var(--bg-card);
      color: var(--accent);
    }}
    .toggle-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--bg-base);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0 10px;
      height: 36px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
      transition: all 0.15s ease;
    }}
    .toggle-pill input {{
      accent-color: var(--amber);
      cursor: pointer;
    }}
    .toggle-pill:has(input:checked) {{
      border-color: var(--amber-border);
      background: var(--amber-bg);
      color: var(--amber);
    }}
    .view-toggle {{
      display: flex;
      background: var(--bg-base);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 2px;
      height: 36px;
      align-items: center;
    }}
    .view-btn {{
      background: none;
      border: none;
      color: var(--text-muted);
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      height: 30px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      white-space: nowrap;
    }}
    .view-btn.active {{
      background: var(--bg-card);
      color: var(--accent);
    }}
    .btn-export {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      height: 36px;
      transition: all 0.15s ease;
      white-space: nowrap;
    }}
    .btn-export:hover {{
      background: var(--bg-card-hover);
      border-color: var(--accent);
    }}
    .btn-export:disabled {{
      opacity: 0.45;
      cursor: not-allowed;
    }}
    .filter-count-pill {{
      font-size: 11px;
      color: var(--text-muted);
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
      padding: 0 4px;
    }}
    .btn-reset-filters {{
      background: none;
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0 9px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      height: 36px;
      display: none;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
      transition: all 0.15s ease;
    }}
    .btn-reset-filters:hover {{
      color: var(--text-main);
      border-color: var(--accent);
      background: var(--bg-card);
    }}

    @media (max-width: 768px) {{
      html, body {{
        height: auto;
        min-height: 100dvh;
        overflow-x: hidden;
        overflow-y: auto;
      }}
      .controls-bar {{
        padding: 8px 12px;
        gap: 8px;
        min-width: 0;
        max-width: 100%;
      }}
      .filters-left {{
        gap: 6px;
        width: 100%;
        min-width: 0;
        max-width: 100%;
      }}
      .filters-right {{
        width: 100%;
        min-width: 0;
        max-width: 100%;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }}
      .search-box {{
        width: 100%;
        flex: 1 1 100%;
        min-width: 0;
      }}
      .search-input {{
        font-size: 16px; /* Prevents auto-zoom on iOS */
      }}
      .select-filter {{
        font-size: 12px;
        flex: 1 1 calc(50% - 4px);
        min-width: 0;
        max-width: calc(50% - 4px);
        width: 0;
        text-overflow: ellipsis;
      }}
      .toggle-pill {{
        flex: 1 1 100%;
        justify-content: flex-start;
      }}
      .market-pills {{
        width: 100%;
        min-width: 0;
        max-width: 100%;
        justify-content: space-around;
      }}
      .market-btn {{
        flex: 1;
        justify-content: center;
        padding: 4px 6px;
        min-width: 0;
      }}
      .btn-export {{
        flex: 1;
        justify-content: center;
        min-width: 0;
      }}
      .view-toggle {{
        flex: 1;
        min-width: 0;
      }}
      .view-btn {{
        flex: 1;
        justify-content: center;
      }}
      .table-container {{
        overflow-y: visible;
        flex: none;
      }}
      .cards-container {{
        overflow-y: visible;
        flex: none;
      }}
    }}

    /* Table Container & Sticky Elements */
    .table-container {{
      flex: 1;
      width: 100%;
      overflow-y: auto;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      position: relative;
    }}
    .mobile-swipe-hint {{
      display: none;
      background: rgba(56, 189, 248, 0.08);
      border-bottom: 1px solid rgba(56, 189, 248, 0.2);
      color: var(--accent);
      font-size: 11px;
      font-weight: 500;
      padding: 7px 12px;
      text-align: center;
    }}
    @media (max-width: 768px) {{
      .mobile-swipe-hint.visible {{
        display: block;
      }}
    }}
    table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      text-align: left;
      white-space: nowrap;
    }}
    thead th {{
      background: var(--bg-surface);
      color: var(--text-muted);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 9px 12px;
      border-bottom: 1px solid var(--border);
      box-shadow: 0 1px 0 var(--border);
      cursor: pointer;
      user-select: none;
      position: sticky;
      top: 0;
      z-index: 20;
    }}
    thead th:hover {{
      color: var(--text-main);
      background: var(--bg-card);
    }}
    thead th.sorted {{
      color: var(--accent);
    }}
    /* Sticky First Column (Ticker) */
    thead th:first-child {{
      position: sticky;
      left: 0;
      top: 0;
      z-index: 30;
      background: var(--bg-surface);
      box-shadow: 2px 0 6px -1px rgba(0, 0, 0, 0.45);
    }}
    tbody td:first-child {{
      position: sticky;
      left: 0;
      z-index: 10;
      background: var(--bg-base);
      box-shadow: 2px 0 6px -1px rgba(0, 0, 0, 0.45);
    }}
    tbody tr {{
      transition: background-color 0.1s ease;
      cursor: pointer;
    }}
    tbody tr:hover td {{
      background-color: var(--bg-card-hover);
    }}
    tbody tr:hover td:first-child {{
      background-color: var(--bg-card-hover);
    }}
    tbody tr.selected td {{
      background-color: rgba(56, 189, 248, 0.12);
    }}
    tbody tr.selected td:first-child {{
      background-color: #10283d;
      box-shadow: inset 3px 0 0 var(--accent), 2px 0 6px -1px rgba(0, 0, 0, 0.45);
    }}
    tbody td {{
      padding: 8px 12px;
      font-size: 12.5px;
      font-variant-numeric: tabular-nums;
      border-bottom: 1px solid var(--border-subtle);
    }}
    @media (max-width: 768px) {{
      tbody td {{
        padding: 10px 10px;
        font-size: 13px;
      }}
      thead th {{
        padding: 8px 10px;
      }}
    }}
    .cell-ticker {{
      font-weight: 700;
      color: var(--text-main);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }}
    .ticker-wrap {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }}
    .grade-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 22px;
      height: 18px;
      padding: 0 4px;
      border-radius: 4px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 10px;
      font-weight: 700;
      line-height: 1;
      letter-spacing: -0.02em;
      flex-shrink: 0;
    }}
    .grade-pill.grade-prime {{
      background: var(--green-bg);
      color: var(--green);
      border: 1px solid var(--green-border);
    }}
    .grade-pill.grade-quality {{
      background: var(--amber-bg);
      color: var(--amber);
      border: 1px solid var(--amber-border);
    }}
    .grade-pill.grade-fail {{
      background: var(--red-bg);
      color: var(--red);
      border: 1px solid var(--red-border);
    }}
    .grade-pill.grade-review {{
      background: rgba(148, 163, 184, 0.12);
      color: var(--text-muted);
      border: 1px solid rgba(148, 163, 184, 0.25);
    }}
    .cell-company {{
      max-width: 220px;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--text-main);
    }}
    .cell-sub {{
      font-size: 11px;
      color: var(--text-dim);
    }}
    .num {{
      text-align: right;
    }}

    /* Badges & Pills */
    .badge {{
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      line-height: 1.3;
      white-space: nowrap;
      max-width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      vertical-align: middle;
    }}
    .badge-green {{
      background: var(--green-bg);
      color: var(--green);
      border: 1px solid var(--green-border);
    }}
    .badge-red {{
      background: var(--red-bg);
      color: var(--red);
      border: 1px solid var(--red-border);
    }}
    .badge-amber {{
      background: var(--amber-bg);
      color: var(--amber);
      border: 1px solid var(--amber-border);
    }}
    .badge-blue {{
      background: var(--blue-bg);
      color: var(--blue);
      border: 1px solid rgba(59, 130, 246, 0.3);
    }}
    .badge-purple {{
      background: var(--purple-bg);
      color: var(--purple);
      border: 1px solid rgba(168, 85, 247, 0.3);
    }}
    .badge-gray, .badge-slate {{
      background: rgba(148, 163, 184, 0.1);
      color: var(--text-muted);
      border: 1px solid rgba(148, 163, 184, 0.2);
    }}

    /* Cards View Component */
    .cards-container {{
      flex: 1;
      width: 100%;
      max-width: 100%;
      min-width: 0;
      overflow-y: auto;
      overflow-x: hidden;
      -webkit-overflow-scrolling: touch;
      padding: 14px 16px;
    }}
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 12px;
      max-width: 1600px;
      margin: 0 auto;
    }}
    @media (max-width: 500px) {{
      .cards-container {{
        padding: 10px;
      }}
      .cards-grid {{
        grid-template-columns: minmax(0, 1fr);
        gap: 10px;
      }}
      .company-card {{
        padding: 12px;
      }}
      .card-metric-val {{
        font-size: 12px;
      }}
    }}
    .company-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 13px 15px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      flex-direction: column;
      gap: 8px;
      min-width: 0;
      max-width: 100%;
      overflow: hidden;
    }}
    .company-card:hover {{
      background: var(--bg-card);
      border-color: var(--accent);
      transform: translateY(-1px);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }}
    .company-card:active {{
      transform: scale(0.99);
    }}
    .company-card.selected {{
      border-color: var(--accent);
      background: rgba(56, 189, 248, 0.1);
      box-shadow: 0 0 0 1px var(--accent);
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }}
    .card-ticker-group {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }}
    .card-ticker {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 16px;
      font-weight: 700;
      color: var(--text-main);
      letter-spacing: -0.01em;
    }}
    .card-company-name {{
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-main);
      line-height: 1.3;
    }}
    .card-meta-line {{
      font-size: 11px;
      color: var(--text-dim);
    }}
    .card-metrics-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 6px;
      margin-top: 4px;
    }}
    .card-metric-cell {{
      background: var(--bg-base);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 6px 8px;
      min-width: 0;
      overflow: hidden;
    }}
    .card-metric-label {{
      font-size: 10px;
      color: var(--text-dim);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .card-metric-val {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
      margin-top: 2px;
      font-variant-numeric: tabular-nums;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 4px;
      border-top: 1px solid var(--border-subtle);
      font-size: 11px;
      color: var(--text-dim);
    }}
    .card-footer-action {{
      color: var(--accent);
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    /* Slide-Out Dossier Drawer */
    .drawer-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.55);
      backdrop-filter: blur(2px);
      z-index: 50;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }}
    .drawer-overlay.open {{
      opacity: 1;
      pointer-events: auto;
    }}
    .dossier-drawer {{
      position: fixed;
      top: 0;
      right: 0;
      bottom: 0;
      width: 100vw;
      max-width: 100vw;
      background: var(--bg-surface);
      border-left: none;
      box-shadow: -8px 0 28px rgba(0,0,0,0.4);
      z-index: 60;
      transform: translateX(100%);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      padding-bottom: env(safe-area-inset-bottom, 0);
    }}
    .dossier-drawer.open {{
      transform: translateX(0);
    }}
    .drawer-header {{
      padding: 16px 24px;
      border-bottom: 1px solid var(--border);
      background: var(--bg-card);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      flex-shrink: 0;
    }}
    /* Drawer Sub-Navigation Tabs */
    .drawer-nav {{
      display: flex;
      background: var(--bg-card);
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
      padding: 0 16px;
      gap: 6px;
      overflow-x: auto;
    }}
    .dossier-tab-btn {{
      padding: 11px 16px;
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      color: var(--text-muted);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.15s ease;
      white-space: nowrap;
      min-height: 42px;
    }}
    .dossier-tab-btn:hover {{
      color: var(--text-main);
      background: rgba(255,255,255,0.02);
    }}
    .dossier-tab-btn.active {{
      color: var(--accent);
      border-bottom-color: var(--accent);
    }}
    .dossier-tab-pane {{
      display: none;
      flex-direction: column;
      gap: 20px;
      min-width: 0;
      max-width: 100%;
    }}
    .dossier-tab-pane.active {{
      display: flex;
    }}

    /* Audit Breakdown Cards */
    .audit-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .audit-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 8px;
    }}
    .audit-card-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .binding-badge {{
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 3px 8px;
      border-radius: 9999px;
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.35);
      white-space: nowrap;
    }}
    .binding-badge.active-constraint {{
      background: rgba(245, 158, 11, 0.2);
      color: var(--amber);
      border-color: rgba(245, 158, 11, 0.4);
    }}
    .audit-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 8px;
    }}
    .audit-stat {{
      background: rgba(17, 24, 39, 0.6);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
    }}
    .audit-stat .lbl {{
      font-size: 10px;
      color: var(--text-dim);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .audit-stat .val {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
      margin-top: 2px;
      font-variant-numeric: tabular-nums;
    }}
    .audit-stat .sub {{
      font-size: 10px;
      color: var(--text-muted);
      margin-top: 2px;
    }}
    .filter-step-box {{
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 10px;
      background: rgba(255,255,255,0.015);
      display: flex;
      flex-direction: column;
      gap: 5px;
    }}
    .filter-step-box.binding {{
      border-color: rgba(245, 158, 11, 0.4);
      background: rgba(245, 158, 11, 0.06);
    }}

    /* Sandbox Panel */
    .sandbox-panel {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .sandbox-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 10px;
    }}
    .sandbox-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}
    @media (max-width: 640px) {{
      .sandbox-grid {{
        grid-template-columns: 1fr;
      }}
    }}
    .sandbox-group {{
      display: flex;
      flex-direction: column;
      gap: 5px;
      background: rgba(17, 24, 39, 0.5);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 8px 10px;
    }}
    .sandbox-group label {{
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .sandbox-group label .sb-val {{
      color: var(--accent);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-weight: 700;
      font-size: 12px;
    }}
    .sandbox-slider {{
      -webkit-appearance: none;
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: var(--border);
      outline: none;
      cursor: pointer;
      margin: 4px 0;
    }}
    .sandbox-slider::-webkit-slider-thumb {{
      -webkit-appearance: none;
      appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--accent);
      cursor: pointer;
      box-shadow: 0 0 6px rgba(56, 189, 248, 0.6);
      transition: transform 0.1s ease;
    }}
    .sandbox-slider::-webkit-slider-thumb:hover {{
      transform: scale(1.15);
    }}
    .sandbox-input-row {{
      display: flex;
      gap: 8px;
      align-items: center;
    }}
    .sandbox-num-input {{
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text-main);
      padding: 5px 8px;
      font-size: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      width: 100%;
    }}
    .sandbox-num-input:focus {{
      outline: none;
      border-color: var(--accent);
    }}
    .cap-btn-group {{
      display: flex;
      gap: 4px;
      margin-top: 2px;
    }}
    .cap-pill-btn {{
      flex: 1;
      padding: 5px 6px;
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 5px;
      color: var(--text-muted);
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
      transition: all 0.15s ease;
    }}
    .cap-pill-btn:hover {{
      color: var(--text-main);
      border-color: var(--accent);
    }}
    .cap-pill-btn.active {{
      background: rgba(56, 189, 248, 0.2);
      border-color: var(--accent);
      color: var(--accent);
      font-weight: 700;
    }}

    /* Delta Table */
    .delta-table-card {{
      background: rgba(17, 24, 39, 0.85);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
    }}
    .delta-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }}
    .delta-table th, .delta-table td {{
      padding: 7px 12px;
      text-align: right;
      border-bottom: 1px solid var(--border-subtle);
    }}
    .delta-table th:first-child, .delta-table td:first-child {{
      text-align: left;
    }}
    .delta-table th {{
      background: rgba(24, 34, 52, 0.6);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-dim);
      font-weight: 600;
    }}
    .delta-table tr:last-child td {{
      border-bottom: none;
    }}
    .diff-pos {{ color: var(--green); font-weight: 700; }}
    .diff-neg {{ color: var(--red); font-weight: 700; }}
    .diff-neutral {{ color: var(--text-muted); }}

    /* Explicit Year-by-Year DCF Schedule Table (Tab 3) */
    .dcf-table-wrap {{
      background: rgba(17, 24, 39, 0.85);
      border: 1px solid var(--border);
      border-radius: 8px;
      width: 100%;
      max-width: 100%;
      overflow-x: scroll;
      overflow-y: hidden;
      scrollbar-width: thin;
      scrollbar-color: var(--text-dim) var(--bg-base);
      -webkit-overflow-scrolling: touch;
    }}
    .dcf-table-wrap::-webkit-scrollbar {{
      height: 10px;
    }}
    .dcf-table-wrap::-webkit-scrollbar-track {{
      background: var(--bg-base);
      border-radius: 0 0 8px 8px;
    }}
    .dcf-table-wrap::-webkit-scrollbar-thumb {{
      background: var(--text-dim);
      border-radius: 5px;
    }}
    .dcf-table-wrap::-webkit-scrollbar-thumb:hover {{
      background: var(--text-muted);
    }}
    .dcf-schedule-table {{
      width: 100%;
      min-width: max-content;
      border-collapse: collapse;
      font-size: 11.5px;
      font-variant-numeric: tabular-nums;
    }}
    .dcf-schedule-table th, .dcf-schedule-table td {{
      padding: 6px 9px;
      text-align: right;
      border-bottom: 1px solid var(--border-subtle);
      white-space: nowrap;
    }}
    .dcf-schedule-table th:first-child, .dcf-schedule-table td:first-child {{
      text-align: left;
      position: sticky;
      left: 0;
      background: #131c2e;
      z-index: 2;
    }}
    .dcf-schedule-table th {{
      background: rgba(24, 34, 52, 0.85);
      font-size: 10.5px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-dim);
      font-weight: 600;
    }}
    .dcf-schedule-table th:first-child {{
      background: #182234;
      z-index: 3;
    }}
    .dcf-schedule-table tbody tr:hover td {{
      background: rgba(56, 189, 248, 0.05);
    }}
    .dcf-schedule-table tbody tr:hover td:first-child {{
      background: #1a2740;
    }}
    .dcf-row-base td {{
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.02);
      border-bottom: 1px solid var(--border);
    }}
    .dcf-row-subtotal td {{
      font-weight: 700;
      color: var(--text-main);
      background: rgba(56, 189, 248, 0.08);
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
    }}
    .dcf-row-subtotal td:first-child {{
      background: #16263d;
    }}
    .dcf-row-terminal td {{
      font-weight: 600;
      color: var(--amber);
      background: rgba(245, 158, 11, 0.08);
      border-bottom: 1px solid var(--border);
    }}
    .dcf-row-terminal td:first-child {{
      background: #23211d;
    }}
    .dcf-row-total td {{
      font-weight: 700;
      font-size: 12px;
      color: var(--green);
      background: rgba(16, 185, 129, 0.12);
      border-top: 2px solid var(--green-border);
      border-bottom: none;
    }}
    .dcf-row-total td:first-child {{
      background: #132a28;
    }}
    .dcf-sub {{
      display: block;
      font-size: 9.5px;
      color: var(--text-dim);
      font-weight: 400;
      margin-top: 1px;
    }}

    .drawer-body {{
      padding: 24px;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .btn-close {{
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 24px;
      cursor: pointer;
      line-height: 1;
      padding: 6px 10px;
      border-radius: 6px;
      min-width: 44px;
      min-height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .btn-close:hover {{
      color: var(--text-main);
      background: rgba(255,255,255,0.06);
    }}
    @media (max-width: 768px) {{
      .dossier-drawer {{
        width: 100%;
        max-width: 100vw;
        left: 0;
        right: 0;
        border-left: none;
      }}
      .drawer-header {{
        padding: 12px 16px;
      }}
      .drawer-body {{
        padding: 16px 14px;
        gap: 14px;
      }}
      .waterfall-stepper {{
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 8px !important;
      }}
      .grid-3 {{
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
      }}
      .grid-2 {{
        grid-template-columns: 1fr !important;
        gap: 8px !important;
      }}
    }}
    @media (max-width: 440px) {{
      .grid-3 {{
        grid-template-columns: 1fr 1fr !important;
      }}
      .waterfall-stepper {{
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 6px !important;
        padding: 8px !important;
      }}
      .step-badge {{
        width: 20px !important;
        height: 20px !important;
        font-size: 10px !important;
      }}
      .step-title {{
        font-size: 9px !important;
      }}
      .step-result {{
        font-size: 9px !important;
      }}
    }}

    /* Waterfall Stepper Component */
    .waterfall-stepper {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 6px;
      background: var(--bg-base);
      padding: 12px;
      border-radius: 8px;
      border: 1px solid var(--border-subtle);
    }}
    .waterfall-step {{
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 4px;
      position: relative;
    }}
    .step-badge {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 700;
    }}
    .step-title {{
      font-size: 10px;
      color: var(--text-dim);
      font-weight: 600;
    }}
    .step-result {{
      font-size: 10px;
      font-weight: 600;
    }}

    /* Dossier Cards */
    .dossier-section {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      min-width: 0;
      max-width: 100%;
    }}
    .section-title {{
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--accent);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}
    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }}
    .metric-box {{
      background: var(--bg-base);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 10px;
      min-width: 0;
    }}
    .metric-box .label {{
      font-size: 11px;
      color: var(--text-dim);
      font-weight: 500;
    }}
    .metric-box .value {{
      font-size: 15px;
      font-weight: 700;
      color: var(--text-main);
      margin-top: 2px;
      font-variant-numeric: tabular-nums;
    }}
    .prose {{
      font-size: 13px;
      color: #cbd5e1;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .methodology-container {{
      flex: 1;
      width: 100%;
      overflow-y: auto;
      overflow-x: hidden;
      -webkit-overflow-scrolling: touch;
      padding: 24px 20px;
    }}
    .methodology-inner {{
      max-width: 1000px;
      margin: 0 auto;
      width: 100%;
    }}
    .formula-code {{
      font-size: 12px;
      color: #cbd5e1;
      margin-top: 4px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: normal;
      overflow-wrap: anywhere;
      background: rgba(0, 0, 0, 0.25);
      padding: 8px;
      border-radius: 4px;
      line-height: 1.5;
    }}

    /* Empty state */
    .empty-state {{
      padding: 60px 20px;
      text-align: center;
      color: var(--text-dim);
      font-size: 14px;
    }}

    /* Custom Scrollbars */
    ::-webkit-scrollbar {{
      width: 6px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: var(--bg-base);
    }}
    ::-webkit-scrollbar-thumb {{
      background: var(--border);
      border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: var(--text-dim);
    }}
  </style>
</head>
<body>

  <!-- Top Global Header -->
  <header class="app-header">
    <div class="brand-title">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span>Quality & Moat Screener</span>
        <span class="badge-version">v{data['version']}</span>
      </div>
      <span class="badge-updated" id="price-update" title="Latest share price date in the screener dataset">Price update: {data.get('price_updated_at') or data.get('generated_at') or '—'}</span>
      <span class="brand-subtitle">Charlie Munger Reject Gates & Equity Bond Valuation</span>
    </div>
    <div class="kpi-bar">
      <div class="kpi-chip">
        <span class="kpi-label" title="Total number of screened companies across all active markets (US, EU, and CA).">Universe</span>
        <span class="kpi-value" id="kpi-universe">{data['summary']['total_companies']}</span>
      </div>
      <div class="kpi-chip">
        <span class="kpi-label" title="Companies passing all 6 Munger Reject Gates cleanly (Quality pass) with fewer than 3 Gate 6 numeric flags.">Prime Grade</span>
        <span class="kpi-value accent" id="kpi-qpass">{data['summary']['quality_pass']}</span>
      </div>
      <div class="kpi-chip">
        <span class="kpi-label" title="Quality Grade companies trading near their 0g price: Valued, Mkt Implied g &lt; 5.0% (ok or saturated_low), and organic Model g &ge; 5.0%.">Growth at ~0g</span>
        <span class="kpi-value accent" id="kpi-growth-0g">{data['summary'].get('growth_0g', 0)}</span>
      </div>
      <div class="kpi-chip">
        <span class="kpi-label" title="Median of (5Y IRR − own hurdle r) over valued Prime Grade stocks; r = 8.50% operating / 10.25% balance-sheet financials. Negative = expected return below the hurdle.">Median IRR vs hurdle</span>
        <span class="kpi-value green" id="kpi-median-irr">{f"{data['summary']['median_excess_irr']*100:+.1f}pp" if data['summary'].get('median_excess_irr') is not None else "—"}</span>
      </div>
    </div>
  </header>

  <!-- View Tabs -->
  <nav class="tab-bar">
    <button class="tab-btn active" data-tab="qpass" onclick="setTab('qpass')" title="Companies passing all 6 Munger Reject Gates cleanly.">
      <span class="tab-label-full">🛡️ Prime Grade</span>
      <span class="tab-label-short">🛡️ Prime</span>
      <span class="pill-count" id="count-qpass">0</span>
    </button>
    <button class="tab-btn" data-tab="growth_0g" onclick="setTab('growth_0g')" title="Quality Grade companies trading near their 0g price (Valued, Mkt Implied g &lt; 5.0%, organic Model g &ge; 5.0%).">
      <span class="tab-label-full">💎 Growth at ~0g</span>
      <span class="tab-label-short">💎 ~0g Growth</span>
      <span class="pill-count" id="count-growth-0g">0</span>
    </button>
    <button class="tab-btn" data-tab="moat_universe" onclick="setTab('moat_universe')" title="Structural franchise cohort passing Gate 1 (Understandable), Gate 2 (Essential Need), and Gate 3 (Moat &amp; Pricing Power).">
      <span class="tab-label-full">🏰 Quality Grade</span>
      <span class="tab-label-short">🏰 Quality</span>
      <span class="pill-count" id="count-moat-universe">0</span>
    </button>
    <button class="tab-btn" data-tab="all" onclick="setTab('all')" title="Every screened company across US, EU, and CA with full 6-gate waterfall status.">
      <span class="tab-label-full">🔍 Full Universe</span>
      <span class="tab-label-short">🔍 All</span>
      <span class="pill-count" id="count-all">0</span>
    </button>
    <button class="tab-btn" data-tab="methodology" onclick="setTab('methodology')" title="Reference documentation for the 6 Munger Reject Gates and the Explicit Mauboussin-Fade DCF model.">
      <span class="tab-label-full">📖 Framework</span>
      <span class="tab-label-short">📖 Framework</span>
    </button>
  </nav>

  <!-- Filter & Controls Toolbar -->
  <section class="controls-bar" id="controls-section">
    <div class="filters-left">
      <!-- Search Input -->
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="filter-search" class="search-input" placeholder="Search ticker, company, sector..." title="Filter companies by ticker symbol, company name, or sector." oninput="handleSearchInput()">
        <button id="search-clear" class="search-clear" onclick="clearSearch()" aria-label="Clear search" title="Clear search">&times;</button>
      </div>

      <!-- Market Universe Pills -->
      <div class="market-pills">
        <button class="market-btn active" data-market="all" onclick="setMarket('all')" title="Show companies from all markets (US, EU, and CA).">All</button>
        <button class="market-btn" data-market="us" onclick="setMarket('us')" title="Filter to US-listed companies.">🇺🇸 US</button>
        <button class="market-btn" data-market="eu" onclick="setMarket('eu')" title="Filter to European-listed companies.">🇪🇺 EU</button>
        <button class="market-btn" data-market="ca" onclick="setMarket('ca')" title="Filter to Canadian-listed companies.">🇨🇦 CA</button>
      </div>

      <!-- Sort Filter -->
      <select id="filter-sort" class="select-filter" title="Sort companies by valuation, growth, return on capital, moat runway, or alphabetically." onchange="applySortFromSelect(this.value)">
        <option value="irr_5y-desc">Sort: 5Y Exp IRR ↓</option>
        <option value="irr_5y-asc">Sort: 5Y Exp IRR ↑</option>
        <option value="vs_par-asc">Sort: Discount vs Fair Value ↑</option>
        <option value="vs_par-desc">Sort: Premium vs Fair Value ↓</option>
        <option value="vs_term-asc">Sort: vs Terminal Price (Floor) ↑</option>
        <option value="vs_term-desc">Sort: vs Terminal Price ↓</option>
        <option value="g_gap-desc">Sort: Growth Margin (g₀ - g_mkt) ↓</option>
        <option value="g_market-asc">Sort: Market-Implied g (at r) ↑</option>
        <option value="g_org_exp-desc">Sort: Model g (g₀) ↓</option>
        <option value="opcost_cagr-desc">Sort: 10Y WLS OpCost Growth ↓</option>
        <option value="sales_1y-asc">Sort: 1Y Growth (Slump) ↑</option>
        <option value="sales_1y-desc">Sort: 1Y Growth ↓</option>
        <option value="sales_cagr-desc">Sort: 10Y WLS Sales Growth ↓</option>
        <option value="buyback_yield-desc">Sort: Buyback Yield ↓</option>
        <option value="roic_exp-desc">Sort: RONIC₀ ↓</option>
        <option value="cur_mult-asc">Sort: Cur P/E ↑</option>
        <option value="cur_mult-desc">Sort: Cur P/E ↓</option>
        <option value="par_mult-desc">Sort: Fair P/E ↓</option>
        <option value="term_mult-desc">Sort: Terminal P/E ↓</option>
        <option value="price-asc">Sort: Share Price ↑</option>
        <option value="price-desc">Sort: Share Price ↓</option>
        <option value="g4_cap-desc">Sort: Our CAP ↓</option>
        <option value="cap_implied-asc">Sort: Market-Implied CAP ↑</option>
        <option value="cap_gap-desc">Sort: Runway Margin ↓</option>
        <option value="ticker-asc">Sort: Ticker A–Z</option>
        <option value="company-asc">Sort: Company A–Z</option>
        <option id="sort-custom-opt" style="display:none;"></option>
      </select>

      <!-- Sector Filter -->
      <select id="filter-sector" class="select-filter" title="Filter companies by industry sector." onchange="applyFilters()">
        <option value="all">All Sectors</option>
      </select>

      <!-- Moat Archetype Filter -->
      <select id="filter-moat" class="select-filter" title="Filter companies by primary Gate 3a economic moat archetype." onchange="applyFilters()">
        <option value="all">All Moats</option>
      </select>

      <!-- Failing Gate Filter (Visible in Growth at ~0g, Quality Grade & Full Universe tabs) -->
      <select id="filter-gate" class="select-filter" style="display:none;" title="Filter companies by 6-Gate waterfall outcome or first failing gate." onchange="applyFilters()">
        <option value="all">All Gate Statuses</option>
        <option value="quality_grade">Quality Grade (G1, G2, G3, &lt;3 G6 Flags)</option>
        <option value="Quality pass">Prime Grade Only</option>
        <option value="Gate 1">Rejected at Gate 1 (Understandability)</option>
        <option value="Gate 2">Rejected at Gate 2 (Essential Need)</option>
        <option value="Gate 3">Rejected at Gate 3 (Moat & Pricing)</option>
        <option value="Gate 4">Rejected at Gate 4 (Runway CAP &lt; 15Y)</option>
        <option value="Gate 5">Rejected at Gate 5 (Management)</option>
        <option value="Gate 6">Rejected at Gate 6 (Cash / Balance Sheet)</option>
      </select>

      <!-- Valuation Status Filter (Visible in Prime Grade, Quality Grade & Full Universe tabs) -->
      <select id="filter-val" class="select-filter" style="display:none;" title="Filter companies by quantitative valuation status (Valued, No value, No data, or Gate 6 review flags)." onchange="applyFilters()">
        <option value="all">All Valuations</option>
        <option value="Valued">Valued</option>
        <option value="No value">No value (Fair value ≤ 0)</option>
        <option value="No data">No data</option>
        <option value="g6flag">Gate 6 = Y but numeric ⚠ (review)</option>
      </select>
    </div>

    <!-- Controls Right: Filter Count, Density, View Toggle & Export Button -->
    <div class="filters-right">
      <span class="filter-count-pill" id="filter-count-pill" title="Number of companies matching current filters vs total in this tab."></span>
      <button class="btn-reset-filters" id="btn-reset-filters" onclick="resetAllFilters()" title="Reset search and filters">✕ Reset</button>
      <button class="btn-export" id="btn-col-density" onclick="toggleColumnDensity()" title="Switch between Essential columns and All 20+ columns" style="padding: 0 10px;">
        <span id="col-density-label">All Cols</span>
      </button>
      <div class="view-toggle">
        <button class="view-btn" id="view-cards-btn" onclick="setViewMode('cards')" title="Card View">
          <span>⊞</span> Cards
        </button>
        <button class="view-btn" id="view-table-btn" onclick="setViewMode('table')" title="Table View">
          <span>☰</span> Table
        </button>
      </div>

      <button class="btn-export" id="btn-export" onclick="exportCurrentView()" title="Download the currently filtered view as a CSV file.">
        <span>📥</span> Export
      </button>
    </div>
  </section>

  <!-- Mobile Horizontal Swipe Hint (outside scroll container so it stays centered) -->
  <div class="mobile-swipe-hint" id="mobile-swipe-hint">👉 Swipe horizontally to view all metrics • Tap any row to open dossier</div>

  <!-- Main Table View -->
  <main class="table-container" id="table-view">
    <table id="screener-table">
      <thead id="table-head"></thead>
      <tbody id="table-body"></tbody>
    </table>
  </main>

  <!-- Responsive Cards View -->
  <main class="cards-container" id="cards-view" style="display: none;">
    <div class="cards-grid" id="cards-grid"></div>
  </main>

  <!-- Shared Empty State -->
  <div id="empty-state" class="empty-state" style="display: none;">
    <div style="font-size: 28px; margin-bottom: 8px;">🔍</div>
    <div>No companies match the selected search and filter criteria.</div>
    <button class="btn-export" style="margin: 14px auto 0;" onclick="resetAllFilters()">✕ Reset All Filters</button>
  </div>

  <!-- Methodology Tab Content (Hidden by default) -->
  <main class="methodology-container" id="methodology-view" style="display:none;">
    <div class="methodology-inner">
    <div class="dossier-section" style="margin-bottom: 24px;">
      <h2 style="font-size: 16px; margin-bottom: 12px; color: var(--accent);">The 6 Munger Reject Gates (v{data['version']})</h2>
      <p style="color: var(--text-muted); margin-bottom: 16px;">
        "Tell me where I am going to die so that I never go there." Every qualitative step is a sequential REJECT gate: a company leaves the funnel at the first gate it fails. Companies clearing all 6 gates earn <strong style="color: var(--green);">Prime Grade</strong> and enter the Quantitative PAR valuation funnel.
      </p>
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <div class="metric-box">
          <strong style="color: var(--accent);">Gate 1: Simple to Understand</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Favours established, transparent business models with long verifiable track records. Rejects opaque structures, proprietary trading risks, and unproven models.</p>
        </div>
        <div class="metric-box">
          <strong style="color: var(--accent);">Gate 2: Essential Western Need & Entrenched Everyday Habits</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Essential survival necessities or entrenched everyday rituals ('likely to' spend) in Western rule-of-law jurisdictions. Rejects big-ticket deferrable cyclicals, pariah regimes, and predatory harm.</p>
        </div>
        <div class="metric-box">
          <strong style="color: var(--accent);">Gate 3: Strong Moat Profile &amp; Pricing Power &ge; Inflation</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Scores all 4 Moat Archetypes 0/1/2 &mdash; (1) <em>Toll booth &amp; switching costs</em>, (2) <em>Irreplaceable infrastructure &amp; intangibles</em> (incl. physical distribution networks, permits, licenses, proprietary data &amp; Lindy brands), (3) <em>Scale economies shared</em> (strictly Nick Sleep's customer-surplus model), and (4) <em>R&amp;D &amp; innovation leadership</em> &mdash; auto-deriving Primary Moat (<code>3a</code>) and deterministic <strong>Initial CAP</strong> (15Y/20Y/25Y/30Y, capped at 20Y without an elite score of 2), PLUS empirical proof: 5Y median GAAP ROIC &ge; 12%, incremental ROIIC &ge; 12%, and pricing power &ge; inflation (<code>3b</code>).</p>
        </div>
        <div class="metric-box">
          <strong style="color: var(--accent);">Gate 4: Low Disruption Risk &amp; Predictable Runway (CAP &ge; 15 Years)</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Deterministic Step 2 adjustment of Initial CAP across <strong>Porter's 5 Competitive Forces</strong> (New Entrants, Rivalry, Buyer Power, Supplier Power, Substitution &mdash; each scored 0/1/2) evaluated through the 5 Macrotrends and Mauboussin industry clock speed (presumptive Substitution &ge; 1 for fast-clock-speed tech/pharma unless structurally unbypassable). Any Force = 2 triggers the Fatal-Flaw Cap (Final CAP &le; 10Y, immediate REJECT); moderate pressures (Force = 1) deduct 0Y (0 ones), &minus;5Y (1&ndash;2 ones), &minus;10Y (3&ndash;4 ones), or &minus;15Y (5 ones) on 5-year steps [0, 5, 10, 15, 20, 25, 30].</p>
        </div>
        <div class="metric-box">
          <strong style="color: var(--accent);">Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Scored 0–2 across 5 vectors: skin in the game, rational capital allocation, customer centricity, plain talk, and low principal-agent friction.</p>
        </div>
        <div class="metric-box">
          <strong style="color: var(--accent);">Gate 6: Real Cash Conversion, Peak-to-Peak Compounding & Fortress Balance Sheet</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Triad: (1) Secular Peak-to-Peak Owner EPS compounding across cycles, (2) Real cash conversion (multi-year FCF &ge; 80% GAAP NI), (3) Peace-of-mind fortress balance sheet (Net Debt &le; 4y Owner Earnings, Interest Coverage &gt; 5x). Your qualitative answer decides; the numeric checks (3-year medians; net debt and interest cover n/a for balance-sheet financials) are shown as review flags in the "G6 Checks" column and the dossier, never as a reject.</p>
        </div>
        <div class="metric-box" style="border-color: rgba(56, 189, 248, 0.35); background: rgba(56, 189, 248, 0.06);">
          <strong style="color: var(--accent);">Dashboard Views &amp; Quality Tiers</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 6px; line-height: 1.55;">
            <strong>&#128737;&#65039; Prime Grade:</strong> Passes all 6 Munger Reject Gates (G1&ndash;G6) cleanly (&lt; 3 Gate 6 numeric flags).<br>
            <strong>&#128142; Growth at ~0g:</strong> Quality Grade companies (G1, G2, G3, &lt; 3 Gate 6 numeric flags) that are <code>Valued</code> and trading near their 0g price (<code>Mkt Implied g &lt; 5.0%</code> with <code>ok</code> or <code>saturated_low</code> flag, while organic <code>Model g &ge; 5.0%</code>).<br>
            <strong>&#127984; Quality Grade:</strong> Structural franchise cohort covering G1 (Understandable), G2 (Essential Need), G3 (Moat &amp; Pricing Power), and G6 Rule Check (&lt; 3 numeric flags).<br>
            <strong>&#128269; Full Universe:</strong> Every screened company across US, EU, and CA with full gate-waterfall status.
          </p>
        </div>
      </div>
    </div>

    <div class="dossier-section">
      <h2 style="font-size: 16px; margin-bottom: 12px; color: var(--accent);">Quantitative Valuation: Explicit Mauboussin-Fade DCF &amp; Slump-Cannibal Compounders (v{data['version']})</h2>
      <div class="metric-box" style="margin-bottom: 12px;">
        <strong style="color: var(--text-main);">1. The 3-Price Framework (Terminal Price · Intrinsic Fair Value · Current Share Price) at r = 8.50% (r<sub>fin</sub> = 10.25% for Balance-Sheet Financials):</strong>
        <p class="formula-code">
          Fair P/E = PV<sub>Stage 1</sub> + PV<sub>Stage 2</sub> &nbsp;|&nbsp; Fair Value = Fair P/E &times; Active EPS &nbsp;|&nbsp; Terminal P/E = (1 &minus; 3.0% / RONIC<sub>term</sub>) / (r &minus; 3.0%) &nbsp;|&nbsp; Terminal Price = Terminal P/E &times; Active EPS<br>
          <span style="font-size: 11px; color: var(--text-dim);">
            <b>Year-1 convention:</b> E<sub>1</sub> = the active (trailing, normalized) Owner EPS — conservative by one year of growth versus a forward E<sub>1</sub> = EPS &times; (1 + g₀).<br>
            <b>Stage 1 (Years t = 1..N, N = Gate 4 CAP):</b> g<sub>t</sub> fades linearly from g₀ to min(g₀, 3.0%) and RONIC<sub>t</sub> from RONIC₀ to min(RONIC₀, 20%, r + 0.5 &times; (RONIC₀ &minus; r)); FCF<sub>t</sub> = E<sub>t</sub>(1 - g<sub>t</sub>/RONIC<sub>t</sub>), E<sub>t+1</sub> = E<sub>t</sub>(1 + g<sub>t</sub>).<br>
            <b>Stage 2 &amp; Standalone Terminal Price:</b> TV<sub>N</sub> = E<sub>N+1</sub>(1 &minus; g<sub>tv</sub>/RONIC<sub>term</sub>) / (r &minus; g<sub>tv</sub>) with g<sub>tv</sub> = max(0, min(g₀, 3.0%)) &mdash; 3.0% historical inflation pass-through (or g₀ when g₀ &lt; 3.0%). Standalone <b>Terminal Price</b> values the business today at 3.0% perpetual inflation growth and "keeping the lights on" reinvestment (3.0% / RONIC<sub>term</sub>), topping out at <b>15.5x</b> Owner EPS for elite compounders (&sim;10.9x for financials). When RONIC = r, Fair P/E = Terminal P/E = 1/r for every g₀ and N.<br>
            <b>No value:</b> when growth is funded at a RONIC far below g the DCF value is &le; 0 &mdash; such stocks are labelled <code style="color: var(--accent);">No value</code> (no discount or IRR is shown). A &#9888; flags RONIC₀ &le; r (growth adds no value; review the capital base against the moat gates).<br>
            <b>Market-Implied Growth (g<sub>market</sub>):</b> root-safe DCF inversion (grid &minus;20%..+50% + bisection) at the company's r &nbsp;|&nbsp; Growth Margin = g₀ - g<sub>market</sub>, shown only for a unique root (saturated results are shown as &le; / &ge; without a margin).<br>
            <b>Balance-Sheet Financials &amp; HoldCos:</b> Insurance, Reinsurance, Banks, deposit-funded Brokers &amp; Multi-Sector Holdings use 5Y median ROE at r<sub>fin</sub> = 10.25%; Mark-to-Market HoldCos / Insurers (5Y FCF Conv or 2Y OCF/NI &lt; 0.25) are valued at 1.0x Book Value / Share. Construction &amp; Engineering and Highways use GAAP ROIC (incl. concession intangibles); a zero terminal value applies only to concessions explicitly listed as expiring.
          </span>
        </p>
      </div>
      <div class="metric-box" style="margin-bottom: 12px;">
        <strong style="color: var(--text-main);">2. 10Y WLS Structural Revenue Growth Ceiling (g₀) &amp; M&amp;A-Matched RONIC₀:</strong>
        <p class="formula-code">
          g₀ = clamp(Sales_WLS + min(0, Buyback_Yield), 0.0%, 18.0%) &nbsp;|&nbsp; g_exp = g₀ + max(0, Buyback_Yield)<br>
          1 / RONIC₀ = (1 − w) / Tangible ROIC + w / GAAP ROIC (capped at 50%), w = bought share of g₀ = min(1, M&amp;A spend &times; GAAP ROIC / g₀), M&amp;A spend = &Sigma; cash-funded &Delta;Goodwill&amp;Intangibles &divide; &Sigma; NOPAT over the 10Y g₀ window (stock-funded years with shares +3% skipped)<br>
          <span style="font-size: 11px; color: var(--text-dim);">
            10-year exponentially-weighted log-linear OLS (&tau; = 5y half-life) on Sales (with OpCost WLS, cycle Owner EPS CAGR net of buybacks, and 1Y Sales as fallbacks; Gate 5 already filters out poor management and cost bloat). Tangible ROIC adds back acquired-intangible amortisation (D&amp;A above capex), exactly as Owner EPS does; invested capital includes minority interests and short-term debt.
          </span>
        </p>
      </div>
      <div class="metric-box" style="margin-bottom: 12px;">
        <strong style="color: var(--text-main);">3. Active Earning Power (50/50 Mid-Cycle Reversion Standard):</strong>
        <p class="formula-code">
          Active EPS = min(Peak_OE_EPS, 0.5 * (Peak_OE_EPS + max(0, Cur_Owner_EPS))) | Peak_eps_est overrides<br>
          <span style="font-size: 11px; color: var(--text-dim);">When current earnings drop below peak, normalizes base earning power to mid-cycle to prevent cyclical bubble peaks from distorting Fair Value and 5Y IRR (guarded against unstripped one-off spikes and multi-class share-basis mismatches).</span>
        </p>
      </div>
      <div class="metric-box">
        <strong style="color: var(--text-main);">4. Textbook 5-Year Cash-Flow IRR with FCF Payout Conservation (Cannibal Slump Compounding):</strong>
        <p class="formula-code">
          P₀ = &Sigma;<sub>t=1..5</sub> [D₀(1 + g_irr)<sup>t</sup> / (1 + IRR)<sup>t</sup>] + [Fair_Value &times; (PE<sub>5</sub>/PE<sub>0</sub>) &times; (1 + g_irr)<sup>5</sup> / (1 + IRR)<sup>5</sup>] (PE<sub>5</sub> = Fair P/E rolled forward 5 years along the fade, remaining CAP N&minus;5) &nbsp;|&nbsp; g_irr = g<sub>org,5y</sub> + min(bb_pos, max(0, FCF_Payout/Cur_Mult - dy))<br>
          <span style="font-size: 11px; color: var(--text-dim);">Solves the exact 5-year cash-flow internal rate of return across growing annual dividends and Year-5 DCF Fair Value while bounding buyback accretion at current P/E so Dividends + Buybacks + Organic Reinvestment never exceed 100% of Owner Earnings.</span>
        </p>
      </div>
    </div>
    </div>
  </main>

  <!-- Slide-Out Dossier Drawer & Backdrop -->
  <div class="drawer-overlay" id="drawer-overlay" onclick="closeDrawer()"></div>
  <aside class="dossier-drawer" id="dossier-drawer">
    <div class="drawer-header">
      <div style="flex: 1; min-width: 0;">
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
          <span class="cell-ticker" id="dossier-ticker" style="font-size: 20px;"></span>
          <span class="badge" id="dossier-market-badge"></span>
          <span class="badge" id="dossier-val-badge"></span>
        </div>
        <div style="font-size: 15px; font-weight: 600; color: var(--text-main); margin-top: 4px; line-height: 1.3;" id="dossier-company"></div>
        <div style="font-size: 11px; color: var(--text-dim); margin-top: 2px; word-break: break-word;" id="dossier-meta"></div>
      </div>
      <button class="btn-close" onclick="closeDrawer()" aria-label="Close drawer">&times;</button>
    </div>

    <!-- Drawer Sub-Navigation Tabs -->
    <div class="drawer-nav">
      <button type="button" class="dossier-tab-btn active" id="tab-btn-dossier-overview" onclick="setDossierTab('overview')">
        <span>📋</span> Overview &amp; Dossier
      </button>
      <button type="button" class="dossier-tab-btn" id="tab-btn-dossier-valuation" onclick="setDossierTab('valuation')">
        <span>🧮</span> Valuation Engine &amp; Sandbox
      </button>
      <button type="button" class="dossier-tab-btn" id="tab-btn-dossier-dcf" onclick="setDossierTab('dcf')">
        <span>📊</span> Explicit DCF Table
      </button>
    </div>

    <div class="drawer-body" id="dossier-content">
      <!-- Tab Pane 1: Overview & Dossier -->
      <div id="pane-dossier-overview" class="dossier-tab-pane active">
        <!-- Waterfall Stepper -->
      <div class="dossier-section">
        <div class="section-title">6 Munger Reject Gates Waterfall</div>
        <div class="waterfall-stepper" id="dossier-stepper"></div>
        <div id="dossier-verdict" style="margin-top: 10px; font-size: 12px; font-weight: 600;"></div>
      </div>

      <!-- Qualitative Research & Moat Analysis -->
      <div class="dossier-section">
        <div class="section-title">Qualitative Investment Thesis & Moat Analysis</div>
        <div class="grid-2" style="margin-bottom: 12px;">
          <div class="metric-box">
            <div class="label" title="Primary economic moat archetype from Gate 3a (e.g., Toll booth, Scale economies, Infrastructure, R&amp;D super-thinkers).">Moat Archetype</div>
            <div class="value" style="font-size: 13px;" id="dossier-moat-type">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Gate 4 Competitive Advantage Period (CAP) in years over which growth g₀ and RONIC₀ fade toward terminal levels (15–30y for Prime Grade).">Moat Runway (CAP)</div>
            <div class="value" style="font-size: 13px;" id="dossier-cap">-</div>
          </div>
        </div>

        <div class="grid-2" id="dossier-g56-row" style="margin-bottom: 12px; display: none;">
          <div class="metric-box">
            <div class="label" title="Gate 5: Honest, able, customer-focused management and rational capital allocation (0 = Red Flag, 1 = Standard Pass, 2 = Elite Compounder).">Management &amp; Allocation (G5)</div>
            <div class="value" style="font-size: 13px;" id="dossier-g5-mgmt">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Gate 6: Real FCF conversion, peak-to-peak Owner EPS compounding, and peace-of-mind fortress balance sheet (Y / N).">Cash &amp; Fortress B/S (G6)</div>
            <div class="value" style="font-size: 13px;" id="dossier-g6-cash">-</div>
          </div>
        </div>

        <div id="dossier-cap-scorecard" class="metric-box" style="margin-bottom: 12px; display: none;">
          <div class="label" style="color: var(--accent);" title="Deterministic two-step CAP audit: Step 1 (4 Moat Archetype scores -> Initial CAP) adjusted by Step 2 (5 Porter Competitive Force risk scores -> Final CAP).">Two-Step CAP Audit (Gate 3 Moats &rarr; Gate 4 Forces)</div>
          <div id="dossier-cap-scorecard-body" style="margin-top: 6px;"></div>
        </div>

        <div id="dossier-moat-note-box" class="metric-box" style="margin-bottom: 12px; display: none;">
          <div class="label" style="color: var(--accent);" title="Qualitative assessment of the company's competitive advantage and pricing power relative to inflation (Gate 3).">Moat & Pricing Power Note (G3m)</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-moat-note"></div>
        </div>

        <div id="dossier-g4n-box" class="metric-box" style="margin-bottom: 12px; display: none;">
          <div class="label" style="color: var(--accent);" title="Gate 4 competitive forces & macrotrend adjustment note (4n).">Competitive Forces &amp; Runway Note (G4n)</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-g4n-note"></div>
        </div>

        <div id="dossier-note-box" class="metric-box" style="margin-bottom: 12px; display: none;">
          <div class="label" style="color: var(--accent);" title="Overall qualitative thesis and rationale from the 6-Gate review.">Gate Review Thesis / Rationale</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-note"></div>
        </div>

        <div id="dossier-evidence-box" class="metric-box" style="display: none;">
          <div class="label" style="color: var(--accent);" title="Gate 4 Inside View: deductive CAP adjustments for AI cognitive disruption, demographics, reshoring, energy limits, and structural inflation.">5-Macrotrend Evidence & Longevity Analysis</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-evidence"></div>
        </div>

        <div id="dossier-g2r-box" class="metric-box" style="display: none;">
          <div class="label" style="color: var(--red);" title="Reason the company failed Gate 2 (e.g., deferrable cyclical, non-essential product, or non-Western jurisdiction risk).">Gate 2 Non-Essential Reason</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-g2r"></div>
        </div>
      </div>

      <!-- Quantitative Valuation Profile -->
      <div class="dossier-section" id="dossier-quant-section">
        <div class="section-title">Explicit Mauboussin-Fade DCF Scorecard (<span id="dossier-rate-title">r</span>)</div>
        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label" title="Latest market share price in the stock's quote currency.">Current Share Price</div>
            <div class="value" id="dossier-price">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Intrinsic Fair Value per share = DCF Fair P/E × Active Owner EPS at hurdle rate r (8.50% operating / 10.25% balance-sheet financials).">DCF Fair Value</div>
            <div class="value" id="dossier-par-val">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Current share price premium (+) or discount (−) relative to DCF Fair Value: (Price / Fair Value) − 1.">Discount vs Fair Value</div>
            <div class="value" id="dossier-vs-par">-</div>
          </div>
        </div>

        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label" title="Standalone Terminal Price floor = Terminal P/E × Active Owner EPS, assuming 3.0% perpetual inflation growth and maintenance reinvestment.">Terminal Price (3% Inf. Floor)</div>
            <div class="value" id="dossier-term-val">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Current share price premium (+) or discount (−) relative to the standalone Terminal Price floor.">vs Terminal Price</div>
            <div class="value" id="dossier-vs-term">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Standalone Terminal P/E floor = (1 − 3.0% / RONIC_term) / (r − 3.0%), capped at ~15.5x for operating companies (~10.9x for financials).">Terminal P/E (Floor)</div>
            <div class="value" id="dossier-term-mult">-</div>
          </div>
        </div>

        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label" title="Current Trailing P/E (Share Price ÷ Active Owner EPS) / 1Y Model-Implied Forward P/E (Cur P/E ÷ (1 + Model g)).">Current P/E (T / F)</div>
            <div class="value" id="dossier-cur-mult">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Explicit Mauboussin-Fade DCF Fair P/E = PV(Stage 1 FCFs) + PV(Stage 2 Terminal Value) at the company's hurdle rate r.">DCF Fair P/E (<span id="dossier-rate-pe">r</span>)</div>
            <div class="value" id="dossier-par-mult">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="5-Year Expected IRR solving across growing annual dividends (with FCF payout conservation) and Year-5 rolled-forward DCF Fair Value.">5Y Expected IRR</div>
            <div class="value" id="dossier-irr">-</div>
          </div>
        </div>

        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label" title="Operating Return on Tangible Invested Capital (adds back acquired-intangible amortisation; invested capital excludes goodwill &amp; intangibles).">Operating ROIC (Tangible)</div>
            <div class="value" id="dossier-roic-op">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="GAAP Return on Invested Capital including goodwill and acquired intangibles (used to blend RONIC₀ for M&amp;A-driven growth).">GAAP ROIC (incl. Goodwill)</div>
            <div class="value" id="dossier-roic-gaap">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Multi-year Free Cash Flow conversion ratio (FCF ÷ GAAP Net Income).">FCF Conversion (÷ NI)</div>
            <div class="value" id="dossier-fcf-conv">-</div>
          </div>
        </div>

        <div class="metric-box" style="margin-bottom: 10px;">
          <div class="label" title="Numeric Gate 6 balance-sheet and cash-conversion checks (3-year medians). Informational review flags only — your qualitative Gate 6 answer decides.">Gate 6 Rule Check (review flags only — your Gate 6 answer decides: <b id="dossier-g6-answer">-</b>)</div>
          <div id="dossier-g6-checks" style="font-size: 12px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 4px 12px; margin-top: 4px;"></div>
        </div>

        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label" title="Organic Growth Ceiling g₀ = clamp(Sales WLS + min(0, Buyback Yield), 0%, 18%), plus positive buyback yield (g_exp) shown after the arrow.">Growth Ceiling (g₀ → +BB)</div>
            <div class="value" id="dossier-g-imp">-</div>
            <div class="subtext" id="dossier-scale-tier" style="font-size: 10px; color: var(--text-dim); margin-top: 2px;"></div>
          </div>
          <div class="metric-box">
            <div class="label" title="Market-implied initial growth rate g₀ that equates the Explicit DCF Fair Value to the current share price at hurdle rate r.">Market-Implied g (<span id="dossier-rate-g">r</span>)</div>
            <div class="value" id="dossier-g-market">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Growth Margin = g₀ − g_market. Positive means our structural growth ceiling exceeds what the market currently prices in.">Growth Margin (g₀ - g_mkt)</div>
            <div class="value" id="dossier-g-margin">-</div>
          </div>
        </div>

        <div class="grid-3">
          <div class="metric-box">
            <div class="label" title="Assigned Competitive Advantage Period (CAP) in years from Gate 4.">Our CAP (Gate 4)</div>
            <div class="value" id="dossier-cap-our">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Market-implied Competitive Advantage Period (years) needed for the DCF to justify the current share price given g₀ and RONIC₀.">Market-Implied CAP</div>
            <div class="value" id="dossier-cap-implied">-</div>
          </div>
          <div class="metric-box">
            <div class="label" title="Runway Margin = Our CAP − Market-Implied CAP. Positive means our moat runway exceeds what the market prices in.">Runway Margin</div>
            <div class="value" id="dossier-cap-margin">-</div>
          </div>
        </div>

        <div id="dossier-fin-note-box" class="metric-box" style="margin-top: 10px; display: none;">
          <div class="label" style="color: var(--text-dim);" title="Data source notes, accounting adjustments, and any active manual financial overrides.">Financial Notes & Overrides</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-fin-note"></div>
        </div>
      </div>
      </div> <!-- End #pane-dossier-overview -->

      <!-- Tab Pane 2: Valuation Engine & Sandbox -->
      <div id="pane-dossier-valuation" class="dossier-tab-pane">
        <!-- Part 1: Audit Breakdown -->
        <div class="dossier-section">
          <div class="section-title" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <span>Valuation Input Audit &amp; Credibility Breakdown</span>
            <span class="binding-badge" id="audit-binding-badge">Binding Rule</span>
          </div>

          <!-- 1. OUR CAP Audit Card -->
          <div class="audit-card">
            <div class="audit-card-header">
              <span class="audit-card-title"><span>🛡️</span> 1. OUR CAP (Moat Runway) &amp; Discount Rate</span>
              <span class="cell-ticker" id="audit-cap-summary" style="font-size: 13px;">-</span>
            </div>
            <div class="audit-grid">
              <div class="audit-stat">
                <span class="lbl" title="Gate 4 Competitive Advantage Period (CAP) in years over which g₀ and RONIC₀ fade toward terminal levels.">Assigned Runway (G4)</span>
                <span class="val" id="audit-cap-years">-</span>
                <span class="sub" id="audit-cap-tier">-</span>
              </div>
              <div class="audit-stat">
                <span class="lbl" title="Hurdle discount rate r applied in the DCF: 8.50% for operating companies, 10.25% for balance-sheet financials.">Discount Rate r</span>
                <span class="val" id="audit-cap-rate">-</span>
                <span class="sub" id="audit-cap-rate-sub">-</span>
              </div>
              <div class="audit-stat">
                <span class="lbl" title="Years of competitive advantage required for the DCF to match the current share price given g₀ and RONIC₀.">Market-Implied CAP</span>
                <span class="val" id="audit-cap-market">-</span>
                <span class="sub" id="audit-cap-gap">-</span>
              </div>
            </div>
            <div class="filter-step-box">
              <div style="display: flex; justify-content: space-between; font-size: 11px; flex-wrap: wrap; gap: 6px;">
                <span style="color: var(--text-dim);" title="Primary economic moat archetype from Gate 3a.">Moat Archetype (G3a): <b style="color: var(--text-main);" id="audit-moat-arch">-</b></span>
                <span style="color: var(--text-dim);" title="Pricing power score from Gate 3b (ability to raise prices ≥ inflation without losing volume).">Pricing Power (G3b): <b style="color: var(--text-main);" id="audit-moat-pricing">-</b></span>
              </div>
              <div id="audit-cap-derivation" style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(148, 163, 184, 0.14);"></div>
            </div>
          </div>

          <!-- 2. Growth Ceiling (g₀) & Per-Share Ceiling (g_exp) Card -->
          <div class="audit-card">
            <div class="audit-card-header">
              <span class="audit-card-title"><span>📈</span> 2. Organic Growth Ceiling (g₀), Buybacks &amp; Marginal RONIC</span>
              <span class="val" style="color: var(--accent); font-size: 14px;" id="audit-gexp-summary">-</span>
            </div>

            <!-- Anchor 1: Near-Term 1Y Momentum / Slump Check -->
            <div class="filter-step-box" id="box-filter-supply">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 11px; color: var(--text-main);" title="Trailing 1-year revenue growth for slump context; never lowers the structural growth ceiling g₀.">Near-Term 1Y Growth vs. Slump Check</strong>
                <span class="val" style="font-size: 12px;" id="audit-sales1y-val">-</span>
              </div>
              <div style="font-size: 11px; color: var(--text-dim); display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px;">
                <span title="Trailing 1-year growth in operating costs (COGS + OpEx).">1Y OpCost Growth: <b id="audit-opcost1y-val" style="color: var(--text-muted);">-</b></span>
                <span title="Net annual share buyback yield (positive = share count reduction; negative = dilution, which reduces g₀).">Buybacks / Dilution: <b id="audit-bb-val" style="color: var(--text-muted);">-</b></span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;">Reference only: a 1Y slump never lowers the structural growth ceiling.</div>
            </div>

            <!-- Anchor 2: 10Y WLS Structural Revenue Growth -->
            <div class="filter-step-box" id="box-filter-demand">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 11px; color: var(--text-main);" title="10-year exponentially-weighted log-linear OLS revenue growth (τ = 5y half-life), primary anchor for g₀.">10Y WLS Structural Revenue Growth (Sales WLS CAGR)</strong>
                <span class="val" style="font-size: 12px;" id="audit-gdemand-val">-</span>
              </div>
              <div style="font-size: 11px; color: var(--text-dim); display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px;">
                <span title="Exponentially-weighted log-linear OLS revenue CAGR over available history (up to 10Y).">Sales WLS (<span id="audit-salesyrs-val">10Y</span>): <b id="audit-salescagr-val" style="color: var(--accent);">-</b></span>
                <span title="10-year WLS growth rate of COGS + OpEx (fallback anchor when sales history is unavailable).">OpCost WLS (COGS+OpEx): <b id="audit-opcostcagr-val" style="color: var(--text-muted);">-</b></span>
                <span title="Cycle Owner Earnings per-share CAGR net of buybacks (reference / fallback growth anchor).">Cycle OE EPS CAGR: <b id="audit-oecagr-val" style="color: var(--text-muted);">-</b></span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;">Weighted least-squares log-growth over up to 10Y (&tau;=5y half-life); Gate 5 filters out management cost bloat.</div>
            </div>

            <!-- Anchor 3: Marginal RONIC -->
            <div class="filter-step-box" id="box-filter-fade">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 11px; color: var(--text-main);" title="Harmonic blend of Tangible ROIC and GAAP ROIC weighted by cash-funded M&amp;A share of growth, capped at 50%.">Marginal RONIC₀ (M&amp;A-Matched, capped)</strong>
                <span class="val" style="font-size: 12px;" id="audit-roic-val">-</span>
              </div>
              <div style="font-size: 11px; color: var(--text-dim); display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px;">
                <span title="Operating Return on Tangible Invested Capital (excludes goodwill &amp; acquired intangibles).">Tangible ROIC: <b id="audit-roictang-val" style="color: var(--text-muted);">-</b></span>
                <span title="GAAP Return on Invested Capital (includes goodwill &amp; acquired intangibles).">GAAP ROIC: <b id="audit-roicgaap-val" style="color: var(--text-muted);">-</b></span>
                <span title="Cash-funded M&amp;A spend (ΔGoodwill &amp; Intangibles ÷ ΣNOPAT over the 10Y window, skipping stock-funded years).">M&amp;A Spend: <b id="audit-mashare-val" style="color: var(--text-muted);">-</b></span>
                <span title="Share of Owner Earnings retained over the past 5 years (1 − 5Y Dividend Payout Ratio).">5Y Retention: <b id="audit-retention-val" style="color: var(--text-muted);">-</b></span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;" id="audit-roic-note">RONIC fades linearly across CAP from RONIC₀ to min(RONIC₀, 20%, r + 0.5·(RONIC₀ − r)).</div>
            </div>

            <!-- Step B: Growth Ceiling (g₀) & Per-Share Ceiling (g_exp) -->
            <div class="filter-step-box" id="box-filter-gravity">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 11px; color: var(--text-main);" title="Organic Growth Ceiling g₀ (used in the DCF) and Per-Share Ceiling g_exp = g₀ + positive buyback yield.">Organic Growth Ceiling (g₀) &amp; Per-Share Ceiling (g_exp)</strong>
                <span class="val" style="font-size: 12px;" id="audit-fade-val">-</span>
              </div>
              <div style="font-size: 11px; color: var(--text-dim); display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px;">
                <span title="Per-share expected growth rate including positive net buybacks: g₀ + max(0, Buyback Yield).">Per-Share Ceiling (g_exp): <b id="audit-glog-val" style="color: var(--text-muted);">-</b></span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;" id="audit-gformula">Formula: g₀ = clamp(Sales WLS growth + min(0, BB), 0%, g_max) fades linearly to min(g₀, g_term) over CAP.</div>
            </div>
          </div>

          <!-- 3. Explicit Mauboussin-Fade DCF Multiple Audit Card -->
          <div class="audit-card">
            <div class="audit-card-header">
              <span class="audit-card-title"><span>⚖️</span> 3. Explicit Mauboussin-Fade DCF Fair P/E (<span id="audit-dcf-rate">r</span>)</span>
              <span class="val" style="color: var(--accent); font-size: 14px;" id="audit-parmult-summary">-</span>
            </div>
            <div class="audit-grid">
              <div class="audit-stat">
                <span class="lbl" title="Present value of Years 1..N Free Cash Flows during the Competitive Advantage Period, per unit of Year-1 Owner EPS.">Stage 1 CAP PV</span>
                <span class="val" id="audit-tgrowth-val">-</span>
                <span class="sub" id="audit-tgrowth-sub">Years 1..N FCF</span>
              </div>
              <div class="audit-stat">
                <span class="lbl" title="Present value at t=0 of the Year-N Value Driver Terminal Value TV_N, per unit of Year-1 Owner EPS.">Stage 2 Terminal PV</span>
                <span class="val" id="audit-troic-val">-</span>
                <span class="sub">Post-CAP Value Driver TV</span>
              </div>
              <div class="audit-stat">
                <span class="lbl" title="Total Explicit DCF Fair P/E = Stage 1 CAP PV + Stage 2 Terminal PV.">Explicit DCF Fair P/E</span>
                <span class="val" id="audit-rawpar-val">-</span>
                <span class="sub">Stage 1 + Stage 2</span>
              </div>
            </div>
            <div class="filter-step-box">
              <div style="display: flex; justify-content: space-between; font-size: 11px; flex-wrap: wrap; gap: 6px;">
                <span title="Standalone Terminal P/E and Terminal Price assuming 3.0% perpetual inflation growth and maintenance reinvestment.">Terminal Floor (3% Inf.): <b id="audit-termmult-val" style="color: var(--accent);">-</b> (<span id="audit-termval-val">-</span>)</span>
                <span title="Year-1 Free Cash Flow payout ratio = 1 − g₀ / RONIC₀ (share of Owner Earnings not needed to fund g₀ growth).">Year-1 FCF Payout (1 - g₀/RONIC₀): <b id="audit-reinv-val" style="color: var(--text-main);">-</b></span>
                <span title="Trailing 5-year low-to-high share price range (historical market reference only).">5Y Low–High Range (reference): <b id="audit-mh-val" style="color: var(--text-main);">-</b></span>
                <span title="Active Owner EPS used as Year-1 E₁ in the DCF (50/50 mid-cycle reversion when below peak, or manual peak_eps_est override).">Normalized Peak EPS (= Year-1 E₁): <b id="audit-peakeps-val" style="color: var(--text-main);">-</b></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Part 2: Interactive Sensitivity Sandbox -->
        <div class="dossier-section">
          <div class="sandbox-panel">
            <div class="sandbox-header">
              <div>
                <div class="section-title" style="margin-bottom: 2px;">Interactive "What-If" Sensitivity Sandbox</div>
                <div style="font-size: 11px; color: var(--text-dim);">Tweak variables below to dynamically recalculate Explicit DCF Fair P/E, Fair Value, and 5Y IRR in real-time.</div>
              </div>
              <div style="display: flex; gap: 8px;">
                <button type="button" class="btn-export" style="padding: 4px 10px; font-size: 11px;" title="Restore all sandbox sliders and overrides to the company's baseline values." onclick="resetSandboxValuation()">↺ Reset</button>
              </div>
            </div>

            <div class="sandbox-grid">
              <!-- Control 1: Moat Runway (CAP) -->
              <div class="sandbox-group">
                <label title="Adjust the Gate 4 Competitive Advantage Period (CAP) in years over which g₀ and RONIC₀ fade.">Moat Runway (Gate 4 CAP): <span class="sb-val" id="sb-val-cap">20y</span></label>
                <div class="cap-btn-group">
                  <button type="button" class="cap-pill-btn" data-cap="5" onclick="setSandboxCap(5)">5y</button>
                  <button type="button" class="cap-pill-btn" data-cap="10" onclick="setSandboxCap(10)">10y</button>
                  <button type="button" class="cap-pill-btn" data-cap="15" onclick="setSandboxCap(15)">15y</button>
                  <button type="button" class="cap-pill-btn" data-cap="20" onclick="setSandboxCap(20)">20y</button>
                  <button type="button" class="cap-pill-btn" data-cap="25" onclick="setSandboxCap(25)">25y</button>
                  <button type="button" class="cap-pill-btn" data-cap="30" onclick="setSandboxCap(30)">30y</button>
                </div>
              </div>

              <!-- Control 2: 10Y WLS Structural Growth Anchor -->
              <div class="sandbox-group">
                <label title="Adjust the 10Y Sales WLS growth anchor (recomputes g₀ after negative buybacks and 0%–18% clamp).">Sales WLS Growth (shifts g₀ inputs): <span class="sb-val" id="sb-val-salescagr">8.0%</span></label>
                <input type="range" class="sandbox-slider" id="sb-slider-salescagr" min="-5" max="30" step="0.5" value="8" oninput="onSandboxSliderChange('salescagr', this.value, '%')">
              </div>

              <!-- Control 3: Marginal RONIC -->
              <div class="sandbox-group">
                <label title="Adjust Marginal RONIC₀ (or ROE for balance-sheet financials), controlling capital efficiency and reinvestment need."><span id="sb-label-roic-text">Marginal RONIC</span>: <span class="sb-val" id="sb-val-roic">20.0%</span></label>
                <input type="range" class="sandbox-slider" id="sb-slider-roic" min="5" max="150" step="0.5" value="20" oninput="onSandboxSliderChange('roic', this.value, '%')">
              </div>

              <!-- Control 4: Peak EPS Normalization -->
              <div class="sandbox-group">
                <label title="Override the Active Owner EPS (E₁) used to scale DCF Fair P/E and Terminal P/E into per-share prices.">Normalized Peak EPS: <span class="sb-val" id="sb-val-peakeps">-</span></label>
                <input type="number" class="sandbox-num-input" id="sb-input-peakeps" step="0.05" oninput="onSandboxPeakChange()">
              </div>

              <!-- Control 5: Direct Expected Growth Override -->
              <div class="sandbox-group">
                <label title="Directly override the initial organic growth ceiling g₀ (%) in the DCF, bypassing the Sales WLS + buyback formula.">Direct Growth Ceiling Override: <span class="sb-val" id="sb-val-gest">None</span></label>
                <div class="sandbox-input-row">
                  <input type="number" class="sandbox-num-input" id="sb-input-gest" placeholder="e.g. 7.5 (overrides g₀)" step="0.1" oninput="onSandboxGestChange()">
                  <button type="button" class="btn-export" style="padding: 4px 8px; font-size: 11px;" title="Clear the direct growth ceiling override." onclick="clearSandboxGest()">Clear</button>
                </div>
              </div>
            </div>

            <!-- Scenario Impact Delta Table -->
            <div class="delta-table-card" style="margin-top: 6px;">
              <table class="delta-table">
                <thead>
                  <tr>
                    <th>Valuation Metric</th>
                    <th>Recorded Baseline</th>
                    <th>Tweaked Scenario</th>
                    <th>Variance (&Delta;)</th>
                  </tr>
                </thead>
                <tbody id="sb-delta-tbody">
                  <!-- Populated by JS -->
                </tbody>
              </table>
            </div>

            <div id="sb-status-box" style="padding: 10px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; display: flex; justify-content: space-between; align-items: center; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35);">
              <span id="sb-status-verdict">Scenario: price vs fair value</span>
              <span id="sb-irr-badge" class="badge badge-slate" style="font-size: 12px;">5Y IRR: -</span>
            </div>
          </div>
        </div>
      </div> <!-- End #pane-dossier-valuation -->

      <!-- Tab Pane 3: Explicit Year-by-Year Mauboussin-Fade DCF Table -->
      <div id="pane-dossier-dcf" class="dossier-tab-pane">
        <div class="dossier-section">
          <div class="section-title" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <span>Explicit Year-by-Year Mauboussin-Fade DCF Schedule</span>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="binding-badge" id="dcf-tab-mode-badge">Baseline DCF</span>
              <button type="button" class="btn-export" id="dcf-tab-reset-btn" style="padding: 3px 8px; font-size: 10.5px; display: none;" onclick="resetSandboxValuation()">↺ Reset Sandbox</button>
            </div>
          </div>

          <!-- Summary Strip -->
          <div class="audit-grid" style="margin-bottom: 12px;">
            <div class="audit-stat">
              <span class="lbl" title="Active Owner EPS used as Year-1 E₁ in the explicit DCF schedule.">Base Peak EPS (E₀)</span>
              <span class="val" id="dcf-sum-e0">-</span>
              <span class="sub" id="dcf-sum-price">Cur Price: -</span>
            </div>
            <div class="audit-stat">
              <span class="lbl" title="Linear fade of annual Owner EPS growth from initial g₀ to terminal g_term (min(g₀, 3.0%)) over N CAP years.">Growth Fade (g₀ → g_term)</span>
              <span class="val" id="dcf-sum-gfade">-</span>
              <span class="sub" id="dcf-sum-cap">Over N = - CAP Yrs</span>
            </div>
            <div class="audit-stat">
              <span class="lbl" title="Linear fade of incremental return on capital from RONIC₀ toward terminal RONIC_term, discounted at hurdle rate r.">ROIC Fade &amp; Discount (r)</span>
              <span class="val" id="dcf-sum-rfade">-</span>
              <span class="sub" id="dcf-sum-disc">Discount Rate r</span>
            </div>
            <div class="audit-stat">
              <span class="lbl" title="DCF Fair Value per share = PV of Stage 1 (Years 1..N) Free Cash Flows + PV of Stage 2 Terminal Value.">Stage 1 PV + Terminal PV</span>
              <span class="val" style="color: var(--accent);" id="dcf-sum-fv">-</span>
              <span class="sub" id="dcf-sum-split">Stage 1: - | TV: -</span>
            </div>
          </div>

          <div id="dcf-special-note" class="metric-box" style="margin-bottom: 12px; display: none; border-color: var(--amber-border); background: rgba(245, 158, 11, 0.08); font-size: 11.5px; color: var(--text-main);"></div>

          <!-- Year-by-Year DCF Table -->
          <div class="dcf-table-wrap">
            <table class="dcf-schedule-table" id="dcf-schedule-table">
              <thead>
                <tr>
                  <th title="Explicit forecast year t = 1..N (CAP) followed by Stage 2 Terminal Value at Year N.">Year / Stage</th>
                  <th title="Annual Owner EPS growth rate g_t fading linearly from g₀ to g_term.">Growth (g<sub>t</sub>)</th>
                  <th title="Incremental Return on New Invested Capital (RONIC_t) and implied reinvestment rate (g_t / RONIC_t).">ROIC<sub>t</sub> (Reinv)</th>
                  <th title="Projected Owner Earnings per share in year t: E(1) = Active EPS, E(t+1) = E(t) × (1 + g_t).">Owner EPS (E<sub>t</sub>)</th>
                  <th title="Projected Free Cash Flow per share in year t: FCF_t = E_t × (1 − g_t / RONIC_t).">Cash Flow (FCF<sub>t</sub>)</th>
                  <th title="Discount factor (1 + r)^t at the company's hurdle rate r.">Disc. Rate (DF)</th>
                  <th title="Present value of Year t cash flow (or Terminal Value): FCF_t / (1 + r)^t.">PV of Cash Flow</th>
                  <th title="Running cumulative sum of discounted cash flows through year t.">Cumulative PV</th>
                </tr>
              </thead>
              <tbody id="dcf-schedule-tbody">
                <!-- Populated dynamically by renderDcfScheduleTable() -->
              </tbody>
            </table>
          </div>
        </div>
      </div> <!-- End #pane-dossier-dcf -->
    </div>
  </aside>

  <!-- Embedded JSON Dataset -->
  <script id="screener-raw-data" type="application/json">
{json_payload}
  </script>

  <!-- Client-Side Reactive Controller -->
  <script>
    const SCREENER_DATA = JSON.parse(document.getElementById('screener-raw-data').textContent);
    let currentTab = 'qpass';
    let currentMarket = 'all';
    let sortColumn = 'g_org_exp';
    let sortAsc = false;
    let selectedCompanyId = null;
    let viewMode = (window.innerWidth <= 768) ? 'cards' : 'table';
    let userSetViewMode = false;
    let compactColumns = true;

    const TAB_DEFAULT_SORTS = {{
      qpass: {{ col: 'g_org_exp', asc: false }},
      growth_0g: {{ col: 'g_org_exp', asc: false }},
      moat_universe: {{ col: 'g_org_exp', asc: false }},
      all: {{ col: 'g_org_exp', asc: false }}
    }};
    let tabSortState = {{}};

    const ALL_COLS = {{
      ticker: {{ key: 'ticker', label: 'Ticker' }},
      company: {{ key: 'company', label: 'Company' }},
      country: {{ key: 'country', label: 'Country' }},
      result: {{ key: 'result', label: 'Gate Status' }},
      rejected_at: {{ key: 'rejected_at', label: 'Failing Gate' }},
      price: {{ key: 'price', label: 'Price', num: true }},
      sales_1y: {{ key: 'sales_1y', label: '1Y Growth', num: true }},
      sales_cagr: {{ key: 'sales_cagr', label: '10Y Sales WLS', num: true }},
      sales_1_3_5y: {{ key: 'sales_1_3_5y', label: '1y/3y/5y g', num: true }},
      g_org_exp: {{ key: 'g_org_exp', label: 'Model g', num: true }},
      buyback_yield: {{ key: 'buyback_yield', label: 'Buyback', num: true }},
      g_market: {{ key: 'g_market', label: 'Mkt Implied g', num: true }},
      g_gap: {{ key: 'g_gap', label: 'g Margin', num: true }},
      par_val: {{ key: 'par_val', label: 'Fair Value', num: true }},
      vs_par: {{ key: 'vs_par', label: 'vs Fair Value', num: true }},
      term_val: {{ key: 'term_val', label: '0 g price', num: true }},
      vs_term: {{ key: 'vs_term', label: 'VS 0 G', num: true }},
      cur_mult: {{ key: 'cur_mult', label: 'Cur P/E (T / F)', num: true }},
      par_mult: {{ key: 'par_mult', label: 'Fair P/E', num: true }},
      term_mult: {{ key: 'term_mult', label: 'Term P/E', num: true }},
      irr_5y: {{ key: 'irr_5y', label: '5Y Exp IRR', num: true }},
      roic_used: {{ key: 'roic_exp', label: 'RONIC₀', num: true }},
      g4_cap: {{ key: 'g4_cap', label: 'Our CAP', num: true }},
      g5_mgmt: {{ key: 'g5_mgmt', label: 'G5 Mgmt', num: true }},
      g6_cash: {{ key: 'g6_cash', label: 'G6 B/S' }},
      cap_implied: {{ key: 'cap_implied', label: 'Mkt CAP', num: true }},
      cap_gap: {{ key: 'cap_gap', label: 'CAP Gap', num: true }},
      g3a_moat_archetype: {{ key: 'g3a_moat_archetype', label: 'Moat Archetype' }},
      fcf_conv: {{ key: 'fcf_conv', label: 'FCF Conv', num: true }},
      g6_flags: {{ key: 'g6_flags', label: 'G6 Checks', num: true }},
      val_status: {{ key: 'val_status', label: 'Valuation' }},
      sector: {{ key: 'sector', label: 'Sector' }}
    }};

    const COL_TIPS = {{
      ticker: "Primary exchange ticker symbol. Click any row to open the full company dossier.",
      company: "Company name.",
      country: "Primary listing or domicile country.",
      result: "Overall 6-Gate verdict: Quality pass (Prime Grade), Rejected, or To review.",
      rejected_at: "First Munger Reject Gate failed.",
      price: "Latest market share price in the stock's quote currency.",
      sales_1y: "Trailing 1-year revenue growth (slump check only; does not lower structural growth ceiling g₀).",
      sales_cagr: "10-year exponentially-weighted log-linear OLS revenue growth rate (τ = 5y half-life).",
      sales_1_3_5y: "Trailing 1-year / 3-year / 5-year revenue CAGR.",
      g_org_exp: "Organic Growth Ceiling g₀ = clamp(Sales WLS + min(0, Buyback Yield), 0%, 18%), fading linearly to min(g₀, 3%) over CAP.",
      buyback_yield: "Net annual share buyback yield (positive = share count reduction; negative = net dilution, which reduces g₀).",
      g_market: "Market-implied initial growth rate g₀ that equates DCF Fair Value to the current share price at hurdle rate r.",
      g_gap: "Growth Margin = g₀ − Mkt Implied g (positive = our growth ceiling exceeds what the market prices in).",
      par_val: "Intrinsic DCF Fair Value per share = Fair P/E × Active Owner EPS at hurdle rate r (8.50% operating / 10.25% financials).",
      vs_par: "Current share price premium (+) or discount (−) relative to DCF Fair Value.",
      term_val: "Standalone Terminal Price floor = Terminal P/E × Active Owner EPS, assuming 3.0% perpetual inflation growth.",
      vs_term: "Current share price premium (+) or discount (−) relative to the standalone Terminal Price floor.",
      cur_mult: "Current Trailing P/E (Share Price ÷ Active Owner EPS) / 1Y Model-Implied Forward P/E (Cur P/E ÷ (1 + Model g)).",
      par_mult: "Explicit Mauboussin-Fade DCF Fair P/E = PV(Stage 1 FCFs) + PV(Stage 2 Terminal Value) at hurdle rate r.",
      term_mult: "Standalone Terminal P/E floor = (1 − 3.0% / RONIC_term) / (r − 3.0%), capped at ~15.5x operating / ~10.9x financials.",
      irr_5y: "5-Year Expected IRR across growing annual dividends (with FCF payout conservation) and Year-5 rolled-forward DCF Fair Value.",
      roic_exp: "Marginal RONIC₀ used by the DCF (Tangible ROIC blended with GAAP ROIC by cash-funded M&A share, capped at 50%; or 5Y median ROE for financials).",
      g4_cap: "Gate 4 Competitive Advantage Period (CAP) in years over which g₀ and RONIC₀ fade (15–30y for Prime Grade).",
      g5_mgmt: "Gate 5 Management & Capital Allocation score (0 = Red Flag, 1 = Standard Pass, 2 = Elite Compounder).",
      g6_cash: "Gate 6 Real Cash Conversion, Peak-to-Peak EPS & Fortress Balance Sheet verdict (Y / N).",
      cap_implied: "Market-implied Competitive Advantage Period (years) needed for the DCF to match the current share price given g₀ and RONIC₀.",
      cap_gap: "Runway Margin = Our CAP − Market-Implied CAP (positive = our moat runway exceeds what the market prices in).",
      g3a_moat_archetype: "Primary economic moat archetype assigned at Gate 3a.",
      fcf_conv: "Multi-year Free Cash Flow conversion ratio (FCF ÷ GAAP Net Income).",
      g6_flags: "Gate 6 numeric review flags (3Y medians): Net debt ÷ owner earnings, Interest cover, Cash conversion, Peak-to-peak EPS.",
      val_status: "Quantitative valuation status: Valued, No value (DCF ≤ 0), or No data.",
      sector: "Industry sector classification."
    }};

    // Initialize Dropdowns & Counts
    function init() {{
      const sectors = new Set();
      const moats = new Set();
      SCREENER_DATA.companies.forEach(c => {{
        if (c.sector) sectors.add(c.sector);
        if (c.g3a_moat_archetype) moats.add(c.g3a_moat_archetype);
      }});

      const sectorSelect = document.getElementById('filter-sector');
      Array.from(sectors).sort().forEach(s => {{
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s;
        sectorSelect.appendChild(opt);
      }});

      const moatSelect = document.getElementById('filter-moat');
      Array.from(moats).sort().forEach(m => {{
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        moatSelect.appendChild(opt);
      }});

      updateTabCounts();
      document.getElementById('view-table-btn').classList.toggle('active', viewMode === 'table');
      document.getElementById('view-cards-btn').classList.toggle('active', viewMode === 'cards');
      updateDensityButton();
      setTab('qpass');

      // Keyboard Esc to close drawer
      window.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') closeDrawer();
      }});

      // Adapt viewMode on resize unless user manually chose one
      window.addEventListener('resize', () => {{
        if (userSetViewMode) return;
        const nextMode = (window.innerWidth <= 768) ? 'cards' : 'table';
        if (nextMode !== viewMode) {{
          viewMode = nextMode;
          document.getElementById('view-table-btn').classList.toggle('active', viewMode === 'table');
          document.getElementById('view-cards-btn').classList.toggle('active', viewMode === 'cards');
          renderCurrentView();
        }}
      }});
    }}

    function passesG123a(c) {{
      if (c.passes_g123a !== undefined) return Boolean(c.passes_g123a);
      const st = c.gate_status || {{}};
      return st['1'] === 'pass' && st['2'] === 'pass' && Boolean(c.g3a_moat_archetype && c.g3a_moat_archetype !== 'None');
    }}

    function passesPrimeGrade(c) {{
      if (c.passes_prime_grade !== undefined) return Boolean(c.passes_prime_grade);
      return c.result === 'Quality pass' && (c.g6_flags || 0) < 3;
    }}

    function passesQualityGrade(c) {{
      if (c.passes_quality_grade !== undefined) return Boolean(c.passes_quality_grade);
      const st = c.gate_status || {{}};
      return passesG123a(c) && st['3b'] === 'pass' && (c.g6_flags || 0) < 3;
    }}

    function passesGrowth0g(c) {{
      if (c.passes_growth_0g !== undefined) return Boolean(c.passes_growth_0g);
      return passesQualityGrade(c)
        && c.val_status === 'Valued'
        && (c.g_market_flag === 'ok' || c.g_market_flag === 'saturated_low')
        && c.g_market !== null && c.g_market !== undefined && c.g_market < 0.05
        && c.g_org_exp !== null && c.g_org_exp !== undefined && c.g_org_exp >= 0.05;
    }}

    function gradeBadgeInfo(c) {{
      if (passesPrimeGrade(c)) {{
        return {{
          label: 'P',
          cls: 'grade-prime',
          tip: 'Prime Grade — passed all 6 Munger Reject Gates cleanly (<3 G6 numeric flags).'
        }};
      }}
      if (passesQualityGrade(c)) {{
        const reason = c.rejected_at
          ? `rejected at ${{c.rejected_at}}`
          : (c.review_at ? `under review at ${{c.review_at}}` : (c.result || 'did not pass G4–G6'));
        return {{
          label: 'Q',
          cls: 'grade-quality',
          tip: `Quality Grade — passed G1–G3 (<3 G6 flags); ${{reason}}.`
        }};
      }}
      const st = c.gate_status || {{}};
      if (st['1'] === 'fail') {{
        return {{
          label: 'G1',
          cls: 'grade-fail',
          tip: 'Failed Gate 1 — Understandable Business.'
        }};
      }}
      if (st['2'] === 'fail') {{
        return {{
          label: 'G2',
          cls: 'grade-fail',
          tip: 'Failed Gate 2 — Essential Need & Market.'
        }};
      }}
      if (st['3b'] === 'fail' || c.g3a_moat_archetype === 'None') {{
        return {{
          label: 'G3',
          cls: 'grade-fail',
          tip: 'Failed Gate 3 — Economic Moat & Pricing Power.'
        }};
      }}
      if ((c.g6_flags || 0) >= 3) {{
        const extra = c.rejected_at ? ` (${{c.rejected_at}})` : '';
        return {{
          label: 'G6',
          cls: 'grade-fail',
          tip: `Excluded from Quality Grade — ${{c.g6_flags}} Gate 6 numeric flags (≥3)${{extra}}.`
        }};
      }}
      const rev = c.review_at ? ` at ${{c.review_at}}` : '';
      return {{
        label: '?',
        cls: 'grade-review',
        tip: `Under review${{rev}}.`
      }};
    }}

    function gradeBadgeHtml(c) {{
      const g = gradeBadgeInfo(c);
      return `<span class="grade-pill ${{g.cls}}" title="${{escHtml(g.tip)}}">${{g.label}}</span>`;
    }}

    function hasMoatArchetype(c) {{
      // Python par_valuation assumes a default 20y CAP whenever a moat archetype is set and Gate 4 is blank
      return Boolean(c.g3a_moat_archetype && String(c.g3a_moat_archetype).trim() !== '' && String(c.g3a_moat_archetype).trim() !== 'None');
    }}

    function parParams(c) {{
      return Object.assign({{ k: 0.085, k_fin: 0.1025, g_anchor_max: 0.13, roic_cap: 0.50, roic_term_max: 0.20, g_base: 0.030 }},
        ((SCREENER_DATA.universes || {{}})[c.universe] || {{}}).par_params || {{}});
    }}

    function updateTabCounts() {{
      const base = SCREENER_DATA.companies.filter(c => currentMarket === 'all' || c.universe === currentMarket);
      const qpass = base.filter(c => passesPrimeGrade(c));
      const growth0g = base.filter(c => passesGrowth0g(c));
      const qualityGrade = base.filter(c => passesQualityGrade(c));
      const valued = qpass.filter(c => c.val_status === 'Valued');
      // Header KPIs follow the market filter (computed client-side)
      const irrs = valued.filter(c => c.irr_5y !== null && c.irr_5y !== undefined && c.disc_rate !== null && c.disc_rate !== undefined)
        .map(c => c.irr_5y - c.disc_rate).sort((a, b) => a - b);
      const medIrr = irrs.length ? (irrs.length % 2 ? irrs[(irrs.length - 1) / 2] : 0.5 * (irrs[irrs.length / 2 - 1] + irrs[irrs.length / 2])) : null;
      const setKpi = (id, v) => {{ const el = document.getElementById(id); if (el) el.textContent = v; }};
      setKpi('kpi-universe', base.length);
      setKpi('kpi-qpass', qpass.length);
      setKpi('kpi-growth-0g', growth0g.length);
      setKpi('kpi-median-irr', medIrr !== null ? `${{medIrr >= 0 ? '+' : ''}}${{(medIrr * 100).toFixed(1)}}pp` : '—');
      document.getElementById('count-qpass').textContent = qpass.length;
      const g0El = document.getElementById('count-growth-0g');
      if (g0El) g0El.textContent = growth0g.length;
      const moatCountEl = document.getElementById('count-moat-universe');
      if (moatCountEl) moatCountEl.textContent = qualityGrade.length;
      document.getElementById('count-all').textContent = base.length;
    }}

    function setTab(tab) {{
      if (currentTab && currentTab !== 'methodology') {{
        tabSortState[currentTab] = {{ col: sortColumn, asc: sortAsc }};
      }}
      currentTab = tab;
      document.querySelectorAll('.tab-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.tab === tab);
      }});

      const isMethodology = tab === 'methodology';
      document.getElementById('controls-section').style.display = isMethodology ? 'none' : 'flex';
      document.getElementById('methodology-view').style.display = isMethodology ? 'block' : 'none';

      if (isMethodology) {{
        document.getElementById('table-view').style.display = 'none';
        document.getElementById('cards-view').style.display = 'none';
        document.getElementById('empty-state').style.display = 'none';
        const hint = document.getElementById('mobile-swipe-hint');
        if (hint) hint.classList.remove('visible');
        return;
      }}

      // Show/hide failing gate filter & valuation filter
      const showGateFilter = (tab === 'all' || tab === 'moat_universe' || tab === 'growth_0g');
      document.getElementById('filter-gate').style.display = showGateFilter ? 'inline-block' : 'none';
      const showValFilter = (tab === 'qpass' || tab === 'all' || tab === 'moat_universe');
      const valFilterEl = document.getElementById('filter-val');
      if (valFilterEl) valFilterEl.style.display = showValFilter ? 'inline-block' : 'none';

      // Restore per-tab sort state or fall back to tab default
      const saved = tabSortState[tab];
      const def = TAB_DEFAULT_SORTS[tab] || {{ col: 'g_org_exp', asc: false }};
      sortColumn = saved ? saved.col : def.col;
      sortAsc = saved ? saved.asc : def.asc;

      syncSortSelect();
      renderCurrentView();
    }}

    function setMarket(m) {{
      currentMarket = m;
      document.querySelectorAll('.market-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.market === m);
      }});
      renderCurrentView();
    }}

    function setViewMode(mode) {{
      userSetViewMode = true;
      viewMode = mode;
      document.getElementById('view-table-btn').classList.toggle('active', mode === 'table');
      document.getElementById('view-cards-btn').classList.toggle('active', mode === 'cards');
      updateDensityButton();
      renderCurrentView();
    }}

    function toggleColumnDensity() {{
      compactColumns = !compactColumns;
      updateDensityButton();
      renderCurrentView();
    }}

    function updateDensityButton() {{
      const btn = document.getElementById('btn-col-density');
      const lbl = document.getElementById('col-density-label');
      if (!btn || !lbl) return;
      btn.style.display = (viewMode === 'table') ? 'flex' : 'none';
      lbl.textContent = compactColumns ? 'Compact Cols' : 'All Cols';
      btn.title = compactColumns ? 'Showing essential columns — click to show all 20+ columns' : 'Showing all columns — click for compact view';
    }}

    function resetAllFilters() {{
      const searchEl = document.getElementById('filter-search');
      if (searchEl) searchEl.value = '';
      const clearBtn = document.getElementById('search-clear');
      if (clearBtn) clearBtn.style.display = 'none';
      ['filter-sector', 'filter-moat', 'filter-gate', 'filter-val'].forEach(id => {{
        const el = document.getElementById(id);
        if (el) el.value = 'all';
      }});
      currentMarket = 'all';
      document.querySelectorAll('.market-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.market === 'all');
      }});
      renderCurrentView();
    }}

    function handleSearchInput() {{
      const input = document.getElementById('filter-search');
      const clearBtn = document.getElementById('search-clear');
      clearBtn.style.display = input.value ? 'block' : 'none';
      applyFilters();
    }}

    function clearSearch() {{
      const input = document.getElementById('filter-search');
      input.value = '';
      document.getElementById('search-clear').style.display = 'none';
      input.focus();
      applyFilters();
    }}

    function applyFilters() {{
      renderCurrentView();
    }}

    function getFilteredData() {{
      const query = (document.getElementById('filter-search').value || '').trim().toLowerCase();
      const sector = document.getElementById('filter-sector').value;
      const moat = document.getElementById('filter-moat').value;
      const gate = document.getElementById('filter-gate').value;
      const valFilter = document.getElementById('filter-val') ? document.getElementById('filter-val').value : 'all';

      return SCREENER_DATA.companies.filter(c => {{
        // Tab restriction
        if (currentTab === 'qpass' && !passesPrimeGrade(c)) return false;
        if (currentTab === 'growth_0g' && !passesGrowth0g(c)) return false;
        if (currentTab === 'moat_universe' && !passesQualityGrade(c)) return false;

        // Market
        if (currentMarket !== 'all' && c.universe !== currentMarket) return false;

        // Sector
        if (sector !== 'all' && c.sector !== sector) return false;

        // Moat
        if (moat !== 'all' && c.g3a_moat_archetype !== moat) return false;

        // Valuation Status (in Prime Grade, Quality Grade & Full Universe tabs)
        if ((currentTab === 'qpass' || currentTab === 'all' || currentTab === 'moat_universe') && valFilter !== 'all') {{
          if (valFilter === 'g6flag') {{
            if (!(c.g6_flags > 0 && c.g6_answer === 'Y')) return false;
          }} else if (c.val_status !== valFilter) return false;
        }}

        // Gate
        if ((currentTab === 'all' || currentTab === 'moat_universe' || currentTab === 'growth_0g') && gate !== 'all') {{
          if ((gate === 'quality_grade' || gate === 'g123a') && !passesQualityGrade(c)) return false;
          if (gate === 'Quality pass' && !passesPrimeGrade(c)) return false;
          if (gate.startsWith('Gate') || gate.startsWith('G')) {{
            const num = gate.replace(/[^0-9]/g, '');
            if (num) {{
              const gPrefix = 'G' + num;
              const gatePrefix = 'Gate ' + num;
              const rejAt = c.rejected_at || '';
              const res = c.result || '';
              const matches = rejAt.startsWith(gPrefix) || rejAt.startsWith(gatePrefix) || res.includes(gPrefix);
              if (!matches) return false;
            }}
          }}
        }}

        // Search Query
        if (query) {{
          const hit = (c.ticker || '').toLowerCase().includes(query) ||
                      (c.company || '').toLowerCase().includes(query) ||
                      (c.sector || '').toLowerCase().includes(query) ||
                      (c.sub_industry || '').toLowerCase().includes(query);
          if (!hit) return false;
        }}

        return true;
      }});
    }}

    function sortData(list) {{
      return list.sort((a, b) => {{
        let vA = a[sortColumn];
        let vB = b[sortColumn];
        if (sortColumn === 'sales_1_3_5y') {{
          const pick = x => x.sales_5y ?? x.sales_3y ?? x.sales_1y ?? null;
          vA = pick(a);
          vB = pick(b);
        }}
        if (sortColumn === 'g_market') {{
          // rows shown as n/a (no_value_creation, multi_root, nav_anchored) sort as empty, not by hidden numbers
          const shown = (x) => ['ok', 'saturated_low', 'saturated_high'].includes(x.g_market_flag);
          if (!shown(a)) vA = null;
          if (!shown(b)) vB = null;
        }}

        if (Array.isArray(vA)) vA = vA.join(', ');
        if (Array.isArray(vB)) vB = vB.join(', ');

        if ((vA === null || vA === undefined || vA === '') && (vB === null || vB === undefined || vB === '')) return 0;
        if (vA === null || vA === undefined || vA === '') return 1;
        if (vB === null || vB === undefined || vB === '') return -1;

        if (typeof vA === 'string' || typeof vB === 'string') {{
          return sortAsc ? String(vA).localeCompare(String(vB)) : String(vB).localeCompare(String(vA));
        }}
        return sortAsc ? (vA - vB) : (vB - vA);
      }});
    }}

    function handleSort(col) {{
      if (sortColumn === col) {{
        sortAsc = !sortAsc;
      }} else {{
        sortColumn = col;
        sortAsc = (col === 'ticker' || col === 'company' || col === 'vs_par' || col === 'vs_term' || col === 'cur_mult');
      }}
      syncSortSelect();
      renderCurrentView();
    }}

    function applySortFromSelect(val) {{
      const lastHyphen = val.lastIndexOf('-');
      if (lastHyphen !== -1) {{
        sortColumn = val.slice(0, lastHyphen);
        sortAsc = (val.slice(lastHyphen + 1) === 'asc');
        renderCurrentView();
      }}
    }}

    function syncSortSelect() {{
      const sortSelect = document.getElementById('filter-sort');
      if (!sortSelect) return;
      const targetVal = `${{sortColumn}}-${{sortAsc ? 'asc' : 'desc'}}`;
      let matched = false;
      for (let opt of sortSelect.options) {{
        if (opt.value === targetVal) {{
          sortSelect.value = targetVal;
          matched = true;
          break;
        }}
      }}
      if (!matched) {{
        let customOpt = document.getElementById('sort-custom-opt');
        if (!customOpt) {{
          customOpt = document.createElement('option');
          customOpt.id = 'sort-custom-opt';
          sortSelect.appendChild(customOpt);
        }}
        const colLabel = (ALL_COLS[sortColumn] && ALL_COLS[sortColumn].label) ? ALL_COLS[sortColumn].label : sortColumn;
        customOpt.value = targetVal;
        customOpt.textContent = `Sort: ${{colLabel}} (${{sortAsc ? '▲ Asc' : '▼ Desc'}})`;
        sortSelect.value = targetVal;
      }}
    }}

    function fmtPct(val, plus=false) {{
      if (val === null || val === undefined) return '-';
      const p = (val * 100).toFixed(1) + '%';
      return (plus && val > 0) ? '+' + p : p;
    }}
    function fmtNum(val, dec=1) {{
      if (val === null || val === undefined) return '-';
      return Number(val).toLocaleString(undefined, {{ minimumFractionDigits: dec, maximumFractionDigits: dec }});
    }}
    function fmtPrice(val, ccy='') {{
      if (val === null || val === undefined) return '-';
      return (ccy ? ccy + ' ' : '') + Number(val).toFixed(2);
    }}

    function escHtml(str) {{
      if (str === null || str === undefined) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}

    function hasActiveFilters() {{
      const q = (document.getElementById('filter-search').value || '').trim();
      const sector = document.getElementById('filter-sector').value;
      const moat = document.getElementById('filter-moat').value;
      const gate = document.getElementById('filter-gate').value;
      const valFilter = document.getElementById('filter-val') ? document.getElementById('filter-val').value : 'all';
      const showExt = (currentTab === 'all' || currentTab === 'moat_universe' || currentTab === 'growth_0g');
      const showVal = (currentTab === 'qpass' || currentTab === 'all' || currentTab === 'moat_universe');
      return Boolean(q) || currentMarket !== 'all' || sector !== 'all' || moat !== 'all' ||
        (showExt && gate !== 'all') || (showVal && valFilter !== 'all');
    }}

    function renderCurrentView() {{
      updateTabCounts();
      if (currentTab === 'methodology') return;
      const data = sortData(getFilteredData());
      const empty = document.getElementById('empty-state');
      const isEmpty = (data.length === 0);
      empty.style.display = isEmpty ? 'block' : 'none';

      const showTable = (viewMode === 'table' && !isEmpty);
      document.getElementById('table-view').style.display = showTable ? 'block' : 'none';
      document.getElementById('cards-view').style.display = (viewMode === 'cards' && !isEmpty) ? 'block' : 'none';

      const hint = document.getElementById('mobile-swipe-hint');
      if (hint) hint.classList.toggle('visible', showTable);

      const countPill = document.getElementById('filter-count-pill');
      if (countPill) countPill.textContent = `${{data.length}} shown`;

      const resetBtn = document.getElementById('btn-reset-filters');
      if (resetBtn) resetBtn.style.display = hasActiveFilters() ? 'inline-flex' : 'none';

      const exportBtn = document.getElementById('btn-export');
      if (exportBtn) exportBtn.disabled = isEmpty;

      updateDensityButton();
      renderTable(data);
      renderCards(data);
    }}

    function renderTable(data) {{
      const thead = document.getElementById('table-head');
      const tbody = document.getElementById('table-body');

      // Canonical column keys per tab — all labels come from ALL_COLS for 100% consistency
      const compactKeys = [
        'ticker', 'company', 'price', 'par_val', 'vs_par', 'term_val', 'vs_term', 'irr_5y',
        'cur_mult', 'par_mult', 'term_mult', 'g_market', 'sales_1_3_5y', 'g_org_exp', 'g4_cap', 'roic_used'
      ];
      const coreValuationCols = [
        'ticker', 'company', 'country', 'price', 'sales_1y', 'sales_cagr',
        'g_market', 'sales_1_3_5y', 'g_org_exp', 'buyback_yield', 'g_gap', 'par_val', 'vs_par',
        'term_val', 'vs_term', 'cur_mult', 'par_mult', 'term_mult', 'irr_5y', 'g4_cap', 'cap_implied',
        'cap_gap', 'g3a_moat_archetype'
      ].map(k => ALL_COLS[k]);

      let cols = [];
      if (compactColumns) {{
        let colKeys = [];
        if (currentTab === 'qpass') {{
          colKeys = [...compactKeys, 'fcf_conv', 'g6_flags'];
        }} else if (currentTab === 'growth_0g') {{
          colKeys = [...compactKeys, 'g5_mgmt', 'g6_cash', 'result', 'rejected_at'];
        }} else if (currentTab === 'moat_universe') {{
          colKeys = [...compactKeys, 'result', 'rejected_at', 'val_status'];
        }} else {{
          colKeys = ['ticker', 'company', 'result', 'rejected_at', ...compactKeys.slice(2), 'val_status'];
        }}
        cols = colKeys.map(k => ALL_COLS[k]).filter(Boolean);
      }} else {{
        if (currentTab === 'qpass') {{
          cols = [...coreValuationCols, ALL_COLS.roic_used, ALL_COLS.fcf_conv, ALL_COLS.g6_flags, ALL_COLS.sector];
        }} else if (currentTab === 'growth_0g') {{
          cols = [...coreValuationCols, ALL_COLS.g5_mgmt, ALL_COLS.g6_cash, ALL_COLS.result, ALL_COLS.rejected_at, ALL_COLS.roic_used, ALL_COLS.fcf_conv, ALL_COLS.g6_flags, ALL_COLS.sector];
        }} else if (currentTab === 'moat_universe') {{
          cols = [...coreValuationCols, ALL_COLS.g5_mgmt, ALL_COLS.g6_cash, ALL_COLS.result, ALL_COLS.rejected_at, ALL_COLS.roic_used, ALL_COLS.fcf_conv, ALL_COLS.g6_flags, ALL_COLS.val_status, ALL_COLS.sector];
        }} else {{
          cols = [
            ALL_COLS.ticker, ALL_COLS.company, ALL_COLS.country, ALL_COLS.result, ALL_COLS.rejected_at,
            ...coreValuationCols.slice(3),
            ALL_COLS.g5_mgmt, ALL_COLS.g6_cash,
            ALL_COLS.roic_used, ALL_COLS.val_status, ALL_COLS.sector
          ];
        }}
      }}

      // Build THEAD
      let thHtml = '<tr>';
      cols.forEach(c => {{
        const isSorted = sortColumn === c.key;
        const arrow = isSorted ? (sortAsc ? ' ▲' : ' ▼') : '';
        const cls = (isSorted ? 'sorted ' : '') + (c.num ? 'num' : '');
        const tipText = COL_TIPS[c.key] || '';
        const tipAttr = tipText ? ` title="${{escHtml(tipText)}}"` : '';
        thHtml += `<th class="${{cls}}"${{tipAttr}} onclick="handleSort('${{c.key}}')">${{c.label}}${{arrow}}</th>`;
      }});
      thHtml += '</tr>';
      thead.innerHTML = thHtml;

      // Build TBODY
      let trHtml = '';
      data.forEach(c => {{
        const isSelected = (c.id === selectedCompanyId);
        trHtml += `<tr class="${{isSelected ? 'selected' : ''}}" data-id="${{c.id}}" onclick="openDrawer('${{c.id}}')">`;

        cols.forEach(col => {{
          let val = c[col.key];
          let cellContent = '';

          if (col.key === 'ticker') {{
            cellContent = `<span class="ticker-wrap">${{gradeBadgeHtml(c)}}<span class="cell-ticker">${{escHtml(val)}}</span></span>`;
          }} else if (col.key === 'company') {{
            cellContent = `<div class="cell-company" title="${{escHtml(val)}}">${{escHtml(val)}}</div>`;
          }} else if (col.key === 'vs_par') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const badgeClass = val <= 0 ? 'badge-green' : 'badge-amber';
              cellContent = `<span class="badge ${{badgeClass}}">${{fmtPct(val, true)}}</span>`;
            }}
          }} else if (col.key === 'vs_term') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const badgeClass = val <= 0 ? 'badge-green' : 'badge-amber';
              cellContent = `<span class="badge ${{badgeClass}}" title="${{val <= 0 ? 'At or below Terminal Price floor' : 'Premium above Terminal Price floor'}}">${{fmtPct(val, true)}}</span>`;
            }}
          }} else if (col.key === 'irr_5y') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const color = irrColor(c, val);
              cellContent = `<strong style="color: ${{color}};">${{fmtPct(val)}}</strong>`;
            }}
          }} else if (col.key === 'val_status') {{
            const bCls = val === 'Valued' ? 'badge-slate' : 'badge-gray';
            const ronicFlag = c.ronic_le_r ? ` <span title="RONIC₀ ≤ r: growth adds no value (Fair P/E ≤ 1/r) — review capital base" style="color: var(--amber);">⚠</span>` : '';
            cellContent = `<span class="badge ${{bCls}}">${{escHtml(val)}}</span>${{ronicFlag}}`;
          }} else if (col.key === 'result') {{
            const bCls = val === 'Quality pass' ? 'badge-green' : (val.startsWith('Rejected') ? 'badge-red' : 'badge-gray');
            cellContent = `<span class="badge ${{bCls}}">${{escHtml(val)}}</span>`;
          }} else if (col.key === 'rejected_at') {{
            cellContent = escHtml(val) || '-';
          }} else if (col.key === 'price' || col.key === 'par_val' || col.key === 'term_val') {{
            cellContent = fmtPrice(val, c.quote_currency);
            if (col.key === 'par_val' && c.ronic_le_r) {{
              cellContent += ` <span title="RONIC₀ ≤ r: growth adds no value (Fair P/E ≤ 1/r) — review capital base" style="color: var(--amber);">⚠</span>`;
            }}
          }} else if (col.key === 'sales_1_3_5y') {{
            const fInt = v => (v === null || v === undefined) ? '-' : Math.round(v * 100) + '%';
            const tip = `1Y: ${{fmtPct(c.sales_1y, true)}} · 3Y: ${{fmtPct(c.sales_3y, true)}} · 5Y: ${{fmtPct(c.sales_5y, true)}}`;
            cellContent = `<span style="white-space: nowrap;" title="${{escHtml(tip)}}">${{fInt(c.sales_1y)}} / ${{fInt(c.sales_3y)}} / ${{fInt(c.sales_5y)}}</span>`;
          }} else if (col.key === 'sales_1y') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const sColor = val < 0 ? 'var(--amber)' : (val < 0.04 ? 'var(--text-muted)' : 'var(--text-main)');
              cellContent = `<span style="color: ${{sColor}};">${{fmtPct(val, true)}}</span>`;
            }}
          }} else if (col.key === 'buyback_yield') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const bbColor = val >= 0.01 ? 'var(--green)' : (val < 0 ? 'var(--red)' : 'var(--text-muted)');
              cellContent = `<span style="color: ${{bbColor}};">${{fmtPct(val, true)}}</span>`;
            }}
          }} else if (col.key === 'g6_flags') {{
            cellContent = g6Markers(c);
          }} else if (col.key === 'roic_exp') {{
            const srcLbl = c.roic_source === 'roe_median' ? 'ROE' : (c.roic_source === 'roic_median' ? 'GAAP ROIC' : 'Tangible ROIC');
            cellContent = (val === null || val === undefined) ? '-'
              : `<span title="RONIC₀ used by the DCF (after M&A blend and 50% cap); input ${{srcLbl}} ${{fmtPct(c.roic_used)}}">${{fmtPct(val)}}</span>`;
          }} else if (col.key === 'roic_used' || col.key === 'fcf_conv' || col.key === 'sales_cagr' || col.key === 'opcost_cagr' || col.key === 'g_org_exp' || col.key === 'g_start' || col.key === 'g_exp') {{
            cellContent = fmtPct(val);
          }} else if (col.key === 'g_market') {{
            cellContent = fmtGMarketCell(c);
          }} else if (col.key === 'g_gap') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const bCls = val >= 0 ? 'badge-green' : 'badge-red';
              cellContent = `<span class="badge ${{bCls}}">${{fmtPct(val, true)}}</span>`;
            }}
          }} else if (col.key === 'cap_implied') {{
            cellContent = (val !== null && val !== undefined) ? `${{fmtNum(val, 1)}}y` : '-';
          }} else if (col.key === 'cap_gap') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const bCls = val >= 0 ? 'badge-green' : 'badge-red';
              const sign = val > 0 ? '+' : '';
              cellContent = `<span class="badge ${{bCls}}">${{sign}}${{fmtNum(val, 1)}}y</span>`;
            }}
          }} else if (col.key === 'g4_cap') {{
            if (val !== null && val !== undefined && val !== '') {{
              const tip = fmtCapTooltip(c);
              cellContent = tip ? `<span title="${{escHtml(tip)}}">${{val}}y</span>` : `${{val}}y`;
            }} else {{
              cellContent = hasMoatArchetype(c) ? `<span style="color: var(--text-dim);" title="Default 20y CAP assumed (Gate 4 unscored)">20y*</span>` : '-';
            }}
          }} else if (col.key === 'g5_mgmt') {{
            if (val === null || val === undefined || val === '') {{
              cellContent = '-';
            }} else {{
              const n = Number(val);
              const bCls = n === 2 ? 'badge-green' : (n === 0 ? 'badge-red' : 'badge-slate');
              cellContent = `<span class="badge ${{bCls}}">${{n}}/2</span>`;
            }}
          }} else if (col.key === 'g6_cash') {{
            if (val === null || val === undefined || val === '') {{
              cellContent = '-';
            }} else {{
              const bCls = val === 'Y' ? 'badge-green' : (val === 'N' ? 'badge-red' : 'badge-gray');
              cellContent = `<span class="badge ${{bCls}}">${{escHtml(val)}}</span>`;
            }}
          }} else if (col.key === 'cur_mult') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const gVal = c.g_org_exp;
              const fwd = (gVal !== null && gVal !== undefined && (1 + gVal) > 0) ? val / (1 + gVal) : null;
              const tip = `Trailing: ${{fmtNum(val, 2)}}x · 1Y Forward (at Model g ${{fmtPct(gVal)}}): ${{fwd !== null ? fmtNum(fwd, 2) + 'x' : '-'}}`;
              cellContent = fwd !== null
                ? `<span style="white-space: nowrap;" title="${{escHtml(tip)}}">${{fmtNum(val, 1)}} / ${{fmtNum(fwd, 1)}}x</span>`
                : `<span title="${{escHtml(tip)}}">${{fmtNum(val, 1)}}x</span>`;
            }}
          }} else if (col.num) {{
            cellContent = fmtNum(val);
          }} else {{
            cellContent = escHtml(val) || '-';
          }}

          trHtml += `<td class="${{col.num ? 'num' : ''}}">${{cellContent}}</td>`;
        }});

        trHtml += '</tr>';
      }});
      tbody.innerHTML = trHtml;
    }}

    function fmtSignedYears(val) {{
      if (val === null || val === undefined) return '-';
      return (val > 0 ? '+' : '') + fmtNum(val, 1) + 'y';
    }}

    const MOAT_SCORE_META = [
      {{ key: '3_tb', short: 'Toll Booth', full: 'Toll booth & switching costs' }},
      {{ key: '3_ia', short: 'Infra & Intangibles', full: 'Irreplaceable infrastructure & intangibles' }},
      {{ key: '3_se', short: 'Scale Shared', full: 'Scale economies shared (Nick Sleep model)' }},
      {{ key: '3_rd', short: 'R&D Leadership', full: 'R&D & innovation leadership' }}
    ];
    const FORCE_SCORE_META = [
      {{ key: '4_ent', short: 'Entrants', full: 'Threat of New Entrants' }},
      {{ key: '4_riv', short: 'Rivalry', full: 'Competitive Rivalry' }},
      {{ key: '4_buy', short: 'Buyers', full: 'Customer Bargaining Power' }},
      {{ key: '4_sup', short: 'Suppliers', full: 'Supplier Bargaining Power' }},
      {{ key: '4_sub', short: 'Substitution', full: 'Threat of Substitution & Clock Speed' }}
    ];

    function fmtCapTooltip(c) {{
      if (c.cap_audited && c.g3_moat_scores && c.g4_force_scores) {{
        const mStr = MOAT_SCORE_META.map(m => `${{m.short}}:${{c.g3_moat_scores[m.key]}}`).join(' ');
        const fStr = FORCE_SCORE_META.map(f => `${{f.short}}:${{c.g4_force_scores[f.key]}}`).join(' ');
        const adj = c.cap_fatal ? `Fatal Cap ≤10y` : `−${{c.cap_haircut || 0}}y`;
        return `Step 1 Initial CAP ${{c.cap_init}}y (${{mStr}}) | Step 2 Forces ${{adj}} (${{fStr}}) -> Final CAP ${{c.g4_cap}}y`;
      }}
      if (c.g4_cap) return `Legacy CAP ${{c.g4_cap}}y (sub-factor audit pending Phase 2)`;
      return '';
    }}

    function renderCapBreakdownHtml(c) {{
      const ms = c.g3_moat_scores || {{}};
      const fs = c.g4_force_scores || {{}};
      if (!c.moat_complete && !c.cap_audited) {{
        if (c.g4_cap !== null && c.g4_cap !== undefined && c.g4_cap !== '') {{
          return `<div style="font-size: 11px; color: var(--text-dim);">Assigned Runway: <strong style="color: var(--text-main);">${{c.g4_cap}}y</strong> &bull; <em>Legacy CAP (Gate 3/4 sub-factor scores pending Phase 2 audit)</em></div>`;
        }}
        return '';
      }}
      const pillStyle = (bg, col, bdr) => `display:inline-flex; align-items:center; gap:4px; font-size:10.5px; padding:2px 6px; border-radius:4px; background:${{bg}}; color:${{col}}; border:1px solid ${{bdr}};`;
      const moatPills = MOAT_SCORE_META.map(m => {{
        const v = ms[m.key];
        if (v === 2) return `<span style="${{pillStyle('rgba(16,185,129,0.16)', 'var(--green)', 'rgba(16,185,129,0.35)')}}" title="${{escHtml(m.full)}}: 2 (Elite)">${{m.short}} <b>2</b></span>`;
        if (v === 1) return `<span style="${{pillStyle('rgba(56,189,248,0.14)', 'var(--accent)', 'rgba(56,189,248,0.32)')}}" title="${{escHtml(m.full)}}: 1 (Supporting)">${{m.short}} <b>1</b></span>`;
        return `<span style="${{pillStyle('rgba(148,163,184,0.08)', 'var(--text-dim)', 'rgba(148,163,184,0.18)')}}" title="${{escHtml(m.full)}}: 0 (Absent)">${{m.short}} 0</span>`;
      }}).join(' ');

      let html = `
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; margin-bottom:4px; gap:6px; flex-wrap:wrap;">
          <span style="color:var(--text-muted); font-weight:600;">Step 1 &mdash; Moat Profile (G3):</span>
          <span style="color:var(--accent); font-weight:700;">Initial CAP: ${{c.cap_init !== null && c.cap_init !== undefined ? c.cap_init + 'y' : '-'}}</span>
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:${{c.cap_audited ? '8px' : '0'}};">${{moatPills}}</div>
      `;

      if (c.cap_audited) {{
        const forcePills = FORCE_SCORE_META.map(f => {{
          const v = fs[f.key];
          if (v === 2) return `<span style="${{pillStyle('rgba(244,63,94,0.18)', 'var(--red)', 'rgba(244,63,94,0.4)')}}" title="${{escHtml(f.full)}}: 2 (Terminal Threat)">${{f.short}} <b>2</b></span>`;
          if (v === 1) return `<span style="${{pillStyle('rgba(245,158,11,0.15)', 'var(--amber)', 'rgba(245,158,11,0.35)')}}" title="${{escHtml(f.full)}}: 1 (Moderate Pressure)">${{f.short}} <b>1</b></span>`;
          return `<span style="${{pillStyle('rgba(16,185,129,0.10)', 'var(--green)', 'rgba(16,185,129,0.22)')}}" title="${{escHtml(f.full)}}: 0 (Benign / Insulated)">${{f.short}} 0</span>`;
        }}).join(' ');
        const adjText = c.cap_fatal
          ? `<span style="color:var(--red); font-weight:700;">Fatal Cap &rarr; ${{c.g4_cap}}y (REJECT)</span>`
          : `<span style="color:${{(c.cap_haircut || 0) > 0 ? 'var(--amber)' : 'var(--green)'}}; font-weight:700;">&minus;${{c.cap_haircut || 0}}y &rarr; Final ${{c.g4_cap}}y</span>`;
        html += `
          <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; margin-bottom:4px; gap:6px; flex-wrap:wrap;">
            <span style="color:var(--text-muted); font-weight:600;">Step 2 &mdash; Competitive Forces (G4):</span>
            ${{adjText}}
          </div>
          <div style="display:flex; flex-wrap:wrap; gap:4px;">${{forcePills}}</div>
        `;
      }}
      return html;
    }}

    // Market-Implied Growth with its solver flag (screener/gates.py solve_market_growth); growth gap only when 'ok'
    // (a saturated g_market is a grid bound, shown as ≤ / ≥, so no gap is computed)
    const G_MARKET_FLAG_LABELS = {{
      saturated_low: '≤', saturated_high: '≥',
      no_value_creation: 'n/a (ROIC ≤ r: growth destroys value)',
      multi_root: '(ambiguous)',
      nav_anchored: 'n/a (NAV-anchored)'
    }};
    function fmtGMarket(c) {{
      const flag = c.g_market_flag;
      if (flag === 'nav_anchored' || flag === 'no_value_creation') return G_MARKET_FLAG_LABELS[flag];
      if (c.g_market === null || c.g_market === undefined) return '-';
      if (flag === 'saturated_low' || flag === 'saturated_high') return `${{G_MARKET_FLAG_LABELS[flag]}} ${{fmtPct(c.g_market, true)}}`;
      if (flag === 'multi_root') return `${{fmtPct(c.g_market, true)}} ${{G_MARKET_FLAG_LABELS[flag]}}`;
      return fmtPct(c.g_market, true);
    }}

    function fmtGMarketCell(c) {{
      const flag = c.g_market_flag;
      if (flag === 'nav_anchored' || flag === 'no_value_creation') {{
        return `<span title="${{escHtml(G_MARKET_FLAG_LABELS[flag])}}" style="cursor: help; color: var(--amber);">⚠</span>`;
      }}
      if (c.g_market === null || c.g_market === undefined) return '-';
      if (flag === 'saturated_low' || flag === 'saturated_high') return `${{G_MARKET_FLAG_LABELS[flag]}} ${{fmtPct(c.g_market, true)}}`;
      if (flag === 'multi_root') {{
        return `${{fmtPct(c.g_market, true)}} <span title="${{escHtml(fmtPct(c.g_market, true) + ' ' + G_MARKET_FLAG_LABELS[flag])}}" style="cursor: help; color: var(--amber);">⚠</span>`;
      }}
      return fmtPct(c.g_market, true);
    }}

    function triadCardsHtml(c) {{
      const g1y = fmtPct(c.sales_1y, true);
      const gCeil = fmtPct(c.g_org_exp);
      const gMkt = fmtGMarketCell(c);
      const gGap = c.g_gap !== null && c.g_gap !== undefined ? fmtPct(c.g_gap, true) : '-';
      const gColor = (c.g_gap !== null && c.g_gap !== undefined) ? (c.g_gap >= 0 ? 'var(--green)' : 'var(--red)') : 'var(--text-muted)';
      const cOur = c.g4_cap ? `${{c.g4_cap}}y` : (hasMoatArchetype(c) ? '20y*' : '-');
      const cMkt = (c.cap_implied !== null && c.cap_implied !== undefined) ? `${{fmtNum(c.cap_implied, 1)}}y` : '-';
      const cGap = fmtSignedYears(c.cap_gap);
      const cColor = (c.cap_gap !== null && c.cap_gap !== undefined) ? (c.cap_gap >= 0 ? 'var(--green)' : 'var(--red)') : 'var(--text-muted)';
      return `
        <div class="card-metric-cell">
          <div class="card-metric-label" title="1Y trailing revenue growth / Organic Growth Ceiling g₀ / Market-implied growth g_mkt / Growth Margin (g₀ − g_mkt).">Growth (1Y / Ceiling / Mkt / Gap)</div>
          <div class="card-metric-val" style="font-size: 11.5px;">
            ${{g1y}} / ${{gCeil}} / ${{gMkt}} <span style="color:${{gColor}};">(${{gGap}})</span>
          </div>
        </div>
        <div class="card-metric-cell">
          <div class="card-metric-label" title="Gate 4 Competitive Advantage Period (Our CAP) / Market-Implied CAP / Runway Margin (Our CAP − Mkt CAP).">Runway (Our / Mkt / Gap)</div>
          <div class="card-metric-val" style="font-size: 11.5px;">
            ${{cOur}} / ${{cMkt}} <span style="color:${{cColor}};">(${{cGap}})</span>
          </div>
        </div>
      `;
    }}

    function renderCards(data) {{
      const cardsGrid = document.getElementById('cards-grid');
      let cardsHtml = '';

      data.forEach(c => {{
        const isSelected = (c.id === selectedCompanyId);
        let badgeHtml = '';
        let metricsHtml = '';

        const vsParText = c.vs_par !== null && c.vs_par !== undefined ? `${{fmtPct(c.vs_par, true)}} vs FV` : escHtml(c.val_status);
        const vsParCls = (c.vs_par !== null && c.vs_par !== undefined)
          ? 'badge-slate'
          : 'badge-gray';

        if (currentTab === 'qpass') {{
          const termBadge = (c.vs_term !== null && c.vs_term !== undefined && c.vs_term <= 0)
            ? `<span class="badge badge-green" style="margin-right:4px;" title="Trading at or below Terminal Price floor">${{fmtPct(c.vs_term, true)}} vs Term</span>` : '';
          badgeHtml = `${{termBadge}}<span class="badge ${{vsParCls}}">${{vsParText}}</span>`;
          const roicExtra = `FCF ${{fmtPct(c.fcf_conv)}}`;
          const roicExtraLabel = 'Op ROIC • FCF Conv';
          const roicExtraTip = 'Marginal RONIC₀ used by the DCF • Multi-year Free Cash Flow conversion (FCF ÷ Net Income).';
          metricsHtml = `
            <div class="card-metric-cell">
              <div class="card-metric-label" title="5-Year Expected IRR across growing annual dividends and Year-5 rolled-forward DCF Fair Value.">5Y Exp IRR</div>
              <div class="card-metric-val" style="color: ${{irrColor(c, c.irr_5y)}};">${{fmtPct(c.irr_5y)}}</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label" title="Current Share Price / DCF Fair Value / Standalone Terminal Price (3% inflation floor).">Price / Fair / Term</div>
              <div class="card-metric-val" style="font-size: 11.5px;">${{fmtPrice(c.price, c.quote_currency)}} / ${{fmtPrice(c.par_val, c.quote_currency)}} / ${{fmtPrice(c.term_val, c.quote_currency)}}</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label" title="Current P/E (Price ÷ Active EPS) / Explicit DCF Fair P/E / Standalone Terminal P/E floor.">Cur / Fair / Term P/E</div>
              <div class="card-metric-val">${{fmtNum(c.cur_mult)}}x / ${{fmtNum(c.par_mult)}}x / ${{fmtNum(c.term_mult)}}x</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label" title="${{roicExtraTip}}">${{roicExtraLabel}}</div>
              <div class="card-metric-val" style="font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${{fmtPct(c.roic_used)}} • ${{roicExtra}}
              </div>
            </div>
          ` + triadCardsHtml(c);
        }} else {{
          const bCls = c.result === 'Quality pass' ? 'badge-green' : (c.result.startsWith('Rejected') ? 'badge-red' : 'badge-gray');
          const termBadge = (c.vs_term !== null && c.vs_term !== undefined && c.vs_term <= 0)
            ? `<span class="badge badge-green" style="margin-right:4px;" title="Trading at or below Terminal Price floor">${{fmtPct(c.vs_term, true)}} vs Term</span>` : '';
          badgeHtml = `<span class="badge ${{bCls}}" style="margin-right:4px;">${{escHtml(c.result)}}</span>${{termBadge}}<span class="badge ${{vsParCls}}">${{vsParText}}</span>`;
          const stageColor = c.result === 'Quality pass' ? 'var(--green)' : 'var(--red)';
          const stageText = escHtml(c.rejected_at) || (c.result === 'Quality pass' ? '✓ Passed All 6 Reject Gates' : escHtml(c.result));
          metricsHtml = `
            <div class="card-metric-cell" style="grid-column: span 2;">
              <div class="card-metric-label" title="6-Gate waterfall outcome (first failed gate) • Gate 3a primary economic moat archetype.">Gate Stage • Moat Archetype</div>
              <div class="card-metric-val" style="font-size: 11.5px; color: ${{stageColor}}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${{stageText}} • <span style="color: var(--text-main);">${{escHtml(c.g3a_moat_archetype) || 'None'}}</span>
              </div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label" title="5-Year Expected IRR across growing annual dividends and Year-5 rolled-forward DCF Fair Value.">5Y Exp IRR</div>
              <div class="card-metric-val" style="color: ${{irrColor(c, c.irr_5y)}};">${{fmtPct(c.irr_5y)}}</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label" title="Current Share Price / DCF Fair Value / Standalone Terminal Price (3% inflation floor).">Price / Fair / Term</div>
              <div class="card-metric-val" style="font-size: 11.5px;">${{fmtPrice(c.price, c.quote_currency)}} / ${{fmtPrice(c.par_val, c.quote_currency)}} / ${{fmtPrice(c.term_val, c.quote_currency)}}</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label" title="Current P/E (Price ÷ Active EPS) / Explicit DCF Fair P/E / Standalone Terminal P/E floor.">Cur / Fair / Term P/E</div>
              <div class="card-metric-val">${{fmtNum(c.cur_mult)}}x / ${{fmtNum(c.par_mult)}}x / ${{fmtNum(c.term_mult)}}x</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label" title="Marginal RONIC₀ used by the DCF • Net annual share buyback yield (positive = buybacks; negative = dilution).">Op ROIC • Buyback</div>
              <div class="card-metric-val" style="font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${{fmtPct(c.roic_used)}} • BB ${{fmtPct(c.buyback_yield, true)}}
              </div>
            </div>
          ` + triadCardsHtml(c);
        }}

        cardsHtml += `
          <div class="company-card ${{isSelected ? 'selected' : ''}}" data-id="${{c.id}}" onclick="openDrawer('${{c.id}}')">
            <div class="card-header">
              <div class="card-ticker-group">
                ${{gradeBadgeHtml(c)}}
                <span class="card-ticker">${{escHtml(c.ticker)}}</span>
                <span class="badge badge-gray" style="font-size: 10px; padding: 1px 5px;">${{escHtml(c.universe.toUpperCase())}}</span>
              </div>
              ${{badgeHtml}}
            </div>
            <div>
              <div class="card-company-name">${{escHtml(c.company)}}</div>
              <div class="card-meta-line">${{escHtml(c.country)}} • ${{escHtml(c.sector || '')}}</div>
            </div>
            <div class="card-metrics-grid">
              ${{metricsHtml}}
            </div>
            <div class="card-footer">
              <span>${{escHtml(c.sub_industry || '')}}</span>
              <span class="card-footer-action">Dossier →</span>
            </div>
          </div>
        `;
      }});

      cardsGrid.innerHTML = cardsHtml;
    }}

    // Slide-Out Dossier Drawer Logic
    function openDrawer(id) {{
      selectedCompanyId = id;
      const c = SCREENER_DATA.companies.find(item => item.id === id);
      if (!c) return;

      // Update selected row style in table
      document.querySelectorAll('tbody tr').forEach(tr => {{
        tr.classList.remove('selected');
      }});
      const selectedRow = document.querySelector(`tbody tr[data-id="${{id}}"]`);
      if (selectedRow) selectedRow.classList.add('selected');

      // Update selected card style in cards view
      document.querySelectorAll('.company-card').forEach(card => {{
        card.classList.remove('selected');
      }});
      const selectedCard = document.querySelector(`.company-card[data-id="${{id}}"]`);
      if (selectedCard) selectedCard.classList.add('selected');

      // Populate Header
      document.getElementById('dossier-ticker').textContent = c.ticker;
      document.getElementById('dossier-company').textContent = c.company;
      document.getElementById('dossier-meta').textContent = `${{c.universe.toUpperCase()}} • ${{c.country}} • ${{c.sector}} • ${{c.sub_industry}}`;

      const mktBadge = document.getElementById('dossier-market-badge');
      mktBadge.textContent = c.universe.toUpperCase();
      mktBadge.className = 'badge badge-gray';

      const valBadge = document.getElementById('dossier-val-badge');
      if (c.result === 'Quality pass') {{
        valBadge.textContent = (c.vs_par !== null ? `${{fmtPct(c.vs_par, true)}} vs fair value` : c.val_status) + (c.ronic_le_r ? ' • ⚠ RONIC₀ ≤ r (review)' : '');
        valBadge.className = `badge ${{c.vs_par !== null ? 'badge-slate' : 'badge-gray'}}`;
      }} else {{
        const vStr = (c.vs_par !== null && c.vs_par !== undefined)
          ? ` • ${{fmtPct(c.vs_par, true)}} vs fair value`
          : ((c.val_status && c.val_status !== 'No data') ? ` • ${{c.val_status}}` : '');
        valBadge.textContent = c.result + vStr;
        valBadge.className = 'badge badge-red';
      }}

      // Build Waterfall Stepper
      const stepper = document.getElementById('dossier-stepper');
      const gates = [
        {{ key: '1', name: 'G1: Understand' }},
        {{ key: '2', name: 'G2: Essential' }},
        {{ key: '3b', name: 'G3: Moat' }},
        {{ key: '4', name: 'G4: Runway' }},
        {{ key: '5', name: 'G5: Mgmt' }},
        {{ key: '6', name: 'G6: Cash' }}
      ];

      let stepperHtml = '';
      gates.forEach(g => {{
        const st = (c.gate_status && c.gate_status[g.key]) || 'blank';
        let bg = 'rgba(148, 163, 184, 0.2)';
        let color = '#94a3b8';
        let icon = '○';
        let label = st.toUpperCase();

        if (st === 'pass') {{
          bg = 'rgba(16, 185, 129, 0.25)';
          color = 'var(--green)';
          icon = '✓';
        }} else if (st === 'fail') {{
          bg = 'rgba(244, 63, 94, 0.25)';
          color = 'var(--red)';
          icon = '✕';
        }}

        if (st !== 'blank') {{
          if (g.key === '4' && c.g4_cap !== null && c.g4_cap !== undefined && c.g4_cap !== '') {{
            label = `${{label}} · ${{c.g4_cap}}Y`;
          }} else if (g.key === '5' && st === 'pass' && Number(c.g5_mgmt) === 2) {{
            label = 'ELITE';
          }}
        }}

        stepperHtml += `
          <div class="waterfall-step">
            <div class="step-badge" style="background:${{bg}}; color:${{color}};">${{icon}}</div>
            <div class="step-title">${{g.name}}</div>
            <div class="step-result" style="color:${{color}};">${{label}}</div>
          </div>
        `;
      }});
      stepper.innerHTML = stepperHtml;

      const verdictEl = document.getElementById('dossier-verdict');
      if (c.result === 'Quality pass') {{
        verdictEl.innerHTML = `<span style="color: var(--green);">✓ Cleared All 6 Munger Reject Gates — Enters Quantitative Funnel</span>`;
      }} else {{
        verdictEl.innerHTML = `<span style="color: var(--red);">✕ ${{escHtml(c.rejected_at || c.result)}}</span>`;
      }}

      // Qualitative Dossier
      document.getElementById('dossier-moat-type').textContent = c.g3a_moat_archetype || 'None';
      document.getElementById('dossier-cap').textContent = (c.g4_cap !== null && c.g4_cap !== undefined && c.g4_cap !== '')
        ? `${{c.g4_cap}} Years Runway${{c.cap_audited ? '' : ' (Legacy)'}}`
        : (passesG123a(c) ? '20 Years (Default / Unscored G4)' : 'Unassigned');

      const hasG5 = c.g5_mgmt !== null && c.g5_mgmt !== undefined && c.g5_mgmt !== '';
      const hasG6 = c.g6_cash !== null && c.g6_cash !== undefined && c.g6_cash !== '';
      const g56Row = document.getElementById('dossier-g56-row');
      if (g56Row) {{
        if (hasG5 || hasG6) {{
          const g5El = document.getElementById('dossier-g5-mgmt');
          const g5Num = hasG5 ? Number(c.g5_mgmt) : null;
          if (g5Num === 2) {{
            g5El.textContent = 'Elite Compounder';
            g5El.style.color = 'var(--green)';
          }} else if (g5Num === 1) {{
            g5El.textContent = 'Standard Pass';
            g5El.style.color = 'var(--text-main)';
          }} else if (g5Num === 0) {{
            g5El.textContent = 'Red Flag';
            g5El.style.color = 'var(--red)';
          }} else {{
            g5El.textContent = '-';
            g5El.style.color = 'var(--text-main)';
          }}

          const g6El = document.getElementById('dossier-g6-cash');
          if (c.g6_cash === 'Y') {{
            g6El.textContent = 'Pass';
            g6El.style.color = 'var(--green)';
          }} else if (c.g6_cash === 'N') {{
            g6El.textContent = 'Fail';
            g6El.style.color = 'var(--red)';
          }} else {{
            g6El.textContent = '-';
            g6El.style.color = 'var(--text-main)';
          }}
          g56Row.style.display = 'grid';
        }} else {{
          g56Row.style.display = 'none';
        }}
      }}

      const capCardBox = document.getElementById('dossier-cap-scorecard');
      const capCardHtml = renderCapBreakdownHtml(c);
      if (capCardHtml) {{
        document.getElementById('dossier-cap-scorecard-body').innerHTML = capCardHtml;
        capCardBox.style.display = 'block';
      }} else {{
        capCardBox.style.display = 'none';
      }}

      // Moat Note
      const mnBox = document.getElementById('dossier-moat-note-box');
      if (c.g3m_moat_note) {{
        document.getElementById('dossier-moat-note').textContent = c.g3m_moat_note;
        mnBox.style.display = 'block';
      }} else {{
        mnBox.style.display = 'none';
      }}

      // Gate 4 Forces & Runway Note
      const g4nBox = document.getElementById('dossier-g4n-box');
      if (c.g4n_note) {{
        document.getElementById('dossier-g4n-note').textContent = c.g4n_note;
        g4nBox.style.display = 'block';
      }} else {{
        g4nBox.style.display = 'none';
      }}

      // General Note / Thesis
      const noteBox = document.getElementById('dossier-note-box');
      if (c.note) {{
        document.getElementById('dossier-note').textContent = c.note;
        noteBox.style.display = 'block';
      }} else {{
        noteBox.style.display = 'none';
      }}

      // Evidence
      const evBox = document.getElementById('dossier-evidence-box');
      if (c.evidence) {{
        document.getElementById('dossier-evidence').textContent = c.evidence;
        evBox.style.display = 'block';
      }} else {{
        evBox.style.display = 'none';
      }}

      // Gate 2 reason
      const g2rBox = document.getElementById('dossier-g2r-box');
      if (c.g2_reason) {{
        document.getElementById('dossier-g2r').textContent = c.g2_reason;
        g2rBox.style.display = 'block';
      }} else {{
        g2rBox.style.display = 'none';
      }}

      // Quantitative Metrics
      document.getElementById('dossier-price').textContent = fmtPrice(c.price, c.quote_currency);
      document.getElementById('dossier-par-val').textContent = fmtPrice(c.par_val, c.quote_currency);
      document.getElementById('dossier-vs-par').textContent = fmtPct(c.vs_par, true);
      const dTermValEl = document.getElementById('dossier-term-val');
      if (dTermValEl) dTermValEl.textContent = fmtPrice(c.term_val, c.quote_currency);
      const dVsTermEl = document.getElementById('dossier-vs-term');
      if (dVsTermEl) {{
        dVsTermEl.textContent = fmtPct(c.vs_term, true);
        dVsTermEl.style.color = (c.vs_term !== null && c.vs_term !== undefined)
          ? (c.vs_term <= 0 ? 'var(--green)' : 'var(--text-main)')
          : 'var(--text-main)';
      }}
      const dTermMultEl = document.getElementById('dossier-term-mult');
      if (dTermMultEl) dTermMultEl.textContent = (c.term_mult !== null && c.term_mult !== undefined) ? fmtNum(c.term_mult) + 'x' : '-';
      const curG = c.g_org_exp;
      const curFwd = (c.cur_mult !== null && c.cur_mult !== undefined && curG !== null && curG !== undefined && (1 + curG) > 0) ? c.cur_mult / (1 + curG) : null;
      document.getElementById('dossier-cur-mult').textContent = (c.cur_mult !== null && c.cur_mult !== undefined)
        ? (curFwd !== null ? `${{fmtNum(c.cur_mult, 1)}} / ${{fmtNum(curFwd, 1)}}x` : `${{fmtNum(c.cur_mult, 1)}}x`)
        : '-';
      document.getElementById('dossier-par-mult').textContent = fmtNum(c.par_mult) + 'x';
      document.getElementById('dossier-irr').textContent = fmtPct(c.irr_5y);
      const rTxt = (c.disc_rate !== null && c.disc_rate !== undefined) ? `r = ${{(c.disc_rate * 100).toFixed(2)}}%` : 'r';
      ['dossier-rate-title', 'dossier-rate-pe', 'dossier-rate-g'].forEach(id => {{ const el = document.getElementById(id); if (el) el.textContent = rTxt; }});

      const opRoicVal = (c.roic_operating !== null && c.roic_operating !== undefined) ? fmtPct(c.roic_operating) : fmtPct(c.roic_used);
      document.getElementById('dossier-roic-op').textContent = opRoicVal;
      document.getElementById('dossier-roic-gaap').textContent = fmtPct(c.roic_median);
      document.getElementById('dossier-fcf-conv').textContent = fmtPct(c.fcf_conv);
      const g6Ans = document.getElementById('dossier-g6-answer');
      if (g6Ans) g6Ans.textContent = c.g6_answer || c.g6_cash || 'blank';
      const g6Box = document.getElementById('dossier-g6-checks');
      if (g6Box) {{
        const chk = c.g6_checks || {{}};
        g6Box.innerHTML = ['netdebt', 'intcov', 'fcfconv', 'p2p'].map(k => {{
          const st = chk[k] || 'n/a';
          const col = st === 'ok' ? 'var(--green)' : (st === 'flag' ? 'var(--amber)' : 'var(--text-dim)');
          const sym = st === 'ok' ? '✓' : (st === 'flag' ? '⚠' : '–');
          return `<div><span style="color: ${{col}};">${{sym}}</span> ${{G6_LABELS[k]}}: <b>${{escHtml(g6Detail(c, k))}}</b>${{st === 'info' ? ' <span style="color: var(--text-dim);">(info)</span>' : ''}}</div>`;
        }}).join('');
      }}

      const gOrgDisp = fmtPct(c.g_org_exp !== null && c.g_org_exp !== undefined ? c.g_org_exp : c.g_start);
      const gExpDisp = fmtPct(c.g_exp);
      document.getElementById('dossier-g-imp').textContent = (c.g_exp !== c.g_org_exp && c.g_exp !== null) ? `${{gOrgDisp}} → ${{gExpDisp}}` : gOrgDisp;
      const scaleEl = document.getElementById('dossier-scale-tier');
      if (scaleEl) {{
        const parts = [];
        if (c.sales_1y !== null && c.sales_1y !== undefined) parts.push(`1Y ${{fmtPct(c.sales_1y, true)}}`);
        if (c.sales_cagr !== null && c.sales_cagr !== undefined) parts.push(`${{c.sales_cagr_yrs ? c.sales_cagr_yrs + 'Y' : '10Y'}} ${{fmtPct(c.sales_cagr)}}`);
        if (c.opcost_cagr !== null && c.opcost_cagr !== undefined) parts.push(`OpCost ${{fmtPct(c.opcost_cagr)}}`);
        if (c.buyback_yield !== null && c.buyback_yield !== undefined) parts.push(`BB ${{fmtPct(c.buyback_yield, true)}}`);
        scaleEl.textContent = parts.join(' · ');
      }}
      document.getElementById('dossier-g-market').textContent = fmtGMarket(c);
      const gMarginEl = document.getElementById('dossier-g-margin');
      gMarginEl.textContent = c.g_gap !== null && c.g_gap !== undefined ? fmtPct(c.g_gap, true) : '-';
      gMarginEl.style.color = (c.g_gap !== null && c.g_gap !== undefined) ? (c.g_gap >= 0 ? 'var(--green)' : 'var(--red)') : 'var(--text-main)';

      document.getElementById('dossier-cap-our').textContent = c.g4_cap ? `${{c.g4_cap}}y` : (hasMoatArchetype(c) ? '20y (Def)' : '-');
      document.getElementById('dossier-cap-implied').textContent = c.cap_implied !== null && c.cap_implied !== undefined ? `${{fmtNum(c.cap_implied, 1)}}y` : '-';
      const capMarginEl = document.getElementById('dossier-cap-margin');
      capMarginEl.textContent = fmtSignedYears(c.cap_gap);
      capMarginEl.style.color = (c.cap_gap !== null && c.cap_gap !== undefined) ? (c.cap_gap >= 0 ? 'var(--green)' : 'var(--red)') : 'var(--text-main)';

      // Fin note
      const fnBox = document.getElementById('dossier-fin-note-box');
      if (c.fin_note) {{
        document.getElementById('dossier-fin-note').textContent = c.fin_note;
        fnBox.style.display = 'block';
      }} else {{
        fnBox.style.display = 'none';
      }}

      // Show drawer
      populateValuationAudit(c);
      initValuationSandbox(c);
      setDossierTab(currentDossierTab);
      const drawerBody = document.getElementById('dossier-content');
      if (drawerBody) drawerBody.scrollTop = 0;
      document.getElementById('drawer-overlay').classList.add('open');
      document.getElementById('dossier-drawer').classList.add('open');
    }}

    function closeDrawer() {{
      document.getElementById('drawer-overlay').classList.remove('open');
      document.getElementById('dossier-drawer').classList.remove('open');
      selectedCompanyId = null;
      document.querySelectorAll('tbody tr').forEach(tr => tr.classList.remove('selected'));
      document.querySelectorAll('.company-card').forEach(card => card.classList.remove('selected'));
    }}

    // --- 2nd Tab: Valuation Engine Audit & Sandbox Logic ---
    let currentDossierTab = 'overview';
    let sbBaseline = {{}};
    let sbCurrent = {{}};

    function setDossierTab(tab) {{
      currentDossierTab = tab;
      document.querySelectorAll('.dossier-tab-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.id === `tab-btn-dossier-${{tab}}`);
      }});
      document.querySelectorAll('.dossier-tab-pane').forEach(pane => {{
        pane.classList.toggle('active', pane.id === `pane-dossier-${{tab}}`);
      }});
    }}

    function populateValuationAudit(c) {{
      const P = parParams(c);
      const k = (c.disc_rate !== null && c.disc_rate !== undefined) ? c.disc_rate : (c.bs_fin ? P.k_fin : P.k);
      // 1. OUR CAP & discount rate
      const hasAssignedCap = c.g4_cap !== null && c.g4_cap !== undefined && c.g4_cap !== '';
      const hasDefCap = !hasAssignedCap && hasMoatArchetype(c);
      document.getElementById('audit-cap-summary').textContent = hasAssignedCap ? `${{c.g4_cap}}y Runway${{c.cap_audited ? ' (Audited)' : ''}}` : (hasDefCap ? '20y Runway (Default)' : 'Unassigned');
      document.getElementById('audit-cap-years').textContent = hasAssignedCap ? `${{c.g4_cap}} Years` : (hasDefCap ? '20 Years (Unscored G4)' : 'None');
      const capTierText = c.g4_cap >= 30 ? 'Fortress (30y)' : (c.g4_cap >= 25 ? 'Elite Compounder (25y)' : (c.g4_cap >= 20 ? 'Compounder (20y)' : (c.g4_cap >= 15 ? 'Standard Pass (15y)' : (hasAssignedCap ? 'Rejected (<15y)' : (hasDefCap ? 'Default Moat (20y)' : 'Unassigned')))));
      document.getElementById('audit-cap-tier').textContent = capTierText;
      document.getElementById('audit-cap-rate').textContent = `${{(k * 100).toFixed(2)}}%`;
      document.getElementById('audit-cap-rate-sub').textContent = c.bs_fin ? 'Balance-Sheet Financial (r_fin)' : 'Operating Company / Fee Financial';
      document.getElementById('audit-cap-market').textContent = (c.cap_implied !== null && c.cap_implied !== undefined) ? `${{fmtNum(c.cap_implied, 1)}}y` : '-';
      document.getElementById('audit-cap-gap').textContent = (c.cap_gap !== null && c.cap_gap !== undefined) ? `${{fmtSignedYears(c.cap_gap)}} runway margin` : '-';
      document.getElementById('audit-moat-arch').textContent = c.g3a_moat_archetype || 'None';
      const pricingMap = {{
        'Y': 'Pass (≥ Inflation & ROIC ≥ 12%)',
        'N': 'Fail (< Inflation or Sub-Hurdle)',
        '2': 'High Pricing Power (Score 2)',
        '1': 'Moderate Pricing Power (Score 1)',
        '0': 'No Pricing Power (Score 0)'
      }};
      document.getElementById('audit-moat-pricing').textContent = pricingMap[c.g3b_pricing] || (c.g3b_pricing || 'Unassigned');
      const capDerivEl = document.getElementById('audit-cap-derivation');
      if (capDerivEl) {{
        const derivHtml = renderCapBreakdownHtml(c);
        capDerivEl.innerHTML = derivHtml || '<span style="font-size:11px; color:var(--text-dim);">Gate 3/4 CAP not yet assigned.</span>';
      }}

      // 2. GROWTH CEILING (g₀), PER-SHARE CEILING (g_exp) & MARGINAL RONIC
      document.getElementById('audit-gexp-summary').textContent = `${{fmtPct(c.g_org_exp)}} → ${{fmtPct(c.g_exp)}}`;
      document.getElementById('audit-sales1y-val').textContent = fmtPct(c.sales_1y, true);
      document.getElementById('audit-opcost1y-val').textContent = fmtPct(c.opcost_1y, true);
      document.getElementById('audit-bb-val').textContent = fmtPct(c.buyback_yield, true);
      const hasOc = c.opcost_cagr !== null && c.opcost_cagr !== undefined;
      const hasS = c.sales_cagr !== null && c.sales_cagr !== undefined;
      const wlsBase = hasS ? c.sales_cagr : (hasOc ? c.opcost_cagr : null);
      document.getElementById('audit-gdemand-val').textContent = wlsBase !== null ? fmtPct(wlsBase) : '-';
      document.getElementById('audit-salescagr-val').textContent = fmtPct(c.sales_cagr);
      document.getElementById('audit-salesyrs-val').textContent = c.sales_cagr_yrs ? `${{c.sales_cagr_yrs}}Y` : '5Y';
      document.getElementById('audit-opcostcagr-val').textContent = fmtPct(c.opcost_cagr);
      document.getElementById('audit-oecagr-val').textContent = fmtPct(c.cagr_oe_eps);
      document.getElementById('audit-roic-val').textContent = `${{fmtPct(c.roic_used)}} → ${{fmtPct(c.roic_exp)}}`;
      document.getElementById('audit-roictang-val').textContent = fmtPct(c.roic_operating);
      document.getElementById('audit-roicgaap-val').textContent = fmtPct(c.roic_median);
      document.getElementById('audit-mashare-val').textContent = (c.ma_reinvest !== null && c.ma_reinvest !== undefined)
        ? `${{fmtPct(c.ma_reinvest)}} of NOPAT → ${{c.ma_alpha ? fmtPct(c.ma_alpha) + ' of g₀ bought' : 'blend off'}}` : '-';
      document.getElementById('audit-retention-val').textContent = fmtPct(c.retention_rate);
      document.getElementById('audit-roic-note').innerHTML = c.ronic_le_r
        ? `<b style="color: var(--amber);">⚠ RONIC₀ ${{fmtPct(c.roic_exp)}} ≤ r ${{(k * 100).toFixed(2)}}%: growth adds no value, so Fair P/E ≤ 1/r. Review the capital base (goodwill, minorities) against the moat gates.</b>`
        : 'RONIC fades linearly across CAP from RONIC₀ to min(RONIC₀, 20%, r + 0.5·(RONIC₀ − r)).';
      document.getElementById('audit-fade-val').textContent = fmtPct(c.g_org_exp);
      document.getElementById('audit-glog-val').textContent = fmtPct(c.g_exp);
      document.getElementById('audit-gformula').textContent = `Formula: g₀ = 4-Pillar Statistical Organic Growth (Dilution-Adjusted Cycle-Spanning Theil-Sen P25 + 3-Driver Triangulation + Empirical Bayes Shrinkage, 0%–${{fmtPct(P.g_anchor_max)}}) fades linearly to min(g₀, ${{fmtPct(P.g_base)}}) over CAP.`;

      // Binding / Dominant Driver Badge: name the term that actually sets g₀
      ['box-filter-supply', 'box-filter-demand', 'box-filter-fade', 'box-filter-gravity'].forEach(id => {{
        const el = document.getElementById(id); if (el) el.classList.remove('binding');
      }});
      const badge = document.getElementById('audit-binding-badge');
      const fadeTxt = `→ ${{fmtPct(Math.min(c.g_org_exp || 0, P.g_base))}} over CAP`;
      let bindTxt;
      if (c.g_org_exp !== null && c.g_org_exp >= P.g_anchor_max - 1e-6) {{
        bindTxt = `${{fmtPct(P.g_anchor_max)}} Ceiling binds`;
        document.getElementById('box-filter-gravity').classList.add('binding');
      }} else if (hasS) {{
        bindTxt = `Sales WLS g₀ ${{fmtPct(c.g_org_exp)}}`;
        document.getElementById('box-filter-demand').classList.add('binding');
      }} else if (hasOc) {{
        bindTxt = `OpCost WLS g₀ ${{fmtPct(c.g_org_exp)}}`;
        document.getElementById('box-filter-demand').classList.add('binding');
      }} else {{
        bindTxt = `Fallback g₀ ${{fmtPct(c.g_org_exp)}}`;
        document.getElementById('box-filter-gravity').classList.add('binding');
      }}
      badge.textContent = `${{bindTxt}} ${{fadeTxt}}`;
      badge.className = 'binding-badge active-constraint';

      // 3. Explicit Mauboussin-Fade DCF Fair Multiple
      document.getElementById('audit-dcf-rate').textContent = `r = ${{(k * 100).toFixed(2)}}%`;
      document.getElementById('audit-tgrowth-sub').textContent = `Years 1..N FCF @ r=${{(k * 100).toFixed(2)}}%`;
      document.getElementById('audit-parmult-summary').textContent = `${{fmtNum(c.par_mult)}}x`;
      document.getElementById('audit-tgrowth-val').textContent = (c.pe_mm !== null && c.pe_mm !== undefined) ? `${{fmtNum(c.pe_mm)}}x` : '-';
      document.getElementById('audit-troic-val').textContent = (c.pe_mck !== null && c.pe_mck !== undefined) ? `${{fmtNum(c.pe_mck)}}x` : '-';
      document.getElementById('audit-rawpar-val').textContent = (c.pe_vd !== null && c.pe_vd !== undefined) ? `${{fmtNum(c.pe_vd)}}x` : '-';
      const auditTermMultEl = document.getElementById('audit-termmult-val');
      if (auditTermMultEl) auditTermMultEl.textContent = (c.term_mult !== null && c.term_mult !== undefined) ? `${{fmtNum(c.term_mult)}}x` : '-';
      const auditTermValEl = document.getElementById('audit-termval-val');
      if (auditTermValEl) auditTermValEl.textContent = fmtPrice(c.term_val, c.quote_currency);
      document.getElementById('audit-reinv-val').textContent = (c.reinv_eff !== null && c.reinv_eff !== undefined) ? `${{Math.round(c.reinv_eff * 100)}}%` : '-';
      const hasHistRange = (c.mult_low_5y !== null && c.mult_low_5y !== undefined && c.mult_high_5y !== null && c.mult_high_5y !== undefined);
      document.getElementById('audit-mh-val').textContent = hasHistRange ? `${{fmtNum(c.mult_low_5y)}}x–${{fmtNum(c.mult_high_5y)}}x` : 'N/A (<12m trading)';
      document.getElementById('audit-peakeps-val').textContent = fmtPrice(c.peak_eps, c.quote_currency)
        + ((c.peak_weight !== null && c.peak_weight !== undefined)
          ? ` (${{(c.peak_weight * 100).toFixed(0)}}% weight on the FY${{c.peak_oe_year ?? '?'}} peak)` : '');
    }}

    const SB_STEP_SNAP = (v) => Math.round(v * 2) / 2;      // sliders use step="0.5"
    const PEAK_EPS_TOL = 1e-4;

    function initValuationSandbox(c) {{
      if (!c) return;

      const cap = (c.g4_cap !== null && c.g4_cap !== undefined) ? c.g4_cap : null;

      // Growth slider = sales WLS CAGR (moving it shifts sales, OpCost and Owner EPS growth by the same delta)
      const baseGrowth = (c.sales_cagr !== null && c.sales_cagr !== undefined) ? c.sales_cagr
        : ((c.cagr_oe_eps !== null && c.cagr_oe_eps !== undefined) ? c.cagr_oe_eps
        : ((c.sales_1y !== null && c.sales_1y !== undefined) ? c.sales_1y
        : ((c.g_org_exp !== null && c.g_org_exp !== undefined) ? c.g_org_exp : 0.08)));
      const salescagr = baseGrowth * 100;
      // RONIC slider starts at the RONIC₀ the DCF actually uses (after M&A blend and cap); moving it sets RONIC₀
      // directly (Python par_valuation scenario["ronic0"], a what-if only) so touching it never jumps.
      const roic = (c.roic_exp !== null && c.roic_exp !== undefined) ? (c.roic_exp * 100)
        : ((c.roic_used !== null && c.roic_used !== undefined) ? (c.roic_used * 100) : 18.0);
      const peakeps = (c.peak_eps !== null && c.peak_eps !== undefined && c.peak_eps > 0) ? c.peak_eps : null;
      const gest = null;   // what-if growth input starts empty (no analyst overrides)

      sbBaseline = {{ cap, salescagr, salescagrSnap: SB_STEP_SNAP(salescagr), roic, roicSnap: SB_STEP_SNAP(roic), peakeps, gest }};
      sbCurrent = {{ cap, salescagr: sbBaseline.salescagrSnap, roic: sbBaseline.roicSnap, peakeps, gest }};

      syncSandboxInputs();
      recalcSandboxValuation();
    }}

    function syncSandboxInputs() {{
      const c = SCREENER_DATA.companies.find(item => item.id === selectedCompanyId) || {{}};

      document.querySelectorAll('.cap-pill-btn').forEach(btn => {{
        btn.classList.toggle('active', sbCurrent.cap !== null && parseInt(btn.dataset.cap, 10) === sbCurrent.cap);
      }});
      const capEl = document.getElementById('sb-val-cap');
      if (capEl) capEl.textContent = sbCurrent.cap !== null ? `${{sbCurrent.cap}}y` : 'Unassigned (20y default)';

      // Sliders with dynamic min/max adjustment to avoid clipping outliers
      const sCagr = document.getElementById('sb-slider-salescagr');
      if (sCagr) {{
        sCagr.min = Math.min(-20, Math.floor(sbCurrent.salescagr - 5));
        sCagr.max = Math.max(40, Math.ceil(sbCurrent.salescagr + 5));
        sCagr.value = sbCurrent.salescagr;
        document.getElementById('sb-val-salescagr').textContent = `${{sbCurrent.salescagr.toFixed(1)}}%`;
      }}
      const sRoic = document.getElementById('sb-slider-roic');
      if (sRoic) {{
        sRoic.min = Math.min(5, Math.floor(sbCurrent.roic - 5));
        sRoic.max = Math.max(150, Math.ceil(sbCurrent.roic + 10));
        sRoic.value = sbCurrent.roic;
        document.getElementById('sb-val-roic').textContent = `${{sbCurrent.roic.toFixed(1)}}%`;
      }}
      const lblRoicText = document.getElementById('sb-label-roic-text');
      if (lblRoicText) {{
        lblRoicText.textContent = `RONIC₀ (${{c.uses_gaap_roic ? (c.bs_fin ? 'ROE' : (c.roic_source === 'roe_median' ? 'ROE — invested capital ≤ 0' : 'GAAP ROIC')) : 'Tangible ROIC'}}, M&A-matched, capped)`;
      }}

      const inPeak = document.getElementById('sb-input-peakeps');
      if (inPeak) inPeak.value = (sbCurrent.peakeps !== null && sbCurrent.peakeps !== undefined) ? sbCurrent.peakeps.toFixed(2) : '';
      const valPeakEl = document.getElementById('sb-val-peakeps');
      if (valPeakEl) valPeakEl.textContent = (sbCurrent.peakeps !== null && sbCurrent.peakeps !== undefined) ? fmtPrice(sbCurrent.peakeps, c.quote_currency) : '-';

      const inGest = document.getElementById('sb-input-gest');
      if (inGest) inGest.value = (sbCurrent.gest !== null && sbCurrent.gest !== undefined) ? sbCurrent.gest.toFixed(1) : '';
      const valGestEl = document.getElementById('sb-val-gest');
      if (valGestEl) valGestEl.textContent = (sbCurrent.gest !== null && sbCurrent.gest !== undefined) ? `${{sbCurrent.gest.toFixed(1)}}%` : 'None';
    }}

    function setSandboxCap(cap) {{
      sbCurrent.cap = cap;
      document.querySelectorAll('.cap-pill-btn').forEach(btn => {{
        btn.classList.toggle('active', parseInt(btn.dataset.cap, 10) === cap);
      }});
      const capEl = document.getElementById('sb-val-cap');
      if (capEl) capEl.textContent = `${{cap}}y`;
      recalcSandboxValuation();
    }}

    function onSandboxSliderChange(key, val, unit) {{
      const num = parseFloat(val);
      sbCurrent[key] = num;
      const labelEl = document.getElementById(`sb-val-${{key}}`);
      if (labelEl) labelEl.textContent = num.toFixed(1) + (unit || '');
      recalcSandboxValuation();
    }}

    function onSandboxPeakChange() {{
      const c = SCREENER_DATA.companies.find(item => item.id === selectedCompanyId) || {{}};
      const peInputEl = document.getElementById('sb-input-peakeps');
      const pe = parseFloat(peInputEl ? peInputEl.value.trim() : '');
      sbCurrent.peakeps = (!isNaN(pe) && pe > 0) ? pe : null;
      const valPeakEl = document.getElementById('sb-val-peakeps');
      if (valPeakEl) valPeakEl.textContent = (sbCurrent.peakeps !== null) ? fmtPrice(sbCurrent.peakeps, c.quote_currency) : '-';
      recalcSandboxValuation();
    }}

    function onSandboxGestChange() {{
      const gestVal = document.getElementById('sb-input-gest').value.trim();
      const parsedG = parseFloat(gestVal);
      sbCurrent.gest = (gestVal === '' || isNaN(parsedG)) ? null : parsedG;
      document.getElementById('sb-val-gest').textContent = sbCurrent.gest !== null ? `${{sbCurrent.gest.toFixed(1)}}%` : 'None';
      recalcSandboxValuation();
    }}

    function clearSandboxGest() {{
      const inGest = document.getElementById('sb-input-gest');
      if (inGest) inGest.value = '';
      sbCurrent.gest = null;
      document.getElementById('sb-val-gest').textContent = 'None';
      recalcSandboxValuation();
    }}

    function resetSandboxValuation() {{
      sbCurrent = {{ cap: sbBaseline.cap, salescagr: sbBaseline.salescagrSnap, roic: sbBaseline.roicSnap, peakeps: sbBaseline.peakeps, gest: sbBaseline.gest }};
      syncSandboxInputs();
      recalcSandboxValuation();
    }}

    function sandboxTweaks() {{
      const peakEdited = sbCurrent.peakeps !== null && sbCurrent.peakeps !== undefined &&
        (sbBaseline.peakeps === null || Math.abs(sbCurrent.peakeps - sbBaseline.peakeps) > PEAK_EPS_TOL);
      return {{
        growth: Math.abs(sbCurrent.salescagr - sbBaseline.salescagrSnap) > 0.01,
        roic: Math.abs(sbCurrent.roic - sbBaseline.roicSnap) > 0.01,
        gest: sbCurrent.gest !== sbBaseline.gest,
        peak: peakEdited,
        cap: sbCurrent.cap !== sbBaseline.cap
      }};
    }}

    function explicitDcfMultiple(g0, roic0, nCap, k=0.085, gTerm=0.030, isFiniteConc=false, roicEndOverride=null, roicTermMax=0.20) {{
      // Mirrors screener/gates.py dcf_schedule_and_continuation: Year-1 E_1 = 1.0 is the trailing normalized EPS;
      // at each year t = 1..N, Reinv_t = E_t * max(0, g_t) / RONIC_t funds E_(t+1) = E_t * (1 + g_t);
      // TV_N = E_(N+1) * (1 - g_tv / RONIC_term) / (r - g_tv) with g_tv = max(0, min(g0, gTerm)).
      const nSteps = Math.max(1, Math.round(nCap));
      const roicStart = Math.max(0.05, roic0);
      const roicTerm = (roicEndOverride !== null && roicEndOverride !== undefined)
        ? Math.max(0.05, roicEndOverride)
        : Math.max(0.05, Math.min(roicStart, roicTermMax, k + 0.5 * (roicStart - k)));
      const gTermEff = Math.min(g0, gTerm);
      let pvStage1 = 0.0;
      let sumFcf1 = 0.0;
      let earn = 1.0;
      const rows = [];
      const fcfs = [];
      for (let t = 1; t <= nSteps; t++) {{
        const frac = nSteps > 1 ? (t - 1.0) / Math.max(1, nSteps - 1) : 1.0;
        const gT = g0 - frac * (g0 - gTermEff);
        const roicT = Math.max(0.05, roicStart - frac * (roicStart - roicTerm));
        const reinvT = Math.max(0.0, gT) / roicT;
        const fcfT = earn * (1.0 - reinvT);
        fcfs.push(fcfT);
        const dfT = 1.0 / Math.pow(1.0 + k, t);
        const pvT = fcfT * dfT;
        sumFcf1 += fcfT;
        pvStage1 += pvT;
        rows.push({{
          t,
          gT,
          roicT,
          reinvT,
          earnT: earn,
          fcfT,
          dfT,
          pvT,
          cumPv: pvStage1
        }});
        earn = earn * (1.0 + gT);
      }}
      let pvStage2 = 0.0;
      const gTv = Math.max(0.0, gTermEff);
      const earnTerm = earn;
      const reinvTerm = gTv / Math.max(0.05, roicTerm);
      const fcfTerm = earnTerm * (1.0 - reinvTerm);
      const dfTerm = 1.0 / Math.pow(1.0 + k, nSteps);
      let termVal = 0.0;
      if (!isFiniteConc) {{
        termVal = fcfTerm / Math.max(0.01, k - gTv);
        pvStage2 = termVal * dfTerm;
      }}
      const total = pvStage1 + pvStage2;
      const fcfs5 = fcfs.concat([fcfTerm, fcfTerm, fcfTerm, fcfTerm, fcfTerm]).slice(0, 5);
      const m5 = Math.min(5, nSteps);
      let pvFirst5 = 0.0;
      for (let t = 0; t < m5; t++) {{
        pvFirst5 += fcfs[t] / Math.pow(1.0 + k, t + 1);
      }}
      const v5 = Math.max(0.0, (total - pvFirst5) * Math.pow(1.0 + k, m5));
      return {{
        pvStage1,
        pvStage2,
        total,
        sumFcf1,
        roicStart,
        roicTerm,
        nSteps,
        rows,
        fcfs5,
        v5,
        terminal: {{
          gTerm: gTv,
          roicTerm,
          reinvTerm,
          earnTerm,
          fcfTerm,
          termVal,
          dfTerm,
          pvStage2,
          cumPv: total
        }}
      }};
    }}

    function terminalMultiple(roic0, k=0.085, gTerm=0.030, isFiniteConc=false, roicEndOverride=null, roicTermMax=0.20) {{
      // Mirrors screener/gates.py terminal_multiple: standalone McKinsey Value-Driver Terminal P/E at 3.0% historical
      // inflation pass-through and 'keeping the lights on' reinvestment (gTerm / roicTerm).
      if (isFiniteConc) return 0.0;
      const roicStart = Math.max(0.05, roic0);
      const roicTerm = (roicEndOverride !== null && roicEndOverride !== undefined)
        ? Math.max(0.05, roicEndOverride)
        : Math.max(0.05, Math.min(roicStart, roicTermMax, k + 0.5 * (roicStart - k)));
      if (roicTerm <= k) return 1.0 / k;
      const gInf = Math.max(0.0, gTerm);
      return (1.0 - gInf / roicTerm) / Math.max(0.01, k - gInf);
    }}

    function renderDcfScheduleTable(c, opts) {{
      const tbody = document.getElementById('dcf-schedule-tbody');
      if (!tbody) return;
      const ccy = c.quote_currency || '';
      const price = c.price;
      const e0 = opts.peak_eps;
      const g0 = opts.g_org_val;
      const roic0 = opts.roic_eff;
      const nCap = opts.n_cap;
      const k = opts.k;
      const gTerm = opts.g_base;
      const isFiniteConc = opts.isFiniteConc;
      const isMtmHoldco = opts.isMtmHoldco;
      const isTweaked = opts.isTweaked;
      const hasInputs = opts.hasValuationInputs;

      const modeBadge = document.getElementById('dcf-tab-mode-badge');
      const resetBtn = document.getElementById('dcf-tab-reset-btn');
      if (modeBadge) {{
        if (isTweaked) {{
          modeBadge.textContent = 'Sandbox Scenario Active';
          modeBadge.className = 'binding-badge active-constraint';
          if (resetBtn) resetBtn.style.display = 'inline-flex';
        }} else {{
          modeBadge.textContent = 'Baseline DCF';
          modeBadge.className = 'binding-badge';
          if (resetBtn) resetBtn.style.display = 'none';
        }}
      }}

      if (!hasInputs || !e0 || e0 <= 0) {{
        document.getElementById('dcf-sum-e0').textContent = '-';
        document.getElementById('dcf-sum-price').textContent = `Cur Price: ${{fmtPrice(price, ccy)}}`;
        document.getElementById('dcf-sum-gfade').textContent = '-';
        document.getElementById('dcf-sum-cap').textContent = 'CAP Unassigned';
        document.getElementById('dcf-sum-rfade').textContent = '-';
        document.getElementById('dcf-sum-disc').textContent = '-';
        document.getElementById('dcf-sum-fv').textContent = 'No Data';
        document.getElementById('dcf-sum-split').textContent = '-';
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 24px; color: var(--text-dim);">Explicit DCF schedule unavailable (missing Peak Owner EPS / valuation inputs, or an [auto] data check — stale fundamentals, share count changed since FY, currency switch unresolved, earnings dominated by non-cash marks — awaiting a refetch / review).</td></tr>`;
        return;
      }}

      const dcf = explicitDcfMultiple(g0, roic0, nCap, k, gTerm, isFiniteConc, null, opts.roic_term_max);
      const navMult = (opts.navMult !== null && opts.navMult !== undefined) ? opts.navMult : (1.0 / roic0);
      const effMult = isMtmHoldco ? navMult : dcf.total;
      const effFv = effMult * e0;
      const pv1Dollar = dcf.pvStage1 * e0;
      const pv2Dollar = dcf.pvStage2 * e0;
      const totalScheduleDollar = dcf.total * e0;
      const s1Share = dcf.total > 0 ? (dcf.pvStage1 / dcf.total) : 1.0;
      const s2Share = dcf.total > 0 ? (dcf.pvStage2 / dcf.total) : 0.0;

      // Populate Top Summary Strip
      const re0 = Math.max(0.0, g0) / dcf.roicStart;
      const fcf0 = e0 * (1.0 - re0);
      document.getElementById('dcf-sum-e0').textContent = fmtPrice(e0, ccy);
      document.getElementById('dcf-sum-price').textContent = `Cur Price: ${{fmtPrice(price, ccy)}} (${{price && e0 ? fmtNum(price / e0) + 'x' : '-'}})`;
      document.getElementById('dcf-sum-gfade').textContent = `${{fmtPct(g0)}} → ${{fmtPct(dcf.terminal.gTerm)}}`;
      document.getElementById('dcf-sum-cap').textContent = `Linear Fade Over N = ${{dcf.nSteps}} CAP Yrs`;
      document.getElementById('dcf-sum-rfade').textContent = `${{fmtPct(dcf.roicStart)}} → ${{fmtPct(dcf.roicTerm)}}`;
      document.getElementById('dcf-sum-disc').textContent = `Discount Rate r = ${{(k * 100).toFixed(2)}}%`;
      document.getElementById('dcf-sum-fv').textContent = `${{fmtPrice(effFv, ccy)}} (${{fmtNum(effMult)}}x)`;
      document.getElementById('dcf-sum-split').textContent = isMtmHoldco
        ? `MTM HoldCo NAV Anchor: 1.0x Book Value / Share = ${{fmtNum(effMult)}}x Peak EPS`
        : `Stage 1: ${{Math.round(s1Share * 100)}}% (${{fmtNum(dcf.pvStage1)}}x) · TV: ${{Math.round(s2Share * 100)}}% (${{fmtNum(dcf.pvStage2)}}x)`;

      const noteEl = document.getElementById('dcf-special-note');
      if (noteEl) {{
        if (isMtmHoldco) {{
          noteEl.style.display = 'block';
          noteEl.innerHTML = `<strong>ℹ️ Mark-to-Market HoldCo / Insurer NAV Rule:</strong> Because reported GAAP EPS already includes unrealized mark-to-market portfolio gains (&Delta;NAV), intrinsic Fair Value is anchored at <b>1.0x NAV = Book Value / Share = ${{fmtPrice(effFv, ccy)}} (${{fmtNum(effMult)}}x Peak EPS)</b>. The table below displays the illustrative operating cash-flow fade schedule at r = ${{(k * 100).toFixed(2)}}%.`;
        }} else if (effFv <= 0) {{
          noteEl.style.display = 'block';
          noteEl.innerHTML = `<strong>⚠ No positive DCF value:</strong> reinvestment g₀ / RONIC₀ = ${{fmtPct(re0)}} of earnings exceeds what the business earns on new capital, so the present value of owner cash flows is ${{fmtNum(effMult)}}x — status <b>No value</b> (no discount or IRR).`;
        }} else if (isFiniteConc) {{
          noteEl.style.display = 'block';
          noteEl.innerHTML = `<strong>ℹ️ Expiring Concession (opt-in):</strong> Concession assets revert to the grantor at expiry, so Stage 2 Terminal Value is <b>0.00</b> and Fair Value is 100% Stage 1 CAP cash flows over N = ${{dcf.nSteps}} years.`;
        }} else {{
          noteEl.style.display = 'none';
        }}
      }}

      const htmlRows = [];

      // Base Row (Year 0)
      htmlRows.push(`<tr class="dcf-row-base">
        <td><b>Year 0 (Base)</b><span class="dcf-sub">Trailing normalized EPS = Year-1 E₁</span></td>
        <td>${{fmtPct(g0)}}<span class="dcf-sub">Initial Ceiling g₀</span></td>
        <td>${{fmtPct(dcf.roicStart)}}<span class="dcf-sub">Reinv ${{Math.round(re0 * 100)}}%</span></td>
        <td>${{fmtPrice(e0, ccy)}}<span class="dcf-sub">1.00x E₀</span></td>
        <td>${{fmtPrice(fcf0, ccy)}}<span class="dcf-sub">Payout ${{Math.round((1.0 - re0) * 100)}}%</span></td>
        <td>${{(k * 100).toFixed(2)}}%<span class="dcf-sub">DF 1.000x</span></td>
        <td>-<span class="dcf-sub">Base Period</span></td>
        <td>-<span class="dcf-sub">0.00x P/E</span></td>
      </tr>`);

      // Year 1 .. N Rows
      dcf.rows.forEach(r => {{
        const earnDollar = r.earnT * e0;
        const fcfDollar = r.fcfT * e0;
        const pvDollar = r.pvT * e0;
        const cumDollar = r.cumPv * e0;
        const pvSharePct = dcf.total > 0 ? (r.pvT / dcf.total) * 100 : 0;
        htmlRows.push(`<tr>
          <td><b>Year ${{r.t}}</b><span class="dcf-sub">CAP Yr ${{r.t}} / ${{dcf.nSteps}}</span></td>
          <td style="color: var(--accent); font-weight: 600;">${{fmtPct(r.gT)}}</td>
          <td>${{fmtPct(r.roicT)}}<span class="dcf-sub">Reinv ${{(r.reinvT * 100).toFixed(1)}}%</span></td>
          <td>${{fmtPrice(earnDollar, ccy)}}<span class="dcf-sub">${{r.earnT.toFixed(2)}}x E₀</span></td>
          <td style="font-weight: 600;">${{fmtPrice(fcfDollar, ccy)}}<span class="dcf-sub">${{r.fcfT.toFixed(2)}}x E₀</span></td>
          <td>${{(k * 100).toFixed(2)}}%<span class="dcf-sub">DF ${{r.dfT.toFixed(3)}}x</span></td>
          <td>${{fmtPrice(pvDollar, ccy)}}<span class="dcf-sub">${{r.pvT.toFixed(2)}}x (${{pvSharePct.toFixed(1)}}%)</span></td>
          <td style="font-weight: 600;">${{fmtPrice(cumDollar, ccy)}}<span class="dcf-sub">${{r.cumPv.toFixed(2)}}x P/E</span></td>
        </tr>`);
      }});

      // Stage 1 Subtotal Row
      htmlRows.push(`<tr class="dcf-row-subtotal">
        <td>Stage 1 Subtotal (Yrs 1–${{dcf.nSteps}})<span class="dcf-sub">Explicit CAP Runway</span></td>
        <td>${{fmtPct(g0)}} → ${{fmtPct(dcf.rows[dcf.rows.length - 1].gT)}}</td>
        <td>${{fmtPct(dcf.roicStart)}} → ${{fmtPct(dcf.roicTerm)}}</td>
        <td>-</td>
        <td>${{fmtPrice(dcf.sumFcf1 * e0, ccy)}}<span class="dcf-sub">&Sigma; Undiscounted FCF</span></td>
        <td>${{(k * 100).toFixed(2)}}%</td>
        <td>${{fmtPrice(pv1Dollar, ccy)}}<span class="dcf-sub">${{dcf.pvStage1.toFixed(2)}}x (${{(s1Share * 100).toFixed(1)}}%)</span></td>
        <td>${{fmtPrice(pv1Dollar, ccy)}}<span class="dcf-sub">${{dcf.pvStage1.toFixed(2)}}x P/E</span></td>
      </tr>`);

      // Stage 2 Terminal Value Row
      const tv = dcf.terminal;
      const earnTermDollar = tv.earnTerm * e0;
      const fcfTermDollar = tv.fcfTerm * e0;
      const tvUndiscDollar = tv.termVal * e0;
      htmlRows.push(`<tr class="dcf-row-terminal">
        <td>Terminal Value (Yr ${{dcf.nSteps + 1}}+ Perpetuity)<span class="dcf-sub">${{isFiniteConc ? 'Concession Expiry (No TV)' : 'FCF / (r − g_tv) Value Driver'}}</span></td>
        <td>${{fmtPct(tv.gTerm)}}<span class="dcf-sub">Inflation Pass-Through</span></td>
        <td>${{fmtPct(tv.roicTerm)}}<span class="dcf-sub">Reinv ${{(tv.reinvTerm * 100).toFixed(1)}}%</span></td>
        <td>${{fmtPrice(earnTermDollar, ccy)}}<span class="dcf-sub">Yr ${{dcf.nSteps + 1}} EPS</span></td>
        <td>${{isFiniteConc ? fmtPrice(0, ccy) : fmtPrice(tvUndiscDollar, ccy)}}<span class="dcf-sub">${{isFiniteConc ? 'Expiry' : 'Yr ' + (dcf.nSteps + 1) + ' FCF: ' + fmtPrice(fcfTermDollar, ccy)}}</span></td>
        <td>${{(k * 100).toFixed(2)}}%<span class="dcf-sub">DF ${{tv.dfTerm.toFixed(3)}}x</span></td>
        <td>${{fmtPrice(pv2Dollar, ccy)}}<span class="dcf-sub">${{dcf.pvStage2.toFixed(2)}}x (${{(s2Share * 100).toFixed(1)}}%)</span></td>
        <td>${{fmtPrice(totalScheduleDollar, ccy)}}<span class="dcf-sub">${{dcf.total.toFixed(2)}}x P/E</span></td>
      </tr>`);

      // Total Intrinsic Fair Value Footer Row
      const vsPct = (price && effFv > 0) ? (price / effFv - 1.0) : null;
      htmlRows.push(`<tr class="dcf-row-total">
        <td>Total Intrinsic DCF Fair Value<span class="dcf-sub">${{vsPct !== null ? 'Cur Price ' + fmtPrice(price, ccy) + ' (' + fmtPct(vsPct, true) + ' vs FV)' : ''}}</span></td>
        <td>${{fmtPct(g0)}} → ${{fmtPct(tv.gTerm)}}</td>
        <td>${{fmtPct(dcf.roicStart)}} → ${{fmtPct(tv.roicTerm)}}</td>
        <td>${{fmtPrice(e0, ccy)}}<span class="dcf-sub">Base E₀</span></td>
        <td>${{fmtPrice((dcf.sumFcf1 + tv.termVal) * e0, ccy)}}<span class="dcf-sub">Total Undisc. Cash</span></td>
        <td>${{(k * 100).toFixed(2)}}%<span class="dcf-sub">Hurdle Rate r</span></td>
        <td>${{fmtPrice(effFv, ccy)}}<span class="dcf-sub">100.0% of Fair Value</span></td>
        <td>${{fmtPrice(effFv, ccy)}}<span class="dcf-sub">Fair P/E: ${{fmtNum(effMult)}}x</span></td>
      </tr>`);

      tbody.innerHTML = htmlRows.join('');
    }}

    function solveImpliedDcfGrowth(targetPe, roic0, nCap, k=0.085, gTerm=0.030, isFiniteConc=false, g0Ref=0.0, roicTermMax=0.20) {{
      // Mirrors screener/gates.py solve_market_growth: grid scan [-20%, +50%] in 1pp steps, bisection in
      // every sign-change bracket; returns {{ g, flag }} with flag in ok | saturated_low | saturated_high |
      // no_value_creation | multi_root.
      if (!targetPe || targetPe <= 0) return {{ g: null, flag: null }};
      const LO = -0.20, HI = 0.50, STEP = 0.01;
      const nPts = Math.round((HI - LO) / STEP);
      const pe = (g) => explicitDcfMultiple(g, roic0, nCap, k, gTerm, isFiniteConc, null, roicTermMax).total;
      const grid = [], pes = [];
      for (let i = 0; i <= nPts; i++) {{ const g = LO + i * STEP; grid.push(g); pes.push(pe(g)); }}
      let increasing = true;
      for (let i = 0; i < nPts; i++) {{ if (pes[i + 1] < pes[i] - 1e-9) {{ increasing = false; break; }} }}
      const roots = [];
      for (let i = 0; i < nPts; i++) {{
        const d0 = pes[i] - targetPe, d1 = pes[i + 1] - targetPe;
        if (d0 === 0) {{ roots.push(grid[i]); continue; }}
        if (d0 * d1 < 0) {{
          let lo = grid[i], hi = grid[i + 1], fLo = d0;
          for (let j = 0; j < 40; j++) {{
            const mid = 0.5 * (lo + hi);
            const fMid = pe(mid) - targetPe;
            if ((fMid < 0) === (fLo < 0)) {{ lo = mid; fLo = fMid; }} else {{ hi = mid; }}
          }}
          roots.push(0.5 * (lo + hi));
        }}
      }}
      if (pes[nPts] - targetPe === 0) roots.push(grid[nPts]);
      const r4 = (x) => Math.round(x * 10000) / 10000;
      const nearest = () => roots.length ? r4(roots.reduce((a, b) => Math.abs(b - g0Ref) < Math.abs(a - g0Ref) ? b : a)) : null;
      if (increasing) {{
        if (roots.length) return {{ g: r4(roots[0]), flag: 'ok' }};
        return targetPe < pes[0] ? {{ g: r4(LO), flag: 'saturated_low' }} : {{ g: r4(HI), flag: 'saturated_high' }};
      }}
      const i0 = Math.round(-LO / STEP), i10 = Math.round((0.10 - LO) / STEP);
      if (pes[i10] < pes[i0]) return {{ g: nearest(), flag: 'no_value_creation' }};
      return {{ g: nearest(), flag: 'multi_root' }};
    }}

    function solveDcfIrr5y(curPe, fcfs5, v5) {{
      // Mirrors screener/gates.py solve_irr_5y (Bellman-consistent DCF schedule, bisection on [-99%, +250%]):
      // Solves sum_{{t=1..5}} [FCF_t / (1 + IRR)^t] + [V_5 / (1 + IRR)^5] = Cur_PE via 60-step bisection.
      if (!curPe || curPe <= 0 || v5 === null || v5 === undefined || !fcfs5 || fcfs5.length < 5) return null;
      let sumCash = v5;
      for (let t = 0; t < 5; t++) sumCash += fcfs5[t];
      if (sumCash <= 0) return null;
      const npv = (rate) => {{
        const d = 1.0 + rate;
        if (d <= 1e-4) return 1e9;
        let pv = v5 / Math.pow(d, 5);
        for (let t = 0; t < 5; t++) pv += fcfs5[t] / Math.pow(d, t + 1);
        return pv - curPe;
      }};
      let lo = -0.99, hi = 2.50;
      const fLo = npv(lo), fHi = npv(hi);
      if (fLo * fHi > 0) return null;
      for (let i = 0; i < 60; i++) {{
        const mid = 0.5 * (lo + hi);
        if (npv(mid) > 0) lo = mid; else hi = mid;
      }}
      return 0.5 * (lo + hi);
    }}

    function irrColor(c, irr) {{
      // v7.7: relative to the company's own hurdle r (8.50% operating / 10.25% balance-sheet financials)
      if (irr === null || irr === undefined) return 'var(--text-muted)';
      const r = (c.disc_rate !== null && c.disc_rate !== undefined) ? c.disc_rate : 0.085;
      return irr >= r + 0.035 ? 'var(--green)' : (irr >= r ? 'var(--accent)' : 'var(--text-muted)');
    }}

    const G6_LABELS = {{ netdebt: 'Net debt ÷ owner earnings', intcov: 'Interest cover', fcfconv: 'Cash conversion', p2p: 'Peak-to-peak' }};
    function g6Detail(c, k) {{
      // Gate 6 rule check (screener/gates.py g6_checks): review flags only, the qualitative Gate 6 decides
      const v = k === 'netdebt' ? (c.g6_netdebt_yrs !== null && c.g6_netdebt_yrs !== undefined ? `${{fmtNum(c.g6_netdebt_yrs)}}y (≤ 4y)` : 'n/a')
        : k === 'intcov' ? (c.g6_intcov !== null && c.g6_intcov !== undefined ? `${{c.g6_intcov >= 99 ? 'no interest' : fmtNum(c.g6_intcov) + 'x'}} (> 5x)` : 'n/a')
        : k === 'fcfconv' ? (c.fcf_conv !== null && c.fcf_conv !== undefined ? `${{fmtPct(c.fcf_conv)}} (≥ 80%)` : 'n/a')
        : (c.p2p_ok === 'Y' ? 'new peak' : (c.p2p_ok === 'N' ? 'below prior peak' : 'n/a'));
      return v;
    }}
    function g6Markers(c) {{
      const chk = c.g6_checks || {{}};
      return ['netdebt', 'intcov', 'fcfconv', 'p2p'].map(k => {{
        const st = chk[k] || 'n/a';
        const sym = st === 'ok' ? '✓' : (st === 'flag' ? '⚠' : '–');
        const col = st === 'ok' ? 'var(--green)' : (st === 'flag' ? 'var(--amber)' : 'var(--text-dim)');
        return `<span title="${{G6_LABELS[k]}}: ${{escHtml(g6Detail(c, k))}}${{st === 'info' ? ' (informational for balance-sheet financials)' : ''}}" style="color: ${{col}}; margin-right: 3px;">${{sym}}</span>`;
      }}).join('');
    }}

    function ronic0(roicActive, rTang, rGaap, maReinvest, g0, gaapBasis) {{
      // Mirrors screener/gates.py ronic0: bought growth (M&A spend × GAAP ROIC) earns GAAP ROIC, the rest tangible ROIC
      const has = (v) => v !== null && v !== undefined;
      if (!gaapBasis && has(rTang) && has(rGaap) && rGaap > 0 && rTang > 1.25 * rGaap && maReinvest > 0 && g0 > 0) {{
        const w = Math.max(0.0, Math.min(1.0, maReinvest * rGaap / g0));
        return [1.0 / ((1.0 - w) / rTang + w / rGaap), w];
      }}
      return [roicActive, 0.0];
    }}

    function recalcSandboxValuation() {{
      // Mirrors screener/gates.py par_valuation (v7.1). With untouched inputs the Python baseline is reproduced exactly;
      // classification (balance-sheet financial, NAV HoldCo, opt-in finite concession, r) always comes from Python.
      const c = SCREENER_DATA.companies.find(item => item.id === selectedCompanyId);
      if (!c) return;
      const P = parParams(c);
      const r4 = (x) => Math.round(x * 10000) / 10000;
      const r1 = (x) => Math.round(x * 10) / 10;
      const has = (v) => v !== null && v !== undefined;

      const price = c.price;
      const peak_eps = sbCurrent.peakeps;
      const fund_cap = sbCurrent.cap;
      const g_base = P.g_base;
      const tw = sandboxTweaks();

      // Step 3 — organic growth ceiling g₀ and per-share ceiling g_exp
      const bb_eff = has(c.bb_eff) ? c.bb_eff : 0.0;
      const bb_pos = Math.max(0.0, bb_eff);
      const bb_org = Math.min(0.0, bb_eff);
      let g_org_exp = c.g_org_exp, g_exp = c.g_exp;
      if (tw.growth || tw.gest) {{
        const d = tw.growth ? (sbCurrent.salescagr - sbBaseline.salescagr) / 100.0 : 0.0;
        const hasSales = has(c.sales_cagr) || tw.growth;
        const s5 = tw.growth ? sbCurrent.salescagr / 100.0 : c.sales_cagr;
        const oc = has(c.opcost_cagr) ? c.opcost_cagr + d : null;
        const g_oe = has(c.cagr_oe_eps) ? c.cagr_oe_eps + d : null;
        const hasStmt = oc !== null || hasSales || has(c.sales_1y) || g_oe !== null;
        let raw_org;
        if (hasStmt) {{
          if (hasSales) raw_org = s5;
          else if (oc !== null) raw_org = oc;
          else raw_org = (g_oe !== null) ? g_oe - bb_pos : (c.sales_1y + bb_org);
        }} else {{
          raw_org = g_base;
        }}
        if (sbCurrent.gest !== null && !isNaN(sbCurrent.gest)) {{
          const g_est_val = sbCurrent.gest / 100.0;
          g_org_exp = r4(Math.max(0.0, Math.min(P.g_anchor_max, g_est_val - bb_pos)));
          g_exp = r4(Math.max(0.0, Math.min(P.g_anchor_max + bb_pos, g_est_val)));
        }} else {{
          g_org_exp = r4(Math.max(0.0, Math.min(P.g_anchor_max, raw_org)));
          g_exp = r4(g_org_exp + bb_pos);
        }}
      }}

      // Step 2 — RONIC₀: the slider sets it directly (scenario ronic0 in Python); a growth change re-weights the M&A blend
      let roic_exp = has(c.roic_exp) ? c.roic_exp : 0.18;
      if (tw.roic) {{
        roic_exp = r4(Math.max(0.05, sbCurrent.roic / 100.0));
      }} else if ((tw.growth || tw.gest) && has(c.roic_used)) {{
        const raw = ronic0(c.roic_used, c.roic_operating, c.roic_median, c.ma_reinvest, g_org_exp, c.uses_gaap_roic)[0];
        roic_exp = r4(Math.max(0.05, Math.min(P.roic_cap, raw)));
      }}

      // Valuation
      const hasHistMults = Boolean(c.mult_low_5y && c.mult_high_5y);
      const hasMoatArch = hasMoatArchetype(c);
      const hasPeakOverride = tw.peak;
      const autoNote = String(c.fin_note || '').split('[auto]')[1] || '';
      // Mirrors screener/gates.py BLOCKING_AUTO_NOTES: statements unusable until refetched / reviewed -> No data
      const BLOCKING_AUTO_NOTES = ['stale fundamentals', 'share count changed since FY', 'currency switch unresolved', 'earnings dominated by non-cash marks'];
      const blockingNote = BLOCKING_AUTO_NOTES.find(tok => autoNote.includes(tok)) || null;
      const staleData = blockingNote !== null;
      const hasValuationInputs = Boolean(!staleData && price && peak_eps && peak_eps > 0 &&
        (hasHistMults || (fund_cap && fund_cap > 0) || hasPeakOverride || hasMoatArch));
      let cur_mult = null, pe_vd = null, par_mult = null, par_val = null, vs_par = null, term_mult = null, term_val = null, vs_term = null, irr_5y = null, cap_implied = null, cap_gap = null, g_market = null, g_gap = null, g_market_flag = null, nav_mult = null;
      const g_org_val = has(g_org_exp) ? g_org_exp : g_base;
      const k = has(c.disc_rate) ? c.disc_rate : (c.bs_fin ? P.k_fin : P.k);
      const n_cap = (fund_cap && fund_cap > 0) ? fund_cap : 20.0;
      const roic_eff = Math.max(roic_exp, 0.05);
      const isMtmHoldco = Boolean(c.mtm_holdco) && !tw.peak;
      const isFiniteConc = Boolean(c.finite_conc);
      const bvps = (has(c.bvps) && c.bvps > 0) ? c.bvps : null;
      let noValue = false;

      if (hasValuationInputs) {{
        cur_mult = price / peak_eps;
        let fcfs5, v5;
        if (isMtmHoldco) {{
          nav_mult = bvps ? (bvps / peak_eps) : (1.0 / roic_eff);
          pe_vd = nav_mult;
          term_mult = nav_mult;
          fcfs5 = [0.0, 0.0, 0.0, 0.0, 0.0];
          v5 = pe_vd * Math.pow(1.0 + k, 5);
        }} else {{
          const dcf = explicitDcfMultiple(g_org_val, roic_eff, n_cap, k, g_base, isFiniteConc, null, P.roic_term_max);
          pe_vd = dcf.total;
          term_mult = terminalMultiple(roic_eff, k, g_base, isFiniteConc, null, P.roic_term_max);
          fcfs5 = dcf.fcfs5;
          v5 = dcf.v5;
        }}
        par_mult = pe_vd;
        par_val = (isMtmHoldco && bvps) ? bvps : par_mult * peak_eps;
        term_val = (isMtmHoldco && bvps) ? bvps : term_mult * peak_eps;
        vs_term = (term_val && term_val > 0) ? (price / term_val - 1.0) : null;
        if (par_val <= 0) {{
          noValue = true;          // growth funded at RONIC far below g: no positive DCF value (no discount / IRR)
        }} else {{
          vs_par = price / par_val - 1.0;
          if (isMtmHoldco) {{
            g_market_flag = 'nav_anchored';
          }} else {{
            const sol = solveImpliedDcfGrowth(cur_mult, roic_eff, n_cap, k, g_base, isFiniteConc, g_org_val, P.roic_term_max);
            g_market = sol.g;
            g_market_flag = sol.flag;
          }}
          if (g_market !== null && g_market_flag === 'ok') g_gap = r4(g_org_val - g_market);
          irr_5y = solveDcfIrr5y(cur_mult, fcfs5, v5);
          const pe_base = 1.0 / k;
          const eff_cap = (fund_cap && fund_cap > 0) ? fund_cap : (hasMoatArch ? 20.0 : null);
          if (eff_cap) {{
            cap_implied = (!isMtmHoldco && par_mult > pe_base + 0.5)
              ? r1(Math.max(0.0, eff_cap * (cur_mult - pe_base) / (par_mult - pe_base)))
              : r1(eff_cap * (price / par_val));
            cap_gap = r1(eff_cap - cap_implied);
          }}
        }}
      }}

      // Populate Delta Table
      const isPctZero = (d) => d === null || isNaN(d) || Math.abs(d) < 0.0002;
      const isMultZero = (d) => d === null || isNaN(d) || Math.abs(d) < 0.02;
      const isPriceZero = (d) => d === null || isNaN(d) || Math.abs(d) < 0.02;
      const isYearZero = (d) => d === null || isNaN(d) || Math.abs(d) < 0.05;
      const diffClass = (val, isZero, inv=false) => {{
        if (isZero || val === null || isNaN(val)) return 'diff-neutral';
        const isPos = inv ? val < 0 : val > 0;
        return isPos ? 'diff-pos' : 'diff-neg';
      }};
      const dGStart = (has(g_org_exp) && has(c.g_org_exp)) ? (g_org_exp - c.g_org_exp) : null;
      const dG = (has(g_exp) && has(c.g_exp)) ? (g_exp - c.g_exp) : null;
      const dMult = (par_mult !== null && has(c.par_mult)) ? (par_mult - c.par_mult) : null;
      const dVal = (par_val !== null && has(c.par_val)) ? (par_val - c.par_val) : null;
      const dVsPar = (vs_par !== null && has(c.vs_par)) ? (vs_par - c.vs_par) : null;
      const dTermMult = (term_mult !== null && has(c.term_mult)) ? (term_mult - c.term_mult) : null;
      const dTermVal = (term_val !== null && has(c.term_val)) ? (term_val - c.term_val) : null;
      const dIrr = (irr_5y !== null && has(c.irr_5y)) ? (irr_5y - c.irr_5y) : null;
      const dCap = (fund_cap !== null && has(c.g4_cap)) ? (fund_cap - c.g4_cap) : null;
      const dCapGap = (cap_gap !== null && has(c.cap_gap)) ? (cap_gap - c.cap_gap) : null;
      const vsLbl = (v) => v !== null && v !== undefined ? fmtPct(v, true) + ' (' + (v <= 0 ? 'Below' : 'Above') + ')' : '-';

      const deltaRows = [
        `<tr><td title="Initial organic growth ceiling g₀ = clamp(Sales WLS + min(0, Buyback Yield), 0%, 18%).">Organic Growth Ceiling (g₀)</td><td>${{fmtPct(c.g_org_exp)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPct(g_org_exp)}}</td>
          <td class="${{diffClass(dGStart, isPctZero(dGStart))}}">${{!isPctZero(dGStart) ? fmtPct(dGStart, true) : '-'}}</td></tr>`,
        `<tr><td title="Expected per-share growth ceiling including positive net buyback yield: g₀ + max(0, Buyback Yield).">Per-Share Ceiling (g₀ + Buyback)</td><td>${{fmtPct(c.g_exp)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPct(g_exp)}}</td>
          <td class="${{diffClass(dG, isPctZero(dG))}}">${{!isPctZero(dG) ? fmtPct(dG, true) : '-'}}</td></tr>`,
        `<tr><td title="Marginal RONIC₀ used by the DCF (Tangible ROIC blended with GAAP ROIC by M&amp;A share, capped at 50%; or ROE for financials).">Marginal RONIC₀</td><td>${{fmtPct(c.roic_exp)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPct(roic_exp)}}</td>
          <td class="${{diffClass(has(c.roic_exp) ? roic_exp - c.roic_exp : null, !has(c.roic_exp) || isPctZero(roic_exp - c.roic_exp))}}">${{has(c.roic_exp) && !isPctZero(roic_exp - c.roic_exp) ? fmtPct(roic_exp - c.roic_exp, true) : '-'}}</td></tr>`,
        `<tr><td title="Explicit Mauboussin-Fade DCF Fair P/E = PV(Stage 1 FCFs) + PV(Stage 2 Terminal Value) at hurdle rate r.">Explicit DCF Fair P/E (r=${{(k * 100).toFixed(2)}}%)</td>
          <td>${{has(c.par_mult) ? fmtNum(c.par_mult) + 'x' : '-'}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{par_mult !== null ? fmtNum(par_mult) + 'x' : '-'}}</td>
          <td class="${{diffClass(dMult, isMultZero(dMult))}}">${{!isMultZero(dMult) ? (dMult > 0 ? '+' : '') + fmtNum(dMult) + 'x' : '-'}}</td></tr>`,
        `<tr><td title="Intrinsic DCF Fair Value per share = Explicit DCF Fair P/E × Active Owner EPS.">DCF Fair Value Price</td><td>${{fmtPrice(c.par_val, c.quote_currency)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPrice(par_val, c.quote_currency)}}</td>
          <td class="${{diffClass(dVal, isPriceZero(dVal))}}">${{!isPriceZero(dVal) ? (dVal > 0 ? '+' : '') + fmtPrice(dVal, c.quote_currency) : '-'}}</td></tr>`,
        `<tr><td title="Current share price premium (+) or discount (−) relative to DCF Fair Value.">Discount vs Fair Value (Price / FV - 1)</td><td>${{vsLbl(c.vs_par)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{vsLbl(vs_par)}}</td>
          <td class="${{diffClass(dVsPar, isPctZero(dVsPar), true)}}">${{!isPctZero(dVsPar) ? fmtPct(dVsPar, true) : '-'}}</td></tr>`,
        `<tr><td title="Standalone Terminal P/E floor = (1 − 3.0% / RONIC_term) / (r − 3.0%).">Terminal P/E (3% Inf. Floor)</td>
          <td>${{has(c.term_mult) ? fmtNum(c.term_mult) + 'x' : '-'}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{term_mult !== null ? fmtNum(term_mult) + 'x' : '-'}}</td>
          <td class="${{diffClass(dTermMult, isMultZero(dTermMult))}}">${{!isMultZero(dTermMult) ? (dTermMult > 0 ? '+' : '') + fmtNum(dTermMult) + 'x' : '-'}}</td></tr>`,
        `<tr><td title="Standalone Terminal Price floor = Terminal P/E × Active Owner EPS.">Terminal Price (Floor)</td><td>${{fmtPrice(c.term_val, c.quote_currency)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPrice(term_val, c.quote_currency)}}</td>
          <td class="${{diffClass(dTermVal, isPriceZero(dTermVal))}}">${{!isPriceZero(dTermVal) ? (dTermVal > 0 ? '+' : '') + fmtPrice(dTermVal, c.quote_currency) : '-'}}</td></tr>`,
        `<tr><td title="5-Year Expected IRR across growing annual dividends (with FCF payout conservation) and Year-5 rolled-forward DCF Fair Value.">5-Year Expected IRR</td><td>${{fmtPct(c.irr_5y)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPct(irr_5y)}}</td>
          <td class="${{diffClass(dIrr, isPctZero(dIrr))}}">${{!isPctZero(dIrr) ? fmtPct(dIrr, true) : '-'}}</td></tr>`,
        `<tr><td title="Competitive Advantage Period (CAP) in years over which g₀ and RONIC₀ fade.">Our Moat Runway (CAP)</td><td>${{c.g4_cap ? c.g4_cap + 'y' : '-'}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fund_cap ? fund_cap + 'y' : '-'}}</td>
          <td class="${{diffClass(dCap, isYearZero(dCap))}}">${{!isYearZero(dCap) ? (dCap > 0 ? '+' : '') + dCap + 'y' : '-'}}</td></tr>`,
        `<tr><td title="Runway Margin = Our Moat Runway (CAP) − Market-Implied CAP.">Runway Margin of Safety</td><td>${{fmtSignedYears(c.cap_gap)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtSignedYears(cap_gap)}}</td>
          <td class="${{diffClass(dCapGap, isYearZero(dCapGap))}}">${{!isYearZero(dCapGap) ? fmtSignedYears(dCapGap) : '-'}}</td></tr>`
      ];
      document.getElementById('sb-delta-tbody').innerHTML = deltaRows.join('');

      // Status Box Verdict
      const sbBox = document.getElementById('sb-status-box');
      const sbVerdict = document.getElementById('sb-status-verdict');
      const sbIrrBadge = document.getElementById('sb-irr-badge');
      if (noValue) {{
        sbBox.style.background = 'rgba(100, 116, 139, 0.12)';
        sbBox.style.borderColor = 'rgba(100, 116, 139, 0.3)';
        sbVerdict.innerHTML = `<span style="color: var(--text-dim);">✕ Scenario Verdict: NO POSITIVE DCF VALUE (Fair P/E ${{fmtNum(par_mult)}}x — growth funded at RONIC₀ ${{fmtPct(roic_exp)}} far below g₀)</span>`;
        sbIrrBadge.className = 'badge badge-slate';
        sbIrrBadge.textContent = '5Y IRR: -';
      }} else if (!hasValuationInputs || vs_par === null) {{
        sbBox.style.background = 'rgba(100, 116, 139, 0.12)';
        sbBox.style.borderColor = 'rgba(100, 116, 139, 0.3)';
        sbVerdict.innerHTML = `<span style="color: var(--text-dim);">— Scenario Verdict: Valuation Unavailable (${{staleData ? 'Data check — ' + escHtml(blockingNote) + ': refetch or review required' : 'Missing Price, Peak EPS, or 5Y Multiples'}})</span>`;
        sbIrrBadge.className = 'badge badge-slate';
        sbIrrBadge.textContent = '5Y IRR: -';
      }} else {{
        // v7.2: no cheap/expensive verdict — the scenario reports price vs fair value and the 5Y IRR only
        sbBox.style.background = 'rgba(100, 116, 139, 0.12)';
        sbBox.style.borderColor = 'rgba(100, 116, 139, 0.3)';
        sbVerdict.innerHTML = `<span style="color: var(--text-main);">Scenario: price ${{fmtPct(vs_par, true)}} vs fair value</span>`;
        sbIrrBadge.className = 'badge badge-slate';
        sbIrrBadge.textContent = `5Y IRR: ${{fmtPct(irr_5y)}}`;
      }}

      // Render Tab 3: Explicit Year-by-Year DCF Schedule Table
      const anySandboxTweaked = tw.growth || tw.roic || tw.gest || tw.peak || tw.cap;
      renderDcfScheduleTable(c, {{
        peak_eps, g_org_val, roic_eff, n_cap, k, g_base, isFiniteConc, isMtmHoldco,
        roic_term_max: P.roic_term_max, navMult: nav_mult, isTweaked: anySandboxTweaked, hasValuationInputs
      }});

      // Runtime parity self-check: with untouched inputs the JS sandbox must reproduce the Python baseline.
      if (!anySandboxTweaked && hasValuationInputs && c.par_mult && par_mult) {{
        const multDrift = Math.abs(par_mult / c.par_mult - 1.0);
        const valDrift = (par_val && c.par_val) ? Math.abs(par_val / c.par_val - 1.0) : 0.0;
        const irrDrift = (irr_5y !== null && has(c.irr_5y)) ? Math.abs(irr_5y - c.irr_5y) : ((irr_5y === null) === !has(c.irr_5y) ? 0.0 : 1.0);
        const gMktDrift = (g_market !== null && has(c.g_market)) ? Math.abs(g_market - c.g_market) : 0.0;
        const flagDrift = (g_market_flag || null) !== (c.g_market_flag || null);
        const statusDrift = (noValue ? 'No value' : 'Valued') !== c.val_status;
        const gapDrift = (g_gap === null) !== !has(c.g_gap) || (g_gap !== null && Math.abs(g_gap - c.g_gap) > 0.002);
        if (multDrift > 0.005 || valDrift > 0.005 || irrDrift > 0.005 || gMktDrift > 0.002 || flagDrift || statusDrift || gapDrift) {{
          console.warn(`[parity] ${{c.id}}: JS sandbox vs Python baseline drift (Fair P/E ${{fmtNum(par_mult)}}x vs ${{fmtNum(c.par_mult)}}x, FV ${{par_val}} vs ${{c.par_val}}, IRR ${{fmtPct(irr_5y)}} vs ${{fmtPct(c.irr_5y)}}, g_mkt ${{g_market}} (${{g_market_flag}}) vs ${{c.g_market}} (${{c.g_market_flag}}), status ${{c.val_status}})`);
          const modeBadge = document.getElementById('dcf-tab-mode-badge');
          if (modeBadge) {{
            modeBadge.textContent = 'Baseline DCF ⚠ JS/Python parity drift';
            modeBadge.className = 'binding-badge active-constraint';
          }}
        }}
      }}
    }}

    // Export Table as CSV
    function exportCurrentView() {{
      const data = sortData(getFilteredData());
      if (!data.length) return;

      const headers = ['Ticker', 'Company', 'Universe', 'Country', 'Sector', 'Sub-Industry', 'Status', 'Failing Gate', 'Moat Archetype', 'Our CAP', 'Market-Implied CAP', 'Runway Margin', '1Y Growth', '10Y Sales WLS', 'OpCost CAGR', 'Model g', 'Buyback Yield', 'Per-Share Ceiling', 'Market-Implied g', 'Growth Margin', 'Price', 'Fair Value', 'Discount', '0 g price', 'VS 0 G', 'Cur P/E', 'Fair P/E', 'Terminal P/E', '5Y IRR', 'Active ROIC', 'Operating ROIC', 'GAAP ROIC', 'FCF Conv'];
      const csvRows = [headers.join(',')];

      data.forEach(c => {{
        const gExpVal = c.g_exp;
        const row = [
          `"${{c.ticker || ''}}"`,
          `"${{(c.company || '').replace(/"/g, '""')}}"`,
          `"${{c.universe || ''}}"`,
          `"${{c.country || ''}}"`,
          `"${{(c.sector || '').replace(/"/g, '""')}}"`,
          `"${{(c.sub_industry || '').replace(/"/g, '""')}}"`,
          `"${{c.result || ''}}"`,
          `"${{(c.rejected_at || '').replace(/"/g, '""')}}"`,
          `"${{(c.g3a_moat_archetype || '').replace(/"/g, '""')}}"`,
          c.g4_cap !== null && c.g4_cap !== undefined ? c.g4_cap : '',
          c.cap_implied !== null && c.cap_implied !== undefined ? c.cap_implied : '',
          c.cap_gap !== null && c.cap_gap !== undefined ? c.cap_gap : '',
          c.sales_1y !== null && c.sales_1y !== undefined ? c.sales_1y : '',
          c.sales_cagr !== null && c.sales_cagr !== undefined ? c.sales_cagr : '',
          c.opcost_cagr !== null && c.opcost_cagr !== undefined ? c.opcost_cagr : '',
          c.g_org_exp !== null && c.g_org_exp !== undefined ? c.g_org_exp : '',
          c.buyback_yield !== null && c.buyback_yield !== undefined ? c.buyback_yield : '',
          gExpVal !== null && gExpVal !== undefined ? gExpVal : '',
          c.g_market !== null && c.g_market !== undefined ? c.g_market : '',
          c.g_gap !== null && c.g_gap !== undefined ? c.g_gap : '',
          c.price !== null && c.price !== undefined ? c.price : '',
          c.par_val !== null && c.par_val !== undefined ? c.par_val : '',
          c.vs_par !== null && c.vs_par !== undefined ? c.vs_par : '',
          c.term_val !== null && c.term_val !== undefined ? c.term_val : '',
          c.vs_term !== null && c.vs_term !== undefined ? c.vs_term : '',
          c.cur_mult !== null && c.cur_mult !== undefined ? c.cur_mult : '',
          c.par_mult !== null && c.par_mult !== undefined ? c.par_mult : '',
          c.term_mult !== null && c.term_mult !== undefined ? c.term_mult : '',
          c.irr_5y !== null && c.irr_5y !== undefined ? c.irr_5y : '',
          c.roic_used !== null && c.roic_used !== undefined ? c.roic_used : '',
          c.roic_operating !== null && c.roic_operating !== undefined ? c.roic_operating : '',
          c.roic_median !== null && c.roic_median !== undefined ? c.roic_median : '',
          c.fcf_conv !== null && c.fcf_conv !== undefined ? c.fcf_conv : ''
        ];
        csvRows.push(row.join(','));
      }});

      const blob = new Blob([csvRows.join(String.fromCharCode(10))], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `screener_${{currentTab}}_${{currentMarket}}_${{new Date().toISOString().slice(0,10)}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    // Boot
    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', init);
    }} else {{
      init();
    }}
  </script>
</body>
</html>
"""
    return html


def build_dashboard(keys: list[str] | None = None, output_file: Path | None = None) -> Path:
    """Build the standalone interactive HTML cockpit."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = output_file or (OUTPUT_DIR / "screener.html")

    data = collect_screener_data(keys)
    html_content = build_dashboard_html(data)

    out_path.write_text(html_content, encoding="utf-8")

    # Also maintain output/index.html for local browsers and static servers
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(html_content, encoding="utf-8")

    # Also maintain docs/index.html for GitHub Pages deployment
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    docs_path = DOCS_DIR / "index.html"
    docs_path.write_text(html_content, encoding="utf-8")

    return out_path
