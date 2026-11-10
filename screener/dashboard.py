"""Standalone Interactive HTML Cockpit Generator for Quality & Moat Screener.

Compiles all universes (US, EU, CA) from data/ into a unified, high-performance,
zero-dependency standalone HTML application (output/screener.html).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import config as C
from .data import DATA_DIR, DOCS_DIR, OUTPUT_DIR, load_universe, universe_keys
from .gates import params, par_valuation, results


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
            val = par_valuation(fin, p, cap=cap_val)

            # Effective ROIC
            r_est = fin.get("roic_est")
            r_op = fin.get("roic_operating")
            r_med = fin.get("roic_median")
            roic_used = r_est if r_est is not None else (r_op if r_op is not None else r_med)

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
                "note": c.get("note"),
                "evidence": c.get("evidence"),
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
                "fcf_conv": fin.get("fcf_conv"),
                "peak_oe_year": fin.get("peak_oe_year"),
                "peak_oe_eps": fin.get("peak_oe_eps"),
                "peak_eps_est": fin.get("peak_eps_est"),
                "mult_low_5y": fin.get("mult_low_5y"),
                "mult_high_5y": fin.get("mult_high_5y"),
                "cagr_oe_eps": fin.get("cagr_oe_eps"),
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
                "g_imp": val.get("g_imp"),
                "coupon": val.get("coupon"),
                "imp_coupon": val.get("imp_coupon"),
                "cap_implied": val.get("cap_implied"),
                "cap_gap": val.get("cap_gap"),
                "g_market": val.get("g_market"),
                "g_gap": val.get("g_gap"),
            }
            all_companies.append(company_record)

    # Global KPI Aggregates
    qpass_count = sum(1 for c in all_companies if c["result"] == C.RES_QPASS)
    below_par_list = [c for c in all_companies if c["result"] == C.RES_QPASS and c["val_status"] == C.V_BELOW_PAR]
    below_par_count = len(below_par_list)
    irrs = [c["irr_5y"] for c in below_par_list if c["irr_5y"] is not None]
    median_irr = sorted(irrs)[len(irrs) // 2] if irrs else 0.0

    return {
        "version": "6.24",
        "generated_at": "2026-11-09",
        "summary": {
            "total_companies": len(all_companies),
            "quality_pass": qpass_count,
            "below_par": below_par_count,
            "median_irr_below_par": median_irr,
        },
        "universes": universes_meta,
        "companies": all_companies,
        "changelog": C.CHANGELOG,
    }


def build_dashboard_html(data: dict[str, Any]) -> str:
    """Generate the complete, self-contained standalone HTML application."""
    json_payload = json.dumps(data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      height: 100%;
      margin: 0;
      padding: 0;
      overflow: hidden;
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

    /* Layout */
    .app-header {{
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-shrink: 0;
      z-index: 40;
    }}
    .brand-title {{
      font-size: 16px;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 10px;
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
    }}
    .kpi-value {{
      font-size: 15px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }}
    .kpi-value.green {{ color: var(--green); }}
    .kpi-value.accent {{ color: var(--accent); }}

    /* Navigation Tabs */
    .tab-bar {{
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border);
      padding: 0 24px;
      display: flex;
      gap: 4px;
      overflow-x: auto;
      flex-shrink: 0;
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

    /* Controls & Filter Bar */
    .controls-bar {{
      padding: 12px 24px;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }}
    .filters-left {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}
    .search-box {{
      position: relative;
      width: 260px;
    }}
    .search-input {{
      width: 100%;
      background: var(--bg-base);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 7px 10px 7px 30px;
      color: var(--text-main);
      font-size: 12px;
      outline: none;
      transition: border-color 0.15s ease;
    }}
    .search-input:focus {{
      border-color: var(--accent);
    }}
    .search-icon {{
      position: absolute;
      left: 10px;
      top: 8px;
      color: var(--text-dim);
      font-size: 12px;
      pointer-events: none;
    }}
    .select-filter {{
      background: var(--bg-base);
      border: 1px solid var(--border);
      color: var(--text-main);
      border-radius: 6px;
      padding: 6px 10px;
      font-size: 12px;
      outline: none;
      cursor: pointer;
    }}
    .market-pills {{
      display: flex;
      background: var(--bg-base);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 2px;
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
    }}
    .market-btn.active {{
      background: var(--bg-card);
      color: var(--accent);
    }}
    .btn-export {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}
    .btn-export:hover {{
      background: var(--bg-card-hover);
      border-color: var(--accent);
    }}

    /* Table Container */
    .table-container {{
      flex: 1;
      width: 100%;
      overflow-y: auto;
      overflow-x: auto;
      position: relative;
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
    tbody tr {{
      transition: background-color 0.1s ease;
      cursor: pointer;
    }}
    tbody tr:hover td {{
      background-color: var(--bg-card-hover);
    }}
    tbody tr.selected td {{
      background-color: rgba(56, 189, 248, 0.12);
    }}
    tbody tr.selected td:first-child {{
      border-left: 3px solid var(--accent);
    }}
    tbody td {{
      padding: 8px 12px;
      font-size: 12.5px;
      font-variant-numeric: tabular-nums;
      border-bottom: 1px solid var(--border-subtle);
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
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      line-height: 1.2;
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
    .badge-gray {{
      background: rgba(148, 163, 184, 0.1);
      color: var(--text-muted);
      border: 1px solid rgba(148, 163, 184, 0.2);
    }}
    .gate-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 4px;
    }}
    .dot-pass {{ background: var(--green); }}
    .dot-fail {{ background: var(--red); }}
    .dot-blank {{ background: var(--text-dim); }}

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
      width: 680px;
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
    }}
    .dossier-drawer.open {{
      transform: translateX(0);
    }}
    .drawer-header {{
      padding: 18px 24px;
      border-bottom: 1px solid var(--border);
      background: var(--bg-card);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}
    .drawer-body {{
      padding: 24px;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .btn-close {{
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 22px;
      cursor: pointer;
      line-height: 1;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .btn-close:hover {{
      color: var(--text-main);
      background: rgba(255,255,255,0.06);
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
    }}
    .prose {{
      font-size: 13px;
      color: #cbd5e1;
      line-height: 1.6;
      white-space: pre-wrap;
    }}

    /* Empty state */
    .empty-state {{
      padding: 60px 20px;
      text-align: center;
      color: var(--text-dim);
    }}
  </style>
</head>
<body>

  <!-- Top Global Header -->
  <header class="app-header">
    <div class="brand-title">
      <span>Quality & Moat Screener</span>
      <span class="badge-version">v{data['version']}</span>
      <span style="color: var(--text-dim); font-size: 12px; font-weight: normal; margin-left: 8px;">Charlie Munger Reject Gates & Equity Bond Valuation</span>
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
        <span class="kpi-label">Below PAR Shortlist</span>
        <span class="kpi-value green">{data['summary']['below_par']}</span>
      </div>
      <div class="kpi-chip">
        <span class="kpi-label">Median 5Y IRR</span>
        <span class="kpi-value green">{f"{data['summary']['median_irr_below_par']*100:.1f}%"}</span>
      </div>
    </div>
  </header>

  <!-- View Tabs -->
  <nav class="tab-bar">
    <button class="tab-btn active" data-tab="shortlist" onclick="setTab('shortlist')">
      <span>★ Below PAR Shortlist</span>
      <span class="pill-count" id="count-shortlist">0</span>
    </button>
    <button class="tab-btn" data-tab="qpass" onclick="setTab('qpass')">
      <span>🛡️ Quality Pass Funnel</span>
      <span class="pill-count" id="count-qpass">0</span>
    </button>
    <button class="tab-btn" data-tab="all" onclick="setTab('all')">
      <span>🔍 Full Universe & Waterfall</span>
      <span class="pill-count" id="count-all">0</span>
    </button>
    <button class="tab-btn" data-tab="methodology" onclick="setTab('methodology')">
      <span>📖 Framework Rubric</span>
    </button>
  </nav>

  <!-- Filter & Controls Toolbar -->
  <section class="controls-bar" id="controls-section">
    <div class="filters-left">
      <!-- Search Input -->
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="filter-search" class="search-input" placeholder="Search ticker, company, sector..." oninput="applyFilters()">
      </div>

      <!-- Market Universe Pills -->
      <div class="market-pills">
        <button class="market-btn active" data-market="all" onclick="setMarket('all')">All Markets</button>
        <button class="market-btn" data-market="us" onclick="setMarket('us')">🇺🇸 US</button>
        <button class="market-btn" data-market="eu" onclick="setMarket('eu')">🇪🇺 Europe</button>
        <button class="market-btn" data-market="ca" onclick="setMarket('ca')">🇨🇦 Canada</button>
      </div>

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
        <option value="Gate 1">Rejected at Gate 1 (Understandability)</option>
        <option value="Gate 2">Rejected at Gate 2 (Essential Need)</option>
        <option value="Gate 3">Rejected at Gate 3 (Moat & Proof)</option>
        <option value="Gate 4">Rejected at Gate 4 (Runway CAP < 15Y)</option>
        <option value="Gate 5">Rejected at Gate 5 (Management)</option>
        <option value="Gate 6">Rejected at Gate 6 (Cash / Balance Sheet)</option>
      </select>
    </div>

    <!-- Export Button -->
    <button class="btn-export" onclick="exportCurrentView()">
      <span>📥</span> Export CSV
    </button>
  </section>

  <!-- Main Table View -->
  <main class="table-container" id="table-view">
    <table id="screener-table">
      <thead id="table-head"></thead>
      <tbody id="table-body"></tbody>
    </table>
    <div id="empty-state" class="empty-state" style="display: none;">
      No companies match the selected search and filter criteria.
    </div>
  </main>

  <!-- Methodology Tab Content (Hidden by default) -->
  <main class="table-container" id="methodology-view" style="display:none; padding: 30px; max-width: 1000px; margin: 0 auto;">
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
      </div>
    </div>

    <div class="dossier-section">
      <h2 style="font-size: 16px; margin-bottom: 12px; color: var(--accent);">Quantitative Valuation: Equity Bond Below PAR</h2>
      <div class="metric-box" style="margin-bottom: 12px;">
        <strong style="color: var(--text-main);">Fundamental PAR Multiple Formula:</strong>
        <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px; font-family: monospace;">
          PAR Multiple = min(mult_high_5y, (2 * (g_imp * 100) + 5Y Cycle Midpoint Multiple + min(Operating_ROIC * 100, 35.0)) / 3)
        </p>
      </div>
      <div class="metric-box">
        <strong style="color: var(--text-main);">Mauboussin Base-Rate Growth Regression:</strong>
        <p style="font-size: 12px; color: #cbd5e1; margin-top: 4px; font-family: monospace;">
          Forward Implied g = min(12.0%, max(2.0%, 0.15 * (Hist_g - 7.0%) + 7.0%))
        </p>
      </div>
    </div>
  </main>

  <!-- Slide-Out Dossier Drawer & Backdrop -->
  <div class="drawer-overlay" id="drawer-overlay" onclick="closeDrawer()"></div>
  <aside class="dossier-drawer" id="dossier-drawer">
    <div class="drawer-header">
      <div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="cell-ticker" id="dossier-ticker" style="font-size: 18px;"></span>
          <span class="badge" id="dossier-market-badge"></span>
          <span class="badge" id="dossier-val-badge"></span>
        </div>
        <div style="font-size: 15px; font-weight: 600; color: var(--text-main); margin-top: 3px;" id="dossier-company"></div>
        <div style="font-size: 11px; color: var(--text-dim); margin-top: 1px;" id="dossier-meta"></div>
      </div>
      <button class="btn-close" onclick="closeDrawer()">&times;</button>
    </div>

    <div class="drawer-body" id="dossier-content">
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
        <div class="section-title">Equity Bond Below PAR Scorecard</div>
        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label">Current Share Price</div>
            <div class="value" id="dossier-price">-</div>
          </div>
          <div class="metric-box">
            <div class="label">Fundamental PAR Value</div>
            <div class="value" id="dossier-par-val">-</div>
          </div>
          <div class="metric-box">
            <div class="label">Margin vs PAR</div>
            <div class="value" id="dossier-vs-par">-</div>
          </div>
        </div>

        <div class="grid-3" style="margin-bottom: 10px;">
          <div class="metric-box">
            <div class="label">Current Multiple</div>
            <div class="value" id="dossier-cur-mult">-</div>
          </div>
          <div class="metric-box">
            <div class="label">PAR Multiple (Ceiling)</div>
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

        <div class="grid-2">
          <div class="metric-box">
            <div class="label">Growth Margin (g_imp vs g_mkt)</div>
            <div class="value" id="dossier-g-margin">-</div>
          </div>
          <div class="metric-box">
            <div class="label">Moat Runway Margin (CAP vs Implied)</div>
            <div class="value" id="dossier-cap-margin">-</div>
          </div>
        </div>

        <div id="dossier-fin-note-box" class="metric-box" style="margin-top: 10px; display: none;">
          <div class="label" style="color: var(--text-dim);">Financial Notes & Overrides</div>
          <div class="prose" style="margin-top: 4px;" id="dossier-fin-note"></div>
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
      setTab('shortlist');

      // Keyboard Esc to close drawer
      window.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') closeDrawer();
      }});
    }}

    function updateTabCounts() {{
      const qpass = SCREENER_DATA.companies.filter(c => c.result === 'Quality pass');
      const shortlist = qpass.filter(c => c.val_status === 'Below PAR');
      document.getElementById('count-shortlist').textContent = shortlist.length;
      document.getElementById('count-qpass').textContent = qpass.length;
      document.getElementById('count-all').textContent = SCREENER_DATA.companies.length;
    }}

    function setTab(tab) {{
      currentTab = tab;
      document.querySelectorAll('.tab-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.tab === tab);
      }});

      const isMethodology = tab === 'methodology';
      document.getElementById('controls-section').style.display = isMethodology ? 'none' : 'flex';
      document.getElementById('table-view').style.display = isMethodology ? 'none' : 'block';
      document.getElementById('methodology-view').style.display = isMethodology ? 'block' : 'none';

      // Show/hide failing gate filter
      document.getElementById('filter-gate').style.display = (tab === 'all') ? 'inline-block' : 'none';

      // Default sort columns per tab
      if (tab === 'shortlist') {{
        sortColumn = 'irr_5y';
        sortAsc = false;
      }} else if (tab === 'qpass') {{
        sortColumn = 'roic_used';
        sortAsc = false;
      }} else if (tab === 'all') {{
        sortColumn = 'ticker';
        sortAsc = true;
      }}

      renderTable();
    }}

    function setMarket(m) {{
      currentMarket = m;
      document.querySelectorAll('.market-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.market === m);
      }});
      renderTable();
    }}

    function applyFilters() {{
      renderTable();
    }}

    function getFilteredData() {{
      const query = (document.getElementById('filter-search').value || '').trim().toLowerCase();
      const sector = document.getElementById('filter-sector').value;
      const moat = document.getElementById('filter-moat').value;
      const gate = document.getElementById('filter-gate').value;

      return SCREENER_DATA.companies.filter(c => {{
        // Tab restriction
        if (currentTab === 'shortlist' && (c.result !== 'Quality pass' || c.val_status !== 'Below PAR')) return false;
        if (currentTab === 'qpass' && c.result !== 'Quality pass') return false;

        // Market
        if (currentMarket !== 'all' && c.universe !== currentMarket) return false;

        // Sector
        if (sector !== 'all' && c.sector !== sector) return false;

        // Moat
        if (moat !== 'all' && c.g3a_moat_archetype !== moat) return false;

        // Gate
        if (currentTab === 'all' && gate !== 'all') {{
          if (gate === 'Quality pass' && c.result !== 'Quality pass') return false;
          if (gate.startsWith('Gate') && (!c.rejected_at || !c.rejected_at.startsWith(gate))) return false;
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
        sortAsc = (col === 'ticker' || col === 'company');
      }}
      renderTable();
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

    function renderTable() {{
      const thead = document.getElementById('table-head');
      const tbody = document.getElementById('table-body');
      const empty = document.getElementById('empty-state');

      const data = sortData(getFilteredData());
      empty.style.display = data.length === 0 ? 'block' : 'none';

      // Define columns per tab
      let cols = [];
      if (currentTab === 'shortlist') {{
        cols = [
          {{ key: 'ticker', label: 'Ticker' }},
          {{ key: 'company', label: 'Company' }},
          {{ key: 'country', label: 'Country' }},
          {{ key: 'price', label: 'Price', num: true }},
          {{ key: 'par_val', label: 'PAR Value', num: true }},
          {{ key: 'vs_par', label: 'vs PAR', num: true }},
          {{ key: 'cur_mult', label: 'Cur P/E', num: true }},
          {{ key: 'par_mult', label: 'PAR Mult', num: true }},
          {{ key: 'irr_5y', label: '5Y Exp IRR', num: true }},
          {{ key: 'roic_used', label: 'Op ROIC', num: true }},
          {{ key: 'g_gap', label: 'Growth Margin', num: true }},
          {{ key: 'cap_gap', label: 'Moat Runway', num: true }},
          {{ key: 'g3a_moat_archetype', label: 'Moat Archetype' }}
        ];
      }} else if (currentTab === 'qpass') {{
        cols = [
          {{ key: 'ticker', label: 'Ticker' }},
          {{ key: 'company', label: 'Company' }},
          {{ key: 'country', label: 'Country' }},
          {{ key: 'sector', label: 'Sector' }},
          {{ key: 'g3a_moat_archetype', label: 'Moat Archetype' }},
          {{ key: 'g4_cap', label: 'CAP', num: true }},
          {{ key: 'roic_used', label: 'Op ROIC', num: true }},
          {{ key: 'fcf_conv', label: 'FCF Conv', num: true }},
          {{ key: 'price', label: 'Price', num: true }},
          {{ key: 'par_val', label: 'PAR Val', num: true }},
          {{ key: 'vs_par', label: 'vs PAR', num: true }},
          {{ key: 'irr_5y', label: '5Y IRR', num: true }},
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
        const isSelected = c.id === selectedCompanyId;
        trHtml += `<tr class="${{isSelected ? 'selected' : ''}}" onclick="openDrawer('${{c.id}}')">`;

        cols.forEach(col => {{
          let val = c[col.key];
          let cellContent = '';

          if (col.key === 'ticker') {{
            cellContent = `<span class="cell-ticker">${{val}}</span>`;
          }} else if (col.key === 'company') {{
            cellContent = `<div class="cell-company" title="${{val}}">${{val}}</div>`;
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
            cellContent = `<span class="badge ${{bCls}}">${{val}}</span>`;
          }} else if (col.key === 'result') {{
            const bCls = val === 'Quality pass' ? 'badge-green' : (val.startsWith('Rejected') ? 'badge-red' : 'badge-gray');
            cellContent = `<span class="badge ${{bCls}}">${{val}}</span>`;
          }} else if (col.key === 'price' || col.key === 'par_val') {{
            cellContent = fmtPrice(val, c.quote_currency);
          }} else if (col.key === 'roic_used' || col.key === 'fcf_conv') {{
            cellContent = fmtPct(val);
          }} else if (col.key === 'g_gap') {{
            cellContent = fmtPct(val, true);
          }} else if (col.key === 'cap_gap') {{
            cellContent = (val !== null && val !== undefined) ? (val > 0 ? `+${{val}}y` : `${{val}}y`) : '-';
          }} else if (col.key === 'g4_cap') {{
            cellContent = val ? `${{val}}y` : '-';
          }} else if (col.num) {{
            cellContent = fmtNum(val);
          }} else {{
            cellContent = val || '-';
          }}

          trHtml += `<td class="${{col.num ? 'num' : ''}}">${{cellContent}}</td>`;
        }});

        trHtml += '</tr>';
      }});
      tbody.innerHTML = trHtml;
    }}

    // Slide-Out Dossier Drawer Logic
    function openDrawer(id) {{
      selectedCompanyId = id;
      const c = SCREENER_DATA.companies.find(item => item.id === id);
      if (!c) return;

      // Update selected row style
      document.querySelectorAll('tbody tr').forEach(tr => {{
        tr.classList.remove('selected');
      }});

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
      gates.forEach(g => {{
        const st = (c.gate_status && c.gate_status[g.key]) || 'blank';
        let bg = 'rgba(148, 163, 184, 0.2)';
        let color = '#94a3b8';
        let icon = '○';

        if (st === 'pass') {{
          bg = 'rgba(16, 185, 129, 0.25)';
          color = 'var(--green)';
          icon = '✓';
        }} else if (st === 'fail') {{
          bg = 'rgba(244, 63, 94, 0.25)';
          color = 'var(--red)';
          icon = '✕';
        }}

        stepperHtml += `
          <div class="waterfall-step">
            <div class="step-badge" style="background:${{bg}}; color:${{color}};">${{icon}}</div>
            <div class="step-title">${{g.name}}</div>
            <div class="step-result" style="color:${{color}};">${{st.toUpperCase()}}</div>
          </div>
        `;
      }});
      stepper.innerHTML = stepperHtml;

      const verdictEl = document.getElementById('dossier-verdict');
      if (c.result === 'Quality pass') {{
        verdictEl.innerHTML = `<span style="color: var(--green);">✓ Cleared All 6 Munger Reject Gates — Enters Quantitative Funnel</span>`;
      }} else {{
        verdictEl.innerHTML = `<span style="color: var(--red);">✕ ${{c.rejected_at || c.result}}</span>`;
      }}

      // Qualitative Dossier
      document.getElementById('dossier-moat-type').textContent = c.g3a_moat_archetype || 'None';
      document.getElementById('dossier-cap').textContent = c.g4_cap ? `${{c.g4_cap}} Years Runway` : 'Unassigned';

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

      document.getElementById('dossier-roic-op').textContent = fmtPct(c.roic_operating);
      document.getElementById('dossier-roic-gaap').textContent = fmtPct(c.roic_median);
      document.getElementById('dossier-fcf-conv').textContent = fmtPct(c.fcf_conv);

      document.getElementById('dossier-g-margin').textContent = c.g_gap !== null ? fmtPct(c.g_gap, true) : '-';
      document.getElementById('dossier-cap-margin').textContent = c.cap_gap !== null ? (c.cap_gap > 0 ? `+${{c.cap_gap}}y` : `${{c.cap_gap}}y`) : '-';

      // Fin note
      const fnBox = document.getElementById('dossier-fin-note-box');
      if (c.fin_note) {{
        document.getElementById('dossier-fin-note').textContent = c.fin_note;
        fnBox.style.display = 'block';
      }} else {{
        fnBox.style.display = 'none';
      }}

      // Show drawer
      document.getElementById('drawer-overlay').classList.add('open');
      document.getElementById('dossier-drawer').classList.add('open');
    }}

    function closeDrawer() {{
      document.getElementById('drawer-overlay').classList.remove('open');
      document.getElementById('dossier-drawer').classList.remove('open');
      selectedCompanyId = null;
      document.querySelectorAll('tbody tr').forEach(tr => tr.classList.remove('selected'));
    }}

    // Export Table as CSV
    function exportCurrentView() {{
      const data = sortData(getFilteredData());
      if (!data.length) return;

      const headers = ['Ticker', 'Company', 'Universe', 'Country', 'Sector', 'Sub-Industry', 'Status', 'Failing Gate', 'Moat Archetype', 'CAP', 'Price', 'PAR Value', 'vs PAR', 'Cur P/E', 'PAR Mult', '5Y IRR', 'Operating ROIC', 'GAAP ROIC', 'FCF Conv'];
      const csvRows = [headers.join(',')];

      data.forEach(c => {{
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
          c.price !== null && c.price !== undefined ? c.price : '',
          c.par_val !== null && c.par_val !== undefined ? c.par_val : '',
          c.vs_par !== null && c.vs_par !== undefined ? c.vs_par : '',
          c.cur_mult !== null && c.cur_mult !== undefined ? c.cur_mult : '',
          c.par_mult !== null && c.par_mult !== undefined ? c.par_mult : '',
          c.irr_5y !== null && c.irr_5y !== undefined ? c.irr_5y : '',
          c.roic_operating !== null && c.roic_operating !== undefined ? c.roic_operating : '',
          c.roic_median !== null && c.roic_median !== undefined ? c.roic_median : '',
          c.fcf_conv !== null && c.fcf_conv !== undefined ? c.fcf_conv : ''
        ];
        csvRows.push(row.join(','));
      }});

      const blob = new Blob([csvRows.join('\\n')], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `screener_${{currentTab}}_${{currentMarket}}_${{new Date().toISOString().slice(0,10)}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    // Boot
    window.addEventListener('DOMContentLoaded', init);
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
