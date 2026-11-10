"""Compile one universe's source data into a versioned screening workbook."""
from __future__ import annotations

import datetime as dt

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

from . import config as C
from .data import BASE_FIELDS, CODES, TAIL_FIELDS

# ------------------------------------------------------------------- styles
FONT = "Calibri"
NAVY = "1F3864"
F_HDR = Font(name=FONT, bold=True, color="FFFFFF")
F_TITLE = Font(name=FONT, bold=True, size=14)
F_BOLD = Font(name=FONT, bold=True)
F_BODY = Font(name=FONT)
F_INPUT = Font(name=FONT, color="0000FF")
F_LINK = Font(name=FONT, color="008000")
F_NOTE = Font(name=FONT, italic=True, color="595959")
FILL_HDR = PatternFill("solid", fgColor=NAVY)
FILL_SUB = PatternFill("solid", fgColor="D9E1F2")
FILL_INPUT = PatternFill("solid", fgColor="FFF2CC")
FILL_RED, FILL_AMBER, FILL_GREEN = (PatternFill("solid", fgColor=c, bgColor=c)
                                    for c in ("F4CCCC", "FFF2CC", "D9EAD3"))
FILL_LGREEN = PatternFill("solid", fgColor="EAF4E4", bgColor="EAF4E4")
FILL_GREY = PatternFill("solid", fgColor="EDEDED", bgColor="EDEDED")
WRAP = Alignment(wrap_text=True, vertical="top")
HDR_ALIGN = Alignment(wrap_text=True, vertical="center", horizontal="center")
THIN = Side(style="thin", color="BFBFBF")

RESULT_FILL = {C.RES_PASS: FILL_GREEN, C.RES_QROIC: FILL_LGREEN, C.RES_NEAR: FILL_AMBER, C.RES_FAIL: FILL_RED}


def q(s: str) -> str:
    """Excel string literal."""
    return '"' + s.replace('"', '""') + '"'


def header(ws, row, col, text, width=None, fill=FILL_HDR, font=F_HDR):
    c = ws.cell(row, col, text)
    c.font, c.fill, c.alignment = font, fill, HDR_ALIGN
    if width:
        ws.column_dimensions[L(col)].width = width
    return c


def body(ws, row, col, value, fmt=None, font=F_BODY, align=None):
    c = ws.cell(row, col, value)
    c.font = font
    if fmt:
        c.number_format = fmt
    if align:
        c.alignment = align
    return c


class Builder:
    def __init__(self, meta: dict, version: str):
        self.m = meta
        self.version = version
        self.n = len(meta["companies"])
        self.last = self.n + 1                       # last data row on Inputs/Screen
        self.has_metrics = bool(meta.get("metric_columns"))
        self.wb = Workbook()
        self.names: dict[str, str] = {}
        self.scr: dict[str, int] = {}                # Screen column key -> index
        self.inp: dict[str, int] = {}                # Inputs column key -> index
        self._cols: list = []
        self._idx: dict | None = None

    # ---------------------------------------------------------------- names
    def name(self, nm: str, sheet: str, ref: str):
        self.names[nm] = f"'{sheet}'!{ref}"
        self.wb.defined_names[nm] = DefinedName(nm, attr_text=self.names[nm])

    def col_name(self, nm, sheet, col, first=2, last=None):
        c = L(col)
        self.name(nm, sheet, f"${c}${first}:${c}${last or self.last}")

    # ---------------------------------------------------------------- build
    def build(self, path):
        wb = self.wb
        self.ws_readme = wb.active
        self.ws_readme.title = "Read Me"
        self.ws_sum = wb.create_sheet("Summary")
        self.ws_list = wb.create_sheet("Shortlists")
        self.ws_meth = wb.create_sheet("Methodology")
        self.ws_inp = wb.create_sheet("Inputs")
        self.ws_ov = wb.create_sheet("Overrides")
        self.ws_scr = wb.create_sheet("Screen")
        self.ws_chk = wb.create_sheet("Data Checks")

        self.methodology()
        self.inputs()
        self.overrides()
        self.screen()
        self.summary()
        self.shortlists()
        self.checks()
        if self.m.get("reevaluations"):
            self.reeval_history()
        self.readme()
        for ws in wb.worksheets:
            ws.sheet_view.zoomScale = 90
        wb.active = 1
        wb.calculation.fullCalcOnLoad = True
        wb.save(path)

    # ---------------------------------------------------------- Methodology
    def methodology(self):
        ws = self.ws_meth
        m = self.m
        for col, w in zip("ABCDE", (62, 14, 40, 90, 14)):
            ws.column_dimensions[col].width = w
        body(ws, 1, 1, m["title"], font=F_TITLE)
        body(ws, 2, 1, m["universe_text"], align=WRAP)
        body(ws, 3, 1, m["caveat"], font=F_BOLD, align=WRAP)
        body(ws, 4, 1, f"Workbook version v{self.version} — see 'Read Me' for change log.", font=F_NOTE)
        for r in (2, 3):
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = 75 if r == 2 else 45

        r = 6
        for col, t in enumerate(("Parameter (yellow = editable; Screen formulas read these cells)",
                                 "Value", "Excel name", "Note / source"), 1):
            header(ws, r, col, t)
        custom = m.get("parameters", {})
        groups = list(C.PARAMETER_GROUPS)
        if self.has_metrics:
            groups.append(C.P5_CHECK_PARAMETERS)
        for title, params in groups:
            r += 1
            body(ws, r, 1, title, font=F_BOLD)
            for col in range(1, 5):
                ws.cell(r, col).fill = FILL_SUB
            for nm, label, val, fmt, note in params:
                r += 1
                if nm in custom:
                    val, note = custom[nm], f"{note} Universe-specific value (universe.json); framework default {val}."
                body(ws, r, 1, label)
                c = body(ws, r, 2, val, fmt=fmt, font=F_INPUT)
                c.fill = FILL_INPUT
                body(ws, r, 3, nm, font=F_NOTE)
                body(ws, r, 4, note, font=F_NOTE, align=WRAP)
                self.name(nm, "Methodology", f"$B${r}")
        r += 1
        body(ws, r, 1, "Sum of pillar weights (check)", font=F_NOTE)
        body(ws, r, 2, "=w_P1+w_P2+w_P3+w_P4+w_P5", fmt="0%")

        r += 2
        body(ws, r, 1, "Scoring scale", font=F_BOLD)
        for t in ("0 = fails the criterion", "1 = partial / mixed",
                  "2 = clearly meets the criterion (for risk criteria in Pillar 3: 2 = LOW risk)"):
            r += 1
            body(ws, r, 1, t)

        r += 2
        body(ws, r, 1, "Result rule", font=F_BOLD)
        for t in (
            f"{C.RES_PASS} = all 5 pillars pass AND 10-year avg ROIC ≥ hurdle.",
            f"{C.RES_QROIC} = all 5 pillars pass but ROIC is below the hurdle or missing.",
            f"{C.RES_NEAR} = at least 'Near-miss: min pillars' pass AND weighted score ≥ 'Near-miss: min weighted score'.",
            f"{C.RES_FAIL} = everything else.",
            "ROIC status = Pass/Fail from the numeric 10Y Avg ROIC when present; otherwise the analyst's "
            "Pass/Fail ROIC judgement; otherwise 'Missing'. " + m.get("roic_note", ""),
            "Raw total = P1 + P2 + P3 + P4 + P5 subtotals (17 scored criteria × 2 = 34 max). The four barrier "
            "sub-types are shown for transparency; only their MAX counts.",
            "Weighted score (/100) = Σ (pillar weight × pillar subtotal ÷ pillar max) ÷ Σ weights × 100. "
            "Confidence-adjusted score = weighted score × confidence multiplier.",
            "Effective score = the Overrides-sheet score where one is logged for that company and criterion, "
            "else the base score on Inputs. Overridden cells show in bold purple on Screen.",
        ):
            r += 1
            body(ws, r, 1, t, align=WRAP)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = 30

        r += 2
        for col, t in enumerate(("Pillar", "Code", "Criterion", "Definition", "Scored?"), 1):
            header(ws, r, col, t)
        first = r + 1
        prev = None
        for code, pillar, short, full, definition in C.CRITERIA:
            r += 1
            body(ws, r, 1, C.PILLAR_LONG[pillar] if pillar != prev else None, align=WRAP)
            body(ws, r, 2, code)
            body(ws, r, 3, full, align=WRAP)
            body(ws, r, 4, definition, align=WRAP)
            body(ws, r, 5, "MAX → P4.3" if code in C.BARRIER_CODES else "Yes")
            prev = pillar
        self.name("crit_Codes", "Methodology", f"$B${first}:$B${r}")
        r += 1
        body(ws, r, 1, None)
        body(ws, r, 2, "P4.3")
        body(ws, r, 3, "Durable Barriers to Entry (scored criterion)")
        body(ws, r, 4, "= MAX of the four sub-types above (one strong barrier is enough).")
        body(ws, r, 5, "Yes")

        r += 2
        body(ws, r, 1, "How the scores were produced", font=F_BOLD)
        for t in m["how_produced"]:
            r += 1
            body(ws, r, 1, t, align=WRAP)
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            ws.row_dimensions[r].height = 48
        r += 1
        body(ws, r, 1, m["sources"], align=WRAP)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        ws.row_dimensions[r].height = 48

    # --------------------------------------------------------------- Inputs
    def input_columns(self):
        cols = [("id", "ID (unique)", "@", 12), ("ticker", "Ticker", "@", 11),
                ("company", "Company", "@", 28), ("country", "Country", "@", 14),
                ("sector", "GICS Sector", "@", 20), ("sub_industry", "GICS Sub-Industry", "@", 28)]
        cols += [(c["key"], c["header"], c["fmt"], c["width"]) for c in self.m.get("extra_columns", [])]
        cols += [(code, f"{code} {short}", "0", 9) for code, _, short, _, _ in C.CRITERIA]
        cols += [("confidence", "Confidence (H/M/L)", "@", 10),
                 ("roic_10y", "10Y Avg ROIC (numeric)", "0.0%", 10),
                 ("roic_judgement", "ROIC judgement if no number (Pass/Fail)", "@", 12),
                 ("moat", "Primary moat source", "@", 32),
                 ("note", "Analyst note", "@", 70),
                 ("evidence", "Key evidence / sources", "@", 30),
                 ("last_reviewed", "Last reviewed (date)", "yyyy-mm-dd", 12)]
        cols += [(c["key"], c["header"], c["fmt"], c["width"]) for c in self.m.get("metric_columns", [])]
        return cols

    def inputs(self):
        ws = self.ws_inp
        cols = self.input_columns()
        for i, (key, title, fmt, width) in enumerate(cols, 1):
            header(ws, 1, i, title, width)
            self.inp[key] = i
        ws.row_dimensions[1].height = 60
        for r, row in enumerate(self.m["companies"], 2):
            for i, (key, _, fmt, _) in enumerate(cols, 1):
                v = row.get(key)
                if key == "last_reviewed" and isinstance(v, str):
                    try:
                        v = dt.date.fromisoformat(v)
                    except ValueError:
                        pass
                body(ws, r, i, v, fmt=fmt if fmt != "@" else None, font=F_INPUT)
        ws.freeze_panes = "D2"
        ws.auto_filter.ref = f"A1:{L(len(cols))}{self.last}"

        s0, s1 = self.inp[CODES[0]], self.inp[CODES[-1]]
        self.name("inp_ID", "Inputs", f"$A$2:$A${self.last}")
        self.name("inp_Company", "Inputs", f"$C$2:$C${self.last}")
        self.name("inp_Scores", "Inputs", f"${L(s0)}$2:${L(s1)}${self.last}")
        self.col_name("inp_Confidence", "Inputs", self.inp["confidence"])
        self.col_name("inp_Note", "Inputs", self.inp["note"])

        def dv(formula, rng, title, prompt):
            v = DataValidation(type="list", formula1=formula, allow_blank=True,
                               showErrorMessage=True, errorTitle=title, error=prompt)
            ws.add_data_validation(v)
            v.add(rng)

        dv('"0,1,2"', f"{L(s0)}2:{L(s1)}{self.last}", "Score", "Scores must be 0, 1 or 2.")
        dv('"H,M,L"', f"{L(self.inp['confidence'])}2:{L(self.inp['confidence'])}{self.last}", "Confidence", "H, M or L.")
        c = L(self.inp["roic_judgement"])
        dv('"Pass,Fail"', f"{c}2:{c}{self.last}", "ROIC judgement", "Pass, Fail or blank.")
        for x in self.m.get("extra_columns", []):
            if x.get("validation"):
                c = L(self.inp[x["key"]])
                dv(q(",".join(x["validation"])), f"{c}2:{c}{self.last}", x["header"], "/".join(x["validation"]))
        self.score_cf(ws, f"{L(s0)}2:{L(s1)}{self.last}")

    def score_cf(self, ws, rng):
        for val, fill in (("0", FILL_RED), ("1", FILL_AMBER), ("2", FILL_GREEN)):
            ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[val], fill=fill))

    # ------------------------------------------------------------ Overrides
    def overrides(self):
        ws = self.ws_ov
        first, last = 5, 4 + C.OVERRIDE_ROWS
        body(ws, 1, 1, "Overrides log — analyst changes to individual criterion scores", font=F_TITLE)
        body(ws, 2, 1, "Enter one row per change in the blue columns A–F. The effective score on Screen uses the "
                       "override; the base score on Inputs is kept untouched. Delete a row to undo. "
                       "Columns G–I are formulas (do not edit).", font=F_NOTE)
        ws.merge_cells("A2:I2")
        ws.row_dimensions[2].height = 30
        cols = [("Company ID", 12), ("Criterion code", 10), ("New score (0/1/2)", 10), ("Reason / evidence", 60),
                ("Analyst", 14), ("Date", 12), ("Company (lookup)", 28), ("Base score (lookup)", 10), ("Status", 16)]
        for i, (t, w) in enumerate(cols, 1):
            header(ws, 4, i, t, w)
        ws.row_dimensions[4].height = 45
        for k, nm in enumerate(("ov_ID", "ov_Code", "ov_Score", None, None, None, None, None, "ov_Status")):
            if nm:
                self.col_name(nm, "Overrides", k + 1, first, last)

        for j, o in enumerate(self.m["overrides"]):
            r = first + j
            for i, key in enumerate(("id", "code", "new_score", "reason", "analyst", "date"), 1):
                v = o.get(key)
                if key == "date" and isinstance(v, str):
                    try:
                        v = dt.date.fromisoformat(v)
                    except ValueError:
                        pass
                body(ws, r, i, v, fmt="yyyy-mm-dd" if key == "date" else None, font=F_INPUT)
        for r in range(first, last + 1):
            for i in range(1, 7):
                ws.cell(r, i).font = F_INPUT
            ws.cell(r, 6).number_format = "yyyy-mm-dd"
            body(ws, r, 7, f'=IF($A{r}="","",IFERROR(INDEX(inp_Company,MATCH($A{r},inp_ID,0)),"?"))')
            body(ws, r, 8, f'=IF(OR($A{r}="",$B{r}=""),"",IFERROR(INDEX(inp_Scores,MATCH($A{r},inp_ID,0),'
                           f'MATCH($B{r},crit_Codes,0)),"?"))')
            body(ws, r, 9, f'=IF($A{r}="","",IF(ISNA(MATCH($A{r},inp_ID,0)),"Unknown ID",'
                           f'IF(ISNA(MATCH($B{r},crit_Codes,0)),"Unknown code",IF($C{r}="","Missing score",'
                           f'IF(AND($C{r}<>0,$C{r}<>1,$C{r}<>2),"Invalid score",'
                           f'IF(COUNTIFS(ov_ID,$A{r},ov_Code,$B{r})>1,"Duplicate","OK"))))))')
        v = DataValidation(type="list", formula1="=crit_Codes", allow_blank=True)
        ws.add_data_validation(v)
        v.add(f"B{first}:B{last}")
        v = DataValidation(type="list", formula1='"0,1,2"', allow_blank=True)
        ws.add_data_validation(v)
        v.add(f"C{first}:C{last}")
        ws.conditional_formatting.add(f"I{first}:I{last}", CellIsRule(operator="equal", formula=['"OK"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(f"I{first}:I{last}", FormulaRule(formula=[f'AND(I{first}<>"",I{first}<>"OK")'], fill=FILL_RED))
        ws.freeze_panes = "A5"

    # --------------------------------------------------------------- Screen
    def screen(self):
        ws = self.ws_scr
        I = lambda key, r: f"Inputs!{L(self.inp[key])}{r}"
        cols: list[tuple] = []          # (key, header, width, fmt, formula(r))
        self._cols, self._idx = cols, None

        def add(key, title, width, fmt, fn):
            cols.append((key, title, width, fmt, fn))

        link = lambda key: (lambda r: f'=IF({I(key, r)}="","",{I(key, r)})')
        for key, title, fmt, width in self.input_columns()[:6 + len(self.m.get("extra_columns", []))]:
            add(key, title, width, None if fmt == "@" else fmt, link(key))
        add("confidence", "Confidence", 8, None, link("confidence"))

        def eff(code):
            return lambda r: (f'=IF(COUNTIFS(ov_ID,$A{r},ov_Code,{q(code)},ov_Status,"OK")>0,'
                              f'SUMIFS(ov_Score,ov_ID,$A{r},ov_Code,{q(code)}),{I(code, r)})')

        short = {c[0]: c[2] for c in C.CRITERIA}
        for p in ("P1", "P2", "P3"):
            codes = [c for c in CODES if c.startswith(p)]
            for code in codes:
                add(code, f"{code} {short[code]}", 8, "0", eff(code))
            add(f"{p}_sub", f"{p} Subtotal (/{C.PILLAR_MAX[p]})", 8, "0",
                (lambda cs: lambda r: f"=SUM({self.ref(cs[0], r)}:{self.ref(cs[-1], r)})")(codes))
            add(f"{p}_pass", f"{p} Pass", 7, None,
                (lambda p, cs: lambda r: f'=IF(AND({self.ref(p + "_sub", r)}>=thr_{p},OR(req_nonzero=0,'
                                         f'MIN({self.ref(cs[0], r)}:{self.ref(cs[-1], r)})>0)),"Pass","Fail")')(p, codes))
        for code in ("P4.1", "P4.2", *C.BARRIER_CODES):
            add(code, f"{code} {short[code]}", 8, "0", eff(code))
        add("P4.3", "P4.3 Durable Barriers (MAX)", 9, "0",
            lambda r: f"=MAX({self.ref('P4.3a', r)}:{self.ref('P4.3d', r)})")
        add("P4_sub", "P4 Subtotal (/6)", 8, "0",
            lambda r: f"={self.ref('P4.1', r)}+{self.ref('P4.2', r)}+{self.ref('P4.3', r)}")
        add("P4_pass", "P4 Pass", 7, None,
            lambda r: f'=IF(AND({self.ref("P4_sub", r)}>=thr_P4,{self.ref("P4.3", r)}>=thr_P4_barrier,'
                      f'{self.ref("P4.1", r)}>=thr_P4_structure),"Pass","Fail")')
        for code in ("P5.1", "P5.2"):
            add(code, f"{code} {short[code]}", 8, "0", eff(code))
        add("P5_sub", "P5 Subtotal (/4)", 8, "0", lambda r: f"={self.ref('P5.1', r)}+{self.ref('P5.2', r)}")
        add("P5_pass", "P5 Pass", 7, None, lambda r: f'=IF({self.ref("P5_sub", r)}>=thr_P5,"Pass","Fail")')

        pillars = ["P1", "P2", "P3", "P4", "P5"]
        add("pillars", "Pillars passed (/5)", 8, "0",
            lambda r: "=" + "+".join(f'({self.ref(p + "_pass", r)}="Pass")' for p in pillars))
        add("raw", "Raw total (/34)", 8, "0", lambda r: "=" + "+".join(self.ref(p + "_sub", r) for p in pillars))
        add("score", "Weighted score (/100)", 9, "0.0",
            lambda r: "=IF(w_P1+w_P2+w_P3+w_P4+w_P5=0,0,ROUND(100*(" +
                      "+".join(f"w_{p}*{self.ref(p + '_sub', r)}/{C.PILLAR_MAX[p]}" for p in pillars) +
                      ")/(w_P1+w_P2+w_P3+w_P4+w_P5),1))")
        add("adj", "Confidence-adj. score (/100)", 9, "0.0",
            lambda r: f'=ROUND({self.ref("score", r)}*IF({self.ref("confidence", r)}="H",conf_H,'
                      f'IF({self.ref("confidence", r)}="M",conf_M,conf_L)),1)')
        add("roic", "10Y Avg ROIC", 9, "0.0%",
            lambda r: f'=IF(ISNUMBER({I("roic_10y", r)}),{I("roic_10y", r)},"")')
        add("roic_status", "ROIC status", 9, None,
            lambda r: f'=IF(ISNUMBER({I("roic_10y", r)}),IF({I("roic_10y", r)}>=roic_hurdle,"Pass","Fail"),'
                      f'IF(OR({I("roic_judgement", r)}="Pass",{I("roic_judgement", r)}="Fail"),'
                      f'{I("roic_judgement", r)},"Missing"))')
        add("result", "Result", 14, None,
            lambda r: f'=IF({self.ref("pillars", r)}=5,IF({self.ref("roic_status", r)}="Pass",'
                      f'{q(C.RES_PASS)},{q(C.RES_QROIC)}),IF(AND({self.ref("pillars", r)}>=nm_pillars,'
                      f'{self.ref("score", r)}>=nm_score),{q(C.RES_NEAR)},{q(C.RES_FAIL)}))')
        add("rank", "Rank", 7, "0", lambda r: f'=COUNTIF(scr_SortKey,">"&{self.ref("sortkey", r)})+1')
        add("failed", "Failed pillar(s) / hurdle", 16, None,
            lambda r: "=TRIM(" + "&".join(f'IF({self.ref(p + "_pass", r)}="Fail","{p} ","")' for p in pillars) +
                      f'&IF({self.ref("roic_status", r)}<>"Pass","ROIC",""))')
        scored = [c for c in CODES if c not in C.BARRIER_CODES]
        scored.insert(scored.index("P5.1"), "P4.3")
        labels = dict(short, **{"P4.3": "Durable Barriers"})
        add("weak", "Weak points (criteria scored 0)", 40, None,
            lambda r: "=MID(" + "&".join(f'IF({self.ref(c, r)}=0,"; {labels[c].split(" (")[0]}","")'
                                         for c in scored) + ",3,500)")
        add("n_ov", "Overrides applied (#)", 9, "0", lambda r: f"=COUNTIFS(ov_ID,$A{r},ov_Status,\"OK\")")
        add("moat", "Primary moat source", 30, None, link("moat"))
        add("note", "Analyst note", 70, None, link("note"))

        if self.has_metrics:
            M = lambda k, r: I(k, r)
            add("p5v_impl", "P5.1 implied by data", 9, "0",
                lambda r: f'=IF(OR(NOT(ISNUMBER({M("ni_down_years", r)})),NOT(ISNUMBER({M("ni_years", r)}))),"n/a",'
                          f'IF({M("ni_years", r)}=0,"n/a",MAX(0,IF({M("ni_down_years", r)}/{M("ni_years", r)}<=p5_ni_good,2,'
                          f'IF({M("ni_down_years", r)}/{M("ni_years", r)}<=p5_ni_ok,1,0))'
                          f'-IF(ISNUMBER({M("inv_minus_rev_pp", r)}),IF({M("inv_minus_rev_pp", r)}>p5_inv_gap,1,0),0)'
                          f'-IF(ISNUMBER({M("rev_cagr", r)}),IF({M("rev_cagr", r)}<0,1,0),0))))')
            add("p5p_impl", "P5.2 implied by data", 9, "0",
                lambda r: f'=IF(ISNUMBER({M("gm_range_pp", r)}),IF({M("gm_range_pp", r)}<=p5_gm_good,2,'
                          f'IF({M("gm_range_pp", r)}<=p5_gm_ok,1,0)),"n/a")')
            add("p5_check", "P5 data check", 11, None,
                lambda r: f'=IF(AND({self.ref("p5v_impl", r)}="n/a",{self.ref("p5p_impl", r)}="n/a"),"No data",'
                          f'IF(OR(IF(ISNUMBER({self.ref("p5v_impl", r)}),ABS({self.ref("P5.1", r)}-{self.ref("p5v_impl", r)})>=p5_flag_gap,FALSE),'
                          f'IF(ISNUMBER({self.ref("p5p_impl", r)}),ABS({self.ref("P5.2", r)}-{self.ref("p5p_impl", r)})>=p5_flag_gap,FALSE)),'
                          f'"Review","Consistent"))')

        add("sortkey", "helper: sort key", 11, "0",
            lambda r: f'=ROUND(IF(rank_basis=2,{self.ref("adj", r)},{self.ref("score", r)})*10,0)*10000+10000-ROW()')
        add("listkey", "helper: list key", 24, None,
            lambda r: f'={self.ref("result", r)}&"|"&(COUNTIFS(scr_Result,{self.ref("result", r)},'
                      f'scr_SortKey,">"&{self.ref("sortkey", r)})+1)')

        self.scr = self._idx = {key: i for i, (key, *_rest) in enumerate(cols, 1)}
        for i, (key, title, width, fmt, fn) in enumerate(cols, 1):
            header(ws, 1, i, title, width)
            for r in range(2, self.last + 1):
                c = body(ws, r, i, fn(r), fmt=fmt)
                if key in ("raw", "score", "result", "pillars"):
                    c.font = F_BOLD
        ws.row_dimensions[1].height = 60
        for key, i in self.scr.items():
            self.col_name("scr_" + key.replace(".", "_"), "Screen", i)
        ws.freeze_panes = "D2"
        ws.auto_filter.ref = f"A1:{L(len(cols))}{self.last}"
        for key in ("sortkey", "listkey"):
            ws.column_dimensions[L(self.scr[key])].outlineLevel = 1
            ws.column_dimensions[L(self.scr[key])].hidden = True

        # conditional formatting
        rng = lambda k1, k2=None: f"{L(self.scr[k1])}2:{L(self.scr[k2 or k1])}{self.last}"
        for a, b in (("P1.1", "P1.4"), ("P2.1", "P2.4"), ("P3.1", "P3.4"), ("P4.1", "P4.3"), ("P5.1", "P5.2")):
            self.score_cf(ws, rng(a, b))
            h = f"{L(self.scr[a])}$1"
            ws.conditional_formatting.add(rng(a, b), FormulaRule(
                formula=[f'COUNTIFS(ov_ID,$A2,ov_Code,LEFT({h},FIND(" ",{h})-1),ov_Status,"OK")>0'],
                font=Font(bold=True, color="7030A0")))
        for p in pillars + ["roic_status"]:
            k = p + "_pass" if p != "roic_status" else p
            ws.conditional_formatting.add(rng(k), CellIsRule(operator="equal", formula=['"Pass"'], fill=FILL_GREEN))
            ws.conditional_formatting.add(rng(k), CellIsRule(operator="equal", formula=['"Fail"'], fill=FILL_RED))
        ws.conditional_formatting.add(rng("roic_status"), CellIsRule(operator="equal", formula=['"Missing"'], fill=FILL_GREY))
        for res, fill in RESULT_FILL.items():
            ws.conditional_formatting.add(rng("result"), CellIsRule(operator="equal", formula=[q(res)], fill=fill))
        if self.has_metrics:
            ws.conditional_formatting.add(rng("p5_check"), CellIsRule(operator="equal", formula=['"Review"'], fill=FILL_AMBER))

    def ref(self, key, r):
        """Cell reference to a Screen column by key. Formula lambdas are only rendered
        after every column has been registered, so forward references resolve."""
        if self._idx is None:
            raise RuntimeError("Screen columns not finalised")
        return f"{L(self._idx[key])}{r}"

    # -------------------------------------------------------------- Summary
    def summary(self):
        ws = self.ws_sum
        m = self.m
        for col, w in zip("ABCDEFGHI", (34, 12, 12, 14, 12, 12, 12, 12, 12)):
            ws.column_dimensions[col].width = w
        body(ws, 1, 1, f"Summary — {m['title']} (universe as of {m['as_of']})", font=F_TITLE)
        body(ws, 2, 1, f"Workbook v{self.version}. All figures are live formulas on the Screen sheet.", font=F_NOTE)
        r = 4
        for col, t in enumerate(("Result", "Companies", "% of universe"), 1):
            header(ws, r, col, t)
        r += 1
        body(ws, r, 1, "Companies screened")
        body(ws, r, 2, "=COUNTA(scr_id)")
        body(ws, r, 3, f"=IF($B${r}=0,0,B{r}/$B${r})", fmt="0.0%")
        tot = r
        for res in C.RESULTS:
            r += 1
            body(ws, r, 1, res)
            body(ws, r, 2, f"=COUNTIF(scr_result,{q(res)})")
            body(ws, r, 3, f"=IF($B${tot}=0,0,B{r}/$B${tot})", fmt="0.0%")
            ws.cell(r, 1).fill = RESULT_FILL[res]

        r += 2
        for col, t in enumerate(("Pillar / hurdle", "Companies passing", "Pass rate"), 1):
            header(ws, r, col, t)
        for p in ("P1", "P2", "P3", "P4", "P5"):
            r += 1
            body(ws, r, 1, f"{p} {C.PILLARS[p]}")
            body(ws, r, 2, f'=COUNTIF(scr_{p}_pass,"Pass")')
            body(ws, r, 3, f"=IF($B${tot}=0,0,B{r}/$B${tot})", fmt="0.0%")
        r += 1
        body(ws, r, 1, "ROIC hurdle")
        body(ws, r, 2, '=COUNTIF(scr_roic_status,"Pass")')
        body(ws, r, 3, f"=IF($B${tot}=0,0,B{r}/$B${tot})", fmt="0.0%")
        r += 1
        body(ws, r, 1, "ROIC data missing", font=F_NOTE)
        body(ws, r, 2, '=COUNTIF(scr_roic_status,"Missing")')

        r += 2
        heads = ["Companies", *C.RESULTS, "PASS rate", "Avg score", "Avg conf-adj."]

        def table(title, rows):
            nonlocal r
            header(ws, r, 1, title)
            for col, t in enumerate(heads, 2):
                header(ws, r, col, t)
            first = r + 1
            for label, crit in rows:
                r += 1
                body(ws, r, 1, label)
                body(ws, r, 2, f"=COUNTIFS({crit})")
                for j, res in enumerate(C.RESULTS):
                    body(ws, r, 3 + j, f"=COUNTIFS({crit},scr_result,{q(res)})")
                body(ws, r, 7, f"=IF(B{r}=0,0,C{r}/B{r})", fmt="0.0%")
                body(ws, r, 8, self._avg(crit, "scr_score", r), fmt="0.0")
                body(ws, r, 9, self._avg(crit, "scr_adj", r), fmt="0.0")
            r += 1
            body(ws, r, 1, "Total", font=F_BOLD)
            for col in range(2, 7):
                body(ws, r, col, f"=SUM({L(col)}{first}:{L(col)}{r - 1})", font=F_BOLD)
            body(ws, r, 7, f"=IF(B{r}=0,0,C{r}/B{r})", fmt="0.0%", font=F_BOLD)
            r += 2

        for b in m["breakdowns"]:
            if "field" in b:
                vals = sorted({c[b["field"]] for c in m["companies"] if c.get(b["field"])})
                table(b["title"], [(v, f"scr_{b['field']},{q(v)}") for v in vals])
            else:
                table(b["title"], [(label, ",".join(f"scr_{k},{q(v)}" for k, v in cond.items()))
                                   for label, cond in b["flags"]])
        table("Confidence", [(v, f"scr_confidence,{q(v)}") for v in ("H", "M", "L")])

        header(ws, r, 1, "Weighted score band")
        header(ws, r, 2, "Companies")
        header(ws, r, 3, "% of universe")
        bands = [(90, 101), (80, 90), (75, 80), (70, 75), (60, 70), (50, 60), (0, 50)]
        for lo, hi in bands:
            r += 1
            body(ws, r, 1, f"{lo}–{min(hi, 100)}" if hi <= 100 else f"≥ {lo}")
            body(ws, r, 2, f'=COUNTIFS(scr_score,">={lo}",scr_score,"<{hi}")')
            body(ws, r, 3, f"=IF($B${tot}=0,0,B{r}/$B${tot})", fmt="0.0%")
        r += 2
        body(ws, r, 1, "Caveat: qualitative screen, not investment advice; see Methodology.", font=F_NOTE)
        ws.freeze_panes = "A4"

    @staticmethod
    def _avg(crit, rng, r):
        return f'=IF(B{r}=0,"",AVERAGEIFS({rng},{crit}))'

    # ----------------------------------------------------------- Shortlists
    def shortlists(self):
        ws = self.ws_list
        body(ws, 1, 1, "Shortlists — live, sorted by ranking score (see Methodology → 'Rank by')", font=F_TITLE)
        body(ws, 2, 1, "Lists fill automatically from Screen. Blank rows = list shorter than its capacity; "
                       "Data Checks warns if a list overflows.", font=F_NOTE)
        country = [("Country", "country", 13, None)] if self.m.get("show_country") else []
        common = [("Ticker", "ticker", 10, None), ("Company", "company", 26, None), *country,
                  ("Sector", "sector", 20, None)]
        blocks = [
            ("Top 25 by ranking score", None, C.LIST_CAPACITY["top"],
             common + [("Score", "score", 8, "0.0"), ("Conf-adj.", "adj", 8, "0.0"),
                       ("Conf.", "confidence", 6, None), ("Result", "result", 16, None)]),
            (f"{C.RES_PASS} list", C.RES_PASS, C.LIST_CAPACITY[C.RES_PASS],
             common + [("Score", "score", 8, "0.0"), ("Conf-adj.", "adj", 8, "0.0"), ("ROIC", "roic", 8, "0.0%"),
                       ("Primary moat source", "moat", 30, None), ("Analyst note", "note", 60, None)]),
            (f"{C.RES_QROIC} list", C.RES_QROIC, C.LIST_CAPACITY[C.RES_QROIC],
             common + [("Score", "score", 8, "0.0"), ("ROIC", "roic", 8, "0.0%"),
                       ("ROIC status", "roic_status", 9, None), ("Primary moat source", "moat", 30, None)]),
            (f"{C.RES_NEAR} list", C.RES_NEAR, C.LIST_CAPACITY[C.RES_NEAR],
             common + [("Score", "score", 8, "0.0"), ("ROIC", "roic_status", 8, None),
                       ("Failed pillar(s) / hurdle", "failed", 18, None), ("Weak points", "weak", 36, None)]),
        ]
        col = 1
        self.list_caps = {}
        for title, res, cap, fields in blocks:
            header(ws, 3, col, title)
            ws.merge_cells(start_row=3, start_column=col, end_row=3, end_column=col + len(fields))
            header(ws, 4, col, "#", 5)
            for j, (t, key, w, fmt) in enumerate(fields, 1):
                header(ws, 4, col + j, t, w)
            count = (f"MIN({cap},COUNTA(scr_id))" if res is None else f'COUNTIF(scr_result,{q(res)})')
            for k in range(1, cap + 1):
                r = 4 + k
                body(ws, r, col, f'=IF({k}<={count},{k},"")', fmt="0")
                key_expr = (f"MATCH({k},scr_rank,0)" if res is None else f'MATCH({q(res + "|" + str(k))},scr_listkey,0)')
                for j, (t, key, w, fmt) in enumerate(fields, 1):
                    body(ws, r, col + j, f'=IF(${L(col)}{r}="","",INDEX(scr_{key},{key_expr}))', fmt=fmt)
            if res is not None:
                self.list_caps[res] = cap
            col += len(fields) + 2
        ws.freeze_panes = "A5"

    # ---------------------------------------------------------- Data Checks
    def checks(self):
        ws = self.ws_chk
        for c, w in zip("ABCD", (60, 14, 22, 12)):
            ws.column_dimensions[c].width = w
        body(ws, 1, 1, "Data Checks — all should read OK before relying on the results", font=F_TITLE)
        for i, t in enumerate(("Check", "Value", "Expected", "Status"), 1):
            header(ws, 3, i, t)
        score_rng = "inp_Scores"
        n_score_cells = f"ROWS(inp_Scores)*COLUMNS(inp_Scores)"
        rows = [
            ("Duplicate company IDs", "=SUMPRODUCT((COUNTIF(inp_ID,inp_ID)>1)*1)", "=0"),
            ("Blank company IDs", f"=ROWS(inp_ID)-COUNTA(inp_ID)", "=0"),
            ("Score inputs not 0/1/2 (incl. blanks)",
             f'={n_score_cells}-COUNTIF({score_rng},0)-COUNTIF({score_rng},1)-COUNTIF({score_rng},2)', "=0"),
            ("Confidence not H/M/L",
             '=ROWS(inp_Confidence)-COUNTIF(inp_Confidence,"H")-COUNTIF(inp_Confidence,"M")-COUNTIF(inp_Confidence,"L")', "=0"),
            ("Missing analyst note", '=COUNTBLANK(inp_Note)', "=0"),
            ("Override rows with a problem (see Overrides → Status)",
             '=COUNTA(ov_ID)-COUNTIF(ov_Status,"OK")', "=0"),
            ("Pillar weights sum to 100%", "=w_P1+w_P2+w_P3+w_P4+w_P5", "=1"),
            ("Result counts reconcile to universe",
             "=" + "+".join(f"COUNTIF(scr_result,{q(x)})" for x in C.RESULTS) + "-COUNTA(scr_id)", "=0"),
        ]
        for res, cap in self.list_caps.items():
            rows.append((f"'{res}' list fits Shortlists capacity ({cap})", f"=COUNTIF(scr_result,{q(res)})", f"<={cap}"))
        rows.append(("Companies with ROIC status 'Missing' (info)", '=COUNTIF(scr_roic_status,"Missing")', "info"))
        if self.has_metrics:
            rows.append(("P5 data check = 'Review' (info — analyst vs EDGAR data disagree)",
                         '=COUNTIF(scr_p5_check,"Review")', "info"))
        r = 3
        for label, f, exp in rows:
            r += 1
            body(ws, r, 1, label)
            body(ws, r, 2, f, fmt="0%" if "weights" in label else "0")
            body(ws, r, 3, exp)
            if exp == "info":
                body(ws, r, 4, "info")
            elif exp.startswith("<="):
                body(ws, r, 4, f'=IF(B{r}{exp},"OK","CHECK")')
            else:
                body(ws, r, 4, f'=IF(ROUND(B{r},6){exp},"OK","CHECK")')
        ws.conditional_formatting.add(f"D4:D{r}", CellIsRule(operator="equal", formula=['"OK"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(f"D4:D{r}", CellIsRule(operator="equal", formula=['"CHECK"'], fill=FILL_RED))
        r += 2
        body(ws, r, 1, "Overall status", font=F_BOLD)
        body(ws, r, 4, f'=IF(COUNTIF(D4:D{r - 2},"CHECK")=0,"OK","CHECK")', font=F_BOLD)
        self.name("chk_Overall", "Data Checks", f"$D${r}")
        ws.conditional_formatting.add(f"D{r}", CellIsRule(operator="equal", formula=['"OK"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(f"D{r}", CellIsRule(operator="equal", formula=['"CHECK"'], fill=FILL_RED))

    # ---------------------------------------------- Re-evaluation history
    def reeval_history(self):
        ws = self.wb.create_sheet("Re-evaluation history")
        rows = self.m["reevaluations"]
        fields = list(rows[0].keys())
        widths = {"Analyst Re-evaluation Justification": 80}
        for i, f in enumerate(fields, 1):
            header(ws, 1, i, f, widths.get(f, 22 if "Scores" in f else 14))
        for r, row in enumerate(rows, 2):
            for i, f in enumerate(fields, 1):
                body(ws, r, i, row.get(f), align=WRAP)
        r = len(rows) + 3
        body(ws, r, 1, "Pre-v2 re-evaluations (pillar-level). The 'Updated' scores are already in the base scores on "
                       "Inputs; criterion-level originals were not kept in v1. New re-evaluations go on Overrides.",
             font=F_NOTE)
        ws.freeze_panes = "A2"

    # --------------------------------------------------------------- Read Me
    def readme(self):
        ws = self.ws_readme
        ws.column_dimensions["A"].width = 26
        ws.column_dimensions["B"].width = 110
        body(ws, 1, 1, self.m["title"], font=F_TITLE)
        info = [("Version", f"v{self.version}"),
                ("Generated", dt.date.today().isoformat() + " by build.py (Python generator)"),
                ("Universe as of", self.m["as_of"]),
                ("Data checks", "=chk_Overall")]
        r = 2
        for k, v in info:
            r += 1
            body(ws, r, 1, k, font=F_BOLD)
            body(ws, r, 2, v)
        ws.conditional_formatting.add(f"B{r}", CellIsRule(operator="equal", formula=['"OK"'], fill=FILL_GREEN))
        ws.conditional_formatting.add(f"B{r}", CellIsRule(operator="equal", formula=['"CHECK"'], fill=FILL_RED))

        def section(title, items):
            nonlocal r
            r += 2
            header(ws, r, 1, title)
            header(ws, r, 2, "")
            for k, v in items:
                r += 1
                body(ws, r, 1, k, font=F_BOLD, align=WRAP)
                body(ws, r, 2, v, align=WRAP)

        section("How to use", [
            ("Change a threshold or weight", "Methodology → yellow cells. Everything recalculates."),
            ("Re-score a company", "Inputs → blue score cells (0/1/2), or log the change on Overrides "
                                   "(keeps the base score and records reason, analyst and date)."),
            ("Read the results", "Summary (counts and breakdowns), Shortlists (ranked lists), Screen (full detail)."),
            ("Before relying on results", "Data Checks → Overall status must be OK."),
            ("Rebuild / new version", "Edit data/<universe>/*.csv or screener/config.py, or run "
                                      "`python sync_from_excel.py` to pull Inputs/Overrides edits from this "
                                      "workbook back into the CSVs, then `python build.py`."),
        ])
        section("Sheets", [
            ("Summary", "Result counts, pillar pass rates, breakdowns by sector/index or country/confidence, score bands."),
            ("Shortlists", "Live Top 25, PASS, Quality – ROIC not met, Near-miss lists."),
            ("Methodology", "Editable parameters (named cells), result rules, criterion definitions, process notes."),
            ("Inputs", "Analyst inputs: base scores, confidence, ROIC, moat, notes, reference data."),
            ("Overrides", "Criterion-level override log; feeds the effective scores on Screen."),
            ("Screen", "All calculations: effective scores, pillar results, weighted score, ROIC status, result, rank."),
            ("Data Checks", "Integrity checks on inputs, overrides, weights and list capacity."),
        ] + ([("Re-evaluation history", "Pre-v2 analyst re-evaluations (pillar-level).")]
             if self.m.get("reevaluations") else []))
        section("Colour legend", [
            ("Blue text", "Hard-coded input (Inputs, Overrides)."),
            ("Yellow fill", "Editable parameter (Methodology)."),
            ("Black text", "Formula — do not overwrite."),
            ("Bold purple score", "Effective score comes from the Overrides log."),
            ("Red / amber / green", "Score 0 / 1 / 2, or Fail / Near-miss / Pass."),
        ])
        section("Change log", [(f"v{v}", "• " + "\n• ".join(items)) for v, items in C.CHANGELOG.items()])
        ws.row_dimensions[r].height = 15 * sum(len(i) for i in C.CHANGELOG.values()) + 10
        r += 2
        body(ws, r, 1, self.m["caveat"], font=F_NOTE, align=WRAP)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.row_dimensions[r].height = 45


def build_workbook(meta: dict, version: str, path) -> None:
    Builder(meta, version).build(path)
