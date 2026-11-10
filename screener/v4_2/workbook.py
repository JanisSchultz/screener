"""Compile one universe's source data into a versioned v4 screening workbook (gate-based 5-Phase framework)."""
from __future__ import annotations

import datetime as dt

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

from . import config as C
from .data import BENCH_COLUMNS, FIN_COLUMNS, HOLD_COLUMNS, TECH_COLUMNS

# ------------------------------------------------------------------- styles
FONT = "Calibri"
F_HDR = Font(name=FONT, bold=True, color="FFFFFF")
F_TITLE = Font(name=FONT, bold=True, size=14)
F_BOLD = Font(name=FONT, bold=True)
F_BODY = Font(name=FONT)
F_INPUT = Font(name=FONT, color="0000FF")
F_NOTE = Font(name=FONT, italic=True, color="595959")
FILL_HDR = PatternFill("solid", fgColor="1F3864")
PHASE_FILL = {0: "7F7F7F", 1: "2F5597", 2: "548235", 3: "7030A0", 4: "C55A11", 5: "1F3864"}
FILL_SUB = PatternFill("solid", fgColor="D9E1F2")
FILL_INPUT = PatternFill("solid", fgColor="FFF2CC")
mk = lambda c: PatternFill("solid", fgColor=c, bgColor=c)
FILL_RED, FILL_AMBER, FILL_GREEN, FILL_LGREEN, FILL_GREY = map(mk, ("F4CCCC", "FFF2CC", "D9EAD3", "EAF4E4", "EDEDED"))
WRAP = Alignment(wrap_text=True, vertical="top")
HDR_ALIGN = Alignment(wrap_text=True, vertical="center", horizontal="center")

Q_FILL = {C.RES_QPASS: FILL_GREEN, **{C.RES_REJ[p]: FILL_RED for p in (1, 2, 3)}, C.RES_REJ[0]: FILL_GREY}
V_FILL = {C.V_ENTRY: FILL_GREEN, C.V_UNREV: FILL_LGREEN, C.V_TIME: FILL_LGREEN, C.V_VAL: FILL_AMBER, C.V_AUDIT: FILL_RED,
          C.V_NODATA: FILL_GREY, C.V_NOTFUNNEL: FILL_GREY}
WATCH = "watch"
ENTRY = "entry"


def q(s) -> str:
    return '"' + str(s).replace('"', '""') + '"'


def header(ws, row, col, text, width=None, phase=None):
    c = ws.cell(row, col, text)
    c.font, c.alignment = F_HDR, HDR_ALIGN
    c.fill = PatternFill("solid", fgColor=PHASE_FILL[phase]) if phase is not None else FILL_HDR
    if width:
        ws.column_dimensions[L(col)].width = width
    return c


def body(ws, row, col, value, fmt=None, font=F_BODY, align=None):
    c = ws.cell(row, col, value)
    c.font = font
    if fmt and fmt != "@":
        c.number_format = fmt
    if align:
        c.alignment = align
    return c


def parse_date(v):
    if isinstance(v, str):
        try:
            return dt.date.fromisoformat(v)
        except ValueError:
            return v
    return v


class Cols:
    """Column registry for a row-per-company sheet. Formula lambdas are rendered after all columns
    are registered, so they may reference columns defined later."""

    def __init__(self, sheet: str):
        self.sheet, self.items, self.idx, self.detail = sheet, [], {}, set()

    def add(self, key, title, width, fmt, fn, phase=None, bold=False, detail=False):
        """detail=True: intermediate calculation, grouped and collapsed on the sheet (click + to expand)."""
        self.items.append((key, title, width, fmt, fn, phase, bold))
        self.idx[key] = len(self.items)
        if detail:
            self.detail.add(len(self.items))

    def ref(self, key, r):
        return f"{L(self.idx[key])}{r}"

    def x(self, key, r):
        return f"'{self.sheet}'!{L(self.idx[key])}{r}"

    def col(self, key):
        return L(self.idx[key])


class Builder:
    def __init__(self, meta: dict, version: str):
        self.m, self.version = meta, version
        self.n = len(meta["companies"])
        self.last = self.n + 1
        self.wb = Workbook()
        self.extra = meta.get("extra_columns", [])
        self.custom = meta.get("parameters", {})

    # ---------------------------------------------------------------- names
    def name(self, nm, sheet, ref):
        self.wb.defined_names[nm] = DefinedName(nm, attr_text=f"'{sheet}'!{ref}")

    def col_name(self, nm, sheet, col, first=2, last=None):
        c = L(col)
        self.name(nm, sheet, f"${c}${first}:${c}${last or self.last}")

    def render(self, ws, cols: Cols, prefix: str, height=64):
        for i, (key, title, width, fmt, fn, phase, bold) in enumerate(cols.items, 1):
            header(ws, 1, i, title, width, phase)
            for r in range(2, self.last + 1):
                c = body(ws, r, i, fn(r), fmt=fmt)
                if bold:
                    c.font = F_BOLD
            self.col_name(f"{prefix}_{key.replace('.', '_')}", ws.title, i)
        ws.row_dimensions[1].height = height
        ws.auto_filter.ref = f"A1:{L(len(cols.items))}{self.last}"
        runs, start = [], None
        for i in range(1, len(cols.items) + 2):
            if i in cols.detail and start is None:
                start = i
            elif i not in cols.detail and start is not None:
                runs.append((start, i - 1))
                start = None
        for a, b in runs:
            ws.column_dimensions.group(L(a), L(b), outline_level=1, hidden=True)
        ws.sheet_properties.outlinePr.summaryRight = False

    # ---------------------------------------------------------------- build
    def build(self, path):
        wb = self.wb
        wb.active.title = "Read Me"
        for t in ("Summary", "Shortlists", "Methodology", "Pre-Screen", "Inputs", "Screen",
                  "Financials", "Valuation", "Technicals", "Benchmarks", "Holdings", "Data Checks"):
            wb.create_sheet(t)
        self.methodology()
        self.prescreen()
        self.inputs()
        self.screen()
        self.financials()
        self.technicals()
        self.valuation()
        self.holdings()
        self.summary()
        self.shortlists()
        self.checks()
        if self.m.get("reevaluations"):
            self.reeval_history()
        self.readme()
        for s in wb.worksheets:
            s.sheet_view.zoomScale = 90
        wb.active = 1
        wb.calculation.fullCalcOnLoad = True
        wb.save(path)

    # ---------------------------------------------------------- Methodology
    def methodology(self):
        ws, m = self.wb["Methodology"], self.m
        for col, w in zip("ABCDEFGH", (46, 12, 34, 70, 34, 34, 34, 22)):
            ws.column_dimensions[col].width = w
        body(ws, 1, 1, m["title"] + " — Gate-based 5-Phase Stock Evaluation Framework", font=F_TITLE)
        body(ws, 2, 1, m["universe_text"], align=WRAP)
        body(ws, 3, 1, m["caveat"], font=F_BOLD, align=WRAP)
        body(ws, 4, 1, f"Workbook version v{self.version} — see 'Read Me' for change log.", font=F_NOTE)
        for r, h in ((2, 75), (3, 45)):
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = h
        r = 6
        for col, t in enumerate(("Parameter (yellow = editable; formulas read these named cells)", "Value",
                                 "Excel name", "Note / source", "Changed on (log)", "Reason for change (log)",
                                 "Framework default"), 1):
            header(ws, r, col, t)
        log = self.m.get("parameter_log", {})
        p_first = r + 1
        for title, params in C.PARAMETER_GROUPS:
            r += 1
            body(ws, r, 1, title, font=F_BOLD)
            for col in range(1, 5):
                ws.cell(r, col).fill = FILL_SUB
            for nm, label, val, fmt, note in params:
                r += 1
                if nm in self.custom:
                    val, note = self.custom[nm], f"{note} Universe-specific value (universe.json); framework default {val}."
                body(ws, r, 1, label)
                c = body(ws, r, 2, val, fmt=fmt, font=F_INPUT)
                c.fill = FILL_INPUT
                body(ws, r, 3, nm, font=F_NOTE)
                body(ws, r, 4, note, font=F_NOTE, align=WRAP)
                ent = log.get(nm, {})
                body(ws, r, 5, parse_date(ent.get("date")), fmt="yyyy-mm-dd", font=F_INPUT)
                body(ws, r, 6, ent.get("reason"), font=F_INPUT, align=WRAP)
                body(ws, r, 7, next(v for n_, _, v, _, _ in params if n_ == nm), fmt=fmt, font=F_NOTE)
                self.name(nm, "Methodology", f"$B${r}")
        self.name("prm_val", "Methodology", f"$B${p_first}:$B${r}")
        self.name("prm_reason", "Methodology", f"$F${p_first}:$F${r}")
        self.name("prm_def", "Methodology", f"$G${p_first}:$G${r}")
        ws.conditional_formatting.add(f"B{p_first}:B{r}", FormulaRule(
            formula=[f'AND($G{p_first}<>"",ROUND($B{p_first}-$G{p_first},9)<>0,$F{p_first}="")'], fill=FILL_RED))

        r += 2
        body(ws, r, 1, "Rules", font=F_BOLD)
        chain = " → ".join(lbl for _, lbl, _ in C.GATES)
        rules = [
            "Every step is a REJECT gate. A company leaves the funnel at the FIRST gate it fails (Screen → 'Rejected at'); "
            f"gate order: {chain}. Phase 1–3 result = '{C.RES_QPASS}' or 'Rejected – <phase>'. Funnel = {C.RES_QPASS}.",
            "Y/N gates: N rejects; blank = not yet reviewed (passes; Data Checks flags it). Gate 1 Understandability is a "
            "negative check: N only if the model is not established or not verifiable from outside. Gate 2 Sole-Owner: the "
            "company value on Inputs if filled in, else N if the listing country is outside your markets (Pre-Screen), else "
            "the sub-industry default. Gate 2 also covers the geopolitical 'Where'.",
            "Model type (Inputs 0.0) selects the Phase 4 tests: Operating, Bank, Insurer or Holding. 2.1c Cyclical selects "
            "cycle-average earnings and sales / book-value growth.",
            "2.1 matrix: High = score ≥ quad_high. Target = both High; Fad Trap = repeat High only; Long-Cycle Trap = "
            "essentiality High only; Low/Low passes. Traps reject if ko_traps = 1.",
            "3.3 Visibility (CAP) is the moat gate: rejects if Qualitative CAP < thr_cap (no strong moat ⇒ CAP ≤ 5). 3.2 "
            "Primary moat names the barrier. 3.4 Culture & Capital Allocation rejects below thr_culture (default: only a 0).",
            "Owner FCF = OCF − maintenance capex − SBC; maintenance capex = MIN(capex, depreciation & amortisation), all "
            "capex if D&A is missing. Normalised E = analyst e_norm_est, else cycle-average NI (cyclicals), else median ROE × "
            "equity (Bank / Insurer), else median net margin × latest sales. Normalised FCF = median owner-FCF margin × sales. "
            "Y_c = MIN(latest E, normalised E, latest FCF, normalised FCF) ÷ market cap (Bank / Insurer: earnings only; "
            "Holding: dividend yield). M_c = 1/Y_c (n/m if ≤ 0). Owner earnings OE = Y_c × market cap. Flags: Peak margin "
            "(latest net margin > (1+n_peak) × median), Below-normal (latest E < normalised). Cyclicals with fewer than a_hist "
            "years and no analyst e_norm_est cannot pass 4.2 ('NeedsNormE').",
            "g = analyst g_est if given, else MIN(v_gcap, MEDIAN of 5-yr CAGRs, 3-yr if no 5-yr): Operating sales / EPS / "
            "owner FCF; cyclicals sales / book value; Bank / Insurer EPS / book value; Holding NAV CAGR. g_moat = analyst "
            "g_moat_est if given, else g. " + m.get("fx_note", ""),
            "4.1 Audit gates by type — A1 Efficiency: Operating median tangible ROIC ≥ a_roic AND GAAP ROIC (incl. goodwill) "
            "≥ a_roic_gaap (if only one exists it must reach a_roic; 'ROIC judgement' if none), Bank median ROTE ≥ f_roe, "
            "Insurer median ROE ≥ f_roe, Holding NAV CAGR ≥ f_nav_g. A2: Operating owner FCF ÷ NI ≥ a_fcfconv, Insurer "
            "combined ratio ≤ f_cr, Bank / Holding n/a. A3 Δ market cap ÷ retained earnings ≥ a_dollar (all). A4 Resilience: "
            "Operating LT debt ÷ owner FCF ≤ a_debt_yrs AND interest cover ≥ a_intcov (debt-free passes), Bank CET1 ≥ f_cet1, "
            "Insurer solvency ≥ f_solv, Holding loan-to-value ≤ f_ltv (Bank / Insurer / Holding inputs are analyst estimates "
            "— verify). Uses the years available; 'No data' never rejects, but if A1 and A2 both have no data the audit is "
            "'No data'. Fewer than a_hist years or no $1-test data → 'Short history' flag.",
            "4.2 Principal Protection: multiple limit M_c ≤ MIN(efficiency% × 100, v_mult_cap) (GAAP ROIC / ROTE / ROE) AND "
            "exit buffer: market-implied CAP n < v_hold_yrs. Holding: limit n/a; exit buffer = discount to NAV ≥ f_navdisc.",
            "Market-implied CAP n (years of g_moat growth priced in; r = v_r, terminal g_T = v_gt): a = (1+g)/(1+r), "
            "K = (1+g_T)/(r−g_T), A = a/(1−a): n = LN((MC/OE − A)/(K − A)) / LN(a). 'n/m' = no finite n (OE ≤ 0, or price "
            "above the value of growing at g_moat forever) and fails.",
            "4.3 Equity Bond: Y_c + g ≥ v_eb.",
            "Buy-below price = today's price × MC_max ÷ market cap, where MC_max is the highest market cap at which 4.2 and "
            "4.3 pass: MIN(OE × multiple limit; OE ÷ (v_eb − g) if g < v_eb; OE × [A(1−a^H) + a^H·K] with H = v_hold_yrs "
            "if g_moat > v_gt). Holding: MIN(NAV × (1 − f_navdisc); dividends ÷ (v_eb − g)). Price vs buy-below ≤ 0% = "
            "the valuation gates pass at today's price. 'none' = no price passes (e.g. g below the hurdle and no yield).",
            "4.4 Weinstein stage: slope = MA30 ÷ MA30 five weeks earlier − 1. Stage 2 = price > MA and slope > t_slope; "
            "Stage 4 = price < MA and slope < −t_slope; flat = Stage 3 if within t_near_high of the 52-wk high, else Stage 1; "
            "'Stage 2 pullback' = rising MA, price below; 'Stage 4 rally' = falling MA, price above. Entry = stock in Stage 2 "
            "and sector in Stage 2 where sector data exists.",
            f"Phase 4 verdict: {C.V_NOTFUNNEL} → {C.V_NODATA} → {C.V_AUDIT} (4.1) → {C.V_VAL} (4.2 or 4.3) → "
            f"{C.V_TIME} (4.4) → {C.V_UNREV} (no 'Reviewed' date on Inputs) → {C.V_ENTRY}. An entry needs your own review.",
            "Guard rails: Methodology values that differ from the framework default need a date and reason (red until "
            "logged; Data Checks). Holdings warns when a position weight > p_max_pos, cash < p_min_cash, or your review is "
            "older than r_max_age days.",
            "Phase 5 band (Y_c + 0.5g): Buy zone = passes 4.3; Hold ≥ l_hold_hi; Stretched hold ≥ l_hold_lo with no "
            "Trigger 1 and a rising 30-wk MA (else 'Stretched – review'); Below band < l_hold_lo. Trigger 1 moat/cash "
            "decay: A1 Efficiency fails, owner FCF conversion < l_fcf_decay, no longer Quality pass, or analyst flag. Trigger 2 "
            "valuation: Y_c + 0.5g < l_hold_lo, implied n > Qualitative CAP, or n/m. Trigger 3: Stage 3/4, or a "
            "Quality-pass name with CAP ≥ the holding's offers Y_c + g > l_opp. Action: one trigger = REVIEW; SELL "
            "candidate only with 2+ triggers or Trigger 1 (moat/cash decay).",
        ]
        for t in rules:
            r += 1
            body(ws, r, 1, t, align=WRAP)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = 45

        r += 2
        for col, t in enumerate(("Phase / section", "Code", "Criterion", "Definition", "N / 0 =", "Y / 1 =", "2 =",
                                 "Seeded from (v3 → v4)"), 1):
            header(ws, r, col, t)
        prev = None
        for f in C.FIELDS:
            r += 1
            body(ws, r, 1, f"{C.PHASE_LONG[f['phase']]} — {f['section']}" if f["section"] != prev else None, align=WRAP)
            prev = f["section"]
            body(ws, r, 2, f["code"])
            body(ws, r, 3, f["name"] + (" (soft)" if f.get("soft") else "") + (" — GATE" if f["type"] == "gate" else ""),
                 align=WRAP)
            body(ws, r, 4, f["definition"], align=WRAP)
            if f["type"] == "score":
                for k in (0, 1, 2):
                    body(ws, r, 5 + k, f["rubric"][k], align=WRAP)
            elif f["type"] == "gate":
                body(ws, r, 5, "REJECT: " + f["rubric"]["N"], align=WRAP)
                body(ws, r, 6, f["rubric"]["Y"], align=WRAP)
            elif f["type"] in ("number", "category"):
                body(ws, r, 5, "Values: " + " / ".join(map(str, f["options"])), align=WRAP)
            elif f["type"] == "flag":
                body(ws, r, 5, "Values: Y / N (information)", align=WRAP)
            body(ws, r, 8, f["seed"], align=WRAP)
        for code, name, rule in (("2.1", "2x2 Demand Quadrant", "From 2.1a and 2.1b (formula on Screen)."),):
            r += 1
            body(ws, r, 2, code)
            body(ws, r, 3, name)
            body(ws, r, 4, rule, align=WRAP)
        r += 2
        body(ws, r, 1, "How the inputs were produced", font=F_BOLD)
        for t in m["how_produced"] + [m["sources"]]:
            r += 1
            body(ws, r, 1, t, align=WRAP)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = 48

    # ----------------------------------------------------------- Pre-Screen
    def prescreen(self):
        ws = self.wb["Pre-Screen"]
        body(ws, 1, 1, C.PHASE_LONG[0], font=F_TITLE)
        body(ws, 2, 1, "Gate 1 (Understandability, Inputs → 0.1): REJECT only if the model is not established or not "
                       "verifiable from outside. Gate 2 (Proud Sole-Owner, incl. your markets): if this were your only "
                       "investment and the market closed for 20 years, would you be a proud and completely comfortable "
                       "owner? If no, it violates your ethics, or the business lives outside your markets, REJECT. "
                       "Defaults for Gate 2: your markets (right, by listing country; N = reject) and sub-industries "
                       "(left); Inputs → 0.2 overrides both per company.",
                 font=F_NOTE, align=WRAP)
        ws.merge_cells("A2:D2")
        ws.row_dimensions[2].height = 75
        for i, (t, w) in enumerate((("GICS Sector", 24), ("GICS Sub-Industry", 40), ("Sole-owner (Y/N)", 10),
                                    ("Note", 50), ("helper: key", 40)), 1):
            header(ws, 4, i, t, w, phase=0)
        rows = self.m["prescreen"]
        first, last = 5, 4 + len(rows)
        for j, p in enumerate(rows):
            r = first + j
            body(ws, r, 1, p["sector"])
            body(ws, r, 2, p["sub_industry"])
            body(ws, r, 3, p.get("sole_owner") or "Y", font=F_INPUT).fill = FILL_INPUT
            body(ws, r, 4, p.get("note"), font=F_INPUT)
            body(ws, r, 5, f'=A{r}&"|"&B{r}', font=F_NOTE)
        self.name("ps_key", "Pre-Screen", f"$E${first}:$E${last}")
        self.name("ps_sole", "Pre-Screen", f"$C${first}:$C${last}")
        v = DataValidation(type="list", formula1='"Y,N"', allow_blank=False)
        ws.add_data_validation(v)
        v.add(f"C{first}:C{last}")
        ws.conditional_formatting.add(f"C{first}:C{last}", CellIsRule(operator="equal", formula=['"N"'], fill=FILL_RED))
        # your markets (listing country)
        for i, (t, w) in enumerate((("Country (listing)", 22), ("In your markets (Y/N)", 10)), 7):
            header(ws, 4, i, t, w, phase=0)
        mk = self.m.get("markets") or [{"country": x, "in_market": "Y"} for x in sorted({c["country"] for c in self.m["companies"]})]
        m_last = 4 + len(mk)
        for j, x in enumerate(mk):
            body(ws, first + j, 7, x["country"])
            body(ws, first + j, 8, x.get("in_market") or "Y", font=F_INPUT).fill = FILL_INPUT
        self.name("mk_country", "Pre-Screen", f"$G${first}:$G${m_last}")
        self.name("mk_in", "Pre-Screen", f"$H${first}:$H${m_last}")
        v2 = DataValidation(type="list", formula1='"Y,N"', allow_blank=False)
        ws.add_data_validation(v2)
        v2.add(f"H{first}:H{m_last}")
        ws.conditional_formatting.add(f"H{first}:H{m_last}", CellIsRule(operator="equal", formula=['"N"'], fill=FILL_RED))
        ws.column_dimensions["F"].width = 3
        ws.freeze_panes = "A5"
        ws.auto_filter.ref = f"A4:D{last}"

    # --------------------------------------------------------------- Inputs
    def input_columns(self):
        cols = [("id", "ID (unique)", "@", 12, None), ("ticker", "Ticker", "@", 11, None),
                ("company", "Company", "@", 26, None), ("country", "Country", "@", 13, None),
                ("sector", "GICS Sector", "@", 20, None), ("sub_industry", "GICS Sub-Industry", "@", 26, None)]
        cols += [(c["key"], c["header"], c["fmt"], c["width"], None) for c in self.extra]
        for f in C.FIELDS:
            w = {"gate": 7, "flag": 7, "category": 14, "score": 8, "number": 8, "text": 40}[f["type"]]
            cols.append((f["code"], f"{f['code']} {f['short']}", "0" if f["type"] in ("score", "number") else "@", w, f["phase"]))
        cols += [("confidence", "Confidence of pre-scores (H/M/L)", "@", 9, None), ("note", "Note", "@", 70, None),
                 ("evidence", "Key evidence / sources", "@", 30, None), ("reviewed", "Reviewed by me (date)", "yyyy-mm-dd", 11, None)]
        return cols

    def inputs(self):
        ws = self.wb["Inputs"]
        cols = self.input_columns()
        self.inp = {}
        for i, (key, title, fmt, width, phase) in enumerate(cols, 1):
            header(ws, 1, i, title, width, phase)
            self.inp[key] = i
        ws.row_dimensions[1].height = 64
        for r, row in enumerate(self.m["companies"], 2):
            for i, (key, _, fmt, _, _) in enumerate(cols, 1):
                v = row.get(key)
                body(ws, r, i, parse_date(v) if key == "reviewed" else v, fmt=fmt, font=F_INPUT)
        ws.freeze_panes = "D2"
        ws.auto_filter.ref = f"A1:{L(len(cols))}{self.last}"
        self.name("inp_ID", "Inputs", f"$A$2:$A${self.last}")
        for k in ("confidence", "3.3n", "0.0", "3.2", "reviewed"):
            self.col_name(f"inp_{k.replace('.', '_')}", "Inputs", self.inp[k])

        def dv(formula, key, msg):
            c = L(self.inp[key])
            v = DataValidation(type="list", formula1=formula, allow_blank=True, showErrorMessage=True, error=msg)
            ws.add_data_validation(v)
            v.add(f"{c}2:{c}{self.last}")

        for f in C.FIELDS:
            c = L(self.inp[f["code"]])
            if f["type"] == "score":
                dv('"0,1,2"', f["code"], "0, 1 or 2")
                self.score_cf(ws, f"{c}2:{c}{self.last}")
            elif f["type"] == "gate":
                dv('"Y,N"', f["code"], "Y or N (blank = not reviewed)")
                self.gate_cf(ws, f"{c}2:{c}{self.last}")
            elif f["type"] in ("number", "category"):
                dv(q(",".join(map(str, f["options"]))), f["code"], " / ".join(map(str, f["options"])))
            elif f["type"] == "flag":
                dv('"Y,N"', f["code"], "Y or N")
        c = L(self.inp["reviewed"])
        v = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True)
        ws.add_data_validation(v)
        v.add(f"{c}2:{c}{self.last}")
        ws.conditional_formatting.add(f"{c}2:{c}{self.last}", FormulaRule(
            formula=[f'AND(ISNUMBER({c}2),TODAY()-{c}2>r_max_age)'], fill=FILL_AMBER))
        dv('"H,M,L"', "confidence", "H, M or L")
        for x in self.extra:
            if x.get("validation"):
                dv(q(",".join(x["validation"])), x["key"], "/".join(x["validation"]))

    @staticmethod
    def score_cf(ws, rng):
        for val, fill in (("0", FILL_RED), ("1", FILL_AMBER), ("2", FILL_GREEN)):
            ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[val], fill=fill))

    @staticmethod
    def gate_cf(ws, rng):
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"N"'], fill=FILL_RED))
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Y"'], fill=FILL_GREEN))

    @staticmethod
    def passfail_cf(ws, rng):
        for ok in ("Pass",):
            ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[q(ok)], fill=FILL_GREEN))
        for bad in ("Fail", "Reject"):
            ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[q(bad)], fill=FILL_RED))
        for na in ("No data", "n/a"):
            ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[q(na)], fill=FILL_GREY))

    # --------------------------------------------------- Screen (Phases 1–3)
    def screen(self):
        ws = self.wb["Screen"]
        S = self.S = Cols("Screen")
        I = lambda key, r: f"Inputs!{L(self.inp[key])}{r}"
        link = lambda key: (lambda r: f'=IF({I(key, r)}="","",{I(key, r)})')
        short = {f["code"]: f["short"] for f in C.FIELDS}
        for key, title, fmt, width, phase in self.input_columns()[:6 + len(self.extra)]:
            S.add(key, title, width, fmt, link(key))
        S.add("conf", "Confidence of pre-scores", 8, None, link("confidence"), detail=True)

        def field(code, width=8, fmt="0", detail=False):
            f = C.FIELD_BY_CODE[code]
            S.add(code, f"{code} {short[code]}" + (" (gate)" if f["type"] == "gate" else ""), width,
                  None if f["type"] in ("gate", "flag", "category", "text") else fmt, link(code), f["phase"], detail=detail)

        fails = {}                                  # gate key -> lambda r: Excel condition that rejects
        for code in C.GATE_CODES:
            fails[code] = lambda r, c=code: f'{S.ref(c, r)}="N"'
        fails["quad"] = lambda r: f'AND(ko_traps=1,ISNUMBER(SEARCH("Trap",{S.ref("quad", r)})))'
        fails["3.3n"] = lambda r: f'N({S.ref("3.3n", r)})<thr_cap'
        fails["3.4"] = lambda r: f'N({S.ref("3.4", r)})<thr_culture'

        def phase_pass(p):
            keys = [k for k, _, ph in C.GATES if ph == p]
            S.add(f"P{p}", f"{C.PHASE_NAMES[p]} pass" if p == 0 else f"Phase {p} {C.PHASE_NAMES[p]} pass", 9, None,
                  lambda r: f'=IF(OR({",".join(fails[k](r) for k in keys)}),"Reject","Pass")', p, bold=True)

        S.add("0.0", "0.0 Model type", 10, None, link("0.0"), 0)
        # Pre-Screen
        field("0.1")
        S.add("in_market", "Listing country in your markets", 8, None,
              lambda r: f'=IFERROR(INDEX(mk_in,MATCH({S.ref("country", r)},mk_country,0)),"Y")', 0, detail=True)
        S.add("so_default", "Sole-Owner default (sub-industry)", 9, None,
              lambda r: f'=IFERROR(INDEX(ps_sole,MATCH({S.ref("sector", r)}&"|"&{S.ref("sub_industry", r)},ps_key,0)),"Y")',
              0, detail=True)
        S.add("0.2", "0.2 Sole-Owner / markets (gate)", 9, None,
              lambda r: f'=IF({I("0.2", r)}<>"",{I("0.2", r)},IF({S.ref("in_market", r)}="N","N",{S.ref("so_default", r)}))', 0)
        phase_pass(0)
        # Phase 1
        field("1.3")
        field("1.4")
        phase_pass(1)
        # Phase 2
        field("2.1a", detail=True)
        field("2.1b", detail=True)
        S.add("quad", "2.1 Demand Quadrant (2x2)", 13, None,
              lambda r: f'=IF(AND({S.ref("2.1a", r)}>=quad_high,{S.ref("2.1b", r)}>=quad_high),"Target",'
                        f'IF({S.ref("2.1b", r)}>=quad_high,"Fad Trap",IF({S.ref("2.1a", r)}>=quad_high,'
                        f'"Long-Cycle Trap","Low/Low")))', 2)
        field("2.1c", 7)
        field("2.3")
        phase_pass(2)
        # Phase 3
        field("3.2", 16)
        field("3.3n", 9)
        field("3.4")
        phase_pass(3)

        S.add("rejected", "Rejected at (first failed gate)", 18, None,
              lambda r: "=" + "".join(f"IF({fails[k](r)},{q(lbl)}," for k, lbl, _ in C.GATES) + '""' + ")" * len(C.GATES),
              bold=True)
        S.add("result", "Phase 1–3 result", 18, None,
              lambda r: "=" + "".join(f'IF({S.ref(f"P{p}", r)}="Reject",{q(C.RES_REJ[p])},' for p in (0, 1, 2, 3))
                        + q(C.RES_QPASS) + "))))", bold=True)
        S.add("funnel", "In Phase 4 funnel", 8, None, lambda r: f'=IF({S.ref("result", r)}={q(C.RES_QPASS)},"Yes","No")')
        S.add("weak", "Watch points (passed, but borderline)", 34, None,
              lambda r: "=MID(" + "&".join(
                  [f'IF({S.ref("3.4", r)}=1,"; 3.4 Culture = 1","")',
                   f'IF(AND(N({S.ref("3.3n", r)})>=thr_cap,N({S.ref("3.3n", r)})<15),"; CAP < 15 yrs","")',
                   f'IF({S.ref("quad", r)}="Low/Low","; Low/Low demand quadrant","")',
                   f'IF(OR({S.ref("0.1", r)}="",{S.ref("1.3", r)}="",{S.ref("1.4", r)}="",{S.ref("2.3", r)}=""),'
                   f'"; gate not reviewed","")']) + ",3,600)")
        S.add("moatnote", "Moat & erosion note", 40, None, link("3.3m"), 3)
        S.add("note", "Note", 40, None, link("note"), detail=True)
        S.add("reviewed", "Reviewed by me", 11, "yyyy-mm-dd", link("reviewed"))
        self.render(ws, S, "scr")
        ws.freeze_panes = "D2"

        rng = lambda a, b=None: f"{S.col(a)}2:{S.col(b or a)}{self.last}"
        for c in C.SCORE_CODES:
            self.score_cf(ws, rng(c))
        for c in C.GATE_CODES:
            self.gate_cf(ws, rng(c))
        for p in (0, 1, 2, 3):
            self.passfail_cf(ws, rng(f"P{p}"))
        for res, fill in Q_FILL.items():
            ws.conditional_formatting.add(rng("result"), CellIsRule(operator="equal", formula=[q(res)], fill=fill))
        ws.conditional_formatting.add(rng("quad"), CellIsRule(operator="equal", formula=['"Target"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("quad"), FormulaRule(formula=[f'ISNUMBER(SEARCH("Trap",{S.col("quad")}2))'], fill=FILL_RED))
        ws.conditional_formatting.add(rng("3.3n"), FormulaRule(formula=[f"N({S.col('3.3n')}2)<thr_cap"], fill=FILL_RED))

    # ------------------------------------------- Financials / Technicals (inputs)
    def input_sheet(self, title, columns, rows_by_id, prefix, note):
        ws = self.wb[title]
        idx = {}
        for i, (key, t, fmt, w) in enumerate(columns, 1):
            header(ws, 1, i, t, w, 4)
            idx[key] = i
        header(ws, 1, len(columns) + 1, "Company (lookup)", 24, 4)
        ws.row_dimensions[1].height = 64
        for r, c in enumerate(self.m["companies"], 2):
            row = rows_by_id.get(c["id"], {})
            for i, (key, _, fmt, _) in enumerate(columns, 1):
                body(ws, r, i, c["id"] if key == "id" else row.get(key), fmt=fmt, font=F_NOTE if key == "id" else F_INPUT)
            body(ws, r, len(columns) + 1, f"=Inputs!C{r}", font=F_NOTE)
        for key, i in idx.items():
            self.col_name(f"{prefix}_{key}", title, i)
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = f"A1:{L(len(columns) + 1)}{self.last}"
        body(ws, self.last + 2, 1, note, font=F_NOTE)
        return idx

    def financials(self):
        self.fin = self.input_sheet(
            "Financials", FIN_COLUMNS, self.m["financials"], "fin",
            "Phase 4 inputs (blue). Filled by fetch_market_data.py (SEC EDGAR / Yahoo Finance) or by hand; row order must "
            "match Inputs. Money in millions of the reporting currency; market cap converted into it. Ratios as fractions.")
        ws = self.wb["Financials"]
        c = L(self.fin["roic_judgement"])
        v = DataValidation(type="list", formula1='"Pass,Fail"', allow_blank=True)
        ws.add_data_validation(v)
        v.add(f"{c}2:{c}{self.last}")

    def technicals(self):
        self.tec = self.input_sheet(
            "Technicals", TECH_COLUMNS, self.m["technicals"], "tec",
            "Weekly technical inputs (Phase 4.4 / 5), filled by fetch_market_data.py; stage is computed on Valuation.")
        ws = self.wb["Benchmarks"]
        body(ws, 1, 1, "Benchmarks — market and sector trend (Phase 4.4)", font=F_TITLE)
        for i, (key, t, fmt, w) in enumerate(BENCH_COLUMNS, 1):
            header(ws, 3, i, t, w, 4)
        sc = len(BENCH_COLUMNS) + 1
        header(ws, 3, sc, "Stage", 18, 4)
        first, cap = 4, 40
        idx = {k: i for i, (k, *_r) in enumerate(BENCH_COLUMNS, 1)}
        for j, b in enumerate(self.m["benchmarks"]):
            for i, (key, _, fmt, _) in enumerate(BENCH_COLUMNS, 1):
                body(ws, first + j, i, b.get(key), fmt=fmt, font=F_INPUT)
        for r in range(first, first + cap):
            P, M, M0, H = (f"{L(idx[k])}{r}" for k in ("price", "ma30", "ma30_prev", "high_52w"))
            body(ws, r, sc, f'=IF(OR(A{r}="",NOT(ISNUMBER({M}))),"",{self.stage_expr(P, M, M0, H)})')
        self.name("bm_name", "Benchmarks", f"$A${first}:$A${first + cap - 1}")
        self.name("bm_stage", "Benchmarks", f"${L(sc)}${first}:${L(sc)}${first + cap - 1}")
        body(ws, first + cap + 1, 1, "Row 'MARKET' = broad market; other rows are named exactly like the GICS sector "
                                     "they benchmark. Refreshed by fetch_market_data.py.", font=F_NOTE)
        ws.freeze_panes = "A4"

    @staticmethod
    def stage_expr(P, M, M0, H):
        slope = f"({M}/{M0}-1)"
        return (f'IF(NOT(ISNUMBER({M0})),"No data",IF({slope}>t_slope,IF({P}>{M},"Stage 2","Stage 2 pullback"),'
                f'IF({slope}<-t_slope,IF({P}<{M},"Stage 4","Stage 4 rally"),'
                f'IF({P}>={H}*(1-t_near_high),"Stage 3","Stage 1"))))')

    # -------------------------------------------------- Valuation (Phase 4)
    def valuation(self):
        ws = self.wb["Valuation"]
        V = self.V = Cols("Valuation")
        S = self.S
        F = lambda k, r: f"Financials!{L(self.fin[k])}{r}"
        T = lambda k, r: f"Technicals!{L(self.tec[k])}{r}"
        num = lambda x: f"ISNUMBER({x})"
        v = V.ref
        pf = lambda x, cond: f'=IF({x}="","No data",IF({cond},"Pass","Fail"))'
        typ = lambda r: v("type", r)
        fin_ = lambda r: f'OR({typ(r)}="Bank",{typ(r)}="Insurer")'
        hold_ = lambda r: f'{typ(r)}="Holding"'
        fv = lambda k, r: f'IF({num(F(k, r))},{F(k, r)},"")'
        D = dict(detail=True)
        V.add("id", "ID", 11, None, lambda r: f"=Screen!A{r}")
        V.add("ticker", "Ticker", 10, None, lambda r: f"=Screen!B{r}")
        V.add("company", "Company", 24, None, lambda r: f"=Screen!C{r}")
        V.add("qres", "Phase 1–3 result", 14, None, lambda r: f"={S.x('result', r)}", **D)
        V.add("funnel", "In funnel", 7, None, lambda r: f"={S.x('funnel', r)}")
        V.add("type", "Model type", 9, None, lambda r: f'=IF({S.x("0.0", r)}="","Operating",{S.x("0.0", r)})', 0)
        V.add("cyc", "Cyclical", 6, None, lambda r: f"={S.x('2.1c', r)}", 2, **D)
        V.add("cap", "Qualitative CAP (yrs)", 8, "0", lambda r: f"={S.x('3.3n', r)}", 3, **D)
        # ---- earnings (detail)
        mcx_ = lambda r: f'MIN({F("capex_ttm_m", r)},IF({num(F("da_ttm_m", r))},{F("da_ttm_m", r)},{F("capex_ttm_m", r)}))'
        V.add("fcf", "Owner FCF latest (m) = OCF − maint. capex − SBC", 11, "#,##0",
              lambda r: f'=IF(AND({num(F("ocf_ttm_m", r))},{num(F("capex_ttm_m", r))}),'
                        f'{F("ocf_ttm_m", r)}-{mcx_(r)}-N({F("sbc_ttm_m", r)}),"")', 4, **D)
        V.add("mc", "Market cap (m)", 11, "#,##0", lambda r: "=" + fv("market_cap_m", r), 4, **D)
        V.add("enorm", "Normalised earnings (m)", 11, "#,##0",
              lambda r: f'=IF({num(F("e_norm_est", r))},{F("e_norm_est", r)},IF({v("cyc", r)}="Y",{fv("ni_avg_m", r)},'
                        f'IF({fin_(r)},IF(AND({num(F("roe_median", r))},{num(F("equity_m", r))}),{F("roe_median", r)}*{F("equity_m", r)},""),'
                        f'IF(AND({num(F("ni_margin_med", r))},{num(F("sales_ttm_m", r))}),{F("ni_margin_med", r)}*{F("sales_ttm_m", r)},""))))', 4, **D)
        V.add("fcfn", "Normalised owner FCF (m)", 11, "#,##0",
              lambda r: f'=IF(AND({num(F("fcf_margin_med", r))},{num(F("sales_ttm_m", r))}),{F("fcf_margin_med", r)}*{F("sales_ttm_m", r)},"")', 4, **D)
        V.add("ep", "E/P (MIN latest, normalised)", 8, "0.0%",
              lambda r: f'=IF(AND({num(v("mc", r))},{num(F("ni_ttm_m", r))}),MIN({F("ni_ttm_m", r)},{v("enorm", r)})/{v("mc", r)},"")', 4, **D)
        V.add("fcfy", "FCF/P (MIN latest, normalised)", 8, "0.0%",
              lambda r: f'=IF(AND({num(v("mc", r))},{num(v("fcf", r))}),MIN({v("fcf", r)},{v("fcfn", r)})/{v("mc", r)},"")', 4, **D)
        V.add("dy", "Dividend yield", 7, "0.0%",
              lambda r: f'=IF({num(v("mc", r))},N({F("dividends_ttm_m", r)})/{v("mc", r)},"")', 4, **D)
        V.add("yc", "Y_c (conservative yield)", 9, "0.0%",
              lambda r: f'=IF({hold_(r)},{v("dy", r)},IF({fin_(r)},{v("ep", r)},'
                        f'IF(AND({num(v("ep", r))},{num(v("fcfy", r))}),MIN({v("ep", r)},{v("fcfy", r)}),"")))', 4, True)
        V.add("mcx", "M_c = 1/Y_c", 8, "0.0",
              lambda r: f'=IF(NOT({num(v("yc", r))}),"",IF({v("yc", r)}<=0,"n/m",1/{v("yc", r)}))', 4, **D)
        V.add("oe", "Owner earnings OE = Y_c × MC (m)", 11, "#,##0",
              lambda r: f'=IF(AND({num(v("yc", r))},{num(v("mc", r))}),{v("yc", r)}*{v("mc", r)},"")', 4, **D)

        def fb(keys, r):
            med = lambda n: "MEDIAN(" + ",".join(F(f"cagr_{k}_{n}", r) for k in keys) + ")"
            return f'IFERROR(MIN(v_gcap,{med(5)}),IFERROR(MIN(v_gcap,{med(3)}),""))'

        V.add("g", "g used", 7, "0.0%",
              lambda r: f'=IF({num(F("g_est", r))},{F("g_est", r)},IF({hold_(r)},IF({num(F("nav_cagr", r))},'
                        f'MIN(v_gcap,{F("nav_cagr", r)}),""),IF({v("cyc", r)}="Y",{fb(("sales", "bv"), r)},'
                        f'IF({fin_(r)},{fb(("eps", "bv"), r)},{fb(("sales", "eps", "fcf"), r)}))))', 4)
        V.add("gm", "g_moat used", 7, "0.0%",
              lambda r: f'=IF({num(F("g_moat_est", r))},{F("g_moat_est", r)},{v("g", r)})', 4, **D)
        V.add("nflag", "Earnings flags", 14, None,
              lambda r: f'=TRIM(IF(AND({num(F("ni_ttm_m", r))},N({F("sales_ttm_m", r)})>0,N({F("ni_margin_med", r)})>0),'
                        f'IF({F("ni_ttm_m", r)}/{F("sales_ttm_m", r)}>(1+n_peak)*{F("ni_margin_med", r)},"Peak margin ",""),"")'
                        f'&IF(AND({num(F("ni_ttm_m", r))},{num(v("enorm", r))}),IF({F("ni_ttm_m", r)}<{v("enorm", r)},"Below-normal",""),""))', 4)
        # ---- 4.1 audit (type-specific)
        V.add("eff", "Efficiency: GAAP ROIC / ROTE / ROE / NAV CAGR", 8, "0.0%",
              lambda r: f'=IF({hold_(r)},{fv("nav_cagr", r)},IF({typ(r)}="Bank",IF({num(F("rote_median", r))},'
                        f'{F("rote_median", r)},{fv("roe_median", r)}),IF({typ(r)}="Insurer",{fv("roe_median", r)},'
                        f'{fv("roic_median", r)})))', 4, **D)
        V.add("roict", "Tangible ROIC (Operating)", 8, "0.0%", lambda r: "=" + fv("roic_tangible_median", r), 4, **D)
        tang, gaap = (lambda r: F("roic_tangible_median", r)), (lambda r: F("roic_median", r))
        V.add("a1", "A1 Efficiency", 8, None,
              lambda r: f'=IF({typ(r)}="Operating",IF(AND({num(tang(r))},{num(gaap(r))}),'
                        f'IF(AND({tang(r)}>=a_roic,{gaap(r)}>=a_roic_gaap),"Pass","Fail"),'
                        f'IF({num(tang(r))},IF({tang(r)}>=a_roic,"Pass","Fail"),IF({num(gaap(r))},IF({gaap(r)}>=a_roic,"Pass","Fail"),'
                        f'IF(OR({F("roic_judgement", r)}="Pass",{F("roic_judgement", r)}="Fail"),{F("roic_judgement", r)},"No data")))),'
                        f'IF({num(v("eff", r))},IF({v("eff", r)}>=IF({hold_(r)},f_nav_g,f_roe),"Pass","Fail"),"No data"))', 4)
        V.add("a2", "A2 Cash integrity / underwriting", 8, None,
              lambda r: f'=IF({typ(r)}="Operating",IF({num(F("fcf_conv", r))},IF({F("fcf_conv", r)}>=a_fcfconv,"Pass","Fail"),"No data"),'
                        f'IF({typ(r)}="Insurer",IF({num(F("combined_ratio", r))},IF({F("combined_ratio", r)}<=f_cr,"Pass","Fail"),"No data"),"n/a"))', 4)
        V.add("dollar", "Buffett $1 ratio", 8, "0.00",
              lambda r: f'=IF(AND({num(F("mcap_delta_m", r))},{num(F("retained_m", r))}),IF({F("retained_m", r)}>0,'
                        f'{F("mcap_delta_m", r)}/{F("retained_m", r)},""),"")', 4, **D)
        V.add("a3", "A3 Buffett $1 test", 8, None,
              lambda r: f'=IF({num(v("dollar", r))},IF({v("dollar", r)}>=a_dollar,"Pass","Fail"),"No data")', 4)
        V.add("debty", "LT debt ÷ owner FCF (yrs)", 8, "0.0",
              lambda r: f'=IF(AND({num(F("lt_debt_m", r))},{num(v("fcf", r))}),IF({F("lt_debt_m", r)}<=0,0,'
                        f'IF({v("fcf", r)}>0,{F("lt_debt_m", r)}/{v("fcf", r)},"n/m")),"")', 4, **D)
        V.add("icov", "Interest cover (×)", 8, "0.0",
              lambda r: f'=IF(AND({num(F("ebit_ttm_m", r))},{num(F("interest_m", r))}),IF({F("interest_m", r)}=0,999,'
                        f'{F("ebit_ttm_m", r)}/ABS({F("interest_m", r)})),"")', 4, **D)
        V.add("a4", "A4 Resilience (debt & cover / CET1 / solvency / LTV)", 9, None,
              lambda r: f'=IF({typ(r)}="Bank",IF({num(F("cet1", r))},IF({F("cet1", r)}>=f_cet1,"Pass","Fail"),"No data"),'
                        f'IF({typ(r)}="Insurer",IF({num(F("solvency", r))},IF({F("solvency", r)}>=f_solv,"Pass","Fail"),"No data"),'
                        f'IF({hold_(r)},IF({num(F("ltv", r))},IF({F("ltv", r)}<=f_ltv,"Pass","Fail"),"No data"),'
                        f'IF(AND({v("debty", r)}="",{v("icov", r)}=""),"No data",IF(OR({v("debty", r)}="n/m",'
                        f'AND({num(v("debty", r))},N({v("debty", r)})>a_debt_yrs),'
                        f'AND({num(v("icov", r))},N({v("icov", r)})<a_intcov,N({F("lt_debt_m", r)})>0)),"Fail","Pass")))))', 4)
        V.add("hist", "History (yrs)", 6, "0",
              lambda r: f'=IF(OR({num(F("roic_years", r))},{num(F("margin_years", r))}),'
                        f'MAX(N({F("roic_years", r)}),N({F("margin_years", r)})),"")', 4, **D)
        tests = ["a1", "a2", "a3", "a4"]
        V.add("audit", "4.1 Audit", 9, None,
              lambda r: f'=IF(OR(' + ",".join(f'{v(t, r)}="Fail"' for t in tests) + '),"Fail",'
                        f'IF(AND({v("a1", r)}="No data",OR({v("a2", r)}="No data",{v("a2", r)}="n/a")),"No data","Pass"))', 4, True)
        V.add("short", "History flag", 10, None,
              lambda r: f'=IF(OR({v("funnel", r)}<>"Yes",{v("audit", r)}="No data"),"",IF(OR(N({v("hist", r)})<a_hist,'
                        f'{v("a3", r)}="No data"),"Short history",""))', 4)
        # ---- 4.2 principal protection + 4.3 equity bond
        V.add("lim", "Multiple limit MIN(eff%×100, cap)", 8, "0.0",
              lambda r: f'=IF({hold_(r)},"",IF({num(v("eff", r))},MIN({v("eff", r)}*100,v_mult_cap),""))', 4, **D)
        V.add("p_lim", "M_c ≤ multiple limit", 8, None,
              lambda r: f'=IF({hold_(r)},"n/a",IF(OR({v("lim", r)}="",{v("mcx", r)}=""),"No data",IF({v("mcx", r)}="n/m","Fail",'
                        f'IF({v("mcx", r)}<={v("lim", r)},"Pass","Fail"))))', 4)
        a = lambda r: f"((1+{v('gm', r)})/(1+v_r))"
        K = "((1+v_gt)/(v_r-v_gt))"
        A = lambda r: f"({a(r)}/(1-{a(r)}))"
        V.add("n", "Market-implied CAP n (yrs)", 8, "0.0",
              lambda r: f'=IF(OR({hold_(r)},{v("mc", r)}="",{v("oe", r)}="",{v("gm", r)}=""),"",'
                        f'IF(OR({v("oe", r)}<=0,v_r<=v_gt),"n/m",'
                        f'IFERROR(LN(({v("mc", r)}/{v("oe", r)}-{A(r)})/({K}-{A(r)}))/LN({a(r)}),"n/m")))', 4)
        V.add("navd", "Holding: discount to NAV", 8, "0%",
              lambda r: f'=IF(AND({hold_(r)},N({F("nav_m", r)})>0,{num(v("mc", r))}),1-{v("mc", r)}/{F("nav_m", r)},"")', 4, **D)
        V.add("p_n", "Exit buffer: n < holding period (Holding: NAV discount)", 9, None,
              lambda r: f'=IF({hold_(r)},IF({v("navd", r)}="","No data",IF({v("navd", r)}>=f_navdisc,"Pass","Fail")),'
                        f'IF({v("n", r)}="","No data",IF({v("n", r)}="n/m","Fail",IF({v("n", r)}<v_hold_yrs,"Pass","Fail"))))', 4)
        V.add("eb", "Equity Bond Y_c + g", 9, "0.0%",
              lambda r: f'=IF(AND({num(v("yc", r))},{num(v("g", r))}),{v("yc", r)}+{v("g", r)},"")', 4, True)
        V.add("p_eb", "4.3 Equity Bond: Y_c + g ≥ hurdle", 9, None, lambda r: pf(v("eb", r), f'{v("eb", r)}>=v_eb'), 4, True)
        V.add("needE", "Needs analyst normalised E", 8, None,
              lambda r: f'=IF(AND({v("cyc", r)}="Y",N({F("margin_years", r)})<a_hist,NOT({num(F("e_norm_est", r))})),"Yes","")', 4, **D)
        ok = lambda x: f'OR({x}="Pass",{x}="n/a")'
        V.add("prot", "4.2 Principal Protection", 9, None,
              lambda r: f'=IF(OR({v("p_lim", r)}="Fail",{v("p_n", r)}="Fail",{v("needE", r)}="Yes"),"Fail",'
                        f'IF(AND({ok(v("p_lim", r))},{v("p_n", r)}="Pass"),"Pass","No data"))', 4, True)
        # ---- buy-below price: highest price at which the three valuation tests pass (OE is price-independent)
        dcf = lambda r: f"({A(r)}*(1-{a(r)}^v_hold_yrs)+{a(r)}^v_hold_yrs*{K})"
        V.add("mcmax", "Max market cap passing 4.2 + 4.3 (m)", 11, "#,##0",
              lambda r: f'=IF({hold_(r)},IF(N({F("nav_m", r)})>0,MIN({F("nav_m", r)}*(1-f_navdisc),'
                        f'IF(N({v("g", r)})<v_eb,N({F("dividends_ttm_m", r)})/(v_eb-N({v("g", r)})),9E+99)),""),'
                        f'IF(OR(NOT({num(v("oe", r))}),{v("g", r)}=""),"",IF({v("oe", r)}<=0,"n/m",'
                        f'MIN(IF({num(v("lim", r))},{v("oe", r)}*{v("lim", r)},9E+99),'
                        f'IF({v("g", r)}<v_eb,{v("oe", r)}/(v_eb-{v("g", r)}),9E+99),'
                        f'IF(AND({v("gm", r)}>v_gt,{v("gm", r)}<>v_r),{v("oe", r)}*{dcf(r)},9E+99)))))', 4, **D)
        V.add("buy", "Buy-below price (quote ccy)", 10, "#,##0.00",
              lambda r: f'=IF(AND({num(v("mcmax", r))},{num(v("mc", r))},{num(F("price", r))}),'
                        f'IF({v("mcmax", r)}>=9E+98,"",IF({v("mcmax", r)}<=0,"none",{F("price", r)}*{v("mcmax", r)}/{v("mc", r)})),'
                        f'IF({v("mcmax", r)}="n/m","n/m",""))', 4, True)
        V.add("vsbuy", "Price vs buy-below", 8, "0%",
              lambda r: f'=IF(AND({num(v("buy", r))},{num(F("price", r))}),{F("price", r)}/{v("buy", r)}-1,"")', 4)
        # ---- 4.4 technicals
        V.add("stage", "Weinstein stage", 13, None,
              lambda r: f'=IF(NOT({num(T("ma30", r))}),"No data",'
                        f'{self.stage_expr(T("price", r), T("ma30", r), T("ma30_prev", r), T("high_52w", r))})', 4)
        V.add("sec", "Sector stage", 11, None, lambda r: f'=IFERROR(INDEX(bm_stage,MATCH(Screen!E{r},bm_name,0)),"No data")', 4, **D)
        V.add("entry", "4.4 Stage 2 entry", 9, None,
              lambda r: f'=IF({v("stage", r)}="No data","No data",IF(AND({v("stage", r)}="Stage 2",'
                        f'OR({v("sec", r)}="No data",{v("sec", r)}="",{v("sec", r)}="Stage 2")),"Pass","Fail"))', 4, True)
        V.add("verdict", "Phase 4 verdict", 15, None,
              lambda r: f'=IF({v("funnel", r)}<>"Yes",{q(C.V_NOTFUNNEL)},IF(OR({v("yc", r)}="",{v("audit", r)}="No data"),'
                        f'{q(C.V_NODATA)},IF({v("audit", r)}<>"Pass",{q(C.V_AUDIT)},'
                        f'IF(OR({v("prot", r)}<>"Pass",{v("p_eb", r)}<>"Pass"),{q(C.V_VAL)},'
                        f'IF({v("entry", r)}<>"Pass",{q(C.V_TIME)},IF({S.x("reviewed", r)}="",{q(C.V_UNREV)},{q(C.V_ENTRY)}))))))', 4, True)
        V.add("why", "Verdict detail (failed tests) [earnings flags]", 34, None,
              lambda r: f'=IF({v("verdict", r)}={q(C.V_NOTFUNNEL)},"",TRIM('
                        + "&".join(f'IF({v(t, r)}="Fail","{lbl} ","")' for t, lbl in
                                   (("a1", "Efficiency"), ("a2", "CashQuality"), ("a3", "$1test"), ("a4", "Resilience"),
                                    ("p_lim", "MultipleLimit"), ("p_n", "ExitBuffer"), ("p_eb", "EquityBond")))
                        + f'&IF({v("needE", r)}="Yes","NeedsNormE ","")'
                        + f'&IF({v("entry", r)}="Fail","Entry("&{v("stage", r)}&IF({v("stage", r)}="Stage 2","; sector "&{v("sec", r)},"")&") ","")'
                        + f'&IF({v("short", r)}<>"","("&{v("short", r)}&") ","")&IF({v("nflag", r)}<>"","["&{v("nflag", r)}&"]","")))', 4)
        # ---- Phase 5 helpers (used by Holdings)
        V.add("hold", "Y_c + 0.5g", 8, "0.0%",
              lambda r: f'=IF(AND({num(v("yc", r))},{num(v("g", r))}),{v("yc", r)}+0.5*{v("g", r)},"")', 5, **D)
        V.add("band", "5.1 Hold band", 14, None,
              lambda r: f'=IF({v("hold", r)}="","",IF({v("p_eb", r)}="Pass","Buy zone",IF({v("hold", r)}>=l_hold_hi,"Hold",'
                        f'IF({v("hold", r)}>=l_hold_lo,IF(AND({v("t1", r)}="No",OR({v("stage", r)}="Stage 2",'
                        f'{v("stage", r)}="Stage 2 pullback")),"Stretched hold","Stretched – review"),"Below band"))))', 5, **D)
        V.add("t1", "Trigger 1 moat/cash decay", 9, None,
              lambda r: f'=IF(OR({v("a1", r)}="Fail",AND({typ(r)}="Operating",{num(F("fcf_conv", r))},'
                        f'N({F("fcf_conv", r)})<l_fcf_decay),AND({typ(r)}="Insurer",{v("a2", r)}="Fail"),'
                        f'{v("qres", r)}<>{q(C.RES_QPASS)}),"Yes","No")', 5, **D)
        V.add("t2", "Trigger 2 valuation", 9, None,
              lambda r: f'=IF(OR(AND({num(v("hold", r))},N({v("hold", r)})<l_hold_lo),{v("n", r)}="n/m",'
                        f'AND({num(v("n", r))},N({v("n", r)})>N({v("cap", r)}))),"Yes","No")', 5, **D)
        V.add("t3s", "Trigger 3 stage 3/4", 9, None,
              lambda r: f'=IF(OR({v("stage", r)}="Stage 3",{v("stage", r)}="Stage 4",{v("stage", r)}="Stage 4 rally"),"Yes","No")', 5, **D)
        # ---- list helpers: rank by Equity Bond within list group / Phase 1–3 result
        V.add("sortkey", "helper: sort key", 10, "0",
              lambda r: f'=IF({v("eb", r)}="",-99990000,ROUND({v("eb", r)}*1000,0)*10000)+10000-ROW()', **D)
        V.add("group", "helper: list group", 12, None,
              lambda r: f'=IF(OR({v("verdict", r)}={q(C.V_ENTRY)},{v("verdict", r)}={q(C.V_UNREV)}),{q(ENTRY)},'
                        f'IF(OR({v("verdict", r)}={q(C.V_VAL)},{v("verdict", r)}={q(C.V_TIME)}),{q(WATCH)},{v("verdict", r)}))', **D)
        V.add("listkey", "helper: list key", 22, None,
              lambda r: f'={v("group", r)}&"|"&(COUNTIFS(val_group,{v("group", r)},val_sortkey,">"&{v("sortkey", r)})+1)', **D)
        V.add("qkey", "helper: quality key", 22, None,
              lambda r: f'={v("qres", r)}&"|"&(COUNTIFS(val_qres,{v("qres", r)},val_sortkey,">"&{v("sortkey", r)})+1)', **D)
        self.render(ws, V, "val")
        ws.freeze_panes = "D2"
        rng = lambda k: f"{V.col(k)}2:{V.col(k)}{self.last}"
        for k in tests + ["audit", "p_lim", "p_n", "prot", "p_eb", "entry"]:
            self.passfail_cf(ws, rng(k))
        for res, fill in V_FILL.items():
            ws.conditional_formatting.add(rng("verdict"), CellIsRule(operator="equal", formula=[q(res)], fill=fill))
        for k in ("stage", "sec"):
            ws.conditional_formatting.add(rng(k), CellIsRule(operator="equal", formula=['"Stage 2"'], fill=FILL_GREEN))
            ws.conditional_formatting.add(rng(k), FormulaRule(formula=[f'OR({V.col(k)}2="Stage 4",{V.col(k)}2="Stage 3")'], fill=FILL_RED))
        for k in ("t1", "t2", "t3s", "needE"):
            ws.conditional_formatting.add(rng(k), CellIsRule(operator="equal", formula=['"Yes"'], fill=FILL_RED))
        ws.conditional_formatting.add(rng("short"), CellIsRule(operator="equal", formula=['"Short history"'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("nflag"), FormulaRule(formula=[f'{V.col("nflag")}2<>""'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("vsbuy"), FormulaRule(formula=[f'AND(ISNUMBER({V.col("vsbuy")}2),{V.col("vsbuy")}2<=0)'], fill=FILL_GREEN))
        for val_, fill in (("Buy zone", FILL_GREEN), ("Hold", FILL_LGREEN), ("Stretched hold", FILL_AMBER),
                           ("Stretched – review", FILL_RED), ("Below band", FILL_RED)):
            ws.conditional_formatting.add(rng("band"), CellIsRule(operator="equal", formula=[q(val_)], fill=fill))

    # ------------------------------------------------- Holdings (Phase 5)
    def holdings(self):
        ws = self.wb["Holdings"]
        first, last = 5, 4 + C.HOLDING_ROWS
        body(ws, 1, 1, C.PHASE_LONG[5], font=F_TITLE)
        body(ws, 2, 1, "Enter positions in the blue columns. Everything else is looked up from Valuation / Screen. "
                       "Action is a prompt to review, not an instruction: one trigger = REVIEW; SELL candidate only with "
                       "2+ triggers or Trigger 1. No margin / leverage is assumed.", font=F_NOTE)
        ws.merge_cells("A2:L2")
        for col, (lbl, val, fmt) in enumerate((("Cash (base ccy)", self.m.get("portfolio_cash"), "#,##0"),
                                                ("Total portfolio, all accounts (base ccy; blank = here + cash)",
                                                 self.m.get("portfolio_total"), "#,##0")), 0):
            body(ws, 3, 1 + 3 * col, lbl, font=F_BOLD)
            c_ = body(ws, 3, 2 + 3 * col, val, fmt=fmt, font=F_INPUT)
            c_.fill = FILL_INPUT
        self.name("hold_cash", "Holdings", "$B$3")
        self.name("hold_total", "Holdings", "$E$3")
        cols = list(HOLD_COLUMNS) + [
            ("company", "Company", None, 24), ("price", "Current price", "#,##0.00", 9), ("ret", "Return since entry", "0.0%", 8),
            ("value", "Position value (base ccy)", "#,##0", 11), ("weight", "Weight", "0.0%", 7),
            ("rev_age", "Days since your review", "0", 7),
            ("qres", "Phase 1–3 result", None, 14), ("eb", "Equity Bond Y_c + g now", "0.0%", 8),
            ("buy", "Buy-below price", "#,##0.00", 9),
            ("hold", "Y_c + 0.5g now", "0.0%", 8), ("band", "5.1 Hold band", None, 14),
            ("t1", "T1 moat/cash decay", None, 8), ("t2", "T2 valuation", None, 9), ("t3s", "T3 stage 3/4", None, 8),
            ("alt", "Best alternative Y_c + g (Quality pass, CAP ≥)", "0.0%", 10), ("alt_id", "Best alternative", None, 11),
            ("t3o", "T3 opportunity cost", None, 9), ("action", "Action", None, 36)]
        for i, (k, t, fmt, w) in enumerate(cols, 1):
            header(ws, 4, i, t, w, 5)
        ws.row_dimensions[4].height = 48
        ix = {k: i for i, (k, *_r) in enumerate(cols, 1)}
        c = lambda k, r: f"{L(ix[k])}{r}"
        for j, h in enumerate(self.m["holdings"]):
            for i, (k, _, fmt, _) in enumerate(HOLD_COLUMNS, 1):
                body(ws, first + j, i, parse_date(h.get(k)) if k == "entry_date" else h.get(k), fmt=fmt, font=F_INPUT)
        for r in range(first, last + 1):
            for i, (k, _, fmt, _) in enumerate(HOLD_COLUMNS, 1):
                ws.cell(r, i).font = F_INPUT
                if fmt and fmt != "@":
                    ws.cell(r, i).number_format = fmt
            m_ = f"MATCH({c('id', r)},val_id,0)"
            look = lambda rng: f'=IF({c("id", r)}="","",IFERROR(INDEX({rng},{m_}),"?"))'
            body(ws, r, ix["company"], look("val_company"))
            body(ws, r, ix["price"], look("fin_price"), fmt="#,##0.00")
            body(ws, r, ix["ret"], f'=IF(OR({c("id", r)}="",NOT(ISNUMBER({c("price", r)})),N({c("entry_price", r)})=0),"",'
                                   f'{c("price", r)}/{c("entry_price", r)}-1)', fmt="0.0%")
            body(ws, r, ix["value"], f'=IF(OR({c("id", r)}="",NOT(ISNUMBER({c("price", r)}))),"",N({c("shares", r)})*'
                                     f'{c("price", r)}*IF(ISNUMBER({c("fx_to_base", r)}),{c("fx_to_base", r)},1))', fmt="#,##0")
            body(ws, r, ix["weight"], f'=IF({c("value", r)}="","",{c("value", r)}/hold_port)', fmt="0.0%")
            body(ws, r, ix["rev_age"], f'=IF({c("id", r)}="","",IFERROR(IF(ISNUMBER(INDEX(inp_reviewed,MATCH({c("id", r)},inp_ID,0))),'
                                       f'TODAY()-INDEX(inp_reviewed,MATCH({c("id", r)},inp_ID,0)),"never"),"?"))', fmt="0")
            for k in ("qres", "eb", "buy", "hold", "band", "t1", "t2", "t3s"):
                body(ws, r, ix[k], look(f"val_{k}"), fmt="0.0%" if k in ("eb", "hold") else "#,##0.00" if k == "buy" else None)
            body(ws, r, ix["alt"], f'=IF({c("id", r)}="","",IFERROR(_xlfn.MAXIFS(val_eb,val_qres,{q(C.RES_QPASS)},val_cap,'
                                   f'">="&INDEX(val_cap,{m_}),val_id,"<>"&{c("id", r)}),""))', fmt="0.0%")
            body(ws, r, ix["alt_id"], f'=IF(OR({c("alt", r)}="",N({c("alt", r)})=0),"",IFERROR(INDEX(val_ticker,'
                                      f'MATCH({c("alt", r)},val_eb,0)),""))')
            body(ws, r, ix["t3o"], f'=IF({c("id", r)}="","",IF(N({c("alt", r)})>l_opp,"Yes","No"))')
            trig = (f'IF(OR({c("t1", r)}="Yes",{c("moat_decay", r)}="Y"),"T1 moat/cash ","")&'
                    f'IF({c("t2", r)}="Yes","T2 valuation ","")&IF({c("t3s", r)}="Yes","T3 stage ","")&'
                    f'IF({c("t3o", r)}="Yes","T3 opportunity","")')
            n_trig = (f'(OR({c("t1", r)}="Yes",{c("moat_decay", r)}="Y")+({c("t2", r)}="Yes")+({c("t3s", r)}="Yes")'
                      f'+({c("t3o", r)}="Yes"))')
            t1 = f'OR({c("t1", r)}="Yes",{c("moat_decay", r)}="Y")'
            warn = (f'IF(N({c("weight", r)})>p_max_pos," | over max position","")&'
                    f'IF(OR({c("rev_age", r)}="never",N({c("rev_age", r)})>r_max_age)," | review overdue","")')
            body(ws, r, ix["action"], f'=IF({c("id", r)}="","",IF(OR({n_trig}>=2,{t1}),"SELL candidate: "&TRIM({trig}),'
                                      f'IF({n_trig}=1,"REVIEW: "&TRIM({trig}),'
                                      f'IF({c("band", r)}="Stretched hold","HOLD (stretched band)",'
                                      f'IF({c("band", r)}="Stretched – review","REVIEW: stretched band (moat / MA)","HOLD"))))&{warn})')
        self.col_name("hold_id", "Holdings", ix["id"], first, last)
        self.col_name("hold_value", "Holdings", ix["value"], first, last)
        self.col_name("hold_weight", "Holdings", ix["weight"], first, last)
        self.col_name("hold_revage", "Holdings", ix["rev_age"], first, last)
        body(ws, 3, 10, "Portfolio value used", font=F_BOLD)
        body(ws, 3, 11, f"=IF(N(E3)>0,E3,SUM({L(ix['value'])}{first}:{L(ix['value'])}{last})+N(B3))", fmt="#,##0")
        self.name("hold_port", "Holdings", "$K$3")
        body(ws, 3, 7, "Cash weight", font=F_BOLD)
        body(ws, 3, 8, "=IF(hold_port=0,\"\",N(hold_cash)/hold_port)", fmt="0.0%")
        body(ws, 3, 9, '=IF(AND(COUNTA(hold_id)>0,N(H3)<p_min_cash),"below min cash","")', font=F_BOLD)
        ws.conditional_formatting.add("I3", FormulaRule(formula=['I3<>""'], fill=FILL_RED))
        ws.conditional_formatting.add(r_w := f"{L(ix['weight'])}{first}:{L(ix['weight'])}{last}",
                                      FormulaRule(formula=[f"N({L(ix['weight'])}{first})>p_max_pos"], fill=FILL_RED))
        self.col_name("hold_action", "Holdings", ix["action"], first, last)
        r_ = lambda k: f"{L(ix[k])}{first}:{L(ix[k])}{last}"
        for k in ("t1", "t2", "t3s", "t3o"):
            ws.conditional_formatting.add(r_(k), CellIsRule(operator="equal", formula=['"Yes"'], fill=FILL_RED))
        ws.conditional_formatting.add(r_("action"), FormulaRule(formula=[f'LEFT({L(ix["action"])}{first},4)="SELL"'], fill=FILL_RED))
        ws.conditional_formatting.add(r_("action"), FormulaRule(formula=[f'LEFT({L(ix["action"])}{first},6)="REVIEW"'], fill=FILL_AMBER))
        ws.conditional_formatting.add(r_("action"), FormulaRule(formula=[f'LEFT({L(ix["action"])}{first},4)="HOLD"'], fill=FILL_GREEN))
        dvm = DataValidation(type="list", formula1='"Y"', allow_blank=True)
        ws.add_data_validation(dvm)
        dvm.add(r_("moat_decay"))
        ws.freeze_panes = "C5"

    # -------------------------------------------------------------- Summary
    def summary(self):
        ws, m = self.wb["Summary"], self.m
        for col, w in zip("ABCDEFGHI", (40, 11, 11, 11, 11, 11, 11, 11, 11)):
            ws.column_dimensions[col].width = w
        body(ws, 1, 1, f"Summary — {m['title']} (universe as of {m['as_of']})", font=F_TITLE)
        body(ws, 2, 1, f"Workbook v{self.version}. Gate-based framework; all figures are live formulas.", font=F_NOTE)
        r = 4
        for col, t in enumerate(("Gate funnel (first failed gate)", "Companies", "% of universe"), 1):
            header(ws, r, col, t)
        r += 1
        tot = r

        def row(label, f, bold=False, phase=None):
            nonlocal r
            c = body(ws, r, 1, label, font=F_BOLD if bold else F_BODY)
            if phase is not None:
                c.fill = FILL_SUB
            body(ws, r, 2, f, font=F_BOLD if bold else F_BODY)
            body(ws, r, 3, f"=IF($B${tot}=0,0,B{r}/$B${tot})", fmt="0.0%")
            r += 1

        row("Universe", "=COUNTA(scr_id)", True)
        remaining = f"B{tot}"
        for p in (0, 1, 2, 3):
            first = r
            for k, lbl, ph in C.GATES:
                if ph == p:
                    row(f"   ✗ rejected at {lbl}", f"=COUNTIF(scr_rejected,{q(lbl)})")
            row(f"Remaining after {C.PHASE_LONG[p].split(' (')[0]}", f"={remaining}-SUM(B{first}:B{r - 1})", True, p)
            remaining = f"B{r - 1}"
        row(f"Phase 1–3: {C.RES_QPASS} (= Phase 4 funnel)", f"=COUNTIF(scr_result,{q(C.RES_QPASS)})", True)
        row("… with valuation data", f'=COUNTIF(scr_funnel,"Yes")-COUNTIF(val_verdict,{q(C.V_NODATA)})')
        row("… 4.1 Audit pass", '=COUNTIFS(val_funnel,"Yes",val_audit,"Pass")')
        row("… … of which short history", '=COUNTIFS(val_funnel,"Yes",val_audit,"Pass",val_short,"Short history")')
        row("… 4.2 Principal Protection pass", '=COUNTIFS(val_funnel,"Yes",val_audit,"Pass",val_prot,"Pass")')
        row("… 4.3 Equity Bond pass", '=COUNTIFS(val_funnel,"Yes",val_audit,"Pass",val_prot,"Pass",val_p_eb,"Pass")')
        row("… 4.4 Stage 2 entry", f"=COUNTIF(val_verdict,{q(C.V_ENTRY)})+COUNTIF(val_verdict,{q(C.V_UNREV)})")
        row(f"… … reviewed by you = {C.V_ENTRY}", f"=COUNTIF(val_verdict,{q(C.V_ENTRY)})", True)
        r += 1
        for col, t in enumerate(("Phase 4 verdict", "Companies"), 1):
            header(ws, r, col, t, phase=4)
        for res in C.V_RESULTS[:-1]:
            r += 1
            body(ws, r, 1, res).fill = V_FILL[res]
            body(ws, r, 2, f"=COUNTIF(val_verdict,{q(res)})")
        r += 2
        for col, t in enumerate(("Holdings (Phase 5)", "Positions"), 1):
            header(ws, r, col, t, phase=5)
        for lbl, f in (("Positions", "=COUNTA(hold_id)"), ("HOLD", '=COUNTIF(hold_action,"HOLD")'),
                       ("HOLD (stretched band)", '=COUNTIF(hold_action,"HOLD (stretched band)")'),
                       ("REVIEW", '=COUNTIF(hold_action,"REVIEW*")'),
                       ("SELL candidate", '=COUNTIF(hold_action,"SELL*")'),
                       ("Review overdue", '=COUNTIF(hold_action,"*review overdue*")'),
                       ("Over max position", '=COUNTIF(hold_action,"*over max position*")')):
            r += 1
            body(ws, r, 1, lbl)
            body(ws, r, 2, f)
        r += 2
        heads = ["Companies", *C.Q_RESULTS, C.V_ENTRY, "Avg CAP (yrs)"]

        def table(title, crit_rows):
            nonlocal r
            header(ws, r, 1, title)
            for col, t in enumerate(heads, 2):
                header(ws, r, col, t)
            first = r + 1
            for label, crit in crit_rows:
                r += 1
                body(ws, r, 1, label)
                body(ws, r, 2, f"=COUNTIFS({crit})")
                for j, res in enumerate(C.Q_RESULTS):
                    body(ws, r, 3 + j, f"=COUNTIFS({crit},scr_result,{q(res)})")
                body(ws, r, 8, f"=COUNTIFS({crit},val_verdict,{q(C.V_ENTRY)})")
                body(ws, r, 9, f'=IF(B{r}=0,"",AVERAGEIFS(scr_3_3n,{crit}))', fmt="0.0")
            r += 1
            body(ws, r, 1, "Total", font=F_BOLD)
            for col in range(2, 9):
                body(ws, r, col, f"=SUM({L(col)}{first}:{L(col)}{r - 1})", font=F_BOLD)
            r += 2

        for b in m["breakdowns"]:
            if "field" in b:
                vals = sorted({c[b["field"]] for c in m["companies"] if c.get(b["field"])})
                table(b["title"], [(x, f"scr_{b['field']},{q(x)}") for x in vals])
            else:
                table(b["title"], [(label, ",".join(f"scr_{k},{q(x)}" for k, x in cond.items())) for label, cond in b["flags"]])
        table("3.2 Primary moat", [(x, f"scr_3_2,{q(x)}") for x in C.MOAT_TYPES])
        table("0.0 Model type", [(x, f"scr_0_0,{q(x)}") for x in C.MODEL_TYPES])
        table("2.1c Cyclical", [(x, f"scr_2_1c,{q(x)}") for x in ("Y", "N")])
        table("2.1 Demand Quadrant (2x2)", [(x, f"scr_quad,{q(x)}") for x in ("Target", "Fad Trap", "Long-Cycle Trap", "Low/Low")])
        table("Confidence of pre-scores", [(x, f"scr_conf,{q(x)}") for x in ("H", "M", "L")])
        body(ws, r, 1, "Caveat: qualitative screen plus mechanical valuation rules — not investment advice; see Methodology.", font=F_NOTE)
        ws.freeze_panes = "A4"

    # ----------------------------------------------------------- Shortlists
    def shortlists(self):
        ws = self.wb["Shortlists"]
        body(ws, 1, 1, "Shortlists — live; ordered by Equity Bond return Y_c + g (no valuation data = last)", font=F_TITLE)
        body(ws, 2, 1, "Blank rows = list shorter than its capacity; Data Checks warns on overflow.", font=F_NOTE)
        ctry = [("Country", "scr_country", 12, None)] if self.m.get("show_country") else []
        vc = [("Ticker", "val_ticker", 9, None), ("Company", "val_company", 24, None)]
        blocks = [
            (f"{C.V_ENTRY} (incl. unreviewed)", "val_listkey", ENTRY, "val_group", C.LIST_CAPACITY[C.V_ENTRY],
             vc + [("Verdict", "val_verdict", 15, None), ("Type", "val_type", 9, None), ("Y_c+g", "val_eb", 8, "0.0%"),
                   ("Y_c", "val_yc", 7, "0.0%"), ("Impl. n", "val_n", 7, "0.0"), ("Buy below", "val_buy", 9, "#,##0.00"),
                   ("vs buy-below", "val_vsbuy", 8, "0%"), ("CAP", "val_cap", 5, "0")]),
            ("Watch – valuation / timing", "val_listkey", WATCH, "val_group", C.LIST_CAPACITY["watch"],
             vc + [("Verdict", "val_verdict", 15, None), ("Type", "val_type", 9, None), ("Y_c+g", "val_eb", 8, "0.0%"),
                   ("Buy below", "val_buy", 9, "#,##0.00"), ("vs buy-below", "val_vsbuy", 8, "0%"),
                   ("Stage", "val_stage", 12, None), ("Failed tests", "val_why", 30, None)]),
            (f"Phase 1–3: {C.RES_QPASS}", "val_qkey", C.RES_QPASS, "val_qres", C.LIST_CAPACITY[C.RES_QPASS],
             vc + ctry + [("Sector", "scr_sector", 18, None), ("Verdict", "val_verdict", 15, None),
                          ("Y_c+g", "val_eb", 8, "0.0%"), ("CAP", "val_cap", 5, "0"), ("Primary moat", "scr_3_2", 16, None),
                          ("Moat & erosion note", "scr_moatnote", 30, None), ("Watch points", "scr_weak", 26, None)]),
        ]
        col = 1
        self.caps = []
        for title, keyname, res, grp, cap, fields in blocks:
            header(ws, 3, col, title, phase=4 if keyname == "val_listkey" else 3)
            ws.merge_cells(start_row=3, start_column=col, end_row=3, end_column=col + len(fields))
            header(ws, 4, col, "#", 4)
            for j, (t, key, w, fmt) in enumerate(fields, 1):
                header(ws, 4, col + j, t, w)
            count = f"COUNTIF({grp},{q(res)})"
            for k in range(1, cap + 1):
                r = 4 + k
                body(ws, r, col, f'=IF({k}<={count},{k},"")', fmt="0")
                key_expr = f"MATCH({q(f'{res}|{k}')},{keyname},0)"
                for j, (t, key, w, fmt) in enumerate(fields, 1):
                    body(ws, r, col + j, f'=IF(${L(col)}{r}="","",INDEX({key},{key_expr}))', fmt=fmt)
            self.caps.append((grp, res, title, cap))
            col += len(fields) + 2
        ws.freeze_panes = "A5"

    # ---------------------------------------------------------- Data Checks
    def checks(self):
        ws = self.wb["Data Checks"]
        for c, w in zip("ABCD", (66, 12, 14, 10)):
            ws.column_dimensions[c].width = w
        body(ws, 1, 1, "Data Checks — all should read OK before relying on the results", font=F_TITLE)
        for i, t in enumerate(("Check", "Value", "Expected", "Status"), 1):
            header(ws, 3, i, t)
        rg = lambda code: f"Inputs!{L(self.inp[code])}2:{L(self.inp[code])}{self.last}"
        bad_scores = "+".join(f"(ROWS({g})-COUNTIF({g},0)-COUNTIF({g},1)-COUNTIF({g},2))" for g in map(rg, C.SCORE_CODES))
        bad_gates = "+".join(f'(COUNTA({g})-COUNTIF({g},"Y")-COUNTIF({g},"N"))' for g in map(rg, C.GATE_CODES + C.FLAG_CODES))
        blank_gates = "+".join(f"(ROWS({g})-COUNTA({g}))" for g in map(rg, C.GATE_CODES) if g != rg("0.2"))
        hml = lambda nm: f'ROWS({nm})-COUNTIF({nm},"H")-COUNTIF({nm},"M")-COUNTIF({nm},"L")'
        rows = [
            ("Duplicate company IDs", "=SUMPRODUCT((COUNTIF(inp_ID,inp_ID)>1)*1)", "=0"),
            ("Blank company IDs", "=ROWS(inp_ID)-COUNTA(inp_ID)", "=0"),
            ("Gate inputs not Y/N (non-blank)", "=" + bad_gates, "=0"),
            ("Gate inputs blank = not reviewed (pass by default; 0.2 blank = sub-industry default is fine)", "=" + blank_gates, "=0"),
            ("Score inputs not 0/1/2 (incl. blanks)", "=" + bad_scores, "=0"),
            ("Qualitative CAP (3.3n) missing", "=ROWS(inp_ID)-COUNT(inp_3_3n)", "=0"),
            ("Primary moat (3.2) not one of the six moats / None",
             "=ROWS(inp_3_2)-" + "-".join(f"COUNTIF(inp_3_2,{q(t)})" for t in C.MOAT_TYPES), "=0"),
            ("Your markets table: country not Y/N (Pre-Screen)",
             '=ROWS(mk_in)-COUNTIF(mk_in,"Y")-COUNTIF(mk_in,"N")', "=0"),
            ("Confidence not H/M/L", f"={hml('inp_confidence')}", "=0"),
            ("Model type (0.0) not Operating / Bank / Insurer / Holding",
             "=ROWS(inp_0_0)-" + "-".join(f"COUNTIF(inp_0_0,{q(t)})" for t in C.MODEL_TYPES), "=0"),
            ("Cyclical flag (2.1c) blank", f"=ROWS({rg('2.1c')})-COUNTA({rg('2.1c')})", "=0"),
            ("Parameters changed from the framework default without a logged reason (Methodology)",
             '=SUMPRODUCT((prm_def<>"")*(ROUND(prm_val-prm_def,9)<>0)*(prm_reason=""))', "=0"),
            ("Holdings with your review overdue (> r_max_age days) or never reviewed",
             '=SUMPRODUCT((hold_id<>"")*(((hold_revage="never")+ISNUMBER(hold_revage)*(hold_revage>r_max_age))>0))', "=0"),
            ("Holdings above max position weight", '=SUMPRODUCT(ISNUMBER(hold_weight)*(hold_weight>p_max_pos))', "=0"),
            ("Financials / Technicals rows aligned with Inputs (ID mismatches)",
             "=SUMPRODUCT((fin_id<>inp_ID)*1)+SUMPRODUCT((tec_id<>inp_ID)*1)", "=0"),
            ("Phase 1–3 results reconcile to universe",
             "=" + "+".join(f"COUNTIF(scr_result,{q(x)})" for x in C.Q_RESULTS) + "-COUNTA(scr_id)", "=0"),
            ("Holdings with unknown company ID", '=SUMPRODUCT((hold_id<>"")*ISNA(MATCH(hold_id,inp_ID,0)))', "=0"),
        ]
        for grp, res, title, cap in self.caps:
            rows.append((f"'{title}' list fits Shortlists capacity ({cap})", f"=COUNTIF({grp},{q(res)})", f"<={cap}"))
        rows += [("MARKET benchmark present (info)", '=COUNTIF(bm_name,"MARKET")', "info"),
                 ("Funnel companies without valuation data (info — run fetch_market_data.py)",
                  f"=COUNTIF(val_verdict,{q(C.V_NODATA)})", "info"),
                 ("Funnel companies with short history (info — 4.1 judged on fewer years)",
                  '=COUNTIF(val_short,"Short history")', "info"),
                 ("Cyclicals needing an analyst normalised E (info — Financials e_norm_est)",
                  '=COUNTIFS(val_needE,"Yes",val_funnel,"Yes")', "info"),
                 (f"Entry signals awaiting your review (info — Inputs 'Reviewed by me')",
                  f"=COUNTIF(val_verdict,{q(C.V_UNREV)})", "info")]
        r = 3
        for label, f, exp in rows:
            r += 1
            body(ws, r, 1, label, align=WRAP)
            body(ws, r, 2, f, fmt="0")
            body(ws, r, 3, exp)
            if exp == "info":
                body(ws, r, 4, "info")
            elif exp[0] in "<>":
                body(ws, r, 4, f'=IF(B{r}{exp},"OK","CHECK")')
            else:
                body(ws, r, 4, f'=IF(ROUND(B{r},6){exp},"OK","CHECK")')
        for rg_ in (f"D4:D{r}", f"D{r + 2}"):
            ws.conditional_formatting.add(rg_, CellIsRule(operator="equal", formula=['"OK"'], fill=FILL_GREEN))
            ws.conditional_formatting.add(rg_, CellIsRule(operator="equal", formula=['"CHECK"'], fill=FILL_RED))
        body(ws, r + 2, 1, "Overall status", font=F_BOLD)
        body(ws, r + 2, 4, f'=IF(COUNTIF(D4:D{r},"CHECK")=0,"OK","CHECK")', font=F_BOLD)
        self.name("chk_Overall", "Data Checks", f"$D${r + 2}")

    # ---------------------------------------------- Re-evaluation history
    def reeval_history(self):
        ws = self.wb.create_sheet("Re-evaluation history")
        rows = self.m["reevaluations"]
        fields = list(rows[0].keys())
        for i, f in enumerate(fields, 1):
            header(ws, 1, i, f, 80 if "Justification" in f else 22 if "Scores" in f else 13)
        for r, row in enumerate(rows, 2):
            for i, f in enumerate(fields, 1):
                body(ws, r, i, row.get(f), align=WRAP)
        body(ws, len(rows) + 3, 1, "Pre-v2 re-evaluations (v2 pillar framework). Their effect is in the carried-over "
                                   "base scores.", font=F_NOTE)
        ws.freeze_panes = "A2"

    # --------------------------------------------------------------- Read Me
    def readme(self):
        ws = self.wb["Read Me"]
        ws.column_dimensions["A"].width = 26
        ws.column_dimensions["B"].width = 115
        body(ws, 1, 1, self.m["title"] + " — Gate-based 5-Phase Stock Evaluation Framework", font=F_TITLE)
        r = 2
        for k, val in (("Version", f"v{self.version}"), ("Generated", dt.date.today().isoformat() + " by build.py"),
                       ("Universe as of", self.m["as_of"]), ("Data checks", "=chk_Overall")):
            r += 1
            body(ws, r, 1, k, font=F_BOLD)
            body(ws, r, 2, val)
        ws.conditional_formatting.add(f"B{r}", CellIsRule(operator="equal", formula=['"OK"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(f"B{r}", CellIsRule(operator="equal", formula=['"CHECK"'], fill=FILL_RED))

        def section(title, items):
            nonlocal r
            r += 2
            header(ws, r, 1, title)
            header(ws, r, 2, "")
            for k, val in items:
                r += 1
                body(ws, r, 1, k, font=F_BOLD, align=WRAP)
                body(ws, r, 2, val, align=WRAP)

        section("Framework", [(C.PHASE_NAMES[p], C.PHASE_LONG[p]) for p in range(6)]
                + [("Gate chain", " → ".join(lbl for _, lbl, _ in C.GATES) + " → 4.1 Audit → 4.2 Principal Protection → "
                                  "4.3 Equity Bond → 4.4 Stage 2")])
        section("How to use", [
            ("Pre-Screen", "Gate 2 default per sub-industry on Pre-Screen (N = reject); per company on Inputs → 0.2 (+ reason 0.2r)."),
            ("Change a threshold", "Methodology → yellow cells, plus date and reason in the log columns (red until logged)."),
            ("Re-score a company", "Inputs → blue cells (Y/N gates, 0/1/2 scores, CAP years, primary moat, model type, cyclical flag). "
                                   "Screen → 'Rejected at' shows the first failed gate."),
            ("Your markets", "Pre-Screen → right-hand table: set a listing country to N to exclude it (Gate 2)."),
            ("Details", "Screen / Valuation show the decision columns; click + above the column letters to expand the "
                        "intermediate calculations."),
            ("Your review", "Inputs → 'Reviewed by me' date after you have checked the scores and the annual report yourself. "
                            "Without it an entry signal stays 'Entry – unreviewed'."),
            ("Financial estimates", "Financials → CET1, solvency, combined ratio, NAV, NAV CAGR, LTV are Claude estimates (fin_note) — "
                                    "verify; e_norm_est overrides normalised earnings."),
            ("Phase 4 data", "Run `python3 fetch_market_data.py` (SEC EDGAR + Yahoo Finance), then `python3 build.py`; or type "
                             "into Financials / Technicals. Analyst growth g / g_moat go in Financials (blank = fallback)."),
            ("Positions", "Holdings → enter ID, entry date/price, shares; Action applies the hold band and sell triggers."),
            ("Before relying on results", "Data Checks → Overall status must be OK. Pre-scored v4 fields carry Confidence v4."),
            ("Rebuild / new version", "`python3 sync_from_excel.py <universe>` pulls your edits back into data/, then `python3 build.py`."),
        ])
        section("Sheets", [
            ("Summary", "Gate-by-gate funnel (where companies are rejected), Phase 4 steps, verdicts, holdings, breakdowns."),
            ("Shortlists", "Entry candidates, Watch (valuation / timing) with buy-below prices, Quality pass — ordered by Y_c + g."),
            ("Methodology", "Parameters (named cells), rules and formulas, gate and score rubrics, how inputs were seeded."),
            ("Pre-Screen", "Gate 2 Sole-Owner defaults: your markets (by listing country) and sub-industries (your inputs)."),
            ("Inputs", "Phase 1–3 inputs per company (gates, scores, CAP years, notes, confidence)."),
            ("Screen", "Phases 1–3: gate values, 2x2 quadrant, strongest moat, phase pass/reject, first failed gate, result."),
            ("Financials / Technicals / Benchmarks", "Phase 4 inputs (fetched or typed)."),
            ("Valuation", "Phase 4 by model type: audit gates, principal protection, Equity Bond, buy-below price, Weinstein "
                          "stage, verdict; normalised earnings and Phase 5 helpers in the collapsed detail columns."),
            ("Holdings", "Phase 5 position tracker with weights, cash floor, review age and REVIEW / SELL candidate actions."),
            ("Data Checks", "Integrity checks."),
        ])
        section("Colour legend", [
            ("Blue text", "Input (Inputs, Financials, Technicals, Benchmarks, Holdings, Pre-Screen)."),
            ("Yellow fill", "Editable parameter / Sole-Owner switch."),
            ("Black text", "Formula — do not overwrite."),
            ("Header colours", "Grey = Pre-Screen, blue = WHY, green = WHAT, purple = HOW, orange = PROOF & ENTRY, navy = LIFECYCLE."),
        ])
        section("Change log", [(f"v{ver}", "• " + "\n• ".join(items)) for ver, items in C.CHANGELOG.items()])
        ws.row_dimensions[r].height = 15 * 2 * len(C.CHANGELOG[max(C.CHANGELOG, key=float)]) + 30
        r += 2
        body(ws, r, 1, self.m["caveat"], font=F_NOTE, align=WRAP)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.row_dimensions[r].height = 45


def build_workbook(meta: dict, version: str, path) -> None:
    Builder(meta, version).build(path)
