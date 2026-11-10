"""Compile one universe's source data into a versioned v6.0 screening workbook
('Equity Bond Below PAR' — Two-Part Qualitative & Quantitative Architecture).
"""
from __future__ import annotations

import datetime as dt

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

from . import config as C
from .gates import funnel_ids

# ------------------------------------------------------------------- styles
FONT = "Calibri"
F_HDR = Font(name=FONT, bold=True, color="FFFFFF")
F_TITLE = Font(name=FONT, bold=True, size=14)
F_BOLD = Font(name=FONT, bold=True)
F_BODY = Font(name=FONT)
F_INPUT = Font(name=FONT, color="0000FF")
F_INPUT_BOLD = Font(name=FONT, bold=True, color="0000FF")
F_NOTE = Font(name=FONT, italic=True, color="595959")
FILL_HDR = PatternFill("solid", fgColor="1F3864")
PHASE_FILL = {0: "7F7F7F", 1: "2F5597", 2: "548235", 3: "7030A0", 4: "2F5597", 5: "7030A0", 6: "548235", 7: "C55A11"}
FILL_SUB = PatternFill("solid", fgColor="D9E1F2")
FILL_INPUT = PatternFill("solid", fgColor="FFF2CC")
mk = lambda c: PatternFill("solid", fgColor=c, bgColor=c)
FILL_RED, FILL_AMBER, FILL_GREEN, FILL_LGREEN, FILL_GREY = map(mk, ("F4CCCC", "FFF2CC", "D9EAD3", "EAF4E4", "EDEDED"))
WRAP = Alignment(wrap_text=True, vertical="top")
HDR_ALIGN = Alignment(wrap_text=True, vertical="center", horizontal="center")

Q_FILL = {C.RES_QPASS: FILL_GREEN, C.RES_REVIEW: FILL_AMBER, **{C.RES_REJ[p]: FILL_RED for p in (2, 3, 4, 5, 6)},
          C.RES_REJ[1]: FILL_GREY}
V_FILL = {C.V_BELOW_PAR: FILL_GREEN, C.V_ABOVE_PAR: FILL_AMBER, C.V_NODATA: FILL_GREY, C.V_NOTFUNNEL: FILL_GREY}


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

    def add(self, key, title, width, fmt, fn, phase=None, bold=False, detail=False, style=None):
        """detail=True: intermediate calculation or raw accounting input, grouped and collapsed on the sheet.
        style: None (formula), 'input' (blue text), 'override' (yellow fill + blue text), 'note' (grey italic)."""
        self.items.append((key, title, width, fmt, fn, phase, bold, style))
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
        for i, (key, title, width, fmt, fn, phase, bold, style) in enumerate(cols.items, 1):
            header(ws, 1, i, title, width, phase)
            for r in range(2, self.last + 1):
                font = F_INPUT_BOLD if (style in ("input", "override") and bold) else (
                    F_INPUT if style in ("input", "override") else (
                        F_NOTE if style == "note" else (F_BOLD if bold else F_BODY)))
                c = body(ws, r, i, fn(r), fmt=fmt, font=font)
                if style == "override":
                    c.fill = FILL_INPUT
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
        for t in ("Summary", "Shortlists", "Qualitative", "Quantitative", "Pre-Screen", "Methodology", "Data Checks"):
            wb.create_sheet(t)
        self.methodology()
        self.prescreen()
        self.qualitative()
        self.quantitative()
        self.summary()
        self.shortlists()
        self.checks()
        self.readme()
        for s in wb.worksheets:
            s.sheet_view.zoomScale = 90
        wb.active = 1
        wb.calculation.fullCalcOnLoad = True
        import os
        import tempfile
        import shutil
        import zipfile
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name
        wb.save(tmp_path)
        ie_xml = (b'<ignoredErrors><ignoredError sqref="A1:AZ1000" formula="1" formulaRange="1" '
                  b'emptyCellReference="1" numberStoredAsText="1" twoDigitTextYear="1"/></ignoredErrors></worksheet>')
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp2:
            tmp2_path = tmp2.name
        with zipfile.ZipFile(tmp_path, "r") as zin, zipfile.ZipFile(tmp2_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith("xl/worksheets/sheet") and item.filename.endswith(".xml"):
                    data = data.replace(b"</worksheet>", ie_xml)
                zout.writestr(item, data)
        os.unlink(tmp_path)
        shutil.move(tmp2_path, path)

    # ---------------------------------------------------------- Methodology
    def methodology(self):
        ws, m = self.wb["Methodology"], self.m
        for col, w in zip("ABCDEFG", (48, 12, 34, 70, 34, 34, 34)):
            ws.column_dimensions[col].width = w
        body(ws, 1, 1, m["title"] + " — Two-Part Qualitative & Quantitative Framework ('Equity Bond Below PAR')", font=F_TITLE)
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
        body(ws, r, 1, "Core Principles ('6 Munger Quality Gates + Equity Bond Below PAR')", font=F_BOLD)
        chain = " → ".join(lbl for _, lbl, _ in C.GATES)
        rules = [
            "Ben Graham & Charlie Munger Principle: 'An investment that upon proper research and simplicity of choice offers "
            "protection of principal and an adequate return' + 'Tell me where I am going to die so that I never go there.' "
            "The model is split into two core sheets: (1) 'Qualitative' (6 Munger Reject Gates) and (2) 'Quantitative' "
            "('Equity Bond Below PAR' — 4–5Y PAR valuation, coupon & timing).",
            "1. Qualitative Sheet ('The Best Street' — 6 Munger Reject Gates): Every qualitative step is a REJECT gate. A company "
            f"leaves the funnel at the FIRST gate it fails ('Rejected at'); gate order: {chain}. Qualitative result = '{C.RES_QPASS}', "
            f"'Rejected – <gate>', or '{C.RES_REVIEW}' when the first gate not yet passed is blank (a blank never passes). "
            "Only 'Quality pass' companies enter the Quantitative sheet.",
            "The 6 Munger Quality Gates: (1) Simple to understand (Gate 1), (2) Products and services serve an essential need of "
            "customers in the Western world with low societal and legislative acceptance risk (Gate 2, blank = Pre-Screen market "
            "table by listing country), (3) Strong moat with the ability to raise prices at or above inflation "
            "(Gate 3: Toll booths / Switching costs, Scale economies shared, Irreplaceable infrastructure, or R&D super-thinkers / "
            "Intangibles; proof of moat: 5Y median ROIC >= 12% & incremental ROIIC >= 12%), "
            "(4) Low risk for business model disruption or obsolescence with a predictable 15+ year runway "
            "(Gate 4: CAP >= thr_cap, default 15 yrs), (5) Honest, able, customer value-for-money focused management with a history of good capital allocation "
            "(Gate 5 >= thr_culture), and (6) Real cash conversion, peak-to-peak compounding across business cycles, "
            "and a self-funding fortress balance sheet (Gate 6; blank = Pre-Screen sub-industry default — N for regulated "
            "utilities and deposit banks; Quantitative → 'G6 rule check' flags net debt > g6_netdebt_yrs, interest cover < "
            "g6_intcov and no new peak vs the prior cycle for your review).",
            "2. Quantitative Sheet ('Equity Bond Below PAR'): Uses one universal Owner Earnings definition across all businesses "
            "with zero business-type exceptions and zero pre-filled overrides: Owner Earnings = Continuing Net Income + "
            "MAX(0, D&A − CapEx), and Owner EPS = Owner Earnings ÷ Diluted Shares (GAAP Net Income already deducts SBC on the "
            "income statement; when CapEx < D&A, excess non-cash acquisition intangible amortisation is added back).",
            "4–5 Year Business Cycle PAR Valuation (computed by fetch_market_data.py, screener/fetch/par.py): Last Peak Owner "
            "EPS = highest Owner EPS of the latest 5 fiscal years (years whose net income is > 30% above operating cash flow "
            "and neighbouring years are left out as one-off gains). Cycle Low / High Multiple = MIN / MAX of the calendar-year "
            "medians of monthly price ÷ the peak Owner EPS known at that month (last 60 months). Cycle g = peak-to-peak growth "
            "vs the prior 5 fiscal years (short Yahoo histories: first year to peak). Crucial methodology condition: the business must "
            "achieve a new high in Owner EPS at the peak of each succeeding business cycle (temporary mid-cycle dips are normal, "
            "provided peak-to-peak growth continues). 3-Pillar Fundamental PAR Multiple = MIN(Cycle High Multiple, "
            "(2 × (Implied Owner EPS g × 100) + (Cycle Low Multiple + Cycle High Multiple) ÷ 2 + min(Operating ROIC × 100, par_roic_cap [35])) ÷ 3). "
            "Integrates Benjamin Graham's secular growth premium (2 × g), the market's empirical 5-year cycle multiple midpoint, and "
            "uncorrupted operating capital return (Operating ROIC = NOPAT ÷ Tangible Invested Capital; businesses on negative net tangible capital "
            "automatically align with the 35% cap). Neutralizes both negative-equity buyback noise and M&A goodwill distortions without inflating asset-heavy businesses. "
            "Crucial guardrail: the resulting multiple is strictly capped at Cycle High Multiple (never projecting through-the-cycle fair value "
            "above the peak multiple the market was willing to pay), protecting balance-sheet financials (Munich Re capped at 11.4x, moving to Above PAR) "
            "and holding companies from unrealistic multiple expansion while leaving pure compounders unaffected. "
            "PAR Value (Price) = PAR Multiple × Last Peak Owner EPS. Current Multiple = Current Share Price ÷ Last Peak Owner EPS. A stock "
            "trading at or below PAR Value (Price vs. PAR <= 0%) is rated 'Below PAR'.",
            "Equity Bond Coupon, Implied Coupon & 5Y Expected IRR (Pull-to-PAR): Shows historical Cycle Owner EPS Growth (g) + "
            "Dividend Yield (DY) = Equity Bond Coupon (g + DY), 5–10Y forward Implied Owner EPS g + DY = Implied Coupon, "
            "and 5Y Expected IRR = (1 + g_imp) × (PAR Value / Price)^(1/5) + DY − 1, capturing both the operating earnings coupon "
            "and the annualized multiple expansion boost from buying Below PAR. Blank yellow cells ('My Peak EPS' and 'My growth g') "
            "let you type your own override when desired.",
            "Financial Health & Timing Context (Non-Disqualifying): Median ROIC, Cash Conversion (FCF ÷ NI), LT Debt ÷ Owner "
            "Earnings (yrs), and Interest Coverage (EBIT ÷ Interest) are colour-coded green/amber for awareness without "
            "kicking a Quality-pass company off the list. Weinstein Stage (Stage 2 vs Stage 1/3/4) and Dip from 52W High (%) "
            "show whether you are buying a Stage 2 uptrend or buying the dip.",
        ]
        for t in rules:
            r += 1
            body(ws, r, 1, t, align=WRAP)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = 48

        r += 2
        for col, t in enumerate(("Gate / section", "Code", "Criterion", "Definition", "N / 0 =", "Y / 1 =", "2 ="), 1):
            header(ws, r, col, t)
        prev = None
        for f in C.FIELDS:
            r += 1
            body(ws, r, 1, f"{C.PHASE_LONG[f['phase']]}" if f["section"] != prev else None, align=WRAP)
            prev = f["section"]
            body(ws, r, 2, f["code"])
            body(ws, r, 3, f["name"] + (" — GATE" if f["type"] == "gate" else ""), align=WRAP)
            body(ws, r, 4, f["definition"], align=WRAP)
            if f["type"] == "score":
                for k in (0, 1, 2):
                    body(ws, r, 5 + k, f["rubric"][k], align=WRAP)
            elif f["type"] == "gate":
                body(ws, r, 5, "REJECT: " + f["rubric"]["N"], align=WRAP)
                body(ws, r, 6, "PASS: " + f["rubric"]["Y"], align=WRAP)
            elif f["type"] in ("number", "category"):
                body(ws, r, 5, "Values: " + " / ".join(map(str, f["options"])), align=WRAP)
        r += 2
        body(ws, r, 1, "Data sources", font=F_BOLD)
        for t in [m["sources"]]:
            r += 1
            body(ws, r, 1, t, align=WRAP)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = 48

    # ----------------------------------------------------------- Pre-Screen
    def prescreen(self):
        ws = self.wb["Pre-Screen"]
        body(ws, 1, 1, C.PHASE_LONG[2], font=F_TITLE)
        body(ws, 2, 1, "Defaults for blank gate inputs. Right: your markets by listing country — N = Gate 2 (Essential Western "
                       "Need) rejects. Left: Gate 6 default by sub-industry — N = Gate 6 (Cash & Fortress Balance Sheet) rejects "
                       "(regulated utilities: capped ROIC, perpetual capex; deposit banks: 10-15x leverage); blank = no default. "
                       "A value typed on Qualitative (2. override / 6. input) supersedes these per company.",
                 font=F_NOTE, align=WRAP)
        ws.merge_cells("A2:D2")
        ws.row_dimensions[2].height = 60
        for i, (t, w) in enumerate((("GICS Sector", 24), ("GICS Sub-Industry", 40), ("Gate 6 default (N / blank)", 10),
                                    ("Note", 50), ("helper: key", 40)), 1):
            header(ws, 4, i, t, w, phase=0)
        rows = self.m["prescreen"]
        first, last = 5, 4 + len(rows)
        for j, p in enumerate(rows):
            r = first + j
            body(ws, r, 1, p["sector"])
            body(ws, r, 2, p["sub_industry"])
            body(ws, r, 3, p.get("g6_default"), font=F_INPUT).fill = FILL_INPUT
            body(ws, r, 4, p.get("note"), font=F_INPUT)
            body(ws, r, 5, f'=A{r}&"|"&B{r}', font=F_NOTE)
        self.name("ps_key", "Pre-Screen", f"$E${first}:$E${last}")
        self.name("ps_g6", "Pre-Screen", f"$C${first}:$C${last}")
        v = DataValidation(type="list", formula1='"N"', allow_blank=True)
        ws.add_data_validation(v)
        v.add(f"C{first}:C{last}")
        ws.conditional_formatting.add(f"C{first}:C{last}", CellIsRule(operator="equal", formula=['"N"'], fill=FILL_RED))
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

    @staticmethod
    def score_cf(ws, rng):
        for val, fill in (("0", FILL_RED), ("1", FILL_AMBER), ("2", FILL_GREEN)):
            ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[val], fill=fill))

    @staticmethod
    def gate_cf(ws, rng):
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"N"'], fill=FILL_RED))
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Y"'], fill=FILL_GREEN))

    # ----------------------------------------- Qualitative (5 Munger Gates unified)
    def qualitative(self):
        ws = self.wb["Qualitative"]
        Q = self.S = Cols("Qualitative")
        comps = self.m["companies"]
        val_fn = lambda key: (lambda r, k=key: comps[r - 2].get(k))

        # 1. Identity columns
        for key, title, fmt, width in (
            ("id", "ID (unique)", "@", 12),
            ("ticker", "Ticker", "@", 10),
            ("company", "Company", "@", 26),
            ("country", "Country", "@", 13),
            ("sector", "GICS Sector", "@", 20),
            ("sub_industry", "GICS Sub-Industry", "@", 26),
        ):
            Q.add(key, title, width, fmt, val_fn(key), bold=(key == "ticker"), style="input")
        for c in self.extra:
            Q.add(c["key"], c["header"], c["width"], c["fmt"], val_fn(c["key"]), style="input")

        fails = {
            "1": lambda r: f'{Q.ref("1", r)}="N"',
            "2": lambda r: f'{Q.ref("2", r)}="N"',
            "3b": lambda r: f'OR({Q.ref("3b", r)}="N",{Q.ref("3a", r)}="None")',
            "4": lambda r: f'AND(ISNUMBER({Q.ref("4", r)}),N({Q.ref("4", r)})<thr_cap)',
            "5": lambda r: f'AND(ISNUMBER({Q.ref("5", r)}),N({Q.ref("5", r)})<thr_culture)',
            "6": lambda r: f'{Q.ref("6", r)}="N"',
        }
        # blank = not yet reviewed: the company stops at that gate as 'To review' (never a silent pass)
        blanks = {
            "1": lambda r: f'{Q.ref("1", r)}=""',
            "2": lambda r: "FALSE",
            "3b": lambda r: f'OR({Q.ref("3b", r)}="",{Q.ref("3a", r)}="")',
            "4": lambda r: f'NOT(ISNUMBER({Q.ref("4", r)}))',
            "5": lambda r: f'NOT(ISNUMBER({Q.ref("5", r)}))',
            "6": lambda r: f'{Q.ref("6", r)}=""',
        }

        # 2. Gate 1: Simple to Understand
        Q.add("1", "1. Simple to Understand (gate)", 10, "@", val_fn("1"), 1, style="input")

        # 3. Gate 2: Essential Western Need & Low Societal / Legislative Risk
        Q.add("2_in", "2. Essential Western Need (override)", 10, "@", val_fn("2"), 2, detail=True, style="input")
        Q.add("in_market", "Listing country in your markets", 8, None,
              lambda r: f'=IFERROR(INDEX(mk_in,MATCH({Q.ref("country", r)},mk_country,0)),"Y")', 2, detail=True)
        Q.add("2", "2. Essential Western Need (gate)", 10, None,
              lambda r: f'=IF({Q.ref("2_in", r)}<>"",{Q.ref("2_in", r)},IF({Q.ref("in_market", r)}="N","N","Y"))', 2)
        Q.add("2r", "2r. Essential Need / Risk reason", 28, "@", val_fn("2r"), 2, detail=True, style="input")

        # 4. Gate 3: Strong Moat & Pricing Power >= Inflation
        Q.add("3a", "3a. Moat Archetype", 22, "@", val_fn("3a"), 3, style="input")
        Q.add("3b", "3b. Pricing >= Inflation (gate)", 10, "@", val_fn("3b"), 3, style="input")

        # 5. Gate 4: Low Disruption Risk / 15+ Year Runway (CAP)
        Q.add("4", "4. Runway — CAP (yrs)", 10, "0", val_fn("4"), 4, style="input")

        # 6. Gate 5: Honest, Able, Customer-Focused Management & Capital Allocation
        Q.add("5", "5. Management & Capital Allocation (0/1/2)", 10, "0", val_fn("5"), 5, style="input")

        # 7. Gate 6: Real Cash Conversion, Peak-to-Peak Compounding & Fortress Balance Sheet
        Q.add("6_in", "6. Peak Compounding & Fortress Balance Sheet (input)", 11, "@", val_fn("6"), 6, style="input")
        Q.add("g6_default", "Gate 6 sub-industry default (Pre-Screen)", 9, None,
              lambda r: f'=IFERROR(""&INDEX(ps_g6,MATCH({Q.ref("sector", r)}&"|"&{Q.ref("sub_industry", r)},ps_key,0)),"")',
              6, detail=True)
        Q.add("6", "6. Cash & Fortress Balance Sheet (gate)", 10, None,
              lambda r: f'=IF({Q.ref("6_in", r)}<>"",{Q.ref("6_in", r)},{Q.ref("g6_default", r)})', 6)

        # 8. Live Qualitative Verdict
        stage_lbl = {"1": "G1 (Simplicity)", "2": "G2 (Need)", "3b": "G3 (Moat/Price)", "4": "G4 (Runway)",
                     "5": "G5 (Management)", "6": "G6 (Fortress/Peak)"}

        def chain(r, on_fail, on_blank, final):
            """IF(fail_1, …, IF(blank_1, …, IF(fail_2, …))) in gate order — mirrors gates.phase_results."""
            body_, n = "", 0
            for k, lbl, p in C.GATES:
                body_ += f"IF({fails[k](r)},{on_fail(k, lbl, p)},"
                n += 1
                if k != "2":
                    body_ += f"IF({blanks[k](r)},{on_blank(k, lbl, p)},"
                    n += 1
            return "=" + body_ + final + ")" * n

        Q.add("stage", "Review Stage / Action", 19, None,
              lambda r: chain(r, lambda k, l, p: q("Rejected @ " + stage_lbl[k]),
                              lambda k, l, p: q("To review @ " + stage_lbl[k]), q("Quality Pass (Funnel)")), bold=True)
        Q.add("rejected", "Rejected at (first failed gate)", 22, None,
              lambda r: chain(r, lambda k, l, p: q(l), lambda k, l, p: '""', '""'), bold=True)
        Q.add("result", "Qualitative result (Gates 1–6)", 22, None,
              lambda r: chain(r, lambda k, l, p: q(C.RES_REJ[p]), lambda k, l, p: q(C.RES_REVIEW), q(C.RES_QPASS)),
              bold=True)
        Q.add("funnel", "In Quantitative funnel", 8, None,
              lambda r: f'=IF({Q.ref("result", r)}={q(C.RES_QPASS)},"Yes","No")', detail=True)

        # 8. Qualitative Notes & Evidence
        Q.add("moatnote", "3m. Moat & erosion note", 42, "@", val_fn("3m"), 3, style="input")
        Q.add("note", "Qualitative note", 55, "@", val_fn("note"), style="input")
        Q.add("evidence", "Key evidence / sources", 30, "@", val_fn("evidence"), detail=True, style="input")

        self.render(ws, Q, "scr")
        ws.freeze_panes = "D2"

        # Named aliases for Data Checks / sync compatibility
        self.inp = dict(Q.idx)
        self.inp["2"] = Q.idx["2_in"]
        self.inp["6"] = Q.idx["6_in"]
        self.inp["3m"] = Q.idx["moatnote"]
        self.name("inp_ID", "Qualitative", f"$A$2:$A${self.last}")
        for k, col_k in (("4", "4"), ("3a", "3a")):
            self.col_name(f"inp_{k}", "Qualitative", Q.idx[col_k])

        def dv(formula, key, msg):
            c = Q.col(key)
            v = DataValidation(type="list", formula1=formula, allow_blank=True, showErrorMessage=True, error=msg)
            ws.add_data_validation(v)
            v.add(f"{c}2:{c}{self.last}")

        rng = lambda a: f"{Q.col(a)}2:{Q.col(a)}{self.last}"

        # Visual Waterfall: gray out downstream gates if any prior gate failed
        c_ref = lambda k: f"${Q.col(k)}2"
        f_abs = {
            "1": f'{c_ref("1")}="N"',
            "2": f'{c_ref("2")}="N"',
            "3b": f'OR({c_ref("3b")}="N",{c_ref("3a")}="None")',
            "4": f'AND(ISNUMBER({c_ref("4")}),N({c_ref("4")})<thr_cap)',
            "5": f'AND(ISNUMBER({c_ref("5")}),N({c_ref("5")})<thr_culture)',
        }
        prior_fails = {
            2: f_abs["1"],
            3: f'OR({f_abs["1"]},{f_abs["2"]})',
            4: f'OR({f_abs["1"]},{f_abs["2"]},{f_abs["3b"]})',
            5: f'OR({f_abs["1"]},{f_abs["2"]},{f_abs["3b"]},{f_abs["4"]})',
            6: f'OR({f_abs["1"]},{f_abs["2"]},{f_abs["3b"]},{f_abs["4"]},{f_abs["5"]})',
        }
        f_inactive = Font(name=FONT, color="8A8A8A")
        for g_num, col_keys in (
            (2, ["2_in", "2", "2r"]),
            (3, ["3a", "3b", "moatnote"]),
            (4, ["4"]),
            (5, ["5"]),
            (6, ["6_in", "g6_default", "6"]),
        ):
            rule_inactive = FormulaRule(formula=[prior_fails[g_num]], fill=FILL_GREY, font=f_inactive, stopIfTrue=True)
            for k in col_keys:
                if k in Q.idx:
                    ws.conditional_formatting.add(rng(k), rule_inactive)

        for f in C.FIELDS:
            col_key = {"2": "2_in", "6": "6_in", "3m": "moatnote"}.get(f["code"], f["code"])
            c = Q.col(col_key)
            if f["type"] == "score":
                dv('"0,1,2"', col_key, "0, 1 or 2")
                self.score_cf(ws, f"{c}2:{c}{self.last}")
            elif f["type"] == "gate":
                dv('"Y,N"', col_key, "Y or N (blank = not reviewed)")
                self.gate_cf(ws, f"{c}2:{c}{self.last}")
            elif f["type"] in ("number", "category"):
                dv(q(",".join(map(str, f["options"]))), col_key, " / ".join(map(str, f["options"])))
        for x in self.extra:
            if x.get("validation"):
                dv(q(",".join(x["validation"])), x["key"], "/".join(x["validation"]))

        self.gate_cf(ws, rng("2"))
        self.gate_cf(ws, rng("6"))
        for res, fill in Q_FILL.items():
            ws.conditional_formatting.add(rng("result"), CellIsRule(operator="equal", formula=[q(res)], fill=fill))
        ws.conditional_formatting.add(rng("4"), FormulaRule(formula=[f"AND(ISNUMBER({Q.col('4')}2),{Q.col('4')}2<thr_cap)"], fill=FILL_RED))
        ws.conditional_formatting.add(rng("4"), FormulaRule(formula=[f"AND(ISNUMBER({Q.col('4')}2),{Q.col('4')}2>=thr_cap)"], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("3a"), CellIsRule(operator="equal", formula=['"None"'], fill=FILL_RED))

        # Review Stage / Action formatting
        ws.conditional_formatting.add(rng("stage"), CellIsRule(operator="equal", formula=['"Quality Pass (Funnel)"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("stage"), FormulaRule(formula=[f'LEFT(${Q.col("stage")}2,9)="To review"'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("stage"), FormulaRule(formula=[f'LEFT(${Q.col("stage")}2,8)="Rejected"'], fill=FILL_GREY, font=f_inactive))

    @staticmethod
    def stage_expr(P, M, M0, H):
        slope = f"({M}/{M0}-1)"
        return (f'IF(NOT(ISNUMBER({M0})),"No data",IF({slope}>t_slope,IF({P}>{M},"Stage 2","Stage 2 pullback"),'
                f'IF({slope}<-t_slope,IF({P}<{M},"Stage 4","Stage 4 rally"),'
                f'IF({P}>={H}*(1-t_near_high),"Stage 3","Stage 1"))))')

    # ------------------------------------- Quantitative (Equity Bond Below PAR)
    def quantitative(self):
        ws = self.wb["Quantitative"]
        V = self.V = Cols("Quantitative")
        Q = self.S
        comps = self.m["companies"]
        fins = self.m["financials"]
        techs = self.m["technicals"]
        f_in = lambda key: (lambda r, k=key: fins.get(comps[r - 2]["id"], {}).get(k))
        t_in = lambda key: (lambda r, k=key: techs.get(comps[r - 2]["id"], {}).get(k))
        num = lambda x: f"ISNUMBER({x})"
        v = V.ref
        D = dict(detail=True)

        # 1. Identity & Funnel
        V.add("id", "ID", 11, None, lambda r: f"={Q.x('id', r)}")
        V.add("ticker", "Ticker", 10, None, lambda r: f"={Q.x('ticker', r)}", bold=True)
        V.add("company", "Company", 24, None, lambda r: f"={Q.x('company', r)}")
        V.add("sector", "GICS Sector", 18, None, lambda r: f"={Q.x('sector', r)}", **D)
        V.add("qres", "Qualitative result", 14, None, lambda r: f"={Q.x('result', r)}", **D)
        V.add("funnel", "In funnel", 7, None, lambda r: f"={Q.x('funnel', r)}", **D)
        V.add("cap", "CAP (yrs)", 7, "0", lambda r: f"={Q.x('4', r)}", 4)
        V.add("quote_ccy", "Quote ccy", 6, "@", f_in("quote_currency"), 6, style="input")

        # 2. 4–5 Year Business Cycle PAR Valuation
        V.add("peak_oe_year", "Peak EPS year", 8, "0", f_in("peak_oe_year"), 4, style="input")
        V.add("peak_oe_eps", "Last Peak Owner EPS", 10, "#,##0.00", f_in("peak_oe_eps"), 4, style="input")
        V.add("peak_eps_est", "My Peak EPS (override)", 10, "#,##0.00", f_in("peak_eps_est"), 4, style="override")
        V.add("peak_eps", "Peak Owner EPS used", 10, "#,##0.00",
              lambda r: f'=IF({num(v("peak_eps_est", r))},{v("peak_eps_est", r)},'
                        f'IF({num(v("peak_oe_eps", r))},{v("peak_oe_eps", r)},""))', 4, **D)
        V.add("price", "Share price", 10, "#,##0.00", f_in("price"), 4, bold=True, style="input")
        V.add("cur_mult", "Current multiple (P ÷ Peak EPS)", 9, '0.0"x"',
              lambda r: f'=IF(AND({num(v("price", r))},{num(v("peak_eps", r))},N({v("peak_eps", r)})>0),'
                        f'{v("price", r)}/{v("peak_eps", r)},"")', 4, bold=True)
        V.add("mult_low_5y", "Cycle low multiple (5Y)", 9, '0.0"x"', f_in("mult_low_5y"), 4, style="input")
        V.add("mult_high_5y", "Cycle high multiple (5Y)", 9, '0.0"x"', f_in("mult_high_5y"), 4, style="input")
        V.add("par_mult", "PAR multiple (fundamental)", 9, '0.0"x"',
              lambda r: f'=IF(AND({num(v("mult_low_5y", r))},{num(v("mult_high_5y", r))}),'
                        f'MIN({v("mult_high_5y", r)},('
                        f'MIN(40,200*MAX(0,IF({num(v("g_imp", r))},{v("g_imp", r)},par_g_base)))+'
                        f'({v("mult_low_5y", r)}+{v("mult_high_5y", r)})/2+'
                        f'IF({num(v("roic_used", r))},MIN({v("roic_used", r)}*100,par_roic_cap),18))/3),"")', 4, bold=True)
        V.add("buy", "PAR value (price)", 10, "#,##0.00",
              lambda r: f'=IF(AND({num(v("par_mult", r))},{num(v("peak_eps", r))}),'
                        f'{v("par_mult", r)}*{v("peak_eps", r)},"")', 4, bold=True)
        V.add("vsbuy", "Price vs. PAR (%)", 9, "+0.0%;-0.0%;0.0%",
              lambda r: f'=IF(AND({num(v("price", r))},{num(v("buy", r))},N({v("buy", r)})>0),'
                        f'{v("price", r)}/{v("buy", r)}-1,"")', 4, bold=True)
        V.add("verdict", "PAR valuation status", 13, None,
              lambda r: f'=IF({v("funnel", r)}<>"Yes",{q(C.V_NOTFUNNEL)},'
                        f'IF(NOT({num(v("vsbuy", r))}),{q(C.V_NODATA)},'
                        f'IF({v("vsbuy", r)}<=0,{q(C.V_BELOW_PAR)},{q(C.V_ABOVE_PAR)})))', 4, bold=True)
        V.add("cap_implied", "Market-implied CAP (yrs)", 11, "0.0",
              lambda r: f'=IF(AND({num(v("cap", r))},{num(v("price", r))},{num(v("buy", r))},N({v("buy", r)})>0),'
                        f'ROUND({v("cap", r)}*({v("price", r)}/{v("buy", r)}),1),"")', 4, **D)
        V.add("cap_margin", "Moat runway margin (yrs)", 11, "+0.0;-0.0;0.0",
              lambda r: f'=IF(AND({num(v("cap", r))},{num(v("cap_implied", r))}),'
                        f'{v("cap", r)}-{v("cap_implied", r)},"")', 4, bold=True)

        # 3. Equity Bond Coupon & Implied 5–10Y Cycle Coupon (No Fixed Hurdle Rate)
        V.add("cagr_oe_eps", "Cycle Owner EPS growth (g)", 9, "0.0%", f_in("cagr_oe_eps"), 4, style="input")
        V.add("g", "Cycle Owner EPS g used", 9, "0.0%",
              lambda r: f'=IF({num(v("cagr_oe_eps", r))},{v("cagr_oe_eps", r)},"")', 4, **D)
        V.add("dy", "Dividend yield (DY)", 8, "0.0%",
              lambda r: f'=IF(AND({num(v("market_cap_m", r))},N({v("market_cap_m", r)})>0),'
                        f'N({v("dividends_ttm_m", r)})/{v("market_cap_m", r)},"")', 4)
        V.add("eb", "Equity Bond coupon (g + DY)", 10, "0.0%",
              lambda r: f'=IF({num(v("g", r))},{v("g", r)}+N({v("dy", r)}),"")', 4, bold=True)
        V.add("g_implied", "Implied Owner EPS g (5–10Y)", 10, "0.0%", f_in("g_implied"), 4, style="input")
        V.add("g_est", "My growth g (override)", 9, "0.0%", f_in("g_est"), 4, style="override")
        V.add("g_imp", "Implied Owner EPS g used", 9, "0.0%",
              lambda r: f'=IF({num(v("g_est", r))},{v("g_est", r)},'
                        f'IF({num(v("g_implied", r))},MIN(par_g_cap,{v("g_implied", r)}),'
                        f'IF({num(v("g", r))},MIN(par_g_cap,MAX(0.02,0.15*(MAX(0,{v("g", r)})-par_g_base)+par_g_base)),par_g_base)))',
              4, **D)
        V.add("eb_imp", "Implied Coupon (Implied g + DY)", 10, "0.0%",
              lambda r: f'=IF({num(v("g_imp", r))},{v("g_imp", r)}+N({v("dy", r)}),"")', 4, bold=True)
        V.add("g_market", "Market-implied g (cycle)", 10, "+0.0%;-0.0%;0.0%",
              lambda r: f'=IF(AND({num(v("cur_mult", r))},{num(v("mult_low_5y", r))},{num(v("mult_high_5y", r))}),'
                        f'(3*{v("cur_mult", r)}-({v("mult_low_5y", r)}+{v("mult_high_5y", r)})/2-'
                        f'IF({num(v("roic_used", r))},MIN({v("roic_used", r)}*100,par_roic_cap),18))/200,"")', 4, **D)
        V.add("g_margin", "Growth margin (g_imp − g_mkt)", 10, "+0.0%;-0.0%;0.0%",
              lambda r: f'=IF(AND({num(v("g_imp", r))},{num(v("g_market", r))}),{v("g_imp", r)}-{v("g_market", r)},"")', 4, bold=True)
        V.add("irr_5y", "5Y Expected IRR (Pull-to-PAR)", 11, "0.0%",
              lambda r: f'=IF(AND({num(v("price", r))},{num(v("buy", r))},'
                        f'N({v("price", r)})>0,N({v("buy", r)})>0,{num(v("g_imp", r))}),'
                        f'(1+{v("g_imp", r)})*({v("buy", r)}/{v("price", r)})^(1/5)+N({v("dy", r)})-1,"")', 4, bold=True)

        # 4. Timing Context (Weinstein Stage 2 & Dip from 52W High)
        V.add("stage", "Weinstein stage", 13, None,
              lambda r: f'=IF(NOT({num(v("ma30", r))}),"No data",'
                        f'{self.stage_expr(v("tec_price", r), v("ma30", r), v("ma30_prev", r), v("high_52w", r))})', 4)
        V.add("dip", "Dip from 52W high (%)", 9, "0.0%",
              lambda r: f'=IF(AND({num(v("price", r))},{num(v("high_52w", r))},N({v("high_52w", r)})>0),'
                        f'MIN(0,{v("price", r)}/{v("high_52w", r)}-1),"")', 4)

        # 5. Financial Health Context (Colour-Coded Indicators, Non-Disqualifying)
        V.add("roic_operating", "Operating ROIC 5Y (Tangible)", 9, "0.0%", f_in("roic_operating"), 4, style="input")
        V.add("roic_est", "My ROIC (override)", 9, "0.0%", f_in("roic_est"), 4, style="override")
        V.add("roic_used", "Operating ROIC used", 9, "0.0%",
              lambda r: f'=IF({num(v("roic_est", r))},{v("roic_est", r)},'
                        f'IF({num(v("roic_operating", r))},{v("roic_operating", r)},'
                        f'IF({num(v("roic_median", r))},{v("roic_median", r)},"")))', 4, **D)
        V.add("roic_median", "Median ROIC 5Y (GAAP)", 9, "0.0%", f_in("roic_median"), 4, style="input")
        V.add("fcf_conv", "Cash conversion (FCF ÷ NI)", 9, "0%", f_in("fcf_conv"), 4, style="input")
        V.add("debty", "LT debt ÷ Owner Earnings (yrs)", 9, "0.0",
              lambda r: f'=IF(AND({num(v("lt_debt_m", r))},{num(v("oe_m", r))}),'
                        f'IF({v("lt_debt_m", r)}<=0,0,IF({v("oe_m", r)}>0,{v("lt_debt_m", r)}/{v("oe_m", r)},"n/m")),"")', 4)
        V.add("icov", "Interest cover (×)", 9, "0.0",
              lambda r: f'=IF(AND({num(v("ebit_ttm_m", r))},{num(v("interest_m", r))}),'
                        f'IF({v("interest_m", r)}=0,999,{v("ebit_ttm_m", r)}/ABS({v("interest_m", r)})),"")', 4)
        V.add("why", "Financial health notes", 24, None,
              lambda r: f'=IF({v("funnel", r)}<>"Yes","",TRIM('
                        f'IF(AND({num(v("roic_used", r))},{v("roic_used", r)}<a_roic_gaap),"ROIC<"&TEXT(a_roic_gaap,"0%")&" ","")&'
                        f'IF(AND({num(v("fcf_conv", r))},{v("fcf_conv", r)}<a_fcfconv),"FCF<"&TEXT(a_fcfconv,"0%")&" ","")&'
                        f'IF(OR({v("debty", r)}="n/m",AND({num(v("debty", r))},N({v("debty", r)})>a_debt_yrs)),"Debt>"&a_debt_yrs&"y ","")&'
                        f'IF(AND({num(v("icov", r))},N({v("icov", r)})<a_intcov,N({v("lt_debt_m", r)})>0),"IntCov<"&a_intcov&"x","")))', 4)
        V.add("netdebty", "Net debt ÷ Owner Earnings (yrs)", 9, "0.0",
              lambda r: f'=IF(AND({num(v("lt_debt_m", r))},{num(v("oe_m", r))}),'
                        f'IF({v("lt_debt_m", r)}-N({v("cash_m", r)})<=0,0,IF({v("oe_m", r)}>0,'
                        f'({v("lt_debt_m", r)}-N({v("cash_m", r)}))/{v("oe_m", r)},"n/m")),"")', 4)
        V.add("p2p_ok", "New peak vs prior cycle (Y/N)", 7, "@", f_in("p2p_ok"), 4, style="input")
        V.add("g6check", "G6 rule check (flags for review)", 22, None,
              lambda r: f'=TRIM(IF(OR({v("netdebty", r)}="n/m",AND({num(v("netdebty", r))},N({v("netdebty", r)})>g6_netdebt_yrs)),'
                        f'"NetDebt>"&g6_netdebt_yrs&"y ","")&'
                        f'IF(AND({num(v("icov", r))},N({v("icov", r)})<g6_intcov,N({v("lt_debt_m", r)})>0),"IntCov<"&g6_intcov&"x ","")&'
                        f'IF({v("p2p_ok", r)}="N","No new peak",""))', 4)
        V.add("fin_note", "Analyst note", 26, "@", f_in("fin_note"), 4, style="input")

        # 6. Raw Accounting & Technical Inputs Used by Formulas (Grouped & Collapsed Detail Columns)
        V.add("fin_currency", "Reporting currency", 8, "@", f_in("fin_currency"), 4, **D, style="input")
        V.add("market_cap_m", "Market cap (m, rep ccy)", 11, "#,##0", f_in("market_cap_m"), 4, **D, style="input")
        V.add("ni_ttm_m", "Net income latest FY (m)", 11, "#,##0", f_in("ni_ttm_m"), 4, **D, style="input")
        V.add("da_ttm_m", "D&A latest FY (m)", 10, "#,##0", f_in("da_ttm_m"), 4, **D, style="input")
        V.add("capex_ttm_m", "CapEx latest FY (m)", 10, "#,##0", f_in("capex_ttm_m"), 4, **D, style="input")
        V.add("oe_m", "Owner Earnings latest FY (m)", 11, "#,##0",
              lambda r: f'=IF({num(v("ni_ttm_m", r))},{v("ni_ttm_m", r)}+MAX(0,N({v("da_ttm_m", r)})-N({v("capex_ttm_m", r)})),"")',
              4, **D)
        V.add("dividends_ttm_m", "Dividends latest FY (m)", 10, "#,##0", f_in("dividends_ttm_m"), 4, **D, style="input")
        V.add("lt_debt_m", "Long-term debt (m)", 10, "#,##0", f_in("lt_debt_m"), 4, **D, style="input")
        V.add("cash_m", "Cash (m)", 10, "#,##0", f_in("cash_m"), 4, **D, style="input")
        V.add("interest_m", "Interest expense (m)", 10, "#,##0", f_in("interest_m"), 4, **D, style="input")
        V.add("ebit_ttm_m", "EBIT latest FY (m)", 10, "#,##0", f_in("ebit_ttm_m"), 4, **D, style="input")
        V.add("as_of", "Data as of", 11, "@", f_in("as_of"), 4, **D, style="input")
        V.add("source", "Source", 16, "@", f_in("source"), 4, **D, style="input")
        V.add("tec_sym", "Price symbol", 10, "@", t_in("symbol"), 4, **D, style="input")
        V.add("tec_as_of", "As of (week)", 11, "@", t_in("as_of"), 4, **D, style="input")
        V.add("tec_price", "Weekly close", 10, "#,##0.00", t_in("price"), 4, **D, style="input")
        V.add("ma30", "30-wk MA", 10, "#,##0.00", t_in("ma30"), 4, **D, style="input")
        V.add("ma30_prev", "30-wk MA 5 wks ago", 10, "#,##0.00", t_in("ma30_prev"), 4, **D, style="input")
        V.add("high_52w", "52-wk high", 10, "#,##0.00", t_in("high_52w"), 4, **D, style="input")

        # 7. Ranking & Shortlist Helpers (Ordered by largest discount to PAR: most negative vsbuy first)
        V.add("sortkey", "helper: sort key", 10, "0",
              lambda r: f'=IF(NOT({num(v("vsbuy", r))}),-999900000,-ROUND({v("vsbuy", r)}*10000,0)*10000)+10000-ROW()', **D)
        V.add("group", "helper: list group", 12, None, lambda r: f'={v("verdict", r)}', **D)
        V.add("listkey", "helper: list key", 22, None,
              lambda r: f'={v("group", r)}&"|"&(COUNTIFS(val_group,{v("group", r)},val_sortkey,">"&{v("sortkey", r)})+1)', **D)

        self.render(ws, V, "val")
        ws.freeze_panes = "D2"

        # Hide non-funnel rows by default so Quantitative opens directly to 'The Best Street'
        funnel_set = set(funnel_ids(self.m))
        for r, c in enumerate(comps, 2):
            if c["id"] not in funnel_set:
                ws.row_dimensions[r].hidden = True

        # Conditional formatting for PAR Valuation, Timing, and Financial Health Indicators
        rng = lambda k: f"{V.col(k)}2:{V.col(k)}{self.last}"
        for res, fill in V_FILL.items():
            ws.conditional_formatting.add(rng("verdict"), CellIsRule(operator="equal", formula=[q(res)], fill=fill))
        ws.conditional_formatting.add(rng("vsbuy"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("vsbuy")}2),{V.col("vsbuy")}2<=0)'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("vsbuy"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("vsbuy")}2),{V.col("vsbuy")}2>0,{V.col("vsbuy")}2<=0.15)'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("vsbuy"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("vsbuy")}2),{V.col("vsbuy")}2>0.15)'], fill=FILL_RED))
        ws.conditional_formatting.add(rng("cap_margin"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("cap_margin")}2),{V.col("cap_margin")}2>0)'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("cap_margin"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("cap_margin")}2),{V.col("cap_margin")}2<0)'], fill=FILL_RED))
        ws.conditional_formatting.add(rng("g_margin"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("g_margin")}2),{V.col("g_margin")}2>0)'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("g_margin"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("g_margin")}2),{V.col("g_margin")}2<0)'], fill=FILL_RED))

        ws.conditional_formatting.add(rng("stage"), CellIsRule(operator="equal", formula=['"Stage 2"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("stage"), CellIsRule(operator="equal", formula=['"Stage 2 pullback"'], fill=FILL_LGREEN))
        ws.conditional_formatting.add(rng("stage"), FormulaRule(
            formula=[f'OR({V.col("stage")}2="Stage 4",{V.col("stage")}2="Stage 3")'], fill=FILL_RED))

        # Financial health indicator colour-coding (informational context)
        ws.conditional_formatting.add(rng("roic_operating"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("roic_operating")}2),{V.col("roic_operating")}2>=a_roic_gaap)'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("roic_operating"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("roic_operating")}2),{V.col("roic_operating")}2<a_roic_gaap)'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("roic_median"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("roic_median")}2),{V.col("roic_median")}2>=a_roic_gaap)'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("roic_median"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("roic_median")}2),{V.col("roic_median")}2<a_roic_gaap)'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("fcf_conv"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("fcf_conv")}2),{V.col("fcf_conv")}2>=a_fcfconv)'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("fcf_conv"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("fcf_conv")}2),{V.col("fcf_conv")}2<a_fcfconv)'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("debty"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("debty")}2),{V.col("debty")}2<=a_debt_yrs)'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("debty"), FormulaRule(
            formula=[f'OR({V.col("debty")}2="n/m",AND(ISNUMBER({V.col("debty")}2),{V.col("debty")}2>a_debt_yrs))'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("icov"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("icov")}2),{V.col("icov")}2>=a_intcov)'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("icov"), FormulaRule(
            formula=[f'AND(ISNUMBER({V.col("icov")}2),{V.col("icov")}2<a_intcov)'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("why"), FormulaRule(formula=[f'{V.col("why")}2<>""'], fill=FILL_AMBER))
        ws.conditional_formatting.add(rng("g6check"), FormulaRule(formula=[f'{V.col("g6check")}2<>""'], fill=FILL_RED))
        ws.conditional_formatting.add(rng("p2p_ok"), CellIsRule(operator="equal", formula=['"N"'], fill=FILL_RED))

    # -------------------------------------------------------------- Summary
    def summary(self):
        ws, m = self.wb["Summary"], self.m
        for col, w in zip("ABCDEFGHIJK", (44, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11)):
            ws.column_dimensions[col].width = w
        body(ws, 1, 1, f"Summary — {m['title']} (universe as of {m['as_of']})", font=F_TITLE)
        body(ws, 2, 1, f"Workbook v{self.version}. Two-Part Qualitative & Quantitative ('6 Munger Gates + Equity Bond Below PAR'); all figures are live formulas.", font=F_NOTE)
        r = 4
        for col, t in enumerate(("1. Qualitative Funnel (6 Munger Reject Gates — First Failed Gate)", "Companies", "% of universe"), 1):
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
        for k, lbl, p in C.GATES:
            first = r
            row(f"   ✗ rejected at {lbl}", f"=COUNTIF(scr_rejected,{q(lbl)})")
            row(f"Remaining after {lbl}", f"={remaining}-B{first}", True, p)
            remaining = f"B{r - 1}"
        row(f"   … awaiting review (blank gate reached): {C.RES_REVIEW}", f"=COUNTIF(scr_result,{q(C.RES_REVIEW)})")
        row(f"Qualitative Pass: {C.RES_QPASS} ('The Best Street')", f"=COUNTIF(scr_result,{q(C.RES_QPASS)})", True)
        row("… with 4–5Y cycle PAR data", f'=COUNTIF(scr_funnel,"Yes")-COUNTIF(val_verdict,{q(C.V_NODATA)})')
        row(f"… Trading Below PAR ({C.V_BELOW_PAR})", f"=COUNTIF(val_verdict,{q(C.V_BELOW_PAR)})", True)
        row("… … of which in Weinstein Stage 2 uptrend",
            f'=COUNTIFS(val_verdict,{q(C.V_BELOW_PAR)},val_stage,"Stage 2")')
        row("… … of which buying the dip (Stage 1 / 2 pullback / 3 / 4)",
            f'=COUNTIF(val_verdict,{q(C.V_BELOW_PAR)})-COUNTIFS(val_verdict,{q(C.V_BELOW_PAR)},val_stage,"Stage 2")')
        row(f"… Above PAR Watchlist ({C.V_ABOVE_PAR})", f"=COUNTIF(val_verdict,{q(C.V_ABOVE_PAR)})")

        r += 1
        for col, t in enumerate(("2. Quantitative PAR Valuation Status", "Companies"), 1):
            header(ws, r, col, t, phase=6)
        for res in C.V_RESULTS[:-1]:
            r += 1
            body(ws, r, 1, res).fill = V_FILL[res]
            body(ws, r, 2, f"=COUNTIF(val_verdict,{q(res)})")

        r += 2
        heads = ["Companies", *C.Q_RESULTS, C.V_BELOW_PAR, "Avg CAP (yrs)"]
        bpar_col = 3 + len(C.Q_RESULTS)
        cap_col = bpar_col + 1

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
                body(ws, r, bpar_col, f"=COUNTIFS({crit},val_verdict,{q(C.V_BELOW_PAR)})")
                body(ws, r, cap_col, f'=IF(B{r}=0,"",AVERAGEIFS(scr_4,{crit}))', fmt="0.0")
            r += 1
            body(ws, r, 1, "Total", font=F_BOLD)
            for col in range(2, cap_col):
                body(ws, r, col, f"=SUM({L(col)}{first}:{L(col)}{r - 1})", font=F_BOLD)
            r += 2

        for b in m["breakdowns"]:
            if "field" in b:
                vals = sorted({c[b["field"]] for c in m["companies"] if c.get(b["field"])})
                table(b["title"], [(x, f"scr_{b['field']},{q(x)}") for x in vals])
            else:
                table(b["title"], [(label, ",".join(f"scr_{k},{q(x)}" for k, x in cond.items())) for label, cond in b["flags"]])
        table("3a. Moat Archetype", [(x, f"scr_3a,{q(x)}") for x in C.MOAT_TYPES])
        body(ws, r, 1, "Caveat: qualitative screen plus mechanical PAR valuation rules — not investment advice; see Methodology.", font=F_NOTE)
        ws.freeze_panes = "A4"

    # ----------------------------------------------------------- Shortlists
    def shortlists(self):
        ws = self.wb["Shortlists"]
        body(ws, 1, 1, "Shortlists — 'Cheapest Houses on the Best Street' (live; ordered by discount to PAR Value)", font=F_TITLE)
        body(ws, 2, 1, "Table 1 = Quality-pass stocks trading Below PAR (ordered by largest discount to PAR). "
                       "Table 2 = Above PAR Watchlist (ordered by closest to PAR).", font=F_NOTE)
        ctry = [("Country", "scr_country", 11, None)] if self.m.get("show_country") else []
        vc = [("Ticker", "val_ticker", 9, None), ("Company", "val_company", 24, None)] + ctry
        par_cols = [
            ("Price", "val_price", 9, "#,##0.00"),
            ("PAR value", "val_buy", 9, "#,##0.00"),
            ("vs PAR", "val_vsbuy", 8, "+0.0%;-0.0%;0.0%"),
            ("Cur mult", "val_cur_mult", 8, '0.0"x"'),
            ("PAR mult", "val_par_mult", 8, '0.0"x"'),
            ("Owner EPS g", "val_g", 8, "0.0%"),
            ("Div yield", "val_dy", 7, "0.0%"),
            ("Coupon (g+DY)", "val_eb", 9, "0.0%"),
            ("Implied Owner EPS g", "val_g_imp", 9, "0.0%"),
            ("Implied g (mkt)", "val_g_market", 8, "+0.0%;-0.0%;0.0%"),
            ("Growth margin", "val_g_margin", 8, "+0.0%;-0.0%;0.0%"),
            ("Implied Coupon", "val_eb_imp", 9, "0.0%"),
            ("5Y Cycle IRR", "val_irr_5y", 9, "0.0%"),
            ("Stage", "val_stage", 12, None),
            ("Dip 52W", "val_dip", 8, "0.0%"),
            ("Op ROIC", "val_roic_used", 7, "0.0%"),
            ("GAAP ROIC", "val_roic_median", 7, "0.0%"),
            ("CAP", "val_cap", 5, "0"),
            ("Implied CAP", "val_cap_implied", 8, "0.0"),
            ("Moat margin", "val_cap_margin", 8, "+0.0;-0.0;0.0"),
            ("Moat archetype", "scr_3a", 18, None),
            ("Health notes", "val_why", 18, None),
        ]
        blocks = [
            (f"1. Trading Below PAR ({C.V_BELOW_PAR} — Price <= PAR Value)", "val_listkey", C.V_BELOW_PAR, "val_group",
             C.LIST_CAPACITY[C.V_BELOW_PAR], vc + par_cols),
            (f"2. Above PAR Watchlist ({C.V_ABOVE_PAR} — Price > PAR Value)", "val_listkey", C.V_ABOVE_PAR, "val_group",
             C.LIST_CAPACITY[C.V_ABOVE_PAR], vc + par_cols),
        ]
        col = 1
        self.caps = []
        for title, keyname, res, grp, cap, fields in blocks:
            header(ws, 3, col, title, phase=6)
            ws.merge_cells(start_row=3, start_column=col, end_row=3, end_column=col + len(fields))
            header(ws, 4, col, "#", 4)
            for j, (t, key, w, fmt) in enumerate(fields, 1):
                header(ws, 4, col + j, t, w)
            count = f"COUNTIF({grp},{q(res)})"
            for k in range(1, cap + 1):
                r = 4 + k
                body(ws, r, col, f'=IF(ROW()-4<={count},ROW()-4,"")', fmt="0")
                key_expr = f"MATCH({q(res + '|')}&${L(col)}{r},{keyname},0)"
                for j, (t, key, w, fmt) in enumerate(fields, 1):
                    body(ws, r, col + j, f'=IF(${L(col)}{r}="","",INDEX({key},{key_expr}))', fmt=fmt,
                         font=F_BOLD if key in ("val_ticker", "val_vsbuy", "val_eb", "val_eb_imp", "val_irr_5y", "val_cap_margin", "val_g_margin") else F_BODY)
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
        rg = lambda code: f"Qualitative!{L(self.inp[code])}2:{L(self.inp[code])}{self.last}"
        bad_scores = "+".join(f"(COUNTA({g})-COUNTIF({g},0)-COUNTIF({g},1)-COUNTIF({g},2))" for g in map(rg, C.SCORE_CODES))
        bad_gates = "+".join(f'(COUNTA({g})-COUNTIF({g},"Y")-COUNTIF({g},"N"))' for g in map(rg, C.GATE_CODES))
        missing_g1 = f"ROWS(Qualitative!{L(self.inp['1'])}2:{L(self.inp['1'])}{self.last})-COUNTA(Qualitative!{L(self.inp['1'])}2:{L(self.inp['1'])}{self.last})"
        rows = [
            ("Duplicate company IDs", "=SUMPRODUCT((COUNTIF(inp_ID,inp_ID)>1)*1)", "=0"),
            ("Blank company IDs", "=ROWS(inp_ID)-COUNTA(inp_ID)", "=0"),
            ("Gate 1 (Simplicity) inputs missing (must be evaluated for all companies)", f"={missing_g1}", "=0"),
            ("Gate inputs not Y/N when entered", "=" + bad_gates, "=0"),
            ("Score inputs not 0/1/2 when entered", "=" + bad_scores, "=0"),
            ("Predictable Runway CAP (Gate 4) non-numeric when entered", "=COUNTA(inp_4)-COUNT(inp_4)", "=0"),
            ("Moat Archetype (Gate 3a) not one of the four archetypes / None when entered",
             "=COUNTA(inp_3a)-" + "-".join(f"COUNTIF(inp_3a,{q(t)})" for t in C.MOAT_TYPES), "=0"),
            ("Your markets table: country not Y/N (Pre-Screen)",
             '=ROWS(mk_in)-COUNTIF(mk_in,"Y")-COUNTIF(mk_in,"N")', "=0"),
            ("Parameters changed from the framework default without a logged reason (Methodology)",
             '=SUMPRODUCT((prm_def<>"")*(ROUND(prm_val-prm_def,9)<>0)*(prm_reason=""))', "=0"),
            ("Quantitative rows aligned with Qualitative (ID mismatches)",
             "=SUMPRODUCT((val_id<>inp_ID)*1)", "=0"),
            ("Qualitative results (Gates 1–6) reconcile to universe",
             "=" + "+".join(f"COUNTIF(scr_result,{q(x)})" for x in C.Q_RESULTS) + "-COUNTA(scr_id)", "=0"),
        ]
        for grp, res, title, cap in self.caps:
            rows.append((f"'{title}' list fits Shortlists capacity ({cap})", f"=COUNTIF({grp},{q(res)})", f"<={cap}"))
        rows += [
            ("Funnel companies without PAR valuation data (info)",
             f"=COUNTIF(val_verdict,{q(C.V_NODATA)})", "info"),
            ("Companies awaiting review — first gate not yet passed is blank (info)",
             f"=COUNTIF(scr_result,{q(C.RES_REVIEW)})", "info"),
            ("Quality-pass companies with Gate 6 rule-check flags (info)",
             f'=COUNTIFS(val_funnel,"Yes",val_g6check,"?*")', "info"),
            ("Funnel companies trading Below PAR (info)",
             f"=COUNTIF(val_verdict,{q(C.V_BELOW_PAR)})", "info"),
        ]
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

    # --------------------------------------------------------------- Read Me
    def readme(self):
        ws = self.wb["Read Me"]
        ws.column_dimensions["A"].width = 28
        ws.column_dimensions["B"].width = 115
        body(ws, 1, 1, self.m["title"] + " — Two-Part Qualitative & Quantitative Framework ('6 Munger Gates + Equity Bond Below PAR')", font=F_TITLE)
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

        section("Framework", [(C.PHASE_NAMES[p], C.PHASE_LONG[p]) for p in (1, 2, 3, 4, 5, 6, 7)]
                + [("Flow", "1. Qualitative (6 Munger Reject Gates) → 2. Quantitative ('Equity Bond Below PAR') → 3. Shortlists")])
        section("How to use", [
            ("1. Qualitative Waterfall", "Sequential Munger reject flow: if a company fails an earlier gate, downstream cells "
                                         "are bypassed and automatically gray out. Use the 'Review Stage / Action' column filter "
                                         "(e.g. 'To review @ G6 (Fortress/Peak)' or 'Quality Pass (Funnel)') to focus on the companies waiting at a stage. "
                                         "A blank gate input stops a company as 'To review' — it never passes silently."),
            ("2. Quantitative ('Equity Bond Below PAR')", "Shows Quality-pass companies with 4–5Y Peak Owner EPS, Cycle Low–High Multiples, "
                                                          "PAR Multiple, PAR Value, Price vs. PAR (%), Equity Bond Coupon (g + DY), "
                                                          "Implied Owner EPS g (5–10Y), Implied Coupon, 5Y Expected IRR (Pull-to-PAR), Weinstein Stage, "
                                                          "Dip from 52W High, and colour-coded Financial Health indicators."),
            ("3. Custom overrides", "On 'Quantitative', use the blank yellow cells ('My Peak EPS', 'My growth g', and 'My ROIC') to type your own "
                                    "Owner EPS, growth, or operating ROIC assumption after reading an annual/quarterly report."),
            ("4. Expand details", "Click the '+' outline buttons above the columns on 'Qualitative' or 'Quantitative' to inspect "
                                  "raw accounting numbers (Market Cap, Net Income, D&A, CapEx, Debt, 30-wk MA)."),
            ("5. Shortlists", "Table 1 ranks all Quality-pass stocks trading Below PAR (Price <= PAR Value) by largest discount to PAR. "
                              "Table 2 ranks Above PAR stocks by closest to PAR."),
            ("6. Rebuild / sync", "`python3 sync_from_excel.py <universe>` pulls your edits back into data/, then `python3 build.py`."),
        ])
        section("Sheets", [
            ("Summary", "6-Gate Qualitative funnel counts, Below PAR / Above PAR counts, Stage 2 vs Dip breakdown, and sector/moat tables."),
            ("Shortlists", "Live ranked lists: (1) Trading Below PAR, (2) Above PAR Watchlist."),
            ("Qualitative", "Unified 6 Munger Reject Gates sheet: all qualitative inputs + live First Failed Gate and Result."),
            ("Quantitative", "Unified PAR Valuation, Equity Bond Coupon, Implied Coupon, 5Y Expected IRR, Timing (Stage 2 / Dip), and Financial Health sheet."),
            ("Pre-Screen", "Defaults for blank inputs: your markets by listing country (Gate 2) and the Gate 6 sub-industry default "
                           "(N for regulated utilities and deposit-taking banks)."),
            ("Methodology", "Parameters (named cells), core principles, and qualitative gate/score rubrics."),
            ("Data Checks", "Integrity and reconciliation checks."),
        ])
        section("Colour legend", [
            ("Blue text", "Data input (Qualitative scores/gates, Quantitative historical cycle numbers, Pre-Screen)."),
            ("Yellow fill + blue text", "Your custom override cells ('My Peak EPS', 'My growth g', Methodology parameters)."),
            ("Black text", "Live formula — do not overwrite."),
            ("Green / Amber / Red fill", "Below PAR / Healthy indicator (green), Watch / Borderline (amber), Reject / Warning (red)."),
        ])
        section("Change log", [(f"v{ver}", "• " + "\n• ".join(items)) for ver, items in C.CHANGELOG.items()])
        ws.row_dimensions[r].height = 15 * 2 * len(C.CHANGELOG[max(C.CHANGELOG, key=float)]) + 30
        r += 2
        body(ws, r, 1, self.m["caveat"], font=F_NOTE, align=WRAP)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.row_dimensions[r].height = 45


def build_workbook(meta: dict, version: str, path) -> None:
    Builder(meta, version).build(path)
