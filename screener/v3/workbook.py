"""Compile one universe's source data into a versioned v3 screening workbook (5-Phase framework)."""
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

Q_FILL = {C.RES_QPASS: FILL_GREEN, C.RES_NEAR: FILL_AMBER, C.RES_FAIL: FILL_RED, C.RES_EXCL: FILL_GREY}
V_FILL = {C.V_ENTRY: FILL_GREEN, C.V_TIME: FILL_LGREEN, C.V_VAL: FILL_AMBER, C.V_AUDIT: FILL_RED,
          C.V_NODATA: FILL_GREY, C.V_NOTFUNNEL: FILL_GREY}


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
        self.sheet, self.items, self.idx = sheet, [], {}

    def add(self, key, title, width, fmt, fn, phase=None, bold=False):
        self.items.append((key, title, width, fmt, fn, phase, bold))
        self.idx[key] = len(self.items)

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

    # ---------------------------------------------------------------- build
    def build(self, path):
        wb = self.wb
        wb.active.title = "Read Me"
        for t in ("Summary", "Shortlists", "Methodology", "Pre-Screen", "Inputs", "Overrides", "Screen",
                  "Financials", "Valuation", "Technicals", "Benchmarks", "Holdings", "Data Checks"):
            wb.create_sheet(t)
        self.methodology()
        self.prescreen()
        self.inputs()
        self.overrides()
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
        for col, w in zip("ABCDEFGH", (46, 12, 34, 70, 34, 34, 34, 12)):
            ws.column_dimensions[col].width = w
        body(ws, 1, 1, m["title"] + " — 5-Phase MECE Stock Evaluation Framework", font=F_TITLE)
        body(ws, 2, 1, m["universe_text"], align=WRAP)
        body(ws, 3, 1, m["caveat"], font=F_BOLD, align=WRAP)
        body(ws, 4, 1, f"Workbook version v{self.version} — see 'Read Me' for change log.", font=F_NOTE)
        for r, h in ((2, 75), (3, 45)):
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = h
        r = 6
        for col, t in enumerate(("Parameter (yellow = editable; formulas read these named cells)", "Value",
                                 "Excel name", "Note / source"), 1):
            header(ws, r, col, t)
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
                self.name(nm, "Methodology", f"$B${r}")

        r += 2
        body(ws, r, 1, "Rules", font=F_BOLD)
        rules = [
            "Scoring scale: 0 = fails, 1 = partial / mixed, 2 = clearly meets (risk criteria: 2 = LOW risk).",
            "Pre-Screen: 'Excluded (pre-screen)' if the sub-industry is marked N on Pre-Screen or the company has "
            "ps_exclude = Y on Inputs. Excluded companies keep their scores but leave the funnel.",
            "Phase 1 WHY passes if subtotal ≥ thr_P1 and Voluntary Test (1.3) ≥ ko_voluntary.",
            "Phase 2 WHAT passes if subtotal ≥ thr_P2 and (if ko_traps = 1) the 2x2 quadrant is not Fad Trap / Long-Cycle Trap.",
            "Phase 3 HOW passes if subtotal ≥ thr_P3, Strongest Power ≥ thr_power, Rational Structure ≥ thr_structure, "
            "Qualitative CAP ≥ thr_cap and Capital Allocation ≥ thr_capalloc.",
            f"Phase 1–3 result: {C.RES_QPASS} = all 3 phases; {C.RES_NEAR} = ≥ nm_phases phases and quality score ≥ "
            f"nm_score; {C.RES_FAIL} otherwise. Quality score /100 = Σ weight × phase% ÷ Σ weights.",
            "Phase 4 funnel = Quality pass (plus Near-miss if funnel_nearmiss = 1). " + m.get("fx_note", ""),
            "True FCF = OCF − CapEx − SBC. Y_c = MIN(E/P, True FCF/P); M_c = MAX(P/E, P/True FCF) = 1/Y_c "
            "(n/m if earnings or FCF ≤ 0). Multiple ceiling = MIN(ROIC × 100, v_mult_cap). Justified P/E = (1 − g/ROIC)/(r − g).",
            "g = analyst g_est if given, else MIN(v_gcap, MEDIAN of 5-yr sales / EPS / True FCF CAGRs), 3-yr CAGRs if "
            "no 5-yr. g_moat = analyst g_moat_est if given, else g.",
            "Bird-in-the-Hand: Y_c + 0.5g > v_bith and Y_c ≥ v_yc_floor. Hohn: True FCF yield + g_moat ≥ v_hohn.",
            "Market-implied CAP n (years of g_moat growth priced in; r = v_r, terminal g_T = v_gt): a = (1+g)/(1+r), "
            "K = (1+g_T)/(r−g_T), A = a/(1−a): n = LN((MC/FCF − A)/(K − A)) / LN(a). "
            "'n/m' = no finite n (True FCF ≤ 0, or price above the value of growing at g_moat forever) and fails. Negative n = "
            "priced below the no-growth value. Pass if n ≤ v_n_ratio × Qualitative CAP. Works for any g_moat ≠ r.",
            "Intrinsic value: Hohn super-company DCF = FCF × [a(1−a^N)/(1−a) + a^N·K] (N = v_dcf_years); Town sticker = "
            "NI × (1+g)^10 × MIN(200·g, v_pe_cap) ÷ (1+v_marr)^10. Margin of safety vs the lower of the two.",
            "Funding break-even years = years until True FCF yield on cost (growing at g_moat) reaches v_funding.",
            "Audit (4.1): A1 ROIC, A2 True FCF conversion, A3 Big Five CAGRs, A4 Buffett $1 test, A5 debt ÷ True FCF, "
            "A6 interest cover. Audit pass = tests passed ≥ MIN(a_req, tests with data); fewer than a_min_tests tests with "
            "data = 'No data'. A1 uses GAAP ROIC, tangible ROIC or either (a_roic_basis).",
            "Weinstein stage (4.3): slope = MA30 ÷ MA30 five weeks earlier − 1. Stage 2 = price > MA and slope > t_slope; "
            "Stage 4 = price < MA and slope < −t_slope; flat = Stage 3 if within t_near_high of the 52-wk high, else Stage 1; "
            "'Stage 2 pullback' = rising MA, price below; 'Stage 4 rally' = falling MA, price above.",
            f"Phase 4 verdict: {C.V_NOTFUNNEL} → {C.V_NODATA} → {C.V_AUDIT} → {C.V_VAL} → {C.V_TIME} → {C.V_ENTRY}.",
            "Phase 5 (Holdings): band = Buy zone (Y_c+0.5g > v_bith), Stretched hold (≥ l_hold_lo), Over-stretched. Trigger 1 "
            "moat/cash decay: ROIC < a_roic, True FCF conversion < l_fcf_decay, no longer Quality pass, or analyst flag. "
            "Trigger 2 valuation detachment: Y_c + 1.0g < l_unadj, M_c > l_mult_max (unless g ≥ l_hyper_g) or n/m, or implied "
            "n > Qualitative CAP. Trigger 3: Stage 3/4, or an equal-or-higher-quality funnel name offers Y_c + 0.5g > l_opp.",
            "Effective score = the Overrides-sheet score where one valid row exists for that company and criterion, else the "
            "Inputs score. Overridden cells show bold purple on Screen.",
        ]
        for t in rules:
            r += 1
            body(ws, r, 1, t, align=WRAP)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = 32

        r += 2
        for col, t in enumerate(("Phase / section", "Code", "Criterion", "Definition", "0 =", "1 =", "2 =", "Carried from"), 1):
            header(ws, r, col, t)
        prev = None
        for f in C.FIELDS:
            r += 1
            body(ws, r, 1, f"{C.PHASE_LONG[f['phase']]} — {f['section']}" if f["section"] != prev else None, align=WRAP)
            prev = f["section"]
            body(ws, r, 2, f["code"])
            body(ws, r, 3, f["name"], align=WRAP)
            body(ws, r, 4, f["definition"], align=WRAP)
            if f["type"] == "score":
                for k in (0, 1, 2):
                    body(ws, r, 5 + k, f["rubric"][k], align=WRAP)
            elif f["type"] in ("category", "number"):
                body(ws, r, 5, "Values: " + " / ".join(map(str, f["options"])), align=WRAP)
            body(ws, r, 8, {"moat": "v2 moat text"}.get(f["legacy"], f["legacy"] or "new (pre-scored)"))
        for code, (name, rule) in C.DERIVED.items():
            r += 1
            body(ws, r, 2, code)
            body(ws, r, 3, name)
            body(ws, r, 4, rule + " (formula)", align=WRAP)
        r += 2
        body(ws, r, 1, "How the scores were produced", font=F_BOLD)
        for t in m["how_produced"] + [m["sources"]]:
            r += 1
            body(ws, r, 1, t, align=WRAP)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = 48

    # ----------------------------------------------------------- Pre-Screen
    def prescreen(self):
        ws = self.wb["Pre-Screen"]
        body(ws, 1, 1, C.PHASE_LONG[0], font=F_TITLE)
        body(ws, 2, 1, "Do you understand this industry well enough to make it the sole financial support of your family "
                       "for the next 100 years (Three Circles: Passion, Talent, Money), and are you proud to endorse its "
                       "products and values as a 100% owner? Set 'In circle' to N for sub-industries outside your circle; "
                       "exclude single companies on Inputs (ps_exclude = Y + reason). Defaults are 'Y' — these are your "
                       "inputs, not pre-scored.", font=F_NOTE, align=WRAP)
        ws.merge_cells("A2:D2")
        ws.row_dimensions[2].height = 60
        for i, (t, w) in enumerate((("GICS Sector", 24), ("GICS Sub-Industry", 40), ("In circle (Y/N)", 10),
                                    ("Note", 50), ("helper: key", 40)), 1):
            header(ws, 4, i, t, w, phase=0)
        rows = self.m["prescreen"]
        first, last = 5, 4 + len(rows)
        for j, p in enumerate(rows):
            r = first + j
            body(ws, r, 1, p["sector"])
            body(ws, r, 2, p["sub_industry"])
            body(ws, r, 3, p.get("in_circle") or "Y", font=F_INPUT).fill = FILL_INPUT
            body(ws, r, 4, p.get("note"), font=F_INPUT)
            body(ws, r, 5, f'=A{r}&"|"&B{r}', font=F_NOTE)
        self.name("ps_key", "Pre-Screen", f"$E${first}:$E${last}")
        self.name("ps_circle", "Pre-Screen", f"$C${first}:$C${last}")
        v = DataValidation(type="list", formula1='"Y,N"', allow_blank=False)
        ws.add_data_validation(v)
        v.add(f"C{first}:C{last}")
        ws.conditional_formatting.add(f"C{first}:C{last}", CellIsRule(operator="equal", formula=['"N"'], fill=FILL_RED))
        ws.freeze_panes = "A5"
        ws.auto_filter.ref = f"A4:D{last}"

    # --------------------------------------------------------------- Inputs
    def input_columns(self):
        cols = [("id", "ID (unique)", "@", 12, None), ("ticker", "Ticker", "@", 11, None),
                ("company", "Company", "@", 26, None), ("country", "Country", "@", 13, None),
                ("sector", "GICS Sector", "@", 20, None), ("sub_industry", "GICS Sub-Industry", "@", 26, None)]
        cols += [(c["key"], c["header"], c["fmt"], c["width"], None) for c in self.extra]
        for f in C.FIELDS:
            w = {"score": 8, "category": 13, "number": 8, "text": 30}[f["type"]]
            cols.append((f["code"], f"{f['code']} {f['short']}", "0" if f["type"] in ("score", "number") else "@", w, f["phase"]))
        cols += [("confidence", "Confidence v2 (H/M/L)", "@", 9, None), ("conf_v3", "Confidence v3 (H/M/L)", "@", 9, None),
                 ("note", "Analyst note (v2)", "@", 60, None), ("note_v3", "v3 note (Phases 1–3)", "@", 60, None),
                 ("evidence", "Key evidence / sources", "@", 30, None), ("last_reviewed", "Last reviewed", "yyyy-mm-dd", 11, None),
                 ("ps_exclude", "Pre-screen: exclude (Y)", "@", 9, 0), ("ps_reason", "Pre-screen: reason", "@", 24, 0)]
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
                body(ws, r, i, parse_date(v) if key == "last_reviewed" else v, fmt=fmt, font=F_INPUT)
        ws.freeze_panes = "D2"
        ws.auto_filter.ref = f"A1:{L(len(cols))}{self.last}"
        self.name("inp_ID", "Inputs", f"$A$2:$A${self.last}")
        self.name("inp_Company", "Inputs", f"$C$2:$C${self.last}")
        self.name("inp_All", "Inputs", f"$A$2:${L(len(cols))}${self.last}")
        self.name("inp_Header", "Inputs", f"$A$1:${L(len(cols))}$1")
        for k in ("confidence", "conf_v3", "note_v3"):
            self.col_name(f"inp_{k}", "Inputs", self.inp[k])

        def dv(formula, key, msg):
            c = L(self.inp[key])
            v = DataValidation(type="list", formula1=formula, allow_blank=True, showErrorMessage=True, error=msg)
            ws.add_data_validation(v)
            v.add(f"{c}2:{c}{self.last}")

        for f in C.FIELDS:
            if f["type"] == "score":
                dv('"0,1,2"', f["code"], "0, 1 or 2")
                c = L(self.inp[f["code"]])
                self.score_cf(ws, f"{c}2:{c}{self.last}")
            elif f["type"] in ("category", "number"):
                dv(q(",".join(map(str, f["options"]))), f["code"], " / ".join(map(str, f["options"])))
        dv('"H,M,L"', "confidence", "H, M or L")
        dv('"H,M,L"', "conf_v3", "H, M or L")
        dv('"Y"', "ps_exclude", "Y or blank")
        for x in self.extra:
            if x.get("validation"):
                dv(q(",".join(x["validation"])), x["key"], "/".join(x["validation"]))

    @staticmethod
    def score_cf(ws, rng):
        for val, fill in (("0", FILL_RED), ("1", FILL_AMBER), ("2", FILL_GREEN)):
            ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[val], fill=fill))

    @staticmethod
    def passfail_cf(ws, rng):
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Pass"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Fail"'], fill=FILL_RED))
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"No data"'], fill=FILL_GREY))

    # ------------------------------------------------------------ Overrides
    def overrides(self):
        ws = self.wb["Overrides"]
        first, last = 5, 4 + C.OVERRIDE_ROWS
        body(ws, 1, 1, "Overrides log — analyst changes to individual 0/1/2 scores", font=F_TITLE)
        body(ws, 2, 1, "One row per change in the blue columns A–F. Screen uses the override; Inputs keeps the base "
                       "score. Delete a row to undo. Columns G–I are formulas.", font=F_NOTE)
        ws.merge_cells("A2:I2")
        cols = [("Company ID", 12), ("Criterion code", 9), ("New score (0/1/2)", 9), ("Reason / evidence", 60),
                ("Analyst", 14), ("Date", 11), ("Company (lookup)", 26), ("Base score (lookup)", 9), ("Status", 15),
                (None, 3), ("Score codes (list)", 9)]
        for i, (t, w) in enumerate(cols, 1):
            if t:
                header(ws, 4, i, t, w)
            else:
                ws.column_dimensions[L(i)].width = w
        for j, code in enumerate(C.SCORE_CODES):
            body(ws, first + j, 11, code, font=F_NOTE)
        self.name("ov_CodeList", "Overrides", f"$K${first}:$K${first + len(C.SCORE_CODES) - 1}")
        for k, nm in ((1, "ov_ID"), (2, "ov_Code"), (3, "ov_Score"), (9, "ov_Status")):
            self.col_name(nm, "Overrides", k, first, last)
        for j, o in enumerate(self.m["overrides"]):
            for i, key in enumerate(("id", "code", "new_score", "reason", "analyst", "date"), 1):
                body(ws, first + j, i, parse_date(o.get(key)) if key == "date" else o.get(key), font=F_INPUT)
        for r in range(first, last + 1):
            for i in range(1, 7):
                ws.cell(r, i).font = F_INPUT
            ws.cell(r, 6).number_format = "yyyy-mm-dd"
            body(ws, r, 7, f'=IF($A{r}="","",IFERROR(INDEX(inp_Company,MATCH($A{r},inp_ID,0)),"?"))')
            body(ws, r, 8, f'=IF(OR($A{r}="",$B{r}=""),"",IFERROR(INDEX(inp_All,MATCH($A{r},inp_ID,0),'
                           f'MATCH($B{r}&" *",inp_Header,0)),"?"))')
            body(ws, r, 9, f'=IF($A{r}="","",IF(ISNA(MATCH($A{r},inp_ID,0)),"Unknown ID",'
                           f'IF(ISNA(MATCH($B{r},ov_CodeList,0)),"Unknown code",IF($C{r}="","Missing score",'
                           f'IF(AND($C{r}<>0,$C{r}<>1,$C{r}<>2),"Invalid score",'
                           f'IF(COUNTIFS(ov_ID,$A{r},ov_Code,$B{r})>1,"Duplicate","OK"))))))')
        for rng, f1 in ((f"B{first}:B{last}", "=ov_CodeList"), (f"C{first}:C{last}", '"0,1,2"')):
            v = DataValidation(type="list", formula1=f1, allow_blank=True)
            ws.add_data_validation(v)
            v.add(rng)
        ws.conditional_formatting.add(f"I{first}:I{last}", CellIsRule(operator="equal", formula=['"OK"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(f"I{first}:I{last}", FormulaRule(formula=[f'AND(I{first}<>"",I{first}<>"OK")'], fill=FILL_RED))
        ws.freeze_panes = "A5"

    # --------------------------------------------------- Screen (Phases 1–3)
    def screen(self):
        ws = self.wb["Screen"]
        S = self.S = Cols("Screen")
        I = lambda key, r: f"Inputs!{L(self.inp[key])}{r}"
        link = lambda key: (lambda r: f'=IF({I(key, r)}="","",{I(key, r)})')
        for key, title, fmt, width, phase in self.input_columns()[:6 + len(self.extra)]:
            S.add(key, title, width, fmt, link(key))
        S.add("conf", "Confidence (worse of v2/v3)", 9, None,
              lambda r: f'=IF(OR({I("confidence", r)}="L",{I("conf_v3", r)}="L"),"L",'
                        f'IF(OR({I("confidence", r)}="M",{I("conf_v3", r)}="M"),"M","H"))')
        S.add("circle", "Pre-screen: in circle", 8, None,
              lambda r: f'=IFERROR(INDEX(ps_circle,MATCH({S.ref("sector", r)}&"|"&{S.ref("sub_industry", r)},ps_key,0)),"Y")', 0)
        S.add("excluded", "Pre-screen: excluded", 8, None,
              lambda r: f'=IF(OR({S.ref("circle", r)}="N",{I("ps_exclude", r)}="Y"),"Yes","No")', 0)

        def eff(code):
            return lambda r: (f'=IF(COUNTIFS(ov_ID,$A{r},ov_Code,{q(code)},ov_Status,"OK")>0,'
                              f'SUMIFS(ov_Score,ov_ID,$A{r},ov_Code,{q(code)}),{I(code, r)})')

        short = {f["code"]: f["short"] for f in C.FIELDS}
        self.score_ranges = []

        def scores(codes, phase):
            for c in codes:
                S.add(c, f"{c} {short[c]}", 8, "0", eff(c), phase)
            self.score_ranges.append((codes[0], codes[-1]))

        def subtotal_pass(p, cond):
            items = C.PHASE_ITEMS[p]
            S.add(f"P{p}_sub", f"Phase {p} subtotal (/{C.PHASE_MAX[p]})", 9, "0",
                  lambda r: "=" + "+".join(S.ref(c, r) for c in items), p, bold=True)
            S.add(f"P{p}_pass", f"Phase {p} {C.PHASE_NAMES[p]} pass", 9, None,
                  lambda r: f'=IF(AND({S.ref(f"P{p}_sub", r)}>=thr_P{p},{cond(r)}),"Pass","Fail")', p, bold=True)

        scores(["1.1a", "1.1b", "1.2", "1.3", "1.4"], 1)
        S.add("1.2t", "1.2t Value Type", 14, None, link("1.2t"), 1)
        S.add("1.2i", "1.2i Invention Path", 13, None, link("1.2i"), 1)
        subtotal_pass(1, lambda r: f'{S.ref("1.3", r)}>=ko_voluntary')

        scores(["2.1a", "2.1b"], 2)
        S.add("quad", "2.1 Demand Quadrant (2x2)", 13, None,
              lambda r: f'=IF(AND({S.ref("2.1a", r)}>=quad_high,{S.ref("2.1b", r)}>=quad_high),"Target",'
                        f'IF({S.ref("2.1b", r)}>=quad_high,"Fad Trap",IF({S.ref("2.1a", r)}>=quad_high,'
                        f'"Long-Cycle Trap","Low/Low")))', 2)
        scores(["2.2a", "2.2b", "2.2c", "2.3a", "2.3b"], 2)
        subtotal_pass(2, lambda r: f'OR(ko_traps<>1,AND({S.ref("quad", r)}<>"Fad Trap",{S.ref("quad", r)}<>"Long-Cycle Trap"))')

        scores(["3.1a", "3.1b", "3.1c"], 3)
        S.add("3.1p", "3.1p ROIC Path", 10, None, link("3.1p"), 3)
        scores(C.POWER_CODES, 3)
        pw = lambda r: f"{S.ref(C.POWER_CODES[0], r)}:{S.ref(C.POWER_CODES[-1], r)}"
        S.add("3.2", "3.2 Strongest Power (MAX)", 9, "0", lambda r: f"=MAX({pw(r)})", 3)
        S.add("3.2x", "3.2x Power Breadth", 9, "0",
              lambda r: f'=IF(COUNTIF({pw(r)},2)>=2,2,IF(AND(COUNTIF({pw(r)},2)=1,COUNTIF({pw(r)},1)>=1),1,0))', 3)
        scores(["3.3a", "3.3b", "3.3c", "3.3d", "3.3e", "3.3f"], 3)
        S.add("3.3n", "3.3n Qualitative CAP (yrs)", 9, "0", link("3.3n"), 3)
        scores(["3.4a", "3.4b", "3.4c"], 3)
        subtotal_pass(3, lambda r: f'{S.ref("3.2", r)}>=thr_power,{S.ref("3.1a", r)}>=thr_structure,'
                                   f'N({S.ref("3.3n", r)})>=thr_cap,{S.ref("3.4c", r)}>=thr_capalloc')

        S.add("phases", "Phases passed (/3)", 8, "0",
              lambda r: "=" + "+".join(f'({S.ref(f"P{p}_pass", r)}="Pass")' for p in (1, 2, 3)), bold=True)
        S.add("score", "Quality score (/100)", 9, "0.0",
              lambda r: "=IF(w_P1+w_P2+w_P3=0,0,ROUND(100*(" + "+".join(
                  f"w_P{p}*{S.ref(f'P{p}_sub', r)}/{C.PHASE_MAX[p]}" for p in (1, 2, 3)) + ")/(w_P1+w_P2+w_P3),1))",
              bold=True)
        S.add("adj", "Confidence-adj. score", 9, "0.0",
              lambda r: f'=ROUND({S.ref("score", r)}*IF({S.ref("conf", r)}="H",conf_H,IF({S.ref("conf", r)}="M",conf_M,conf_L)),1)')
        S.add("result", "Phase 1–3 result", 15, None,
              lambda r: f'=IF({S.ref("excluded", r)}="Yes",{q(C.RES_EXCL)},IF({S.ref("phases", r)}=3,{q(C.RES_QPASS)},'
                        f'IF(AND({S.ref("phases", r)}>=nm_phases,{S.ref("score", r)}>=nm_score),{q(C.RES_NEAR)},{q(C.RES_FAIL)})))',
              bold=True)
        S.add("funnel", "In Phase 4 funnel", 8, None,
              lambda r: f'=IF(OR({S.ref("result", r)}={q(C.RES_QPASS)},AND(funnel_nearmiss=1,{S.ref("result", r)}={q(C.RES_NEAR)})),"Yes","No")')
        S.add("rank", "Rank", 6, "0", lambda r: f'=COUNTIF(scr_sortkey,">"&{S.ref("sortkey", r)})+1')
        S.add("failed", "Failed phase(s) / knock-outs", 22, None,
              lambda r: f'=TRIM(IF({S.ref("P1_pass", r)}="Fail","P1"&IF({S.ref("1.3", r)}<ko_voluntary,"(voluntary)","")&" ","")'
                        f'&IF({S.ref("P2_pass", r)}="Fail","P2"&IF(AND(ko_traps=1,ISNUMBER(SEARCH("Trap",{S.ref("quad", r)}))),'
                        f'"("&{S.ref("quad", r)}&")","")&" ","")&IF({S.ref("P3_pass", r)}="Fail","P3 ",""))')
        weak = [c for c in C.SCORE_CODES if c not in C.POWER_CODES]
        weak.insert(weak.index("3.3a"), "3.2")
        lab = dict(short, **{"3.2": "Strongest Power"})
        S.add("weak", "Weak points (scored 0)", 40, None,
              lambda r: "=MID(" + "&".join(f'IF({S.ref(c, r)}=0,"; {c} {lab[c]}","")' for c in weak) + ",3,600)")
        S.add("n_ov", "Overrides applied", 8, "0", lambda r: f'=COUNTIFS(ov_ID,$A{r},ov_Status,"OK")')
        S.add("benefit", "Power: benefit", 30, None, link("3.2bb"), 3)
        S.add("barrier", "Power: barrier", 30, None, link("3.2br"), 3)
        S.add("note_v3", "v3 note", 60, None, link("note_v3"))
        S.add("sortkey", "helper: sort key", 10, "0",
              lambda r: f'=ROUND(IF(rank_basis=2,{S.ref("adj", r)},{S.ref("score", r)})*10,0)*10000+10000-ROW()')
        S.add("listkey", "helper: list key", 22, None,
              lambda r: f'={S.ref("result", r)}&"|"&(COUNTIFS(scr_result,{S.ref("result", r)},scr_sortkey,">"&{S.ref("sortkey", r)})+1)')
        self.render(ws, S, "scr")
        ws.freeze_panes = "D2"
        for k in ("sortkey", "listkey"):
            ws.column_dimensions[S.col(k)].hidden = True

        rng = lambda a, b=None: f"{S.col(a)}2:{S.col(b or a)}{self.last}"
        for a, b in self.score_ranges + [("3.2", "3.2x")]:
            self.score_cf(ws, rng(a, b))
        for a, b in self.score_ranges:
            h = f"{S.col(a)}$1"
            ws.conditional_formatting.add(rng(a, b), FormulaRule(
                formula=[f'COUNTIFS(ov_ID,$A2,ov_Code,LEFT({h},FIND(" ",{h})-1),ov_Status,"OK")>0'],
                font=Font(bold=True, color="7030A0")))
        for p in (1, 2, 3):
            self.passfail_cf(ws, rng(f"P{p}_pass"))
        for res, fill in Q_FILL.items():
            ws.conditional_formatting.add(rng("result"), CellIsRule(operator="equal", formula=[q(res)], fill=fill))
        ws.conditional_formatting.add(rng("quad"), CellIsRule(operator="equal", formula=['"Target"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(rng("quad"), FormulaRule(formula=[f'ISNUMBER(SEARCH("Trap",{S.col("quad")}2))'], fill=FILL_RED))
        ws.conditional_formatting.add(rng("excluded"), CellIsRule(operator="equal", formula=['"Yes"'], fill=FILL_GREY))

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
            "Weekly technical inputs (Phase 4.3 / 5), filled by fetch_market_data.py; stage is computed on Valuation.")
        ws = self.wb["Benchmarks"]
        body(ws, 1, 1, "Benchmarks — market and sector trend (Phase 4.3)", font=F_TITLE)
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
        V.add("id", "ID", 11, None, lambda r: f"=Screen!A{r}")
        V.add("ticker", "Ticker", 10, None, lambda r: f"=Screen!B{r}")
        V.add("company", "Company", 24, None, lambda r: f"=Screen!C{r}")
        V.add("qres", "Phase 1–3 result", 14, None, lambda r: f"={S.x('result', r)}")
        V.add("qscore", "Quality score", 8, "0.0", lambda r: f"={S.x('score', r)}")
        V.add("funnel", "In funnel", 7, None, lambda r: f"={S.x('funnel', r)}")
        V.add("fcf", "True FCF (m)", 11, "#,##0",
              lambda r: f'=IF(AND({num(F("ocf_ttm_m", r))},{num(F("capex_ttm_m", r))}),'
                        f'{F("ocf_ttm_m", r)}-{F("capex_ttm_m", r)}-N({F("sbc_ttm_m", r)}),"")', 4)
        V.add("mc", "Market cap (m)", 11, "#,##0", lambda r: f'=IF({num(F("market_cap_m", r))},{F("market_cap_m", r)},"")', 4)
        V.add("ep", "E/P", 8, "0.0%",
              lambda r: f'=IF(AND({num(v("mc", r))},{num(F("ni_ttm_m", r))}),{F("ni_ttm_m", r)}/{v("mc", r)},"")', 4)
        V.add("fcfy", "True FCF yield", 8, "0.0%",
              lambda r: f'=IF(AND({num(v("mc", r))},{num(v("fcf", r))}),{v("fcf", r)}/{v("mc", r)},"")', 4)
        V.add("yc", "Y_c = MIN(E/P, FCF/P)", 9, "0.0%",
              lambda r: f'=IF(AND({num(v("ep", r))},{num(v("fcfy", r))}),MIN({v("ep", r)},{v("fcfy", r)}),"")', 4, True)
        V.add("mcx", "M_c = MAX(P/E, P/FCF)", 9, "0.0",
              lambda r: f'=IF(NOT({num(v("yc", r))}),"",IF({v("yc", r)}<=0,"n/m",1/{v("yc", r)}))', 4, True)
        V.add("g", "g used", 8, "0.0%",
              lambda r: f'=IF({num(F("g_est", r))},{F("g_est", r)},IFERROR(MIN(v_gcap,MEDIAN({F("cagr_sales_5", r)},'
                        f'{F("cagr_eps_5", r)},{F("cagr_fcf_5", r)})),IFERROR(MIN(v_gcap,MEDIAN({F("cagr_sales_3", r)},'
                        f'{F("cagr_eps_3", r)},{F("cagr_fcf_3", r)})),"")))', 4)
        V.add("gm", "g_moat used", 8, "0.0%",
              lambda r: f'=IF({num(F("g_moat_est", r))},{F("g_moat_est", r)},{v("g", r)})', 4)
        # 4.1 audit
        V.add("roic", "Median ROIC (GAAP)", 8, "0.0%", lambda r: f'=IF({num(F("roic_median", r))},{F("roic_median", r)},"")', 4)
        V.add("roict", "Median ROIC (tangible)", 8, "0.0%",
              lambda r: f'=IF({num(F("roic_tangible_median", r))},{F("roic_tangible_median", r)},"")', 4)
        V.add("roic_t", "ROIC used for A1", 8, "0.0%",
              lambda r: f'=IF(a_roic_basis=2,{v("roict", r)},IF(a_roic_basis=3,IF(AND({num(v("roic", r))},{num(v("roict", r))}),'
                        f'MAX({v("roic", r)},{v("roict", r)}),IF({num(v("roic", r))},{v("roic", r)},{v("roict", r)})),{v("roic", r)}))', 4)
        V.add("a1", "A1 ROIC ≥ hurdle", 8, None,
              lambda r: f'=IF({num(v("roic_t", r))},IF({v("roic_t", r)}>=a_roic,"Pass","Fail"),'
                        f'IF(OR({F("roic_judgement", r)}="Pass",{F("roic_judgement", r)}="Fail"),{F("roic_judgement", r)},"No data"))', 4)
        V.add("a2", "A2 True FCF conversion", 8, None,
              lambda r: f'=IF({num(F("fcf_conv", r))},IF({F("fcf_conv", r)}>=a_fcfconv,"Pass","Fail"),"No data")', 4)
        cagrs = [f"cagr_{x}_{n}" for x in ("bv", "eps", "sales", "fcf") for n in (10, 5, 3)]
        crng = lambda r: f"{F(cagrs[0], r)}:{F(cagrs[-1], r)}"
        V.add("big5n", "Big Five: CAGRs available", 8, "0", lambda r: f"=COUNT({crng(r)})", 4)
        V.add("big5k", "Big Five: CAGRs ≥ bar", 8, "0", lambda r: f'=COUNTIF({crng(r)},">="&a_cagr)', 4)
        V.add("a3", "A3 Big Five growth", 8, None,
              lambda r: f'=IF({v("big5n", r)}<a_cagr_minavail,"No data",IF({v("big5k", r)}/{v("big5n", r)}'
                        f'>=a_cagr_count/12,"Pass","Fail"))', 4)
        V.add("dollar", "Buffett $1 ratio", 8, "0.00",
              lambda r: f'=IF(AND({num(F("mcap_delta_m", r))},{num(F("retained_m", r))}),IF({F("retained_m", r)}>0,'
                        f'{F("mcap_delta_m", r)}/{F("retained_m", r)},""),"")', 4)
        V.add("a4", "A4 Buffett $1 test", 8, None,
              lambda r: f'=IF({num(v("dollar", r))},IF({v("dollar", r)}>=a_dollar,"Pass","Fail"),"No data")', 4)
        V.add("debty", "LT debt ÷ True FCF (yrs)", 8, "0.0",
              lambda r: f'=IF(AND({num(F("lt_debt_m", r))},{num(v("fcf", r))}),IF({F("lt_debt_m", r)}<=0,0,'
                        f'IF({v("fcf", r)}>0,{F("lt_debt_m", r)}/{v("fcf", r)},"n/m")),"")', 4)
        V.add("a5", "A5 Debt payable", 8, None,
              lambda r: f'=IF({v("debty", r)}="","No data",IF({v("debty", r)}="n/m","Fail",'
                        f'IF({v("debty", r)}<=a_debt_yrs,"Pass","Fail")))', 4)
        V.add("icov", "Interest cover (×)", 8, "0.0",
              lambda r: f'=IF(AND({num(F("ebit_ttm_m", r))},{num(F("interest_m", r))}),IF({F("interest_m", r)}=0,999,'
                        f'{F("ebit_ttm_m", r)}/ABS({F("interest_m", r)})),"")', 4)
        V.add("a6", "A6 Interest cover", 8, None,
              lambda r: f'=IF({num(v("icov", r))},IF({v("icov", r)}>=a_intcov,"Pass","Fail"),'
                        f'IF(AND({num(F("lt_debt_m", r))},N({F("lt_debt_m", r)})=0),"Pass","No data"))', 4)
        tests = ["a1", "a2", "a3", "a4", "a5", "a6"]
        V.add("audit_n", "Audit tests passed (/6)", 8, "0",
              lambda r: "=" + "+".join(f'({v(t, r)}="Pass")' for t in tests), 4, True)
        V.add("audit_d", "Audit tests with data", 8, "0",
              lambda r: "=" + "+".join(f'({v(t, r)}<>"No data")' for t in tests), 4)
        V.add("audit", "4.1 Audit", 9, None,
              lambda r: f'=IF({v("audit_d", r)}<a_min_tests,"No data",IF({v("audit_n", r)}>=MIN(a_req,{v("audit_d", r)}),"Pass","Fail"))', 4, True)
        # 4.2 valuation
        V.add("ceil", "Multiple ceiling (×)", 8, "0.0",
              lambda r: f'=IF({num(v("roic", r))},MIN({v("roic", r)}*100,v_mult_cap),"")', 4)
        V.add("v_ceil", "M_c ≤ ceiling", 8, None,
              lambda r: f'=IF(OR({v("ceil", r)}="",{v("mcx", r)}=""),"No data",IF({v("mcx", r)}="n/m","Fail",'
                        f'IF({v("mcx", r)}<={v("ceil", r)},"Pass","Fail")))', 4)
        V.add("jpe", "Justified P/E", 8, "0.0",
              lambda r: f'=IF(AND({num(v("roic", r))},{num(v("g", r))}),IF(AND({v("roic", r)}>0,v_r>{v("g", r)}),'
                        f'(1-{v("g", r)}/{v("roic", r)})/(v_r-{v("g", r)}),"n/m"),"")', 4)
        V.add("bith", "BitH return Y_c + 0.5g", 9, "0.0%",
              lambda r: f'=IF(AND({num(v("yc", r))},{num(v("g", r))}),{v("yc", r)}+0.5*{v("g", r)},"")', 4, True)
        V.add("v_bith", "BitH hurdle", 8, None,
              lambda r: f'=IF({v("bith", r)}="","No data",IF(AND({v("bith", r)}>v_bith,{v("yc", r)}>=v_yc_floor),"Pass","Fail"))', 4)
        V.add("hohn", "Hohn return FCF yld + g_moat", 9, "0.0%",
              lambda r: f'=IF(AND({num(v("fcfy", r))},{num(v("gm", r))}),{v("fcfy", r)}+{v("gm", r)},"")', 4)
        V.add("v_hohn", "Hohn hurdle", 8, None,
              lambda r: f'=IF({v("hohn", r)}="","No data",IF({v("hohn", r)}>=v_hohn,"Pass","Fail"))', 4)
        a = lambda r: f"((1+{v('gm', r)})/(1+v_r))"
        K = "((1+v_gt)/(v_r-v_gt))"
        A = lambda r: f"({a(r)}/(1-{a(r)}))"
        V.add("n", "Market-implied CAP n (yrs)", 9, "0.0",
              lambda r: f'=IF(OR({v("mc", r)}="",{v("fcf", r)}="",{v("gm", r)}=""),"",'
                        f'IF(OR({v("fcf", r)}<=0,v_r<=v_gt),"n/m",'
                        f'IFERROR(LN(({v("mc", r)}/{v("fcf", r)}-{A(r)})/({K}-{A(r)}))/LN({a(r)}),"n/m")))', 4, True)
        V.add("cap", "Qualitative CAP (yrs)", 8, "0", lambda r: f"={S.x('3.3n', r)}", 3)
        V.add("v_n", "Implied n ≤ ratio × CAP", 8, None,
              lambda r: f'=IF({v("n", r)}="","No data",IF({v("n", r)}="n/m","Fail",'
                        f'IF({v("n", r)}<=v_n_ratio*N({v("cap", r)}),"Pass","Fail")))', 4)
        V.add("iv_hohn", "Hohn DCF value (m)", 11, "#,##0",
              lambda r: f'=IF(OR({v("fcf", r)}="",{v("gm", r)}=""),"",IF({v("fcf", r)}<=0,"n/m",'
                        f'IFERROR({v("fcf", r)}*({a(r)}*(1-{a(r)}^v_dcf_years)/(1-{a(r)})+{a(r)}^v_dcf_years*{K}),"n/m")))', 4)
        V.add("iv_town", "Town sticker value (m)", 11, "#,##0",
              lambda r: f'=IF(OR(NOT({num(F("ni_ttm_m", r))}),{v("g", r)}=""),"",IF(OR({F("ni_ttm_m", r)}<=0,{v("g", r)}<=0),"n/m",'
                        f'{F("ni_ttm_m", r)}*(1+{v("g", r)})^10*MIN(200*{v("g", r)},v_pe_cap)/(1+v_marr)^10))', 4)
        V.add("mos", "Margin of safety", 8, "0%",
              lambda r: f'=IF(OR(NOT(ISNUMBER({v("iv_hohn", r)})),NOT(ISNUMBER({v("iv_town", r)})),{v("mc", r)}=""),"",'
                        f'1-{v("mc", r)}/MIN({v("iv_hohn", r)},{v("iv_town", r)}))', 4)
        V.add("v_mos", "MoS ≥ min", 8, None,
              lambda r: f'=IF({v("mos", r)}="","No data",IF({v("mos", r)}>=v_mos,"Pass","Fail"))', 4)
        V.add("fund", "Yrs to funding-rate yield on cost", 8, "0.0",
              lambda r: f'=IF(OR({v("fcfy", r)}="",{v("gm", r)}=""),"",IF({v("fcfy", r)}>=v_funding,0,'
                        f'IF(OR({v("fcfy", r)}<=0,{v("gm", r)}<=0),"never",LN(v_funding/{v("fcfy", r)})/LN(1+{v("gm", r)}))))', 4)
        vtests = ["v_ceil", "v_bith", "v_hohn", "v_n"]
        V.add("valn", "4.2 Valuation", 9, None,
              lambda r: f'=IF(OR({v("v_bith", r)}="No data",{v("v_hohn", r)}="No data"),"No data",'
                        f'IF(AND(' + ",".join(f'{v(t, r)}="Pass"' for t in vtests) +
                        f',OR(v_req_mos<>1,{v("v_mos", r)}="Pass")),"Pass","Fail"))', 4, True)
        # 4.3 technicals
        V.add("stage", "Weinstein stage", 13, None,
              lambda r: f'=IF(NOT({num(T("ma30", r))}),"No data",'
                        f'{self.stage_expr(T("price", r), T("ma30", r), T("ma30_prev", r), T("high_52w", r))})', 4)
        V.add("mkt", "Market stage", 11, None, lambda r: '=IFERROR(INDEX(bm_stage,MATCH("MARKET",bm_name,0)),"No data")', 4)
        V.add("sec", "Sector stage", 11, None, lambda r: f'=IFERROR(INDEX(bm_stage,MATCH(Screen!E{r},bm_name,0)),"No data")', 4)
        V.add("rs", "RS vs market (52w)", 8, "0.0%", lambda r: f'=IF({num(T("rs_52w", r))},{T("rs_52w", r)},"")', 4)
        V.add("volr", "Volume ratio", 7, "0.00", lambda r: f'=IF({num(T("vol_ratio", r))},{T("vol_ratio", r)},"")', 4)
        V.add("entry", "4.3 Stage 2 entry", 9, None,
              lambda r: f'=IF({v("stage", r)}="No data","No data",IF(AND({v("stage", r)}="Stage 2",'
                        f'OR(t_req_market<>1,{v("mkt", r)}="Stage 2"),'
                        f'OR(t_req_sector<>1,{v("sec", r)}="No data",{v("sec", r)}="",{v("sec", r)}="Stage 2"),'
                        f'N({v("rs", r)})>0,OR(t_req_vol<>1,N({v("volr", r)})>=t_vol)),"Pass","Fail"))', 4, True)
        V.add("verdict", "Phase 4 verdict", 15, None,
              lambda r: f'=IF({v("funnel", r)}<>"Yes",{q(C.V_NOTFUNNEL)},IF(OR({v("yc", r)}="",{v("audit", r)}="No data"),'
                        f'{q(C.V_NODATA)},IF({v("audit", r)}<>"Pass",{q(C.V_AUDIT)},IF({v("valn", r)}<>"Pass",{q(C.V_VAL)},'
                        f'IF({v("entry", r)}<>"Pass",{q(C.V_TIME)},{q(C.V_ENTRY)})))))', 4, True)
        V.add("why", "Verdict detail (failed tests)", 30, None,
              lambda r: f'=IF({v("verdict", r)}={q(C.V_NOTFUNNEL)},"",TRIM('
                        + "&".join(f'IF({v(t, r)}="Fail","{lbl} ","")' for t, lbl in
                                   (("a1", "ROIC"), ("a2", "FCFconv"), ("a3", "Big5"), ("a4", "$1test"), ("a5", "Debt"),
                                    ("a6", "IntCov"), ("v_ceil", "Multiple"), ("v_bith", "BitH"), ("v_hohn", "Hohn"),
                                    ("v_n", "ImpliedCAP"), ("v_mos", "MoS")))
                        + f'&IF({v("entry", r)}="Fail",{v("stage", r)},"")))', 4)
        # Phase 5 helpers (used by Holdings)
        V.add("band", "5.1 Hold band", 13, None,
              lambda r: f'=IF({v("bith", r)}="","",IF({v("bith", r)}>v_bith,"Buy zone",IF({v("bith", r)}>=l_hold_lo,'
                        f'"Stretched hold","Over-stretched")))', 5)
        V.add("t1", "Trigger 1 moat/cash decay", 9, None,
              lambda r: f'=IF(OR(AND({num(v("roic", r))},N({v("roic", r)})<a_roic),AND({num(F("fcf_conv", r))},'
                        f'N({F("fcf_conv", r)})<l_fcf_decay),{v("qres", r)}<>{q(C.RES_QPASS)}),"Yes","No")', 5)
        V.add("t2", "Trigger 2 valuation detachment", 9, None,
              lambda r: f'=IF(OR(AND({num(v("yc", r))},{num(v("g", r))},N({v("yc", r)})+N({v("g", r)})<l_unadj),'
                        f'AND(ISNUMBER({v("mcx", r)}),N({v("mcx", r)})>l_mult_max,N({v("g", r)})<l_hyper_g),'
                        f'{v("mcx", r)}="n/m",{v("n", r)}="n/m",AND(ISNUMBER({v("n", r)}),N({v("n", r)})>N({v("cap", r)}))),"Yes","No")', 5)
        V.add("t3s", "Trigger 3 stage 3/4", 9, None,
              lambda r: f'=IF(OR({v("stage", r)}="Stage 3",{v("stage", r)}="Stage 4",{v("stage", r)}="Stage 4 rally"),"Yes","No")', 5)
        V.add("sortkey", "helper: sort key", 10, "0",
              lambda r: f'=IF({v("bith", r)}="",-99990000,ROUND({v("bith", r)}*1000,0)*10000)+10000-ROW()')
        V.add("listkey", "helper: list key", 22, None,
              lambda r: f'={v("verdict", r)}&"|"&(COUNTIFS(val_verdict,{v("verdict", r)},val_sortkey,">"&{v("sortkey", r)})+1)')
        self.render(ws, V, "val")
        ws.freeze_panes = "D2"
        for k in ("sortkey", "listkey"):
            ws.column_dimensions[V.col(k)].hidden = True
        rng = lambda k: f"{V.col(k)}2:{V.col(k)}{self.last}"
        for k in tests + ["audit"] + vtests + ["v_mos", "valn", "entry"]:
            self.passfail_cf(ws, rng(k))
        for res, fill in V_FILL.items():
            ws.conditional_formatting.add(rng("verdict"), CellIsRule(operator="equal", formula=[q(res)], fill=fill))
        for k in ("stage", "mkt", "sec"):
            ws.conditional_formatting.add(rng(k), CellIsRule(operator="equal", formula=['"Stage 2"'], fill=FILL_GREEN))
            ws.conditional_formatting.add(rng(k), FormulaRule(formula=[f'OR({V.col(k)}2="Stage 4",{V.col(k)}2="Stage 3")'], fill=FILL_RED))
        for k in ("t1", "t2", "t3s"):
            ws.conditional_formatting.add(rng(k), CellIsRule(operator="equal", formula=['"Yes"'], fill=FILL_RED))
        for val_, fill in (("Buy zone", FILL_GREEN), ("Stretched hold", FILL_AMBER), ("Over-stretched", FILL_RED)):
            ws.conditional_formatting.add(rng("band"), CellIsRule(operator="equal", formula=[q(val_)], fill=fill))

    # ------------------------------------------------- Holdings (Phase 5)
    def holdings(self):
        ws = self.wb["Holdings"]
        first, last = 5, 4 + C.HOLDING_ROWS
        body(ws, 1, 1, C.PHASE_LONG[5], font=F_TITLE)
        body(ws, 2, 1, "Enter positions in the blue columns. Everything else is looked up from Valuation / Screen. "
                       "Action is a prompt to review, not an instruction.", font=F_NOTE)
        ws.merge_cells("A2:L2")
        cols = list(HOLD_COLUMNS) + [
            ("company", "Company", None, 24), ("price", "Current price", "#,##0.00", 9), ("ret", "Return since entry", "0.0%", 8),
            ("qres", "Phase 1–3 result", None, 14), ("bith", "Y_c + 0.5g now", "0.0%", 8), ("band", "5.1 Hold band", None, 13),
            ("t1", "T1 moat/cash decay", None, 8), ("t2", "T2 valuation detachment", None, 9), ("t3s", "T3 stage 3/4", None, 8),
            ("alt", "Best alternative Y_c+0.5g (≥ quality)", "0.0%", 10), ("alt_id", "Best alternative", None, 11),
            ("t3o", "T3 opportunity cost", None, 9), ("action", "Action", None, 34)]
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
            for k in ("qres", "bith", "band", "t1", "t2", "t3s"):
                body(ws, r, ix[k], look(f"val_{k}"), fmt="0.0%" if k == "bith" else None)
            body(ws, r, ix["alt"], f'=IF({c("id", r)}="","",IFERROR(_xlfn.MAXIFS(val_bith,val_funnel,"Yes",val_qscore,'
                                   f'">="&INDEX(val_qscore,{m_}),val_id,"<>"&{c("id", r)}),""))', fmt="0.0%")
            body(ws, r, ix["alt_id"], f'=IF(OR({c("alt", r)}="",N({c("alt", r)})=0),"",IFERROR(INDEX(val_ticker,'
                                      f'MATCH({c("alt", r)},val_bith,0)),""))')
            body(ws, r, ix["t3o"], f'=IF({c("id", r)}="","",IF(N({c("alt", r)})>l_opp,"Yes","No"))')
            trig = (f'IF(OR({c("t1", r)}="Yes",{c("moat_decay", r)}="Y"),"T1 moat/cash ","")&'
                    f'IF({c("t2", r)}="Yes","T2 valuation ","")&IF({c("t3s", r)}="Yes","T3 stage ","")&'
                    f'IF({c("t3o", r)}="Yes","T3 opportunity","")')
            body(ws, r, ix["action"], f'=IF({c("id", r)}="","",IF(LEN({trig})>0,"REVIEW – SELL: "&TRIM({trig}),'
                                      f'IF({c("band", r)}="Stretched hold","HOLD (stretched band)","HOLD")))')
        self.col_name("hold_id", "Holdings", ix["id"], first, last)
        self.col_name("hold_action", "Holdings", ix["action"], first, last)
        r_ = lambda k: f"{L(ix[k])}{first}:{L(ix[k])}{last}"
        for k in ("t1", "t2", "t3s", "t3o"):
            ws.conditional_formatting.add(r_(k), CellIsRule(operator="equal", formula=['"Yes"'], fill=FILL_RED))
        ws.conditional_formatting.add(r_("action"), FormulaRule(formula=[f'LEFT({L(ix["action"])}{first},6)="REVIEW"'], fill=FILL_RED))
        ws.conditional_formatting.add(r_("action"), FormulaRule(formula=[f'LEFT({L(ix["action"])}{first},4)="HOLD"'], fill=FILL_GREEN))
        dvm = DataValidation(type="list", formula1='"Y"', allow_blank=True)
        ws.add_data_validation(dvm)
        dvm.add(r_("moat_decay"))
        ws.freeze_panes = "C5"

    # -------------------------------------------------------------- Summary
    def summary(self):
        ws, m = self.wb["Summary"], self.m
        for col, w in zip("ABCDEFGHI", (36, 11, 11, 11, 11, 11, 11, 11, 11)):
            ws.column_dimensions[col].width = w
        body(ws, 1, 1, f"Summary — {m['title']} (universe as of {m['as_of']})", font=F_TITLE)
        body(ws, 2, 1, f"Workbook v{self.version}. 5-Phase framework; all figures are live formulas.", font=F_NOTE)
        r = 4
        for col, t in enumerate(("Funnel", "Companies", "% of universe"), 1):
            header(ws, r, col, t)
        r += 1
        tot = r
        rows = [("Universe", "=COUNTA(scr_id)", True),
                ("Excluded at Pre-Screen", f"=COUNTIF(scr_result,{q(C.RES_EXCL)})", False),
                ("Phase 1 WHY pass", '=COUNTIF(scr_P1_pass,"Pass")', False),
                ("Phase 2 WHAT pass", '=COUNTIF(scr_P2_pass,"Pass")', False),
                ("Phase 3 HOW pass", '=COUNTIF(scr_P3_pass,"Pass")', False),
                (f"Phase 1–3: {C.RES_QPASS}", f"=COUNTIF(scr_result,{q(C.RES_QPASS)})", True),
                (f"Phase 1–3: {C.RES_NEAR}", f"=COUNTIF(scr_result,{q(C.RES_NEAR)})", False),
                ("Phase 4 funnel", '=COUNTIF(scr_funnel,"Yes")', True),
                ("… with valuation data", f'=COUNTIF(scr_funnel,"Yes")-COUNTIF(val_verdict,{q(C.V_NODATA)})', False),
                ("… 4.1 audit pass", '=COUNTIFS(val_funnel,"Yes",val_audit,"Pass")', False),
                ("… 4.2 valuation pass", '=COUNTIFS(val_funnel,"Yes",val_audit,"Pass",val_valn,"Pass")', False),
                (f"… {C.V_ENTRY}", f"=COUNTIF(val_verdict,{q(C.V_ENTRY)})", True)]
        for label, f, bold in rows:
            body(ws, r, 1, label, font=F_BOLD if bold else F_BODY)
            body(ws, r, 2, f, font=F_BOLD if bold else F_BODY)
            body(ws, r, 3, f"=IF($B${tot}=0,0,B{r}/$B${tot})", fmt="0.0%")
            r += 1
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
                       ("REVIEW – SELL", '=COUNTIF(hold_action,"REVIEW*")')):
            r += 1
            body(ws, r, 1, lbl)
            body(ws, r, 2, f)
        r += 2
        heads = ["Companies", *C.Q_RESULTS, "In funnel", C.V_ENTRY, "Avg quality"]

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
                body(ws, r, 7, f'=COUNTIFS({crit},scr_funnel,"Yes")')
                body(ws, r, 8, f"=COUNTIFS({crit},val_verdict,{q(C.V_ENTRY)})")
                body(ws, r, 9, f'=IF(B{r}=0,"",AVERAGEIFS(scr_score,{crit}))', fmt="0.0")
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
        table("Confidence (worse of v2/v3)", [(x, f"scr_conf,{q(x)}") for x in ("H", "M", "L")])
        table("2x2 Demand Quadrant", [(x, f"scr_quad,{q(x)}") for x in ("Target", "Fad Trap", "Long-Cycle Trap", "Low/Low")])
        body(ws, r, 1, "Caveat: qualitative screen plus mechanical valuation rules — not investment advice; see Methodology.", font=F_NOTE)
        ws.freeze_panes = "A4"

    # ----------------------------------------------------------- Shortlists
    def shortlists(self):
        ws = self.wb["Shortlists"]
        body(ws, 1, 1, "Shortlists — live; Phase 1–3 lists by quality score, Phase 4 lists by Y_c + 0.5g", font=F_TITLE)
        body(ws, 2, 1, "Blank rows = list shorter than its capacity; Data Checks warns on overflow.", font=F_NOTE)
        ctry = [("Country", "country", 12, None)] if self.m.get("show_country") else []
        qc = [("Ticker", "ticker", 9, None), ("Company", "company", 24, None), *ctry, ("Sector", "sector", 18, None)]
        vc = [("Ticker", "ticker", 9, None), ("Company", "company", 24, None)]
        blocks = [
            ("Top 25 by quality score", "scr", None, C.LIST_CAPACITY["top"],
             qc + [("Score", "score", 7, "0.0"), ("Conf.", "conf", 5, None), ("Result", "result", 14, None)]),
            (f"Phase 4: {C.V_ENTRY}", "val", C.V_ENTRY, C.LIST_CAPACITY[C.V_ENTRY],
             vc + [("Y_c+0.5g", "bith", 8, "0.0%"), ("Y_c", "yc", 7, "0.0%"), ("M_c", "mcx", 7, "0.0"),
                   ("Impl. n", "n", 7, "0.0"), ("MoS", "mos", 7, "0%"), ("Quality", "qscore", 7, "0.0")]),
            (f"Phase 4: {C.V_TIME}", "val", C.V_TIME, C.LIST_CAPACITY[C.V_TIME],
             vc + [("Y_c+0.5g", "bith", 8, "0.0%"), ("Stage", "stage", 12, None), ("Market", "mkt", 10, None),
                   ("Quality", "qscore", 7, "0.0")]),
            (f"Phase 4: {C.V_VAL}", "val", C.V_VAL, C.LIST_CAPACITY[C.V_VAL],
             vc + [("Y_c+0.5g", "bith", 8, "0.0%"), ("M_c", "mcx", 7, "0.0"), ("Impl. n", "n", 7, "0.0"),
                   ("Failed tests", "why", 26, None)]),
            (f"Phase 1–3: {C.RES_QPASS}", "scr", C.RES_QPASS, C.LIST_CAPACITY[C.RES_QPASS],
             qc + [("Score", "score", 7, "0.0"), ("CAP", "3_3n", 5, "0"), ("Power: benefit", "benefit", 28, None)]),
            (f"Phase 1–3: {C.RES_NEAR}", "scr", C.RES_NEAR, C.LIST_CAPACITY[C.RES_NEAR],
             qc + [("Score", "score", 7, "0.0"), ("Failed", "failed", 16, None), ("Weak points", "weak", 32, None)]),
        ]
        col = 1
        self.caps = []
        for title, pre, res, cap, fields in blocks:
            header(ws, 3, col, title, phase=4 if pre == "val" else 3)
            ws.merge_cells(start_row=3, start_column=col, end_row=3, end_column=col + len(fields))
            header(ws, 4, col, "#", 4)
            for j, (t, key, w, fmt) in enumerate(fields, 1):
                header(ws, 4, col + j, t, w)
            rng = "scr_result" if pre == "scr" else "val_verdict"
            count = f"MIN({cap},COUNTA(scr_id))" if res is None else f"COUNTIF({rng},{q(res)})"
            for k in range(1, cap + 1):
                r = 4 + k
                body(ws, r, col, f'=IF({k}<={count},{k},"")', fmt="0")
                key_expr = f"MATCH({k},scr_rank,0)" if res is None else f"MATCH({q(f'{res}|{k}')},{pre}_listkey,0)"
                for j, (t, key, w, fmt) in enumerate(fields, 1):
                    body(ws, r, col + j, f'=IF(${L(col)}{r}="","",INDEX({pre}_{key},{key_expr}))', fmt=fmt)
            if res:
                self.caps.append((rng, res, cap))
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
        rngs = [f"Inputs!{L(self.inp[c])}2:{L(self.inp[c])}{self.last}" for c in C.SCORE_CODES]
        bad_scores = "+".join(f"(ROWS({g})-COUNTIF({g},0)-COUNTIF({g},1)-COUNTIF({g},2))" for g in rngs)
        cap_col = L(self.inp["3.3n"])
        rows = [
            ("Duplicate company IDs", "=SUMPRODUCT((COUNTIF(inp_ID,inp_ID)>1)*1)", "=0"),
            ("Blank company IDs", "=ROWS(inp_ID)-COUNTA(inp_ID)", "=0"),
            ("Score inputs not 0/1/2 (incl. blanks)", "=" + bad_scores, "=0"),
            ("Confidence v2/v3 not H/M/L", '=2*ROWS(inp_ID)-COUNTIF(inp_confidence,"H")-COUNTIF(inp_confidence,"M")'
                                           '-COUNTIF(inp_confidence,"L")-COUNTIF(inp_conf_v3,"H")-COUNTIF(inp_conf_v3,"M")'
                                           '-COUNTIF(inp_conf_v3,"L")', "=0"),
            ("Qualitative CAP (3.3n) missing", f"=ROWS(inp_ID)-COUNT(Inputs!{cap_col}2:{cap_col}{self.last})", "=0"),
            ("Override rows with a problem (Overrides → Status)", '=COUNTA(ov_ID)-COUNTIF(ov_Status,"OK")', "=0"),
            ("Quality weights sum > 0", "=w_P1+w_P2+w_P3", ">0"),
            ("Financials / Technicals rows aligned with Inputs (ID mismatches)",
             "=SUMPRODUCT((fin_id<>inp_ID)*1)+SUMPRODUCT((tec_id<>inp_ID)*1)", "=0"),
            ("Phase 1–3 results reconcile to universe",
             "=" + "+".join(f"COUNTIF(scr_result,{q(x)})" for x in C.Q_RESULTS) + "-COUNTA(scr_id)", "=0"),
            ("Holdings with unknown company ID", '=SUMPRODUCT((hold_id<>"")*ISNA(MATCH(hold_id,inp_ID,0)))', "=0"),
        ]
        for rng, res, cap in self.caps:
            rows.append((f"'{res}' list fits Shortlists capacity ({cap})", f"=COUNTIF({rng},{q(res)})", f"<={cap}"))
        rows += [("MARKET benchmark present (info — needed for Stage 2 entry)", '=COUNTIF(bm_name,"MARKET")', "info"),
                 ("Funnel companies without valuation data (info — run fetch_market_data.py)",
                  f"=COUNTIF(val_verdict,{q(C.V_NODATA)})", "info"),
                 ("Companies excluded at Pre-Screen (info)", f"=COUNTIF(scr_result,{q(C.RES_EXCL)})", "info")]
        r = 3
        for label, f, exp in rows:
            r += 1
            body(ws, r, 1, label)
            body(ws, r, 2, f, fmt="0.00" if "weights" in label else "0")
            body(ws, r, 3, exp)
            if exp == "info":
                body(ws, r, 4, "info")
            elif exp[0] in "<>":
                body(ws, r, 4, f'=IF(B{r}{exp},"OK","CHECK")')
            else:
                body(ws, r, 4, f'=IF(ROUND(B{r},6){exp},"OK","CHECK")')
        for rg in (f"D4:D{r}", f"D{r + 2}"):
            ws.conditional_formatting.add(rg, CellIsRule(operator="equal", formula=['"OK"'], fill=FILL_GREEN))
            ws.conditional_formatting.add(rg, CellIsRule(operator="equal", formula=['"CHECK"'], fill=FILL_RED))
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
                                   "v2 base scores.", font=F_NOTE)
        ws.freeze_panes = "A2"

    # --------------------------------------------------------------- Read Me
    def readme(self):
        ws = self.wb["Read Me"]
        ws.column_dimensions["A"].width = 26
        ws.column_dimensions["B"].width = 115
        body(ws, 1, 1, self.m["title"] + " — 5-Phase MECE Stock Evaluation Framework", font=F_TITLE)
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

        section("Framework", [(C.PHASE_NAMES[p], C.PHASE_LONG[p]) for p in range(6)])
        section("How to use", [
            ("Circle of competence", "Pre-Screen → set sub-industries outside your circle to N; Inputs → ps_exclude = Y for single names."),
            ("Change a threshold or weight", "Methodology → yellow cells. Everything recalculates."),
            ("Re-score a company", "Inputs → blue cells, or log the change on Overrides (keeps base score, records reason)."),
            ("Phase 4 data", "Run `python3 fetch_market_data.py` (SEC EDGAR + Yahoo Finance), then `python3 build.py`; or type "
                             "into Financials / Technicals. Analyst growth g / g_moat go in Financials (blank = fallback)."),
            ("Positions", "Holdings → enter ID, entry date/price, shares; Action applies the hold band and sell triggers."),
            ("Before relying on results", "Data Checks → Overall status must be OK. Pre-scored v3 fields carry Confidence v3."),
            ("Rebuild / new version", "`python3 sync_from_excel.py <universe>` pulls your edits back into data/, then `python3 build.py`."),
        ])
        section("Sheets", [
            ("Summary", "Funnel from universe to entry candidates, verdicts, holdings actions, breakdowns."),
            ("Shortlists", "Top 25, Entry candidates, Watch – timing, Watch – valuation, Quality pass, Near-miss."),
            ("Methodology", "Parameters (named cells), rules and formulas, criterion rubrics, process notes."),
            ("Pre-Screen", "Circle-of-competence table by sub-industry (your inputs)."),
            ("Inputs", "Phase 1–3 inputs per company (scores, categories, CAP years, notes, confidence)."),
            ("Overrides", "Criterion-level override log feeding Screen."),
            ("Screen", "Phases 1–3: effective scores, 2x2 quadrant, Strongest Power, phase gates, quality score, result."),
            ("Financials / Technicals / Benchmarks", "Phase 4 inputs (fetched or typed)."),
            ("Valuation", "Phase 4: audit, Y_c / M_c, BitH & Hohn hurdles, implied CAP, DCF / sticker MoS, Weinstein stage, "
                          "verdict, Phase 5 triggers."),
            ("Holdings", "Phase 5 position tracker."),
            ("Data Checks", "Integrity checks."),
        ])
        section("Colour legend", [
            ("Blue text", "Input (Inputs, Overrides, Financials, Technicals, Benchmarks, Holdings, Pre-Screen)."),
            ("Yellow fill", "Editable parameter / circle-of-competence switch."),
            ("Black text", "Formula — do not overwrite."),
            ("Bold purple score", "Effective score comes from the Overrides log."),
            ("Header colours", "Grey = Pre-Screen, blue = WHY, green = WHAT, purple = HOW, orange = PROOF & ENTRY, navy = LIFECYCLE."),
        ])
        section("Change log", [(f"v{ver}", "• " + "\n• ".join(items)) for ver, items in C.CHANGELOG.items()])
        ws.row_dimensions[r].height = 15 * len(C.CHANGELOG["3.0"]) + 30
        r += 2
        body(ws, r, 1, self.m["caveat"], font=F_NOTE, align=WRAP)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.row_dimensions[r].height = 45


def build_workbook(meta: dict, version: str, path) -> None:
    Builder(meta, version).build(path)
