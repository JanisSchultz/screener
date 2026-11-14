"""Standalone Interactive HTML Cockpit Generator for Quality & Moat Screener.

Compiles all universes (US, EU, CA) from data/ into a unified, high-performance,
zero-dependency standalone HTML application (output/screener.html).
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from . import config as C
from .data import DATA_DIR, DOCS_DIR, OUTPUT_DIR, load_universe, universe_keys
from .gates import params, par_valuation, results, uses_gaap_roic


def collect_screener_data(keys: list[str] | None = None) -> dict[str, Any]:
    """Collect and compute all gate results and valuations across universes."""
    universe_list = keys or universe_keys()
    all_companies = []
    universes_meta = {}

    for u_key in universe_list:
        meta = load_universe(u_key)
        universes_meta[u_key] = {
            "key": u_key,
            "title": meta.get("title", u_key.upper()),
            "index_name": meta.get("index_name", u_key.upper()),
            "currency": meta.get("currency", "USD"),
            "as_of": meta.get("as_of", "2026-10-31"),
            "parameters": meta.get("parameters", {}),
        }
        p = params(meta)
        res_map = results(meta)

        for c in meta["companies"]:
            cid = c["id"]
            fin = meta["financials"].get(cid, {})
            pres = res_map.get(cid, {})
            cap_val = c.get("4")
            sub_ind = c.get("sub_industry", "")
            val = par_valuation(fin, p, cap=cap_val, moat=c.get("3a"), sub_industry=sub_ind)

            # Effective ROIC (GAAP ROIC for Balance-Sheet Financials & IFRIC-12 Concessions; Tangible ROIC otherwise)
            r_est = fin.get("roic_est")
            r_op = fin.get("roic_operating")
            r_med = fin.get("roic_median")
            if r_est is not None:
                roic_used = r_est
            elif uses_gaap_roic(sub_ind):
                roic_used = r_med if r_med is not None else r_op
            else:
                roic_used = r_op if r_op is not None else r_med

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
                "g3a_moat_archetype": c.get("3a"),
                "g3b_pricing": c.get("3b"),
                "g3m_moat_note": c.get("3m"),
                "g4_cap": cap_val,
                "g5_mgmt": c.get("5"),
                "g6_cash": c.get("6"),
                "calamity_flag": c.get("calamity") or "",
                "calamity_note": c.get("calamity_note") or "",
                "note": c.get("note"),
                "evidence": c.get("evidence"),
                # Gate Waterfall status
                "result": pres.get("result", C.RES_REVIEW),
                "rejected_at": pres.get("rejected_at", ""),
                "review_at": pres.get("review_at", ""),
                "gate_status": pres.get("status", {}),
                "failed_gates": [lbl for _, lbl, _ in pres.get("failed", [])],
                "waived_gates": [lbl for _, lbl, _ in pres.get("waived", [])],
                "waived_keys": [k for k, _, _ in pres.get("waived", [])],
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
                "roic_est": r_est,
                "roic_used": roic_used,
                "uses_gaap_roic": uses_gaap_roic(sub_ind),
                "fcf_conv": fin.get("fcf_conv"),
                "peak_oe_year": fin.get("peak_oe_year"),
                "peak_oe_eps": fin.get("peak_oe_eps"),
                "peak_eps_est": fin.get("peak_eps_est"),
                "mult_low_5y": fin.get("mult_low_5y"),
                "mult_high_5y": fin.get("mult_high_5y"),
                "cagr_oe_eps": fin.get("cagr_oe_eps"),
                "sales_1y": fin.get("sales_1y"),
                "sales_cagr": fin.get("sales_cagr"),
                "sales_cagr_yrs": fin.get("sales_cagr_yrs"),
                "opcost_1y": fin.get("opcost_1y"),
                "opcost_cagr": fin.get("opcost_cagr"),
                "cap_growth": fin.get("cap_growth"),
                "buyback_yield": fin.get("buyback_yield"),
                "retention_rate": fin.get("retention_rate"),
                "roiic": fin.get("roiic"),
                "g_implied": fin.get("g_implied"),
                "g_est": fin.get("g_est"),
                "p2p_ok": fin.get("p2p_ok"),
                "fin_note": fin.get("fin_note"),
                # Quantitative Valuation
                "val_status": val.get("status", C.V_NODATA),
                "peak_eps": val.get("peak_eps"),
                "cur_mult": val.get("cur_mult"),
                "par_mult": val.get("par_mult"),
                "par_val": val.get("par_val"),
                "vs_par": val.get("vs_par"),
                "irr_5y": val.get("irr_5y"),
                "dy": val.get("dy"),
                "g_hist": val.get("g"),
                "g_start": val.get("g_start"),
                "g_org_start": val.get("g_org_start"),
                "g_1y": val.get("g_1y"),
                "g_hist_5y": val.get("g_hist"),
                "g_cap": val.get("g_cap"),
                "g_log": val.get("g_log"),
                "size_factor": val.get("size_factor"),
                "g_exp": val.get("g_exp"),
                "g_org_exp": val.get("g_org_exp"),
                "g_irr": val.get("g_irr"),
                "g_imp": val.get("g_imp"),
                "g_fund": val.get("g_fund"),
                "g_demand": val.get("g_demand"),
                "g_raw": val.get("g_raw"),
                "scale_tier": val.get("scale_tier"),
                "scale_cap": val.get("scale_cap"),
                "coupon": val.get("coupon"),
                "exp_coupon": val.get("exp_coupon"),
                "imp_coupon": val.get("imp_coupon"),
                "cap_implied": val.get("cap_implied"),
                "cap_gap": val.get("cap_gap"),
                "g_market": val.get("g_market"),
                "g_gap": val.get("g_gap"),
                "pers": val.get("pers"),
                "g_mult": val.get("g_mult"),
                "reinv_eff": val.get("reinv_eff"),
                "eff_g_mult": val.get("eff_g_mult"),
                "pe_mm": val.get("pe_mm"),
                "pe_mck": val.get("pe_mck"),
                "pe_vd": val.get("pe_vd"),
                "t_growth": val.get("t_growth"),
                "t_hist": val.get("t_hist"),
                "t_hist_raw": val.get("t_hist_raw"),
                "t_roic": val.get("t_roic"),
                "raw_par": val.get("raw_par"),
                "roic_log": val.get("roic_log"),
                "roic_exp": val.get("roic_exp"),
                "roic_fade_ratio": val.get("roic_fade_ratio"),
                "retention": val.get("retention"),
                "r_inc": val.get("r_inc"),
                "zc_pricing": val.get("zc_pricing"),
                "bb_eff": val.get("bb_eff"),
            }
            all_companies.append(company_record)

    # Global KPI Aggregates
    qpass_count = sum(1 for c in all_companies if c["result"] == C.RES_QPASS)
    calamity_list = [c for c in all_companies if c["result"] == C.RES_CALAMITY]
    calamity_below_par = sum(1 for c in calamity_list if c["val_status"] == C.V_BELOW_PAR)
    below_par_list = [c for c in all_companies if c["result"] == C.RES_QPASS and c["val_status"] == C.V_BELOW_PAR]
    below_par_count = len(below_par_list)
    irrs = [c["irr_5y"] for c in below_par_list if c["irr_5y"] is not None]
    median_irr = statistics.median(irrs) if irrs else 0.0

    return {
        "version": "6.35",
        "generated_at": "2026-11-14",
        "summary": {
            "total_companies": len(all_companies),
            "quality_pass": qpass_count,
            "calamity_pass": len(calamity_list),
            "calamity_below_par": calamity_below_par,
            "below_par": below_par_count,
            "median_irr_below_par": median_irr,
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
      gap: 8px;
      flex-shrink: 0;
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

    @media (max-width: 768px) {{
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
      .mobile-swipe-hint {{
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
      background-color: rgba(56, 189, 248, 0.18);
      border-left: 3px solid var(--accent);
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
      width: 720px;
      max-width: 95vw;
      background: var(--bg-surface);
      border-left: 1px solid var(--border);
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
    .formula-code {{
      font-size: 12px;
      color: #cbd5e1;
      margin-top: 4px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-all;
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
      height: 6px;
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
      <span class="brand-subtitle">Charlie Munger Reject Gates & Equity Bond Valuation</span>
    </div>
    <div class="kpi-bar">
      <div class="kpi-chip">
        <span class="kpi-label">Universe</span>
        <span class="kpi-value">{data['summary']['total_companies']}</span>
      </div>
      <div class="kpi-chip">
        <span class="kpi-label">Quality Pass</span>
        <span class="kpi-value accent">{data['summary']['quality_pass']}</span>
      </div>
      <div class="kpi-chip">
        <span class="kpi-label">Calamity</span>
        <span class="kpi-value amber">{data['summary']['calamity_pass']}</span>
      </div>
      <div class="kpi-chip">
        <span class="kpi-label">Below PAR</span>
        <span class="kpi-value green">{data['summary']['below_par']}</span>
      </div>
      <div class="kpi-chip">
        <span class="kpi-label">Median IRR</span>
        <span class="kpi-value green">{f"{data['summary']['median_irr_below_par']*100:.1f}%"}</span>
      </div>
    </div>
  </header>

  <!-- View Tabs -->
  <nav class="tab-bar">
    <button class="tab-btn active" data-tab="shortlist" onclick="setTab('shortlist')">
      <span class="tab-label-full">★ Below PAR Shortlist</span>
      <span class="tab-label-short">★ Shortlist</span>
      <span class="pill-count" id="count-shortlist">0</span>
    </button>
    <button class="tab-btn" data-tab="qpass" onclick="setTab('qpass')">
      <span class="tab-label-full">🛡️ Quality Pass Funnel</span>
      <span class="tab-label-short">🛡️ Quality</span>
      <span class="pill-count" id="count-qpass">0</span>
    </button>
    <button class="tab-btn" data-tab="calamity" onclick="setTab('calamity')">
      <span class="tab-label-full">⚠️ Calamity Watchlist</span>
      <span class="tab-label-short">⚠️ Calamity</span>
      <span class="pill-count" id="count-calamity">0</span>
    </button>
    <button class="tab-btn" data-tab="all" onclick="setTab('all')">
      <span class="tab-label-full">🔍 Full Universe & Waterfall</span>
      <span class="tab-label-short">🔍 All</span>
      <span class="pill-count" id="count-all">0</span>
    </button>
    <button class="tab-btn" data-tab="methodology" onclick="setTab('methodology')">
      <span class="tab-label-full">📖 Framework Rubric</span>
      <span class="tab-label-short">📖 Rubric</span>
    </button>
  </nav>

  <!-- Filter & Controls Toolbar -->
  <section class="controls-bar" id="controls-section">
    <div class="filters-left">
      <!-- Search Input -->
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="filter-search" class="search-input" placeholder="Search ticker, company, sector..." oninput="handleSearchInput()">
        <button id="search-clear" class="search-clear" onclick="clearSearch()" aria-label="Clear search">&times;</button>
      </div>

      <!-- Market Universe Pills -->
      <div class="market-pills">
        <button class="market-btn active" data-market="all" onclick="setMarket('all')">All</button>
        <button class="market-btn" data-market="us" onclick="setMarket('us')">🇺🇸 US</button>
        <button class="market-btn" data-market="eu" onclick="setMarket('eu')">🇪🇺 EU</button>
        <button class="market-btn" data-market="ca" onclick="setMarket('ca')">🇨🇦 CA</button>
      </div>

      <!-- Sort Filter -->
      <select id="filter-sort" class="select-filter" onchange="applySortFromSelect(this.value)">
        <option value="irr_5y-desc">Sort: 5Y Exp IRR ↓</option>
        <option value="irr_5y-asc">Sort: 5Y Exp IRR ↑</option>
        <option value="vs_par-asc">Sort: Discount vs Fair Value ↑</option>
        <option value="vs_par-desc">Sort: Premium vs Fair Value ↓</option>
        <option value="g_gap-desc">Sort: Growth Margin (g₀ - g_mkt) ↓</option>
        <option value="g_market-asc">Sort: Market-Implied g (r=8.5%) ↑</option>
        <option value="g_org_exp-desc">Sort: Growth Ceiling (g₀) ↓</option>
        <option value="opcost_cagr-desc">Sort: 3–5Y OpCost Growth ↓</option>
        <option value="sales_1y-asc">Sort: 1Y Growth (Slump) ↑</option>
        <option value="sales_1y-desc">Sort: 1Y Growth ↓</option>
        <option value="sales_cagr-desc">Sort: 3–5Y Growth ↓</option>
        <option value="buyback_yield-desc">Sort: Buyback Yield ↓</option>
        <option value="roic_used-desc">Sort: Op ROIC ↓</option>
        <option value="cur_mult-asc">Sort: Cur P/E ↑</option>
        <option value="cur_mult-desc">Sort: Cur P/E ↓</option>
        <option value="par_mult-desc">Sort: Fair P/E ↓</option>
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
      <select id="filter-sector" class="select-filter" onchange="applyFilters()">
        <option value="all">All Sectors</option>
      </select>

      <!-- Moat Archetype Filter -->
      <select id="filter-moat" class="select-filter" onchange="applyFilters()">
        <option value="all">All Moats</option>
      </select>

      <!-- Failing Gate Filter (Visible in Full Universe tab) -->
      <select id="filter-gate" class="select-filter" style="display:none;" onchange="applyFilters()">
        <option value="all">All Gate Statuses</option>
        <option value="Quality pass">Quality Pass Only</option>
        <option value="Calamity pass">Calamity Pass (Conditional)</option>
        <option value="Gate 1">Rejected at Gate 1 (Understandability)</option>
        <option value="Gate 2">Rejected at Gate 2 (Essential Need)</option>
        <option value="Gate 3">Rejected at Gate 3 (Moat & Proof)</option>
        <option value="Gate 4">Rejected at Gate 4 (Runway CAP < 15Y)</option>
        <option value="Gate 5">Rejected at Gate 5 (Management)</option>
        <option value="Gate 6">Rejected at Gate 6 (Cash / Balance Sheet)</option>
      </select>

      <!-- Shortlist Calamity Toggle (Visible in Shortlist tab; off by default) -->
      <label id="toggle-calamities-wrap" class="toggle-pill" style="display:none;" title="Overlay temporary fixable calamities (Gates 3b, 5, 6) trading Below PAR">
        <input type="checkbox" id="toggle-calamities" onchange="applyFilters()">
        <span>Include Calamities</span>
      </label>
    </div>

    <!-- Controls Right: View Toggle & Export Button -->
    <div class="filters-right">
      <div class="view-toggle">
        <button class="view-btn" id="view-cards-btn" onclick="setViewMode('cards')" title="Card View">
          <span>⊞</span> Cards
        </button>
        <button class="view-btn" id="view-table-btn" onclick="setViewMode('table')" title="Table View">
          <span>☰</span> Table
        </button>
      </div>

      <button class="btn-export" onclick="exportCurrentView()">
        <span>📥</span> Export
      </button>
    </div>
  </section>

  <!-- Main Table View -->
  <main class="table-container" id="table-view">
    <div class="mobile-swipe-hint">👉 Swipe horizontally to view all metrics • Tap any row to open dossier</div>
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
    No companies match the selected search and filter criteria.
  </div>

  <!-- Methodology Tab Content (Hidden by default) -->
  <main class="table-container" id="methodology-view" style="display:none; padding: 24px 20px; max-width: 1000px; margin: 0 auto; width: 100%;">
    <div class="dossier-section" style="margin-bottom: 24px;">
      <h2 style="font-size: 16px; margin-bottom: 12px; color: var(--accent);">The 6 Munger Reject Gates (v{data['version']})</h2>
      <p style="color: var(--text-muted); margin-bottom: 16px;">
        "Tell me where I am going to die so that I never go there." Every qualitative step is a sequential REJECT gate: a company leaves the funnel at the first gate it fails. Only companies clearing all 6 gates enter the Quantitative valuation sheet.
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
          <strong style="color: var(--accent);">Gate 3: Strong Moat & Pricing Power >= Inflation</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Requires a proven economic moat archetype (Toll booth, Scale economies, Infrastructure, R&D super-thinkers) PLUS empirical proof of moat: 5Y median ROIC &ge; 12% and incremental ROIIC &ge; 12%.</p>
        </div>
        <div class="metric-box">
          <strong style="color: var(--accent);">Gate 4: Low Disruption Risk & Predictable Runway (CAP &ge; 15 Years)</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Two-step longevity engine: Outside View anchors baseline CAP in Mauboussin & Callahan empirical persistence tiers (10–30Y). Inside View deductively haircuts CAP for 5 Macrotrends (AI cognitive disruption, demographic aging, supply chain reshoring, energy limits, structural inflation).</p>
        </div>
        <div class="metric-box">
          <strong style="color: var(--accent);">Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Scored 0–2 across 5 vectors: skin in the game, rational capital allocation, customer centricity, plain talk, and low principal-agent friction.</p>
        </div>
        <div class="metric-box">
          <strong style="color: var(--accent);">Gate 6: Real Cash Conversion, Peak-to-Peak Compounding & Fortress Balance Sheet</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Triad: (1) Secular Peak-to-Peak Owner EPS compounding across cycles, (2) Real cash conversion (multi-year FCF &ge; 80% GAAP NI), (3) Peace-of-mind fortress balance sheet (Net Debt &le; 4y Owner Earnings, Interest Coverage &gt; 5x).</p>
        </div>
        <div class="metric-box" style="border-color: var(--amber-border); background: rgba(245, 158, 11, 0.08);">
          <strong style="color: var(--amber);">Conditional Calamity Pass (Buffett Temporary Fixable Calamities — Gates 3b, 5, 6 Only)</strong>
          <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">Great franchises with an intact moat and runway occasionally breach Gate 3b (trailing ROIC/pricing dip), Gate 5 (outgoing/remediating management), or Gate 6 (temporary M&amp;A bridge debt or capex surge). Flagging <code style="color: var(--amber);">calamity = Y</code> preserves raw failed scores, evaluates all remaining gates, and admits them into Quantitative PAR valuation under a separate <strong style="color: var(--amber);">Calamity pass</strong> tier. Gates 1, 2, 3a (moat != None), and 4 (CAP &ge; 15Y) are never waivable.</p>
        </div>
      </div>
    </div>

    <div class="dossier-section">
      <h2 style="font-size: 16px; margin-bottom: 12px; color: var(--accent);">Quantitative Valuation: Explicit Mauboussin-Fade DCF &amp; Slump-Cannibal Compounders (v6.35)</h2>
      <div class="metric-box" style="margin-bottom: 12px;">
        <strong style="color: var(--text-main);">1. Explicit N-Year Mauboussin-Fade DCF Fair Value at Cost of Equity r = 8.50% (v6.35):</strong>
        <p class="formula-code">
          Fair P/E = PV<sub>Stage 1</sub> + PV<sub>Stage 2</sub> &nbsp;|&nbsp; Fair Value = Fair P/E &times; Active EPS &nbsp;|&nbsp; Discount = Price / Fair Value - 1<br>
          <span style="font-size: 11px; color: var(--text-dim);">
            <b>Stage 1 (Years t = 1..N, N = Gate 4 CAP):</b> Linear fade of organic growth g<sub>t</sub> = g₀ - ((t-1)/N)(g₀ - 3.5%) and return on capital ROIC<sub>t</sub> = ROIC₀ - ((t-1)/N)(ROIC₀ - ROIC<sub>term</sub>), where E<sub>t</sub> = E<sub>t-1</sub>(1 + g<sub>t</sub>) and FCF<sub>t</sub> = E<sub>t</sub>(1 - g<sub>t</sub>/ROIC<sub>t</sub>), discounted at r = 8.50%.<br>
            <b>Stage 2 (Post-CAP Perpetuity at t = N):</b> Terminal steady state g<sub>term</sub> = 3.5% and ROIC<sub>term</sub> = clamp(ROIC₀, 12%, 20%), discounted back from Year N at r = 8.50%.<br>
            <b>Market-Implied Growth (g<sub>market</sub> at r = 8.50%):</b> Exact DCF inversion solving for the starting organic growth rate g<sub>market</sub> where DCF_PE(g<sub>market</sub>) == Cur_Mult &nbsp;|&nbsp; Growth Margin = g₀ - g<sub>market</sub>.<br>
            <b>Balance-Sheet Financials &amp; Concessions:</b> Uses GAAP ROIC (<code style="color: var(--accent);">roic_median</code>) for Insurance, Reinsurance, Banks, Multi-Sector Holdings &amp; IFRIC-12 Concessions; Mark-to-Market HoldCos use <code style="color: var(--accent);">Fair P/E = 1 / ROIC₀</code> (P/B = 1.0x); IFRIC-12 Concessions (FCF Conv &gt; 1.25x) omit Stage 2 terminal perpetuity.
          </span>
        </p>
      </div>
      <div class="metric-box" style="margin-bottom: 12px;">
        <strong style="color: var(--text-main);">2. Operating Cost Base Growth Ceiling (g₀ = OpCost CAGR):</strong>
        <p class="formula-code">
          Organic Growth Ceiling (g₀) = clamp(OpCost_CAGR + min(0, Buyback_Yield), 2.0%, Scale_Cap) &nbsp;|&nbsp; Per-Share Ceiling (g_exp) = g₀ + max(0, Buyback_Yield)<br>
          <span style="font-size: 11px; color: var(--text-dim);">
            Because companies clearing the 6 Munger Reject Gates maintain structurally constant margins over the cycle (Gate 3b pricing power &ge; inflation, Gate 5 rejects SG&amp;A bloat), the 3–5Y CAGR of the operating cost base (<code style="color: var(--accent);">OpCost = Sales - EBIT = COGS + OpEx</code>) measures real physical capacity and customer volume expansion without temporary margin noise. Comparing 1Y Growth against 3–5Y Growth and OpCost GrowthCeiling immediately highlights temporary 1-year growth slumps.
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
          P₀ = &Sigma;<sub>t=1..5</sub> [D₀(1 + g_irr)<sup>t</sup> / (1 + IRR)<sup>t</sup>] + [Fair_Value(1 + g_irr)<sup>5</sup> / (1 + IRR)<sup>5</sup>] &nbsp;|&nbsp; g_irr = g<sub>org,5y</sub> + min(bb_pos, max(0, FCF_Payout/Cur_Mult - dy))<br>
          <span style="font-size: 11px; color: var(--text-dim);">Solves the exact 5-year cash-flow internal rate of return across growing annual dividends and Year-5 DCF Fair Value while bounding buyback accretion at current P/E so Dividends + Buybacks + Organic Reinvestment never exceed 100% of Owner Earnings.</span>
        </p>
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
            <div class="label">Moat Archetype</div>
            <div class="value" style="font-size: 13px;" id="dossier-moat-type">-</div>
          </div>
          <div class="metric-box">
            <div class="label">Moat Runway (CAP)</div>
            <div class="value" style="font-size: 13px;" id="dossier-cap">-</div>
          </div>
        </div>

        <div id="dossier-calamity-box" class="metric-box" style="margin-bottom: 12px; display: none; border-color: var(--amber-border); background: rgba(245, 158, 11, 0.08);">
          <div class="label" style="color: var(--amber);">⚠️ Temporary Calamity Rationale &amp; Kill-Switch</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-calamity-note"></div>
        </div>

        <div id="dossier-moat-note-box" class="metric-box" style="margin-bottom: 12px; display: none;">
          <div class="label" style="color: var(--accent);">Moat & Pricing Power Note</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-moat-note"></div>
        </div>

        <div id="dossier-note-box" class="metric-box" style="margin-bottom: 12px; display: none;">
          <div class="label" style="color: var(--accent);">Gate Review Thesis / Rationale</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-note"></div>
        </div>

        <div id="dossier-evidence-box" class="metric-box" style="display: none;">
          <div class="label" style="color: var(--accent);">5-Macrotrend Evidence & Longevity Analysis</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-evidence"></div>
        </div>

        <div id="dossier-g2r-box" class="metric-box" style="display: none;">
          <div class="label" style="color: var(--red);">Gate 2 Non-Essential Reason</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-g2r"></div>
        </div>
      </div>

      <!-- Quantitative Valuation Profile -->
      <div class="dossier-section" id="dossier-quant-section">
        <div class="section-title">Explicit Mauboussin-Fade DCF Scorecard (r = 8.5%)</div>
        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label">Current Share Price</div>
            <div class="value" id="dossier-price">-</div>
          </div>
          <div class="metric-box">
            <div class="label">DCF Fair Value</div>
            <div class="value" id="dossier-par-val">-</div>
          </div>
          <div class="metric-box">
            <div class="label">Discount vs Fair Value</div>
            <div class="value" id="dossier-vs-par">-</div>
          </div>
        </div>

        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label">Current Multiple</div>
            <div class="value" id="dossier-cur-mult">-</div>
          </div>
          <div class="metric-box">
            <div class="label">DCF Fair P/E (r=8.5%)</div>
            <div class="value" id="dossier-par-mult">-</div>
          </div>
          <div class="metric-box">
            <div class="label">5Y Expected IRR</div>
            <div class="value" id="dossier-irr">-</div>
          </div>
        </div>

        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label">Operating ROIC (Tangible)</div>
            <div class="value" id="dossier-roic-op">-</div>
          </div>
          <div class="metric-box">
            <div class="label">GAAP ROIC (incl. Goodwill)</div>
            <div class="value" id="dossier-roic-gaap">-</div>
          </div>
          <div class="metric-box">
            <div class="label">FCF Conversion (÷ NI)</div>
            <div class="value" id="dossier-fcf-conv">-</div>
          </div>
        </div>

        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label">Growth Ceiling (g₀ → +BB)</div>
            <div class="value" id="dossier-g-imp">-</div>
            <div class="subtext" id="dossier-scale-tier" style="font-size: 10px; color: var(--text-dim); margin-top: 2px;"></div>
          </div>
          <div class="metric-box">
            <div class="label">Market-Implied g (8.5%)</div>
            <div class="value" id="dossier-g-market">-</div>
          </div>
          <div class="metric-box">
            <div class="label">Growth Margin (g₀ - g_mkt)</div>
            <div class="value" id="dossier-g-margin">-</div>
          </div>
        </div>

        <div class="grid-3">
          <div class="metric-box">
            <div class="label">Our CAP (Gate 4)</div>
            <div class="value" id="dossier-cap-our">-</div>
          </div>
          <div class="metric-box">
            <div class="label">Market-Implied CAP</div>
            <div class="value" id="dossier-cap-implied">-</div>
          </div>
          <div class="metric-box">
            <div class="label">Runway Margin</div>
            <div class="value" id="dossier-cap-margin">-</div>
          </div>
        </div>

        <div id="dossier-fin-note-box" class="metric-box" style="margin-top: 10px; display: none;">
          <div class="label" style="color: var(--text-dim);">Financial Notes & Overrides</div>
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
              <span class="audit-card-title"><span>🛡️</span> 1. OUR CAP (Moat Runway) &amp; Mauboussin Fade</span>
              <span class="cell-ticker" id="audit-cap-summary" style="font-size: 13px;">-</span>
            </div>
            <div class="audit-grid">
              <div class="audit-stat">
                <span class="lbl">Assigned Runway (G4)</span>
                <span class="val" id="audit-cap-years">-</span>
                <span class="sub" id="audit-cap-tier">-</span>
              </div>
              <div class="audit-stat">
                <span class="lbl">ROIC Persistence (w)</span>
                <span class="val" id="audit-cap-pers">-</span>
                <span class="sub">Initial ROIC₀ Retention</span>
              </div>
              <div class="audit-stat">
                <span class="lbl">DCF Growth Slope</span>
                <span class="val" id="audit-cap-gmult">-</span>
                <span class="sub" id="audit-cap-gmult-sub">Points per 1% g₀</span>
              </div>
              <div class="audit-stat">
                <span class="lbl">Market-Implied CAP</span>
                <span class="val" id="audit-cap-market">-</span>
                <span class="sub" id="audit-cap-gap">-</span>
              </div>
            </div>
            <div class="filter-step-box">
              <div style="display: flex; justify-content: space-between; font-size: 11px; flex-wrap: wrap; gap: 6px;">
                <span style="color: var(--text-dim);">Moat Archetype (G3a): <b style="color: var(--text-main);" id="audit-moat-arch">-</b></span>
                <span style="color: var(--text-dim);">Pricing Power (G3b): <b style="color: var(--text-main);" id="audit-moat-pricing">-</b></span>
              </div>
            </div>
          </div>

          <!-- 2. Growth Ceiling (g₀) & Per-Share Ceiling (g_exp) Card -->
          <div class="audit-card">
            <div class="audit-card-header">
              <span class="audit-card-title"><span>📈</span> 2. Organic Growth Ceiling (g₀) &amp; Buybacks — Operating Cost Base Proxy</span>
              <span class="val" style="color: var(--accent); font-size: 14px;" id="audit-gexp-summary">-</span>
            </div>

            <!-- Anchor 1: Near-Term 1Y Momentum / Slump Check -->
            <div class="filter-step-box" id="box-filter-supply">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 11px; color: var(--text-main);">Near-Term 1Y Growth vs. Slump Check</strong>
                <span class="val" style="font-size: 12px;" id="audit-g1y-val">-</span>
              </div>
              <div style="font-size: 11px; color: var(--text-dim); display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px;">
                <span>1Y Sales Growth: <b id="audit-sales1y-val" style="color: var(--text-muted);">-</b></span>
                <span>1Y OpCost Growth: <b id="audit-opcost1y-val" style="color: var(--text-muted);">-</b></span>
                <span>Buybacks / Dilution: <b id="audit-bb-val" style="color: var(--text-muted);">-</b></span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;">Compares 1Y top-line &amp; operating cost momentum against 3–5Y normal growth ceiling to spot temporary slumps.</div>
            </div>

            <!-- Anchor 2: 3-5Y Operating Cost Base & Sales Growth -->
            <div class="filter-step-box" id="box-filter-demand">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 11px; color: var(--text-main);">3–5Y Operating Cost Base &amp; Revenue Compounding</strong>
                <span class="val" style="font-size: 12px;" id="audit-gdemand-val">-</span>
              </div>
              <div style="font-size: 11px; color: var(--text-dim); display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px;">
                <span>Sales CAGR (<span id="audit-salesyrs-val">5Y</span>): <b id="audit-salescagr-val" style="color: var(--text-muted);">-</b></span>
                <span>OpCost CAGR (COGS+OpEx): <b id="audit-opcostcagr-val" style="color: var(--accent);">-</b></span>
                <span>Cycle OE EPS CAGR: <b id="audit-oecagr-val" style="color: var(--text-muted);">-</b></span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;">Primary Growth Ceiling Proxy: OpCost = Sales - EBIT (COGS + OpEx) measures normal structural business growth.</div>
            </div>

            <!-- Anchor 3: Capital Growth & ROIC Profile -->
            <div class="filter-step-box" id="box-filter-fade">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 11px; color: var(--text-main);">Capital Reinvestment &amp; Mauboussin ROIC Profile</strong>
                <span class="val" style="font-size: 12px;" id="audit-gfund-val">-</span>
              </div>
              <div style="font-size: 11px; color: var(--text-dim); display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px;">
                <span>5Y Cap Growth: <b id="audit-capgrowth-val" style="color: var(--text-muted);">-</b></span>
                <span>Op ROIC → Initial ROIC₀: <b id="audit-roic-val" style="color: var(--text-muted);">-</b></span>
                <span>ROIC Fade Ratio: <b id="audit-roicfade-val" style="color: var(--text-muted);">-</b></span>
                <span>5Y Retention: <b id="audit-retention-val" style="color: var(--text-muted);">-</b></span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;">ROIC fades linearly across CAP from Initial ROIC₀ down to terminal steady-state clamp(ROIC₀, 12%, 20%).</div>
            </div>

            <!-- Step B: Growth Ceiling (g₀) & Per-Share Ceiling (g_exp) -->
            <div class="filter-step-box" id="box-filter-gravity">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="font-size: 11px; color: var(--text-main);">Organic Growth Ceiling (g₀) &amp; Per-Share Ceiling (g_exp)</strong>
                <span class="val" style="font-size: 12px;" id="audit-fade-val">-</span>
              </div>
              <div style="font-size: 11px; color: var(--text-dim); display: flex; flex-wrap: wrap; gap: 8px; margin-top: 2px;">
                <span>Organic Ceiling (g₀): <b id="audit-graw-val" style="color: var(--accent);">-</b></span>
                <span>Per-Share Ceiling (g_exp): <b id="audit-glog-val" style="color: var(--text-muted);">-</b></span>
                <span>CAP Persistence (w): <b id="audit-fadew-val" style="color: var(--text-muted);">-</b></span>
                <span>Log-Rev Size Factor: <b id="audit-sizefactor-val" style="color: var(--text-muted);">-</b></span>
                <span>Scale Tier: <b id="audit-scaletier-val" style="color: var(--text-muted);">-</b> (<b id="audit-scalecap-val" style="color: var(--text-muted);">-</b>)</span>
                <span>Analyst Override: <b id="audit-gest-val" style="color: var(--text-muted);">-</b></span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;">Formula: g₀ = clamp(OpCost_CAGR + min(0, BB), 2.0%, Scale_Cap) fades linearly to 3.5% over CAP in the DCF.</div>
            </div>
          </div>

          <!-- 3. Explicit Mauboussin-Fade DCF Multiple Audit Card -->
          <div class="audit-card">
            <div class="audit-card-header">
              <span class="audit-card-title"><span>⚖️</span> 3. Explicit Mauboussin-Fade DCF Fair P/E (r = 8.50%)</span>
              <span class="val" style="color: var(--accent); font-size: 14px;" id="audit-parmult-summary">-</span>
            </div>
            <div class="audit-grid">
              <div class="audit-stat">
                <span class="lbl">Stage 1 CAP PV</span>
                <span class="val" id="audit-tgrowth-val">-</span>
                <span class="sub" id="audit-tgrowth-sub">Years 1..N FCF @ r=8.5%</span>
              </div>
              <div class="audit-stat">
                <span class="lbl">Stage 2 Terminal PV</span>
                <span class="val" id="audit-troic-val">-</span>
                <span class="sub">Post-CAP Perpetuity @ 3.5%</span>
              </div>
              <div class="audit-stat">
                <span class="lbl">Explicit DCF Fair P/E</span>
                <span class="val" id="audit-rawpar-val">-</span>
                <span class="sub">Stage 1 + Stage 2 (100% Weight)</span>
              </div>
              <div class="audit-stat">
                <span class="lbl">5Y Harmonic P/E (Ref)</span>
                <span class="val" id="audit-thist-val">-</span>
                <span class="sub" id="audit-thist-sub">Reference Only (0% Weight)</span>
              </div>
            </div>
            <div class="filter-step-box">
              <div style="display: flex; justify-content: space-between; font-size: 11px; flex-wrap: wrap; gap: 6px;">
                <span>Year-1 FCF Payout (1 - g₀/ROIC₀): <b id="audit-reinv-val" style="color: var(--text-main);">-</b></span>
                <span>5Y Low–High Range: <b id="audit-mh-val" style="color: var(--text-main);">-</b></span>
                <span>Normalized Peak EPS: <b id="audit-peakeps-val" style="color: var(--text-main);">-</b></span>
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
                <button type="button" class="btn-export" style="padding: 4px 10px; font-size: 11px;" onclick="resetSandboxValuation()">↺ Reset</button>
                <button type="button" class="btn-export" style="padding: 4px 10px; font-size: 11px;" id="btn-copy-sandbox" onclick="copySandboxOverrideJson()">📋 Copy JSON</button>
              </div>
            </div>

            <div class="sandbox-grid">
              <!-- Control 1: Moat Runway (CAP) -->
              <div class="sandbox-group">
                <label>Moat Runway (Gate 4 CAP): <span class="sb-val" id="sb-val-cap">20y</span></label>
                <div class="cap-btn-group">
                  <button type="button" class="cap-pill-btn" data-cap="5" onclick="setSandboxCap(5)">5y</button>
                  <button type="button" class="cap-pill-btn" data-cap="10" onclick="setSandboxCap(10)">10y</button>
                  <button type="button" class="cap-pill-btn" data-cap="15" onclick="setSandboxCap(15)">15y</button>
                  <button type="button" class="cap-pill-btn" data-cap="20" onclick="setSandboxCap(20)">20y</button>
                  <button type="button" class="cap-pill-btn" data-cap="25" onclick="setSandboxCap(25)">25y</button>
                  <button type="button" class="cap-pill-btn" data-cap="30" onclick="setSandboxCap(30)">30y</button>
                </div>
              </div>

              <!-- Control 2: 1Y Sales Growth -->
              <div class="sandbox-group">
                <label>1Y Sales Growth (Slump Check): <span class="sb-val" id="sb-val-sales1y">8.0%</span></label>
                <input type="range" class="sandbox-slider" id="sb-slider-sales1y" min="-10" max="30" step="0.5" value="8" oninput="onSandboxSliderChange('sales1y', this.value, '%')">
              </div>

              <!-- Control 3: 3-5Y Growth Ceiling Driver -->
              <div class="sandbox-group">
                <label>3–5Y Normal / OpCost Growth (g₀): <span class="sb-val" id="sb-val-salescagr">8.0%</span></label>
                <input type="range" class="sandbox-slider" id="sb-slider-salescagr" min="-5" max="30" step="0.5" value="8" oninput="onSandboxSliderChange('salescagr', this.value, '%')">
              </div>

              <!-- Control 4: Operating Capital Growth -->
              <div class="sandbox-group">
                <label>Operating Capital Growth: <span class="sb-val" id="sb-val-capgrowth">8.0%</span></label>
                <input type="range" class="sandbox-slider" id="sb-slider-capgrowth" min="0" max="30" step="0.5" value="8" oninput="onSandboxSliderChange('capgrowth', this.value, '%')">
              </div>

              <!-- Control 5: Tangible Operating ROIC -->
              <div class="sandbox-group">
                <label><span id="sb-label-roic-text">Tangible Operating ROIC</span>: <span class="sb-val" id="sb-val-roic">20.0%</span></label>
                <input type="range" class="sandbox-slider" id="sb-slider-roic" min="5" max="150" step="0.5" value="20" oninput="onSandboxSliderChange('roic', this.value, '%')">
              </div>

              <!-- Control 6: Buyback Yield -->
              <div class="sandbox-group">
                <label>Buyback Yield (Dilution if &lt; 0): <span class="sb-val" id="sb-val-bb">1.0%</span></label>
                <input type="range" class="sandbox-slider" id="sb-slider-bb" min="-3" max="5" step="0.2" value="1" oninput="onSandboxSliderChange('bb', this.value, '%')">
              </div>

              <!-- Control 7: Peak EPS Normalization -->
              <div class="sandbox-group">
                <label>Normalized Peak EPS: <span class="sb-val" id="sb-val-peakeps">-</span></label>
                <input type="number" class="sandbox-num-input" id="sb-input-peakeps" step="0.05" oninput="onSandboxInputChange()">
              </div>

              <!-- Control 8: 5Y Multiple Low / High -->
              <div class="sandbox-group">
                <label>5Y Multiple Low / High (Ref):</label>
                <div class="sandbox-input-row">
                  <input type="number" class="sandbox-num-input" id="sb-input-ml" placeholder="Low (e.g. 15)" step="0.5" oninput="onSandboxInputChange()">
                  <span style="color: var(--text-dim);">-</span>
                  <input type="number" class="sandbox-num-input" id="sb-input-mh" placeholder="High (e.g. 30)" step="0.5" oninput="onSandboxInputChange()">
                </div>
              </div>

              <!-- Control 9: Direct Expected Growth Override -->
              <div class="sandbox-group">
                <label>Direct Growth Ceiling Override: <span class="sb-val" id="sb-val-gest">None</span></label>
                <div class="sandbox-input-row">
                  <input type="number" class="sandbox-num-input" id="sb-input-gest" placeholder="e.g. 7.5 (overrides g₀)" step="0.1" oninput="onSandboxInputChange()">
                  <button type="button" class="btn-export" style="padding: 4px 8px; font-size: 11px;" onclick="clearSandboxGest()">Clear</button>
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
              <span id="sb-status-verdict">Scenario Verdict: BELOW PAR</span>
              <span id="sb-irr-badge" class="badge badge-green" style="font-size: 12px;">5Y IRR: 12.4%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>

  <!-- Embedded JSON Dataset -->
  <script id="screener-raw-data" type="application/json">
{json_payload}
  </script>

  <!-- Client-Side Reactive Controller -->
  <script>
    const SCREENER_DATA = JSON.parse(document.getElementById('screener-raw-data').textContent);
    let currentTab = 'shortlist';
    let currentMarket = 'all';
    let sortColumn = 'irr_5y';
    let sortAsc = false;
    let selectedCompanyId = null;
    let viewMode = (window.innerWidth <= 768) ? 'cards' : 'table';

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
      setTab('shortlist');

      // Keyboard Esc to close drawer
      window.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') closeDrawer();
      }});
    }}

    function calamityTag(c) {{
      if (!c || c.result !== 'Calamity pass') return '';
      const ks = (c.waived_keys && c.waived_keys.length) ? c.waived_keys.map(k => 'G' + k).join(', ') : 'G3b/5/6';
      return `CALAMITY · ${{ks}}`;
    }}

    function updateTabCounts() {{
      const incCal = document.getElementById('toggle-calamities') && document.getElementById('toggle-calamities').checked;
      const base = SCREENER_DATA.companies.filter(c => currentMarket === 'all' || c.universe === currentMarket);
      const qpass = base.filter(c => c.result === 'Quality pass');
      const calamity = base.filter(c => c.result === 'Calamity pass');
      const shortlist = base.filter(c => (c.result === 'Quality pass' || (incCal && c.result === 'Calamity pass')) && c.val_status === 'Below PAR');
      document.getElementById('count-shortlist').textContent = shortlist.length;
      document.getElementById('count-qpass').textContent = qpass.length;
      document.getElementById('count-calamity').textContent = calamity.length;
      document.getElementById('count-all').textContent = base.length;
    }}

    function setTab(tab) {{
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
        return;
      }}

      // Show/hide failing gate filter & shortlist calamity toggle
      document.getElementById('filter-gate').style.display = (tab === 'all') ? 'inline-block' : 'none';
      document.getElementById('toggle-calamities-wrap').style.display = (tab === 'shortlist') ? 'inline-flex' : 'none';

      // Default sort columns per tab
      if (tab === 'shortlist' || tab === 'calamity') {{
        sortColumn = 'irr_5y';
        sortAsc = false;
      }} else if (tab === 'qpass') {{
        sortColumn = 'roic_used';
        sortAsc = false;
      }} else if (tab === 'all') {{
        sortColumn = 'ticker';
        sortAsc = true;
      }}

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
      viewMode = mode;
      document.getElementById('view-table-btn').classList.toggle('active', mode === 'table');
      document.getElementById('view-cards-btn').classList.toggle('active', mode === 'cards');
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

      const incCal = document.getElementById('toggle-calamities') && document.getElementById('toggle-calamities').checked;

      return SCREENER_DATA.companies.filter(c => {{
        // Tab restriction
        if (currentTab === 'shortlist') {{
          const okRes = (c.result === 'Quality pass') || (incCal && c.result === 'Calamity pass');
          if (!okRes || c.val_status !== 'Below PAR') return false;
        }}
        if (currentTab === 'qpass' && c.result !== 'Quality pass') return false;
        if (currentTab === 'calamity' && c.result !== 'Calamity pass') return false;

        // Market
        if (currentMarket !== 'all' && c.universe !== currentMarket) return false;

        // Sector
        if (sector !== 'all' && c.sector !== sector) return false;

        // Moat
        if (moat !== 'all' && c.g3a_moat_archetype !== moat) return false;

        // Gate
        if (currentTab === 'all' && gate !== 'all') {{
          if (gate === 'Quality pass' && c.result !== 'Quality pass') return false;
          if (gate === 'Calamity pass' && c.result !== 'Calamity pass') return false;
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

        if ((vA === null || vA === undefined) && (vB === null || vB === undefined)) return 0;
        if (vA === null || vA === undefined) return 1;
        if (vB === null || vB === undefined) return -1;

        if (typeof vA === 'string') {{
          return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
        }}
        return sortAsc ? (vA - vB) : (vB - vA);
      }});
    }}

    function handleSort(col) {{
      if (sortColumn === col) {{
        sortAsc = !sortAsc;
      }} else {{
        sortColumn = col;
        sortAsc = (col === 'ticker' || col === 'company' || col === 'vs_par' || col === 'cur_mult');
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
        customOpt.value = targetVal;
        customOpt.textContent = `Sort: ${{sortColumn}} (${{sortAsc ? '▲ Asc' : '▼ Desc'}})`;
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

    function renderCurrentView() {{
      updateTabCounts();
      if (currentTab === 'methodology') return;
      const data = sortData(getFilteredData());
      const empty = document.getElementById('empty-state');
      const isEmpty = (data.length === 0);
      empty.style.display = isEmpty ? 'block' : 'none';

      document.getElementById('table-view').style.display = (viewMode === 'table' && !isEmpty) ? 'block' : 'none';
      document.getElementById('cards-view').style.display = (viewMode === 'cards' && !isEmpty) ? 'block' : 'none';

      renderTable(data);
      renderCards(data);
    }}

    function renderTable(data) {{
      const thead = document.getElementById('table-head');
      const tbody = document.getElementById('table-body');

      // Define columns per tab (Shortlist, Quality Pass, and Calamity share the exact same core columns in order)
      const coreValuationCols = [
        {{ key: 'ticker', label: 'Ticker' }},
        {{ key: 'company', label: 'Company' }},
        {{ key: 'country', label: 'Country' }},
        {{ key: 'price', label: 'Price', num: true }},
        {{ key: 'sales_1y', label: '1Y Growth', num: true }},
        {{ key: 'sales_cagr', label: '3–5Y Growth', num: true }},
        {{ key: 'opcost_cagr', label: 'OpCost g', num: true }},
        {{ key: 'g_org_exp', label: 'Growth Ceiling', num: true }},
        {{ key: 'buyback_yield', label: 'Buyback', num: true }},
        {{ key: 'g_market', label: 'Mkt Implied g', num: true }},
        {{ key: 'g_gap', label: 'g Margin', num: true }},
        {{ key: 'par_val', label: 'Fair Value', num: true }},
        {{ key: 'vs_par', label: 'Discount', num: true }},
        {{ key: 'cur_mult', label: 'Cur P/E', num: true }},
        {{ key: 'par_mult', label: 'Fair P/E', num: true }},
        {{ key: 'irr_5y', label: '5Y Exp IRR', num: true }},
        {{ key: 'roic_used', label: 'Op ROIC', num: true }},
        {{ key: 'g4_cap', label: 'Our CAP', num: true }},
        {{ key: 'cap_implied', label: 'Mkt CAP', num: true }},
        {{ key: 'cap_gap', label: 'CAP Gap', num: true }},
        {{ key: 'g3a_moat_archetype', label: 'Moat Archetype' }}
      ];
      let cols = [];
      if (currentTab === 'shortlist') {{
        cols = [...coreValuationCols];
      }} else if (currentTab === 'qpass') {{
        cols = [
          ...coreValuationCols,
          {{ key: 'fcf_conv', label: 'FCF Conv', num: true }},
          {{ key: 'val_status', label: 'Valuation' }},
          {{ key: 'sector', label: 'Sector' }}
        ];
      }} else if (currentTab === 'calamity') {{
        cols = [
          ...coreValuationCols,
          {{ key: 'waived_gates', label: 'Waived Gate(s)' }},
          {{ key: 'val_status', label: 'Valuation' }}
        ];
      }} else {{
        cols = [
          {{ key: 'ticker', label: 'Ticker' }},
          {{ key: 'company', label: 'Company' }},
          {{ key: 'country', label: 'Country' }},
          {{ key: 'sector', label: 'Sector' }},
          {{ key: 'result', label: 'Status' }},
          {{ key: 'rejected_at', label: 'Failing Gate / Stage' }},
          {{ key: 'g3a_moat_archetype', label: 'Moat Archetype' }},
          {{ key: 'g4_cap', label: 'CAP', num: true }}
        ];
      }}

      // Build THEAD
      let thHtml = '<tr>';
      cols.forEach(c => {{
        const isSorted = sortColumn === c.key;
        const arrow = isSorted ? (sortAsc ? ' ▲' : ' ▼') : '';
        const cls = (isSorted ? 'sorted ' : '') + (c.num ? 'num' : '');
        thHtml += `<th class="${{cls}}" onclick="handleSort('${{c.key}}')">${{c.label}}${{arrow}}</th>`;
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
            const cTag = (c.result === 'Calamity pass')
              ? ` <span class="badge badge-amber" style="font-size: 9px; padding: 1px 5px; margin-left: 4px;">${{escHtml(calamityTag(c))}}</span>`
              : '';
            cellContent = `<span class="cell-ticker">${{escHtml(val)}}</span>${{cTag}}`;
          }} else if (col.key === 'company') {{
            cellContent = `<div class="cell-company" title="${{escHtml(val)}}">${{escHtml(val)}}</div>`;
          }} else if (col.key === 'waived_gates') {{
            cellContent = `<span class="badge badge-amber">${{escHtml(calamityTag(c))}}</span>`;
          }} else if (col.key === 'vs_par') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const badgeClass = val <= 0 ? 'badge-green' : 'badge-amber';
              cellContent = `<span class="badge ${{badgeClass}}">${{fmtPct(val, true)}}</span>`;
            }}
          }} else if (col.key === 'irr_5y') {{
            if (val === null || val === undefined) cellContent = '-';
            else {{
              const color = val >= 0.12 ? 'var(--green)' : (val >= 0.08 ? 'var(--accent)' : 'var(--text-muted)');
              cellContent = `<strong style="color: ${{color}};">${{fmtPct(val)}}</strong>`;
            }}
          }} else if (col.key === 'val_status') {{
            const bCls = val === 'Below PAR' ? 'badge-green' : (val === 'Above PAR' ? 'badge-amber' : 'badge-gray');
            cellContent = `<span class="badge ${{bCls}}">${{escHtml(val)}}</span>`;
          }} else if (col.key === 'result') {{
            const bCls = val === 'Quality pass' ? 'badge-green' : (val === 'Calamity pass' ? 'badge-amber' : (val.startsWith('Rejected') ? 'badge-red' : 'badge-gray'));
            cellContent = `<span class="badge ${{bCls}}">${{escHtml(val)}}</span>`;
          }} else if (col.key === 'rejected_at') {{
            if (c.result === 'Calamity pass') {{
              cellContent = `<span style="color: var(--amber); font-size: 11px;">Waived: ${{escHtml((c.waived_gates || []).join(', '))}}</span>`;
            }} else {{
              cellContent = escHtml(val) || '-';
            }}
          }} else if (col.key === 'price' || col.key === 'par_val') {{
            cellContent = fmtPrice(val, c.quote_currency);
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
          }} else if (col.key === 'roic_used' || col.key === 'fcf_conv' || col.key === 'sales_cagr' || col.key === 'opcost_cagr' || col.key === 'g_org_exp' || col.key === 'g_start' || col.key === 'g_imp' || col.key === 'g_exp') {{
            cellContent = fmtPct(val);
          }} else if (col.key === 'g_market') {{
            cellContent = fmtPct(val, true);
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
            cellContent = val ? `${{val}}y` : '-';
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

    function triadCardsHtml(c) {{
      const g1y = fmtPct(c.sales_1y, true);
      const gCeil = fmtPct(c.g_org_exp !== null && c.g_org_exp !== undefined ? c.g_org_exp : c.g_imp);
      const gMkt = fmtPct(c.g_market, true);
      const gGap = c.g_gap !== null && c.g_gap !== undefined ? fmtPct(c.g_gap, true) : '-';
      const gColor = (c.g_gap !== null && c.g_gap !== undefined) ? (c.g_gap >= 0 ? 'var(--green)' : 'var(--red)') : 'var(--text-muted)';
      const cOur = c.g4_cap ? `${{c.g4_cap}}y` : '-';
      const cMkt = (c.cap_implied !== null && c.cap_implied !== undefined) ? `${{fmtNum(c.cap_implied, 1)}}y` : '-';
      const cGap = fmtSignedYears(c.cap_gap);
      const cColor = (c.cap_gap !== null && c.cap_gap !== undefined) ? (c.cap_gap >= 0 ? 'var(--green)' : 'var(--red)') : 'var(--text-muted)';
      return `
        <div class="card-metric-cell">
          <div class="card-metric-label">Growth (1Y / Ceiling / Mkt / Gap)</div>
          <div class="card-metric-val" style="font-size: 11.5px;">
            ${{g1y}} / ${{gCeil}} / ${{gMkt}} <span style="color:${{gColor}};">(${{gGap}})</span>
          </div>
        </div>
        <div class="card-metric-cell">
          <div class="card-metric-label">Runway (Our / Mkt / Gap)</div>
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

        if (currentTab === 'shortlist' || currentTab === 'qpass' || currentTab === 'calamity') {{
          const vsParText = c.vs_par !== null && c.vs_par !== undefined ? `${{fmtPct(c.vs_par, true)}} vs FV` : escHtml(c.val_status);
          const vsParCls = (c.vs_par !== null && c.vs_par !== undefined)
            ? (c.vs_par <= 0 ? 'badge-green' : 'badge-amber')
            : (c.val_status === 'Below PAR' ? 'badge-green' : (c.val_status === 'Above PAR' ? 'badge-amber' : 'badge-gray'));
          const calBadge = c.result === 'Calamity pass' ? `<span class="badge badge-amber" style="margin-right:4px;">${{escHtml(calamityTag(c))}}</span>` : '';
          badgeHtml = `${{calBadge}}<span class="badge ${{vsParCls}}">${{vsParText}}</span>`;
          metricsHtml = `
            <div class="card-metric-cell">
              <div class="card-metric-label">5Y Exp IRR</div>
              <div class="card-metric-val" style="color: ${{c.irr_5y >= 0.12 ? 'var(--green)' : 'var(--accent)'}};">${{fmtPct(c.irr_5y)}}</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label">Price / Fair Value</div>
              <div class="card-metric-val">${{fmtPrice(c.price, c.quote_currency)}} / ${{fmtPrice(c.par_val)}}</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label">Cur P/E / Fair P/E</div>
              <div class="card-metric-val">${{fmtNum(c.cur_mult)}}x / ${{fmtNum(c.par_mult)}}x</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label">Op ROIC • Buyback</div>
              <div class="card-metric-val" style="font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${{fmtPct(c.roic_used)}} • BB ${{fmtPct(c.buyback_yield, true)}}
              </div>
            </div>
          ` + triadCardsHtml(c);
        }} else {{
          const bCls = c.result === 'Quality pass' ? 'badge-green' : (c.result === 'Calamity pass' ? 'badge-amber' : (c.result.startsWith('Rejected') ? 'badge-red' : 'badge-gray'));
          badgeHtml = `<span class="badge ${{bCls}}">${{escHtml(c.result)}}</span>`;
          const stageColor = c.result === 'Quality pass' ? 'var(--green)' : (c.result === 'Calamity pass' ? 'var(--amber)' : 'var(--red)');
          const stageText = c.result === 'Calamity pass'
            ? `⚠ Waived: ${{(c.waived_gates || []).join(', ')}}`
            : (escHtml(c.rejected_at) || (c.result === 'Quality pass' ? '✓ Passed All 6 Reject Gates' : escHtml(c.result)));
          metricsHtml = `
            <div class="card-metric-cell" style="grid-column: span 2;">
              <div class="card-metric-label">Gate Stage / Result</div>
              <div class="card-metric-val" style="font-size: 12px; color: ${{stageColor}};">
                ${{stageText}}
              </div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label">Moat Archetype</div>
              <div class="card-metric-val" style="font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${{escHtml(c.g3a_moat_archetype) || '-'}}</div>
            </div>
            <div class="card-metric-cell">
              <div class="card-metric-label">Moat Runway (CAP)</div>
              <div class="card-metric-val">${{c.g4_cap ? c.g4_cap + 'y CAP' : '-'}}</div>
            </div>
          `;
        }}

        cardsHtml += `
          <div class="company-card ${{isSelected ? 'selected' : ''}}" data-id="${{c.id}}" onclick="openDrawer('${{c.id}}')">
            <div class="card-header">
              <div class="card-ticker-group">
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
        valBadge.textContent = c.val_status + (c.vs_par !== null ? ` (${{fmtPct(c.vs_par, true)}})` : '');
        valBadge.className = `badge ${{c.val_status === 'Below PAR' ? 'badge-green' : 'badge-amber'}}`;
      }} else if (c.result === 'Calamity pass') {{
        valBadge.textContent = `${{calamityTag(c)}} • ${{c.val_status}}` + (c.vs_par !== null ? ` (${{fmtPct(c.vs_par, true)}})` : '');
        valBadge.className = 'badge badge-amber';
      }} else {{
        valBadge.textContent = c.result;
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
      const waivedKeys = c.waived_keys || [];
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
        }} else if (st === 'fail' && c.result === 'Calamity pass' && waivedKeys.includes(g.key)) {{
          bg = 'rgba(245, 158, 11, 0.25)';
          color = 'var(--amber)';
          icon = '⚠';
          label = 'WAIVED';
        }} else if (st === 'fail') {{
          bg = 'rgba(244, 63, 94, 0.25)';
          color = 'var(--red)';
          icon = '✕';
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
      }} else if (c.result === 'Calamity pass') {{
        const wList = (c.waived_gates || []).join(', ');
        verdictEl.innerHTML = `<span style="color: var(--amber);">⚠ Conditional Calamity Pass (Waived: ${{escHtml(wList)}}) — Enters Quantitative PAR Funnel</span>`;
      }} else {{
        verdictEl.innerHTML = `<span style="color: var(--red);">✕ ${{c.rejected_at || c.result}}</span>`;
      }}

      // Qualitative Dossier
      document.getElementById('dossier-moat-type').textContent = c.g3a_moat_archetype || 'None';
      document.getElementById('dossier-cap').textContent = c.g4_cap ? `${{c.g4_cap}} Years Runway` : 'Unassigned';

      // Calamity Note
      const calBox = document.getElementById('dossier-calamity-box');
      if (c.calamity_note) {{
        document.getElementById('dossier-calamity-note').textContent = c.calamity_note;
        calBox.style.display = 'block';
      }} else {{
        calBox.style.display = 'none';
      }}

      // Moat Note
      const mnBox = document.getElementById('dossier-moat-note-box');
      if (c.g3m_moat_note) {{
        document.getElementById('dossier-moat-note').textContent = c.g3m_moat_note;
        mnBox.style.display = 'block';
      }} else {{
        mnBox.style.display = 'none';
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
      document.getElementById('dossier-cur-mult').textContent = fmtNum(c.cur_mult) + 'x';
      document.getElementById('dossier-par-mult').textContent = fmtNum(c.par_mult) + 'x';
      document.getElementById('dossier-irr').textContent = fmtPct(c.irr_5y);

      const opRoicVal = (c.roic_est !== null && c.roic_est !== undefined)
        ? `${{fmtPct(c.roic_est)}} (Est.)`
        : ((c.roic_operating !== null && c.roic_operating !== undefined) ? fmtPct(c.roic_operating) : fmtPct(c.roic_used));
      document.getElementById('dossier-roic-op').textContent = opRoicVal;
      document.getElementById('dossier-roic-gaap').textContent = fmtPct(c.roic_median);
      document.getElementById('dossier-fcf-conv').textContent = fmtPct(c.fcf_conv);

      const gOrgDisp = fmtPct(c.g_org_exp !== null && c.g_org_exp !== undefined ? c.g_org_exp : c.g_start);
      const gExpDisp = fmtPct(c.g_exp !== null && c.g_exp !== undefined ? c.g_exp : c.g_imp);
      document.getElementById('dossier-g-imp').textContent = (c.g_exp !== c.g_org_exp && c.g_exp !== null) ? `${{gOrgDisp}} → ${{gExpDisp}}` : gOrgDisp;
      const scaleEl = document.getElementById('dossier-scale-tier');
      if (scaleEl) {{
        const parts = [];
        if (c.g_est !== null && c.g_est !== undefined) {{
          parts.push(`Override ${{fmtPct(c.g_est)}}`);
        }} else {{
          if (c.sales_1y !== null && c.sales_1y !== undefined) parts.push(`1Y ${{fmtPct(c.sales_1y, true)}}`);
          if (c.sales_cagr !== null && c.sales_cagr !== undefined) parts.push(`5Y ${{fmtPct(c.sales_cagr)}}`);
          if (c.opcost_cagr !== null && c.opcost_cagr !== undefined) parts.push(`OpCost ${{fmtPct(c.opcost_cagr)}}`);
        }}
        if (c.buyback_yield !== null && c.buyback_yield !== undefined) parts.push(`BB ${{fmtPct(c.buyback_yield, true)}}`);
        scaleEl.textContent = parts.join(' · ');
      }}
      document.getElementById('dossier-g-market').textContent = fmtPct(c.g_market, true);
      const gMarginEl = document.getElementById('dossier-g-margin');
      gMarginEl.textContent = c.g_gap !== null && c.g_gap !== undefined ? fmtPct(c.g_gap, true) : '-';
      gMarginEl.style.color = (c.g_gap !== null && c.g_gap !== undefined) ? (c.g_gap >= 0 ? 'var(--green)' : 'var(--red)') : 'var(--text-main)';

      document.getElementById('dossier-cap-our').textContent = c.g4_cap ? `${{c.g4_cap}}y` : '-';
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
      // 1. OUR CAP
      document.getElementById('audit-cap-summary').textContent = c.g4_cap ? `${{c.g4_cap}}y Runway` : 'Unassigned';
      document.getElementById('audit-cap-years').textContent = c.g4_cap ? `${{c.g4_cap}} Years` : 'None';
      const capTierText = c.g4_cap >= 30 ? 'Fortress (30y+)' : (c.g4_cap >= 20 ? 'Compounder (20y+)' : (c.g4_cap ? 'Standard (<20y)' : 'Unassigned'));
      document.getElementById('audit-cap-tier').textContent = capTierText;
      document.getElementById('audit-cap-pers').textContent = (c.pers !== null && c.pers !== undefined) ? `${{Math.round(c.pers * 100)}}%` : (c.g4_cap >= 30 ? '85%' : (c.g4_cap >= 20 ? '75%' : '62%'));
      const effSlope = (c.eff_g_mult !== null && c.eff_g_mult !== undefined) ? c.eff_g_mult : c.g_mult;
      document.getElementById('audit-cap-gmult').textContent = (effSlope !== null && effSlope !== undefined) ? `${{Math.round(effSlope)}}x` : '-';
      const gmultSubEl = document.getElementById('audit-cap-gmult-sub');
      if (gmultSubEl) gmultSubEl.textContent = (effSlope !== null && effSlope !== undefined) ? `+${{(effSlope / 100).toFixed(2)}}x P/E per 1% g` : 'Points per 1% g';
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

      // 2. GROWTH CEILING (g₀) & PER-SHARE CEILING (g_exp)
      document.getElementById('audit-gexp-summary').textContent = `${{fmtPct(c.g_org_exp)}} → ${{fmtPct(c.g_exp)}}`;
      document.getElementById('audit-g1y-val').textContent = (c.sales_1y !== null && c.sales_1y !== undefined) ? fmtPct(c.sales_1y, true) : 'N/A';
      document.getElementById('audit-sales1y-val').textContent = fmtPct(c.sales_1y, true);
      const oc1yEl = document.getElementById('audit-opcost1y-val');
      if (oc1yEl) oc1yEl.textContent = fmtPct(c.opcost_1y, true);
      document.getElementById('audit-bb-val').textContent = fmtPct(c.buyback_yield, true);
      document.getElementById('audit-gdemand-val').textContent = (c.opcost_cagr !== null && c.opcost_cagr !== undefined) ? fmtPct(c.opcost_cagr) : fmtPct(c.sales_cagr);
      document.getElementById('audit-salescagr-val').textContent = fmtPct(c.sales_cagr);
      document.getElementById('audit-salesyrs-val').textContent = c.sales_cagr_yrs ? `${{c.sales_cagr_yrs}}Y` : '5Y';
      const ocCagrEl = document.getElementById('audit-opcostcagr-val');
      if (ocCagrEl) ocCagrEl.textContent = fmtPct(c.opcost_cagr);
      document.getElementById('audit-oecagr-val').textContent = fmtPct(c.cagr_oe_eps);
      document.getElementById('audit-gfund-val').textContent = (c.cap_growth !== null && c.cap_growth !== undefined) ? fmtPct(c.cap_growth) : 'N/A';
      document.getElementById('audit-capgrowth-val').textContent = fmtPct(c.cap_growth);
      document.getElementById('audit-roic-val').textContent = `${{fmtPct(c.roic_used)}} → ${{fmtPct(c.roic_exp)}}`;
      const rFadeEl = document.getElementById('audit-roicfade-val');
      if (rFadeEl) rFadeEl.textContent = (c.roic_fade_ratio !== null && c.roic_fade_ratio !== undefined) ? `${{c.roic_fade_ratio.toFixed(2)}}x` : '1.00x';
      document.getElementById('audit-retention-val').textContent = (c.retention !== null && c.retention !== undefined) ? fmtPct(c.retention) : ((c.retention_rate !== null && c.retention_rate !== undefined) ? fmtPct(c.retention_rate) : '-');
      const fadePers = c.pers || (c.g4_cap >= 30 ? 0.85 : (c.g4_cap >= 20 ? 0.75 : 0.62));
      document.getElementById('audit-fade-val').textContent = fmtPct(c.g_org_exp);
      document.getElementById('audit-graw-val').textContent = fmtPct(c.g_org_exp);
      document.getElementById('audit-glog-val').textContent = fmtPct(c.g_exp);
      document.getElementById('audit-fadew-val').textContent = `${{Math.round(fadePers * 100)}}%`;
      document.getElementById('audit-sizefactor-val').textContent = (c.size_factor !== null && c.size_factor !== undefined) ? `${{c.size_factor.toFixed(2)}}x` : '1.00x';
      document.getElementById('audit-scaletier-val').textContent = c.scale_tier || 'MID/SM';
      document.getElementById('audit-scalecap-val').textContent = fmtPct(c.scale_cap);
      document.getElementById('audit-gest-val').textContent = (c.g_est !== null && c.g_est !== undefined) ? fmtPct(c.g_est) : 'None';

      // Binding / Dominant Driver Badge
      const boxSupply = document.getElementById('box-filter-supply');
      const boxDemand = document.getElementById('box-filter-demand');
      const boxFade = document.getElementById('box-filter-fade');
      const boxGravity = document.getElementById('box-filter-gravity');
      [boxSupply, boxDemand, boxFade, boxGravity].forEach(el => {{ if (el) el.classList.remove('binding'); }});

      const badge = document.getElementById('audit-binding-badge');
      if (c.g_est !== null && c.g_est !== undefined) {{
        badge.textContent = `Analyst Override (${{fmtPct(c.g_est)}})`;
        badge.className = 'binding-badge active-constraint';
      }} else if (c.opcost_cagr !== null && c.opcost_cagr !== undefined) {{
        if (boxDemand) boxDemand.classList.add('binding');
        badge.textContent = `OpCost Ceiling g₀ ${{fmtPct(c.g_org_exp)}} → 3.5% CAP Fade`;
        badge.className = 'binding-badge active-constraint';
      }} else {{
        if (boxGravity) boxGravity.classList.add('binding');
        badge.textContent = `Growth Ceiling g₀ ${{fmtPct(c.g_org_exp)}} → 3.5% CAP Fade`;
        badge.className = 'binding-badge active-constraint';
      }}

      // 3. Explicit Mauboussin-Fade DCF Fair Multiple
      document.getElementById('audit-parmult-summary').textContent = `${{fmtNum(c.par_mult)}}x`;
      const peMm = (c.pe_mm !== null && c.pe_mm !== undefined) ? c.pe_mm : c.t_growth;
      const peMck = (c.pe_mck !== null && c.pe_mck !== undefined) ? c.pe_mck : c.t_roic;
      const peVd = (c.pe_vd !== null && c.pe_vd !== undefined) ? c.pe_vd : c.raw_par;
      document.getElementById('audit-tgrowth-val').textContent = (peMm !== null && peMm !== undefined) ? `${{fmtNum(peMm)}}x` : '-';
      document.getElementById('audit-thist-val').textContent = (c.t_hist !== null && c.t_hist !== undefined) ? `${{fmtNum(c.t_hist)}}x` : '-';
      document.getElementById('audit-troic-val').textContent = (peMck !== null && peMck !== undefined) ? `${{fmtNum(peMck)}}x` : '-';
      document.getElementById('audit-rawpar-val').textContent = (peVd !== null && peVd !== undefined) ? `${{fmtNum(peVd)}}x` : '-';
      document.getElementById('audit-reinv-val').textContent = (c.reinv_eff !== null && c.reinv_eff !== undefined) ? `${{Math.round(c.reinv_eff * 100)}}%` : '100%';
      const hasHistRange = (c.mult_low_5y !== null && c.mult_low_5y !== undefined && c.mult_high_5y !== null && c.mult_high_5y !== undefined);
      const rangeStr = hasHistRange
        ? `${{fmtNum(c.mult_low_5y)}}x–${{fmtNum(c.mult_high_5y)}}x`
        : ((c.mult_high_5y !== null && c.mult_high_5y !== undefined) ? `${{fmtNum(c.mult_high_5y)}}x` : 'N/A (<12m trading)');
      document.getElementById('audit-mh-val').textContent = rangeStr;
      const thistSubEl = document.getElementById('audit-thist-sub');
      if (thistSubEl) thistSubEl.textContent = hasHistRange ? 'Reference Only (0% Weight in Pure DCF)' : 'No 5Y History (100% Pure DCF)';
      document.getElementById('audit-peakeps-val').textContent = fmtPrice(c.peak_eps, c.quote_currency);
    }}

    function initValuationSandbox(c) {{
      if (!c) return;

      const cap = (c.g4_cap !== null && c.g4_cap !== undefined) ? c.g4_cap : null;

      // Base growth fallback hierarchy: sales_cagr -> cagr_oe_eps -> sales_1y -> g_start -> 8.0%
      const baseGrowth = (c.sales_cagr !== null && c.sales_cagr !== undefined) ? c.sales_cagr
        : ((c.cagr_oe_eps !== null && c.cagr_oe_eps !== undefined) ? c.cagr_oe_eps
        : ((c.sales_1y !== null && c.sales_1y !== undefined) ? c.sales_1y
        : ((c.g_start !== null && c.g_start !== undefined) ? c.g_start : 0.08)));

      const salescagr = (c.sales_cagr !== null && c.sales_cagr !== undefined) ? (c.sales_cagr * 100) : (baseGrowth * 100);
      const sales1y = (c.sales_1y !== null && c.sales_1y !== undefined) ? (c.sales_1y * 100) : (baseGrowth * 100);
      const capgrowth = (c.cap_growth !== null && c.cap_growth !== undefined) ? (c.cap_growth * 100) : (baseGrowth * 100);
      const roic = (c.roic_used !== null && c.roic_used !== undefined) ? (c.roic_used * 100)
        : ((c.roic_operating !== null && c.roic_operating !== undefined) ? (c.roic_operating * 100)
        : ((c.roic_median !== null && c.roic_median !== undefined) ? (c.roic_median * 100) : 18.0));

      const bb = (c.buyback_yield !== null && c.buyback_yield !== undefined) ? (c.buyback_yield * 100) : 0.0;
      const peakeps = (c.peak_eps !== null && c.peak_eps !== undefined) ? c.peak_eps : ((c.price && c.price > 0) ? c.price / 15 : null);
      const ml = (c.mult_low_5y !== null && c.mult_low_5y !== undefined) ? c.mult_low_5y : null;
      const mh = (c.mult_high_5y !== null && c.mult_high_5y !== undefined) ? c.mult_high_5y : null;
      const gest = (c.g_est !== null && c.g_est !== undefined) ? (c.g_est * 100) : null;

      sbBaseline = {{ cap, sales1y, salescagr, capgrowth, roic, bb, peakeps, ml, mh, gest }};
      sbCurrent = {{ ...sbBaseline }};

      syncSandboxInputs();
      recalcSandboxValuation();
    }}

    function syncSandboxInputs() {{
      const c = SCREENER_DATA.companies.find(item => item.id === selectedCompanyId) || {{}};

      // Update CAP Pills
      document.querySelectorAll('.cap-pill-btn').forEach(btn => {{
        btn.classList.toggle('active', sbCurrent.cap !== null && parseInt(btn.dataset.cap, 10) === sbCurrent.cap);
      }});
      const capEl = document.getElementById('sb-val-cap');
      if (capEl) capEl.textContent = sbCurrent.cap !== null ? `${{sbCurrent.cap}}y` : 'Unassigned';

      // Sliders & value displays with dynamic min/max adjustment to avoid clipping outliers
      const s1y = document.getElementById('sb-slider-sales1y');
      if (s1y) {{
        s1y.min = Math.min(-20, Math.floor(sbCurrent.sales1y - 5));
        s1y.max = Math.max(40, Math.ceil(sbCurrent.sales1y + 5));
        s1y.value = sbCurrent.sales1y;
        document.getElementById('sb-val-sales1y').textContent = `${{sbCurrent.sales1y.toFixed(1)}}%`;
      }}

      const sCagr = document.getElementById('sb-slider-salescagr');
      if (sCagr) {{
        sCagr.min = Math.min(-20, Math.floor(sbCurrent.salescagr - 5));
        sCagr.max = Math.max(40, Math.ceil(sbCurrent.salescagr + 5));
        sCagr.value = sbCurrent.salescagr;
        document.getElementById('sb-val-salescagr').textContent = `${{sbCurrent.salescagr.toFixed(1)}}%`;
      }}

      const sCapG = document.getElementById('sb-slider-capgrowth');
      if (sCapG) {{
        sCapG.min = Math.min(-20, Math.floor(sbCurrent.capgrowth - 5));
        sCapG.max = Math.max(40, Math.ceil(sbCurrent.capgrowth + 5));
        sCapG.value = sbCurrent.capgrowth;
        document.getElementById('sb-val-capgrowth').textContent = `${{sbCurrent.capgrowth.toFixed(1)}}%`;
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
        lblRoicText.textContent = (c.roic_est !== null && c.roic_est !== undefined)
          ? 'Normalized Operating ROIC'
          : (c.uses_gaap_roic ? 'GAAP ROIC (incl. Goodwill)' : 'Tangible Operating ROIC');
      }}

      const sBb = document.getElementById('sb-slider-bb');
      if (sBb) {{
        sBb.value = sbCurrent.bb;
        document.getElementById('sb-val-bb').textContent = `${{sbCurrent.bb.toFixed(1)}}%`;
      }}

      // Numeric inputs
      const inPeak = document.getElementById('sb-input-peakeps');
      if (inPeak) inPeak.value = (sbCurrent.peakeps !== null && sbCurrent.peakeps !== undefined) ? sbCurrent.peakeps.toFixed(2) : '';
      const valPeakEl = document.getElementById('sb-val-peakeps');
      if (valPeakEl) valPeakEl.textContent = (sbCurrent.peakeps !== null && sbCurrent.peakeps !== undefined) ? fmtPrice(sbCurrent.peakeps, c.quote_currency) : '-';

      const inMl = document.getElementById('sb-input-ml');
      if (inMl) inMl.value = (sbCurrent.ml !== null && sbCurrent.ml !== undefined) ? sbCurrent.ml.toFixed(1) : '';

      const inMh = document.getElementById('sb-input-mh');
      if (inMh) inMh.value = (sbCurrent.mh !== null && sbCurrent.mh !== undefined) ? sbCurrent.mh.toFixed(1) : '';

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

    function onSandboxInputChange() {{
      const c = SCREENER_DATA.companies.find(item => item.id === selectedCompanyId) || {{}};

      const peInput = document.getElementById('sb-input-peakeps').value.trim();
      const pe = parseFloat(peInput);
      sbCurrent.peakeps = (!isNaN(pe) && pe > 0) ? pe : null;
      const valPeakEl = document.getElementById('sb-val-peakeps');
      if (valPeakEl) valPeakEl.textContent = (sbCurrent.peakeps !== null && sbCurrent.peakeps !== undefined) ? fmtPrice(sbCurrent.peakeps, c.quote_currency) : '-';

      const mlVal = document.getElementById('sb-input-ml').value.trim();
      const parsedMl = parseFloat(mlVal);
      sbCurrent.ml = (!isNaN(parsedMl) && parsedMl > 0) ? parsedMl : null;

      const mhVal = document.getElementById('sb-input-mh').value.trim();
      const parsedMh = parseFloat(mhVal);
      sbCurrent.mh = (!isNaN(parsedMh) && parsedMh > 0) ? parsedMh : null;

      const gestVal = document.getElementById('sb-input-gest').value.trim();
      if (gestVal === '') {{
        sbCurrent.gest = null;
        document.getElementById('sb-val-gest').textContent = 'None';
      }} else {{
        const parsedG = parseFloat(gestVal);
        if (!isNaN(parsedG)) {{
          sbCurrent.gest = parsedG;
          document.getElementById('sb-val-gest').textContent = `${{parsedG.toFixed(1)}}%`;
        }}
      }}
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
      sbCurrent = {{ ...sbBaseline }};
      syncSandboxInputs();
      recalcSandboxValuation();
    }}

    function copySandboxOverrideJson() {{
      const c = SCREENER_DATA.companies.find(item => item.id === selectedCompanyId);
      if (!c) return;
      const overrideObj = {{
        id: c.id,
        ticker: c.ticker,
        universe: c.universe,
        company: c.company,
        qualitative: {{
          gate_4_runway_cap: sbCurrent.cap
        }},
        quantitative_overrides: {{
          peak_eps_est: (sbCurrent.peakeps !== null && sbCurrent.peakeps !== undefined) ? Math.round(sbCurrent.peakeps * 100) / 100 : null,
          g_est: sbCurrent.gest !== null ? Math.round(sbCurrent.gest * 10) / 1000 : null,
          roic_est: Math.round(sbCurrent.roic * 10) / 1000,
          fin_note: `Sandbox sensitivity: CAP ${{sbCurrent.cap !== null ? sbCurrent.cap + 'y' : 'Unassigned'}}, g ${{sbCurrent.gest !== null ? sbCurrent.gest : sbCurrent.salescagr}}%, ROIC ${{sbCurrent.roic}}%`
        }}
      }};
      const jsonStr = JSON.stringify(overrideObj, null, 2);
      navigator.clipboard.writeText(jsonStr).then(() => {{
        const btn = document.getElementById('btn-copy-sandbox');
        const orig = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => {{ btn.textContent = orig; }}, 2000);
      }}).catch(() => {{
        prompt('Copy Override JSON:', jsonStr);
      }});
    }}

    function explicitDcfMultiple(g0, roic0, nCap, k=0.085, gTerm=0.035, roicTermFloor=0.12, roicTermCap=0.20, isFiniteConc=false) {{
      const nSteps = Math.max(1, Math.round(nCap));
      const roicStart = Math.max(0.05, roic0);
      const roicTerm = Math.max(roicTermFloor, Math.min(roicStart, roicTermCap));
      let pvStage1 = 0.0;
      let earn = 1.0;
      for (let t = 1; t <= nSteps; t++) {{
        const frac = (t - 1.0) / nSteps;
        const gT = g0 - frac * (g0 - gTerm);
        const roicT = Math.max(0.05, roicStart - frac * (roicStart - roicTerm));
        earn = earn * (1.0 + gT);
        const reinvT = Math.min(0.95, Math.max(0.0, gT) / roicT);
        const fcfT = earn * (1.0 - reinvT);
        pvStage1 += fcfT / Math.pow(1.0 + k, t);
      }}
      let pvStage2 = 0.0;
      if (!isFiniteConc) {{
        const earnTerm = earn * (1.0 + gTerm);
        const reinvTerm = Math.min(0.95, Math.max(0.0, gTerm) / roicTerm);
        const fcfTerm = earnTerm * (1.0 - reinvTerm);
        const termVal = fcfTerm / Math.max(0.01, k - gTerm);
        pvStage2 = termVal / Math.pow(1.0 + k, nSteps);
      }}
      return {{ pvStage1, pvStage2, total: pvStage1 + pvStage2 }};
    }}

    function solveImpliedDcfGrowth(targetPe, roic0, nCap, k=0.085, gTerm=0.035, roicTermFloor=0.12, roicTermCap=0.20, isFiniteConc=false) {{
      if (!targetPe || targetPe <= 0) return null;
      let lo = -0.15, hi = 0.35;
      const peLo = explicitDcfMultiple(lo, roic0, nCap, k, gTerm, roicTermFloor, roicTermCap, isFiniteConc).total;
      if (targetPe <= peLo) return Math.round(lo * 10000) / 10000;
      const peHi = explicitDcfMultiple(hi, roic0, nCap, k, gTerm, roicTermFloor, roicTermCap, isFiniteConc).total;
      if (targetPe >= peHi) return Math.round(hi * 10000) / 10000;
      for (let i = 0; i < 40; i++) {{
        const mid = 0.5 * (lo + hi);
        const peMid = explicitDcfMultiple(mid, roic0, nCap, k, gTerm, roicTermFloor, roicTermCap, isFiniteConc).total;
        if (Math.abs(peMid - targetPe) < 1e-7) {{ lo = mid; hi = mid; break; }}
        if (peMid < targetPe) lo = mid;
        else hi = mid;
      }}
      return Math.round(0.5 * (lo + hi) * 10000) / 10000;
    }}

    function recalcSandboxValuation() {{
      const c = SCREENER_DATA.companies.find(item => item.id === selectedCompanyId);
      if (!c) return;

      const price = c.price;
      const peak_eps = sbCurrent.peakeps;
      const ml = sbCurrent.ml;
      const mh = sbCurrent.mh;
      const mc = c.market_cap_m;

      const size_factor = (c.size_factor !== null && c.size_factor !== undefined) ? c.size_factor : 1.0;
      const scale_cap = (c.scale_cap !== null && c.scale_cap !== undefined) ? c.scale_cap : 0.120;

      const fund_cap = sbCurrent.cap;
      let pers = 0.75;
      if (fund_cap !== null && fund_cap !== undefined) {{
        if (fund_cap >= 30) pers = 0.85;
        else if (fund_cap >= 20) pers = 0.75;
        else pers = 0.62;
      }}

      const bb_eff = Math.max(-0.03, Math.min(0.035, sbCurrent.bb / 100.0));
      const bb_pos = Math.max(0.0, bb_eff);
      const bb_org = Math.min(0.0, bb_eff);
      const s1_val = sbCurrent.sales1y / 100.0;
      const s5_val = sbCurrent.salescagr / 100.0;
      const cg_val = sbCurrent.capgrowth / 100.0;

      const s1Tweaked = (sbBaseline.sales1y !== undefined) && Math.abs(sbCurrent.sales1y - sbBaseline.sales1y) > 0.01;
      const s5Tweaked = (sbBaseline.salescagr !== undefined) && Math.abs(sbCurrent.salescagr - sbBaseline.salescagr) > 0.01;
      const cgTweaked = (sbBaseline.capgrowth !== undefined) && Math.abs(sbCurrent.capgrowth - sbBaseline.capgrowth) > 0.01;
      const isGrowthTweaked = s1Tweaked || s5Tweaked || cgTweaked;

      const deltaS1 = s1Tweaked ? (sbCurrent.sales1y - sbBaseline.sales1y) / 100.0 : 0.0;
      const deltaS5 = s5Tweaked ? (sbCurrent.salescagr - sbBaseline.salescagr) / 100.0 : 0.0;
      const oc_1y = (c.opcost_1y !== null && c.opcost_1y !== undefined) ? (c.opcost_1y + deltaS1) : null;
      const oc_cagr = (c.opcost_cagr !== null && c.opcost_cagr !== undefined) ? (c.opcost_cagr + deltaS5) : null;
      const g_oe = (c.cagr_oe_eps !== null && c.cagr_oe_eps !== undefined) ? (c.cagr_oe_eps + deltaS5) : null;

      // Mauboussin Galton ROIC Regression
      const roic_op = sbCurrent.roic / 100.0;
      const roic_avg = 0.12;
      const roic_log_k = 0.25;
      let roic_log = Math.round(Math.max(0.05, roic_op) * 10000) / 10000;
      let roic_exp = roic_log;
      let roic_fade_ratio = 1.0;
      if (roic_op > roic_avg) {{
        roic_log = Math.round((roic_avg + roic_log_k * Math.log(1.0 + (roic_op - roic_avg) / roic_log_k)) * 10000) / 10000;
        roic_exp = Math.round((pers * (roic_log - roic_avg) + roic_avg) * 10000) / 10000;
        roic_fade_ratio = Math.round((roic_exp / roic_log) * 10000) / 10000;
      }}

      // Normal Organic Growth Ceiling (g₀) Anchored on Operating Cost Base (OpCost CAGR)
      const g_base = 0.035;
      let base_org = g_base;
      if (oc_cagr !== null) {{
        base_org = oc_cagr;
      }} else if ((c.sales_cagr !== null && c.sales_cagr !== undefined) || s5Tweaked) {{
        base_org = s5_val;
      }} else if (g_oe !== null) {{
        base_org = g_oe - bb_pos;
      }} else if ((c.sales_1y !== null && c.sales_1y !== undefined) || s1Tweaked) {{
        base_org = s1_val;
      }} else if (c.g_implied !== null && c.g_implied !== undefined) {{
        base_org = c.g_implied - bb_pos;
      }}

      const eff_scale_cap = s5Tweaked ? 0.22 : scale_cap;
      const g_org_start = Math.round(Math.max(-0.04, Math.min(0.22, base_org + bb_org)) * 10000) / 10000;
      const g_start = Math.round(Math.max(-0.04, Math.min(0.22, base_org + bb_eff)) * 10000) / 10000;

      let g_exp = null, g_org_exp = null;
      if (sbCurrent.gest !== null && !isNaN(sbCurrent.gest)) {{
        const g_est_val = sbCurrent.gest / 100.0;
        g_org_exp = Math.round(Math.max(0.02, Math.min(eff_scale_cap, g_est_val > 0.02 ? g_est_val - bb_pos : g_est_val)) * 10000) / 10000;
        g_exp = Math.round(Math.max(0.02, Math.min(eff_scale_cap + bb_pos, g_est_val)) * 10000) / 10000;
      }} else {{
        g_org_exp = Math.round(Math.max(0.02, Math.min(eff_scale_cap, g_org_start)) * 10000) / 10000;
        g_exp = Math.round((g_org_exp + bb_pos) * 10000) / 10000;
      }}
      g_org_exp = Math.min(g_exp, g_org_exp);
      const bb_contrib = Math.round(Math.max(0.0, g_exp - g_org_exp) * 10000) / 10000;

      // Valuation
      const hasHistMults = Boolean(ml && mh);
      const hasValuationInputs = Boolean(price && peak_eps && peak_eps > 0 && (hasHistMults || fund_cap !== null || c.peak_eps_est !== null));
      let cur_mult = null, pe_vd = null, par_mult = null, par_val = null, vs_par = null, irr_5y = null, cap_implied = null, cap_gap = null, g_market = null, g_gap = null;

      if (hasValuationInputs) {{
        cur_mult = price / peak_eps;
        const g_org_val = (g_org_exp !== null && g_org_exp > 0) ? g_org_exp : 0.035;

        // Explicit N-Year Mauboussin-Fade DCF Fair Multiple (v6.35, r = 8.50%)
        const k = 0.085;
        const n_cap = (fund_cap !== null && fund_cap !== undefined && fund_cap > 0) ? fund_cap : 20.0;
        const roic_eff = Math.max(roic_exp, 0.05);
        const subInd = (c.sub_industry || '').trim();
        const fcfConv = (c.fcf_conv !== null && c.fcf_conv !== undefined) ? c.fcf_conv : null;
        const isPeakEdited = (sbBaseline.peakeps !== null && sbBaseline.peakeps !== undefined && peak_eps !== null) && Math.abs(peak_eps - sbBaseline.peakeps) > 0.01;
        const hasPeakOverride = (c.peak_eps_est !== null && c.peak_eps_est !== undefined) || isPeakEdited;
        const isMtmHoldco = !hasPeakOverride && !subInd.includes('Insurance Brokers') && (subInd.includes('Multi-Sector Holdings') || subInd.includes('Insurance')) && (
          fcfConv !== null ? (fcfConv < 0.25) : (subInd.includes('Multi-Sector Holdings') && (mh === null || mh < 12.0))
        );
        const isFiniteConc = (subInd.includes('Construction & Engineering') || subInd.includes('Highways & Railtracks')) && (fcfConv !== null && fcfConv > 1.25);
        let pe_mm, pe_mck, reinv_eff;
        if (isMtmHoldco) {{
          pe_mm = 1.0 / roic_eff;
          pe_mck = 0.0;
          pe_vd = pe_mm;
          reinv_eff = 1.0;
        }} else {{
          const reinv_stage1 = Math.min(0.95, Math.max(0.0, g_org_val) / roic_eff);
          reinv_eff = 1.0 - reinv_stage1;
          const dcf = explicitDcfMultiple(g_org_val, roic_eff, n_cap, k, g_base, roic_avg, 0.20, isFiniteConc);
          pe_mm = dcf.pvStage1;
          pe_mck = dcf.pvStage2;
          pe_vd = dcf.total;
        }}

        par_mult = pe_vd;
        par_val = par_mult * peak_eps;
        vs_par = price / par_val - 1.0;

        // Exact DCF-inverted Market-Implied Growth (g_market at r = 8.5%)
        if (isMtmHoldco) {{
          g_market = Math.round(Math.max(-0.15, Math.min(0.35, g_org_val + (cur_mult - par_mult) * (k - g_base))) * 10000) / 10000;
        }} else {{
          g_market = solveImpliedDcfGrowth(cur_mult, roic_eff, n_cap, k, g_base, roic_avg, 0.20, isFiniteConc);
        }}
        if (g_org_exp !== null && g_market !== null) {{
          g_gap = Math.round((g_org_exp - g_market) * 10000) / 10000;
        }}

        const dy = (mc && mc > 0 && c.dividends_ttm_m) ? Math.max(0.0, c.dividends_ttm_m / mc) : 0.0;
        const g_org_5y = (g_org_exp !== null)
          ? (isMtmHoldco ? g_org_exp : Math.round((g_org_exp - (2.0 / Math.max(5.0, n_cap)) * (g_org_exp - g_base)) * 10000) / 10000)
          : g_base;
        let g_irr = Math.round((g_org_5y + bb_contrib) * 10000) / 10000;
        if (bb_contrib > 0 && cur_mult > 0) {{
          const bb_fcf_cap = Math.max(0.0, (Math.max(0.0, reinv_eff) / cur_mult) - dy);
          g_irr = Math.round((g_org_5y + Math.min(bb_contrib, bb_fcf_cap)) * 10000) / 10000;
        }}
        if (price > 0 && par_val > 0 && g_irr !== null && g_irr > -1.0) {{
          const r_par = par_val / price;
          if (dy <= 1e-12) {{
            irr_5y = (1.0 + g_irr) * Math.pow(r_par, 0.2) - 1.0;
          }} else {{
            let u = Math.pow(r_par, -0.2) / (1.0 + dy);
            for (let i = 0; i < 12; i++) {{
              const u2 = u * u, u3 = u2 * u, u4 = u3 * u, u5 = u4 * u;
              const f_val = dy * (u + u2 + u3 + u4 + u5) + r_par * u5 - 1.0;
              if (Math.abs(f_val) < 1e-12) break;
              const f_deriv = dy * (1.0 + 2.0 * u + 3.0 * u2 + 4.0 * u3 + 5.0 * u4) + 5.0 * r_par * u4;
              if (f_deriv <= 0) break;
              u = Math.max(1e-6, u - f_val / f_deriv);
            }}
            irr_5y = (1.0 + g_irr) / u - 1.0;
          }}
        }}
        const pe_base = 1.0 / k;
        if (fund_cap && price > 0 && par_val > 0) {{
          if (!isMtmHoldco && par_mult > pe_base + 0.5) {{
            cap_implied = Math.round(Math.max(0.0, fund_cap * (cur_mult - pe_base) / (par_mult - pe_base)) * 10) / 10;
          }} else {{
            cap_implied = Math.round(fund_cap * (price / par_val) * 10) / 10;
          }}
        }} else {{
          cap_implied = null;
        }}
        cap_gap = (fund_cap !== null && cap_implied !== null) ? Math.round((fund_cap - cap_implied) * 10) / 10 : null;
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

      const dGStart = (g_org_exp !== null && c.g_org_exp !== null && c.g_org_exp !== undefined) ? (g_org_exp - c.g_org_exp) : null;
      const dG = (g_exp !== null && c.g_exp !== null && c.g_exp !== undefined) ? (g_exp - c.g_exp) : null;
      const dMult = (par_mult !== null && c.par_mult !== null) ? (par_mult - c.par_mult) : null;
      const dVal = (par_val !== null && c.par_val !== null) ? (par_val - c.par_val) : null;
      const dVsPar = (vs_par !== null && c.vs_par !== null) ? (vs_par - c.vs_par) : null;
      const dIrr = (irr_5y !== null && c.irr_5y !== null) ? (irr_5y - c.irr_5y) : null;
      const dCap = (fund_cap !== null && c.g4_cap !== null) ? (fund_cap - c.g4_cap) : null;
      const dCapGap = (cap_gap !== null && c.cap_gap !== null) ? (cap_gap - c.cap_gap) : null;

      const deltaRows = [
        `<tr>
          <td>Organic Growth Ceiling (g₀)</td>
          <td>${{fmtPct(c.g_org_exp)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPct(g_org_exp)}}</td>
          <td class="${{diffClass(dGStart, isPctZero(dGStart))}}">${{!isPctZero(dGStart) ? fmtPct(dGStart, true) : '-'}}</td>
        </tr>`,
        `<tr>
          <td>Per-Share Ceiling (g₀ + Buyback)</td>
          <td>${{fmtPct(c.g_exp)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPct(g_exp)}}</td>
          <td class="${{diffClass(dG, isPctZero(dG))}}">${{!isPctZero(dG) ? fmtPct(dG, true) : '-'}}</td>
        </tr>`,
        `<tr>
          <td>Explicit DCF Fair P/E (r=8.5%)</td>
          <td>${{c.par_mult !== null ? fmtNum(c.par_mult) + 'x' : '-'}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{par_mult !== null ? fmtNum(par_mult) + 'x' : '-'}}</td>
          <td class="${{diffClass(dMult, isMultZero(dMult))}}">${{!isMultZero(dMult) ? (dMult > 0 ? '+' : '') + fmtNum(dMult) + 'x' : '-'}}</td>
        </tr>`,
        `<tr>
          <td>DCF Fair Value Price</td>
          <td>${{fmtPrice(c.par_val, c.quote_currency)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPrice(par_val, c.quote_currency)}}</td>
          <td class="${{diffClass(dVal, isPriceZero(dVal))}}">${{!isPriceZero(dVal) ? (dVal > 0 ? '+' : '') + fmtPrice(dVal, c.quote_currency) : '-'}}</td>
        </tr>`,
        `<tr>
          <td>Discount vs Fair Value (Price / FV - 1)</td>
          <td>${{c.vs_par !== null ? fmtPct(c.vs_par, true) + ' (' + (c.vs_par <= 0 ? 'Below' : 'Above') + ')' : '-'}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{vs_par !== null ? fmtPct(vs_par, true) + ' (' + (vs_par <= 0 ? 'Below' : 'Above') + ')' : '-'}}</td>
          <td class="${{diffClass(dVsPar, isPctZero(dVsPar), true)}}">${{!isPctZero(dVsPar) ? fmtPct(dVsPar, true) : '-'}}</td>
        </tr>`,
        `<tr>
          <td>5-Year Expected IRR</td>
          <td>${{fmtPct(c.irr_5y)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtPct(irr_5y)}}</td>
          <td class="${{diffClass(dIrr, isPctZero(dIrr))}}">${{!isPctZero(dIrr) ? fmtPct(dIrr, true) : '-'}}</td>
        </tr>`,
        `<tr>
          <td>Our Moat Runway (CAP)</td>
          <td>${{c.g4_cap ? c.g4_cap + 'y' : '-'}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fund_cap ? fund_cap + 'y' : '-'}}</td>
          <td class="${{diffClass(dCap, isYearZero(dCap))}}">${{!isYearZero(dCap) ? (dCap > 0 ? '+' : '') + dCap + 'y' : '-'}}</td>
        </tr>`,
        `<tr>
          <td>Runway Margin of Safety</td>
          <td>${{fmtSignedYears(c.cap_gap)}}</td>
          <td style="font-weight: 600; color: var(--accent);">${{fmtSignedYears(cap_gap)}}</td>
          <td class="${{diffClass(dCapGap, isYearZero(dCapGap))}}">${{!isYearZero(dCapGap) ? fmtSignedYears(dCapGap) : '-'}}</td>
        </tr>`
      ];

      document.getElementById('sb-delta-tbody').innerHTML = deltaRows.join('');

      // Status Box Verdict
      const sbBox = document.getElementById('sb-status-box');
      const sbVerdict = document.getElementById('sb-status-verdict');
      const sbIrrBadge = document.getElementById('sb-irr-badge');

      if (!hasValuationInputs || par_val === null || par_val <= 0 || vs_par === null) {{
        sbBox.style.background = 'rgba(100, 116, 139, 0.12)';
        sbBox.style.borderColor = 'rgba(100, 116, 139, 0.3)';
        sbVerdict.innerHTML = `<span style="color: var(--text-dim);">— Scenario Verdict: Valuation Unavailable (Missing Price, Peak EPS, or 5Y Multiples)</span>`;
        sbIrrBadge.className = 'badge badge-slate';
        sbIrrBadge.textContent = '5Y IRR: -';
      }} else if (vs_par <= 0) {{
        sbBox.style.background = 'rgba(16, 185, 129, 0.15)';
        sbBox.style.borderColor = 'rgba(16, 185, 129, 0.35)';
        sbVerdict.innerHTML = `<span style="color: var(--green);">✓ Scenario Verdict: BELOW FAIR VALUE (${{fmtPct(vs_par, true)}}) — Buyable Quality Funnel</span>`;
        sbIrrBadge.className = 'badge badge-green';
        sbIrrBadge.textContent = `5Y IRR: ${{fmtPct(irr_5y)}}`;
      }} else {{
        sbBox.style.background = 'rgba(244, 63, 94, 0.15)';
        sbBox.style.borderColor = 'rgba(244, 63, 94, 0.35)';
        sbVerdict.innerHTML = `<span style="color: var(--red);">✕ Scenario Verdict: ABOVE FAIR VALUE (${{fmtPct(vs_par, true)}}) — Fully Valued / Overpriced</span>`;
        sbIrrBadge.className = 'badge badge-red';
        sbIrrBadge.textContent = `5Y IRR: ${{fmtPct(irr_5y)}}`;
      }}
    }}

    // Export Table as CSV
    function exportCurrentView() {{
      const data = sortData(getFilteredData());
      if (!data.length) return;

      const headers = ['Ticker', 'Company', 'Universe', 'Country', 'Sector', 'Sub-Industry', 'Status', 'Failing Gate', 'Calamity Flag', 'Waived Gates', 'Calamity Rationale', 'Moat Archetype', 'Our CAP', 'Market-Implied CAP', 'Runway Margin', '1Y Growth', '3-5Y Growth', 'OpCost CAGR', 'Growth Ceiling', 'Buyback Yield', 'Per-Share Ceiling', 'Market-Implied g', 'Growth Margin', 'Price', 'Fair Value', 'Discount', 'Cur P/E', 'Fair P/E', '5Y IRR', 'Active ROIC', 'Operating ROIC', 'GAAP ROIC', 'FCF Conv'];
      const csvRows = [headers.join(',')];

      data.forEach(c => {{
        const gExpVal = (c.g_exp !== null && c.g_exp !== undefined) ? c.g_exp : c.g_imp;
        const row = [
          `"${{c.ticker || ''}}"`,
          `"${{(c.company || '').replace(/"/g, '""')}}"`,
          `"${{c.universe || ''}}"`,
          `"${{c.country || ''}}"`,
          `"${{(c.sector || '').replace(/"/g, '""')}}"`,
          `"${{(c.sub_industry || '').replace(/"/g, '""')}}"`,
          `"${{c.result || ''}}"`,
          `"${{(c.rejected_at || '').replace(/"/g, '""')}}"`,
          `"${{c.calamity_flag || ''}}"`,
          `"${{((c.waived_gates || []).join('; ')).replace(/"/g, '""')}}"`,
          `"${{(c.calamity_note || '').replace(/"/g, '""')}}"`,
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
          c.cur_mult !== null && c.cur_mult !== undefined ? c.cur_mult : '',
          c.par_mult !== null && c.par_mult !== undefined ? c.par_mult : '',
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
