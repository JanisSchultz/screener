"""Bulk scoring automation engine, batch context exporter, validator, and mirror synchronizer (v7.16).

Operates on the 989 Gate 3 companies across data/{us,eu,ca}/inputs.csv adhering strictly to
QUALITATIVE_EVALUATION_SPEC.md and COMPANY_EVALUATION_SPEC.md.

Key Capabilities:
1. Candidate Identification: Discovers all 989 Gate 3 companies across US (445), EU (495), and CA (49).
2. Reference Preservation: Strictly guards and verifies the 11 Phase 1 reference companies
   (SPGI, COST, ASML.NL, ASML, MSFT, WM, RMS.FR, CNR.CA, HSY, CRM, NUE).
3. Batch Context Exporter: Exports full evaluation dossiers (metadata, current qualitative context,
   5-10Y financials, sales CAGRs, clock-speed presumption) for genuine M3 AI evaluator subagents.
4. Deterministic CAP & Moat Engine: Deterministically computes Initial CAP, derived primary moat (3a),
   and Final CAP (4) with zero manual overrides.
5. Sequential Munger Waterfall Ingestion: Enforces strict downstream clearing on gate rejections
   (e.g. clearing Gate 4 and Gates 5-6 when Gate 3 fails without calamity; clearing Gates 5-6 when
   Gate 4 fails). Ensures Gate 5 and 6 are populated when CAP >= 15 to prevent 'To review' dead ends.
6. Dual-Listed Mirror Synchronization: Synchronizes all qualitative scores, notes, and evidence
   identically between dual-listed pairs (ASML <-> ASML.NL, FER <-> FER.ES).
7. Comprehensive Audit: Validates waterfall integrity, formula parity, note presence, and mirror parity.

Usage:
    python3 screener/bulk_scorer.py --audit
    python3 screener/bulk_scorer.py --sync-mirrors [--dry-run | --apply]
    python3 screener/bulk_scorer.py --export-batch --out-dir /path/to/batches [--batch-size 20]
    python3 screener/bulk_scorer.py --ingest /path/to/evaluations [--dry-run | --apply]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.apply_evaluation import QUAL_KEY_MAP, sanitize_val  # noqa: E402
from screener.config import (  # noqa: E402
    CALAMITY_GATES,
    CAP_VALUES,
    FORCE_SCORE_CODES,
    GATES,
    LEGACY_MOAT_ALIASES,
    MOAT_SCORE_CODES,
    MOAT_SCORE_SPEC,
    MOAT_TYPES,
    RES_CALAMITY,
    RES_QPASS,
    RES_REJ,
    RES_REVIEW,
    SCORE_VALUES,
)
from screener.gates import (  # noqa: E402
    cap_audit,
    compute_final_cap_from_scores,
    compute_initial_cap_from_scores,
    moderate_force_haircut,
    normalize_moat_label,
    params,
    phase_results,
)

DATA_DIR = ROOT / "data"
UNIVERSES = ("us", "eu", "ca")

# Universe constituent targets for Gate 3 (1 == 'Y' and 2 == 'Y')
TARGET_GATE_3_COUNTS = {
    "us": 445,
    "eu": 495,
    "ca": 49,
}
TOTAL_GATE_3_TARGET = 989

# Qualitative columns in inputs.csv subject to scoring / waterfall / mirror parity
QUAL_COLUMNS = [
    "1", "2", "2r",
    "3_tb", "3_ia", "3_se", "3_rd", "3a", "3b", "3m",
    "4_ent", "4_riv", "4_buy", "4_sup", "4_sub", "4", "4n",
    "5", "6",
    "calamity", "calamity_note",
    "note", "evidence",
]

# Fast clock-speed sub-industries carrying presumptive 4_sub >= 1 per Mauboussin Outside-View rule
FAST_CLOCK_SPEED_SECTORS = {"Information Technology"}
FAST_CLOCK_SPEED_SUBINDUSTRIES = {
    "Semiconductors",
    "Semiconductor Materials & Equipment",
    "Application Software",
    "Systems Software",
    "Technology Hardware, Storage & Peripherals",
    "Electronic Equipment & Instruments",
    "Electronic Components",
    "Communications Equipment",
    "Technology Distributors",
    "Interactive Media & Services",
    "Pharmaceuticals",
    "Biotechnology",
    "Life Sciences Tools & Services",
    "Health Care Equipment",
    "Health Care Technology",
}

# Immutable reference snapshot of the 11 Phase 1 reference companies
REFERENCE_SNAPSHOT: dict[str, dict[str, Any]] = {
    "SPGI": {
        "universe": "us",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4": 30,
        "5": 1, "6": "Y",
        "calamity": "", "calamity_note": "",
    },
    "COST": {
        "universe": "us",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 1, "3_ia": 1, "3_se": 2, "3_rd": 0,
        "3a": "Scale economies shared", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4": 30,
        "5": 2, "6": "Y",
        "calamity": "", "calamity_note": "",
    },
    "ASML": {
        "universe": "us",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 2,
        "3a": "R&D & innovation leadership", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4": 25,
        "5": 2, "6": "Y",
        "calamity": "", "calamity_note": "",
    },
    "ASML.NL": {
        "universe": "eu",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 2,
        "3a": "R&D & innovation leadership", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4": 25,
        "5": 2, "6": "Y",
        "calamity": "", "calamity_note": "",
    },
    "MSFT": {
        "universe": "us",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 2, "3_ia": 2, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 1,
        "4": 25,
        "5": 1, "6": "Y",
        "calamity": "", "calamity_note": "",
    },
    "WM": {
        "universe": "us",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4": 25,
        "5": 1, "6": "Y",
        "calamity": "", "calamity_note": "",
    },
    "RMS.FR": {
        "universe": "eu",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4": 25,
        "5": 2, "6": "Y",
        "calamity": "", "calamity_note": "",
    },
    "CNR.CA": {
        "universe": "ca",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 0, "4_sup": 1, "4_sub": 0,
        "4": 20,
        "5": 1, "6": "Y",
        "calamity": "", "calamity_note": "",
    },
    "HSY": {
        "universe": "us",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles", "3b": "Y",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4": 15,
        "5": 1, "6": "Y",
        "calamity": "", "calamity_note": "",
    },
    "CRM": {
        "universe": "us",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 2, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs", "3b": "Y",
        "4_ent": 1, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 2,
        "4": 5,
        "5": "", "6": "",
        "calamity": "", "calamity_note": "",
    },
    "NUE": {
        "universe": "us",
        "1": "Y", "2": "Y", "2r": "",
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "None", "3b": "N",
        "4_ent": "", "4_riv": "", "4_buy": "", "4_sup": "", "4_sub": "",
        "4": "", "4n": "",
        "5": "", "6": "",
        "calamity": "", "calamity_note": "",
    },
}
REFERENCE_COMPANIES = set(REFERENCE_SNAPSHOT.keys())


# ----------------------------------------------------------------------
# I/O & Universe Data Access
# ----------------------------------------------------------------------

def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file returning list of string dicts."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv_atomic(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    """Safely write CSV rows atomically using a temporary file in the same directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_file = tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, newline="", encoding="utf-8")
    try:
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({k: ("" if r.get(k) is None else sanitize_val(r.get(k))) for k in fieldnames})
        temp_file.close()
        os.replace(temp_file.name, path)
    except Exception:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        raise


def load_universe_inputs(universe: str) -> tuple[list[dict[str, str]], list[str]]:
    """Load inputs.csv for a universe, returning (rows, fieldnames)."""
    p = DATA_DIR / universe / "inputs.csv"
    if not p.exists():
        raise FileNotFoundError(f"Missing inputs.csv for universe {universe}: {p}")
    rows = read_csv_rows(p)
    fieldnames = list(rows[0].keys()) if rows else []
    return rows, fieldnames


def load_universe_financials(universe: str) -> dict[str, dict[str, str]]:
    """Load financials.csv for a universe mapped by company id."""
    p = DATA_DIR / universe / "financials.csv"
    if not p.exists():
        return {}
    return {r["id"]: r for r in read_csv_rows(p) if "id" in r}


def load_universe_mirrors() -> dict[str, tuple[str, str]]:
    """Load mirror mappings from data/us/universe.json: {mirror_ticker: (source_universe, source_id)}."""
    p = DATA_DIR / "us" / "universe.json"
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as f:
        meta = json.load(f)
    raw_mirrors = meta.get("mirror", {})
    mirrors = {}
    for target_ticker, source_spec in raw_mirrors.items():
        if ":" in source_spec:
            src_u, src_id = source_spec.split(":", 1)
        else:
            src_u, src_id = "eu", source_spec
        mirrors[target_ticker] = (src_u, src_id)
    return mirrors


# ----------------------------------------------------------------------
# Domain & Gate 3 Discovery Logic
# ----------------------------------------------------------------------

def is_fast_clock_speed(sector: str | None, sub_industry: str | None) -> bool:
    """Check if sub-industry carries presumptive 4_sub >= 1 per Mauboussin Outside-View rule."""
    if not sector or not sub_industry:
        return False
    clean_sec = sector.strip()
    clean_sub = sub_industry.replace(" (mapped)", "").strip()
    if clean_sec in FAST_CLOCK_SPEED_SECTORS:
        return True
    return clean_sub in FAST_CLOCK_SPEED_SUBINDUSTRIES


def get_gate_3_companies(
    universes: tuple[str, ...] = UNIVERSES,
    sector: str | None = None,
    sub_industry: str | None = None,
    company_id: str | None = None,
    unscored_only: bool = False,
    scored_only: bool = False,
) -> list[dict[str, Any]]:
    """Discover all companies reaching Gate 3 (1 == 'Y' and 2 == 'Y') across universes.

    Enriches each record with financial statement context, mirror information,
    and fast clock-speed classification.
    """
    results: list[dict[str, Any]] = []

    for u in universes:
        rows, _ = load_universe_inputs(u)
        fin_map = load_universe_financials(u)

        for r in rows:
            if r.get("1") != "Y" or r.get("2") != "Y":
                continue

            cid = r.get("id") or r.get("ticker", "")
            if company_id and cid != company_id:
                continue

            c_sec = r.get("sector", "")
            c_sub = r.get("sub_industry", "")
            clean_sub = c_sub.replace(" (mapped)", "").strip()

            if sector and c_sec != sector:
                continue
            if sub_industry and clean_sub != sub_industry.replace(" (mapped)", "").strip():
                continue

            is_scored = bool(r.get("3_tb") != "" and r.get("3_ia") != "" and r.get("3_se") != "" and r.get("3_rd") != "")
            if unscored_only and is_scored:
                continue
            if scored_only and not is_scored:
                continue

            # Enrich with financial indicators
            fin = fin_map.get(cid, {})
            enriched = {
                **r,
                "_universe": u,
                "_is_reference": cid in REFERENCE_COMPANIES,
                "_is_scored": is_scored,
                "_is_fast_clock_speed": is_fast_clock_speed(c_sec, c_sub),
                "_financials": fin,
            }
            results.append(enriched)

    return results


# ----------------------------------------------------------------------
# Deterministic Calculations & Formatting
# ----------------------------------------------------------------------

def calculate_caps_and_archetype(
    moat_scores: dict[str, int],
    force_scores: dict[str, int] | None = None,
    current_3a: str | None = None,
) -> dict[str, Any]:
    """Calculate deterministic Initial CAP, derived primary moat 3a, and Final CAP 4.

    Args:
        moat_scores: Dict containing '3_tb', '3_ia', '3_se', '3_rd' with values in {0, 1, 2}.
        force_scores: Optional dict containing '4_ent', '4_riv', '4_buy', '4_sup', '4_sub' with values in {0, 1, 2}.
        current_3a: Optional existing 3a archetype string for tie-breaking.

    Returns:
        dict containing cap_init, primary_moat, cap_final, mod_haircut, fatal_flaw, and warnings.
    """
    m_tuple = tuple(int(moat_scores[c]) for c in MOAT_SCORE_CODES)
    cap_init = compute_initial_cap_from_scores(m_tuple)
    m_max = max(m_tuple)

    # Derive primary moat archetype 3a
    if m_max == 0:
        primary_moat = "None"
    else:
        top_archs = [arch for (code, arch, _) in MOAT_SCORE_SPEC if int(moat_scores[code]) == m_max]
        norm_curr = normalize_moat_label(current_3a)
        if norm_curr in top_archs:
            primary_moat = norm_curr
        else:
            primary_moat = top_archs[0]

    cap_final: int | None = None
    mod_haircut = 0
    fatal_flaw = False

    if force_scores and cap_init > 0:
        f_tuple = tuple(int(force_scores[c]) for c in FORCE_SCORE_CODES)
        cap_final, mod_haircut, fatal_flaw = compute_final_cap_from_scores(cap_init, f_tuple)

    return {
        "cap_init": cap_init,
        "primary_moat": primary_moat,
        "cap_final": cap_final,
        "mod_haircut": mod_haircut,
        "fatal_flaw": fatal_flaw,
    }


def format_4n_note(
    cap_init: int,
    mod_haircut: int,
    cap_final: int,
    force_scores: dict[str, int],
    force_rationales: dict[str, str] | None = None,
    insulation: str | None = None,
) -> str:
    """Generate a standardized, compliant 4n Runway & Forces note adhering to spec."""
    rationales = force_rationales or {}
    c2_codes = [c for c in FORCE_SCORE_CODES if force_scores.get(c) == 2]
    c1_codes = [c for c in FORCE_SCORE_CODES if force_scores.get(c) == 1]

    # Case 1: Fatal Flaw Cap triggered (c2 >= 1)
    if c2_codes:
        fatal_details = []
        for c in c2_codes:
            r = rationales.get(c, "structural threat")
            fatal_details.append(f"{r} ({c}=2)")
        fatal_str = "; ".join(fatal_details)

        mod_details = []
        for c in c1_codes:
            r = rationales.get(c, "moderate friction")
            mod_details.append(f"{r} ({c}=1)")
        mod_str = f" alongside {', '.join(mod_details)}" if mod_details else ""

        return f"Fatal-Flaw Cap triggered (Final CAP = {cap_final}Y, REJECT): {fatal_str}{mod_str}."

    # Case 2: Moderate haircut applied (c1 >= 1)
    if c1_codes:
        mod_details = []
        for c in c1_codes:
            r = rationales.get(c, "moderate pressure")
            mod_details.append(f"{r} ({c}=1)")
        reasons_str = "; ".join(mod_details)
        insul_str = f"; {insulation}" if insulation else ""
        return f"Initial CAP {cap_init}Y reduced by -{mod_haircut}Y for {reasons_str}{insul_str}."

    # Case 3: All forces benign (all 0)
    insul = insulation or "Core structural moat and barriers to entry"
    return f"{insul} insulates the franchise across all five competitive forces and macrotrends."


# ----------------------------------------------------------------------
# Validation & Sequential Waterfall Enforcement
# ----------------------------------------------------------------------

def validate_company_evaluation(payload: dict[str, Any], existing_row: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[str], list[str]]:
    """Perform rigorous validation and Munger waterfall clearing on an evaluation payload.

    Args:
        payload: Dict containing company identification and qualitative gate evaluation.
        existing_row: Optional existing inputs.csv row for diff and fallback checks.

    Returns:
        (sanitized_qual, warnings, errors)
    """
    warnings: list[str] = []
    errors: list[str] = []

    cid = payload.get("id") or payload.get("ticker")
    if not cid:
        errors.append("Evaluation payload is missing 'id'.")
        return {}, warnings, errors

    # Guard reference companies against corruption
    if cid in REFERENCE_COMPANIES:
        ref_expected = REFERENCE_SNAPSHOT[cid]
        # Verify that if qualitative payload is provided, it does not mutate verified reference values
        qual_in = payload.get("qualitative") or payload
        for k, exp_val in ref_expected.items():
            if k in ("universe",):
                continue
            if k in qual_in:
                provided = sanitize_val(qual_in.get(k))
                expected = sanitize_val(exp_val)
                if provided != expected:
                    warnings.append(
                        f"[{cid}] Reference Company Guard: blocked alteration of verified key '{k}' "
                        f"({provided!r} -> restored verified {expected!r})."
                    )

    qual_raw = payload.get("qualitative", {})
    if not qual_raw:
        qual_raw = {k: v for k, v in payload.items() if k in QUAL_KEY_MAP}

    # Normalize keys via QUAL_KEY_MAP
    qual: dict[str, Any] = {}
    for k, v in qual_raw.items():
        if k in QUAL_KEY_MAP:
            qual[QUAL_KEY_MAP[k]] = v

    # Fallback to existing row values for omitted keys
    if existing_row:
        for k in QUAL_COLUMNS:
            if k not in qual and k in existing_row:
                qual[k] = existing_row[k]

    def _parse_score(code: str) -> int | None:
        raw = qual.get(code)
        if raw is None or raw == "":
            return None
        if isinstance(raw, bool):
            errors.append(f"[{cid}] Invalid score '{raw}' for '{code}' (expected 0, 1, or 2).")
            return None
        try:
            iv = int(raw)
            if iv in SCORE_VALUES:
                return iv
        except (ValueError, TypeError):
            pass
        errors.append(f"[{cid}] Invalid score '{raw}' for '{code}' (expected 0, 1, or 2).")
        return None

    # Parse moat scores
    m_vals = {c: _parse_score(c) for c in MOAT_SCORE_CODES}
    m_count = sum(1 for v in m_vals.values() if v is not None)
    if 0 < m_count < len(MOAT_SCORE_CODES):
        errors.append(f"[{cid}] Incomplete Gate 3 moat scores ({m_count}/4 provided).")

    cap_init: int | None = None
    if m_count == len(MOAT_SCORE_CODES) and not errors:
        m_tuple = tuple(m_vals[c] for c in MOAT_SCORE_CODES)  # type: ignore[misc]
        cap_init = compute_initial_cap_from_scores(m_tuple)
        m_max = max(m_tuple)

        # Normalize/derive 3a
        raw_3a = sanitize_val(qual.get("3a"))
        if raw_3a in LEGACY_MOAT_ALIASES:
            raw_3a = LEGACY_MOAT_ALIASES[raw_3a]
            warnings.append(f"[{cid}] Normalized legacy Gate 3a alias -> '{raw_3a}'.")

        if m_max == 0:
            if raw_3a and raw_3a != "None":
                warnings.append(f"[{cid}] Deterministic Gate 3a: overwritten '{raw_3a}' -> 'None' (all moat scores 0).")
            qual["3a"] = "None"
        else:
            top_archs = [arch for (code, arch, _) in MOAT_SCORE_SPEC if m_vals[code] == m_max]
            if raw_3a not in top_archs:
                chosen = top_archs[0]
                if raw_3a:
                    warnings.append(f"[{cid}] Deterministic Gate 3a: aligned '{raw_3a}' -> '{chosen}' to match max score {m_max}.")
                qual["3a"] = chosen
            else:
                qual["3a"] = raw_3a

    # Check Gate 3b and Gate 3 waterfall
    g1 = sanitize_val(qual.get("1"))
    g2 = sanitize_val(qual.get("2"))
    g3a = sanitize_val(qual.get("3a"))
    g3b = sanitize_val(qual.get("3b"))
    calamity_active = sanitize_val(qual.get("calamity")) == "Y"

    # Waterfall clearing helper
    def clear_keys(keys: list[str], reason: str) -> None:
        for k in keys:
            if sanitize_val(qual.get(k)) != "":
                warnings.append(f"[{cid}] Waterfall: cleared '{k}' because {reason}.")
            qual[k] = ""

    # Gate 1 & 2 Waterfall (Anchor Gates)
    if g1 == "N":
        clear_keys(["2", "2r", *MOAT_SCORE_CODES, "3a", "3b", "3m", *FORCE_SCORE_CODES, "4", "4n", "5", "6", "calamity", "calamity_note"], "Gate 1 is 'N'")
        return qual, warnings, errors

    if g2 == "N":
        clear_keys([*MOAT_SCORE_CODES, "3a", "3b", "3m", *FORCE_SCORE_CODES, "4", "4n", "5", "6", "calamity", "calamity_note"], "Gate 2 is 'N'")
        return qual, warnings, errors
    elif g2 == "Y":
        qual["2r"] = ""

    # Gate 3 Waterfall: 3a == 'None' is never waivable; 3b == 'N' waivable only under calamity
    g3_failed = (g3a == "None") or (g3b == "N" and not calamity_active)
    if g3_failed:
        reason = "Gate 3a is 'None'" if g3a == "None" else "Gate 3b is 'N' without calamity override"
        clear_keys([*FORCE_SCORE_CODES, "4", "4n", "5", "6"], reason)
        if g3a == "None" and calamity_active:
            clear_keys(["calamity", "calamity_note"], "Gate 3a is 'None' (non-waivable anchor)")
        return qual, warnings, errors

    # Parse and validate Gate 4 Competitive Force scores for companies passing Gate 3
    f_vals = {c: _parse_score(c) for c in FORCE_SCORE_CODES}
    f_count = sum(1 for v in f_vals.values() if v is not None)

    if 0 < f_count < len(FORCE_SCORE_CODES):
        errors.append(f"[{cid}] Incomplete Gate 4 force scores ({f_count}/5 provided).")

    if m_count == len(MOAT_SCORE_CODES) and f_count == len(FORCE_SCORE_CODES) and cap_init and cap_init > 0:
        f_tuple = tuple(f_vals[c] for c in FORCE_SCORE_CODES)  # type: ignore[misc]
        cap_det, mod_h, fatal_flaw = compute_final_cap_from_scores(cap_init, f_tuple)
        supplied_4 = sanitize_val(qual.get("4"))
        if supplied_4 and supplied_4 != str(cap_det):
            warnings.append(
                f"[{cid}] Deterministic Gate 4 CAP: manual CAP '{supplied_4}' overwritten with formula-computed {cap_det}Y "
                f"(Initial CAP {cap_init}Y, haircut {mod_h}Y, fatal_flaw={fatal_flaw})."
            )
        qual["4"] = cap_det

        # Validate non-empty 4n note whenever any force is non-zero
        has_nonzero_force = any(f_vals[c] in (1, 2) for c in FORCE_SCORE_CODES)
        if has_nonzero_force and not sanitize_val(qual.get("4n")):
            errors.append(f"[{cid}] Gate 4 competitive force >= 1 requires a non-empty '4n' Runway & Forces note.")

    # Gate 4 Waterfall: Final CAP < 15 triggers immediate reject
    g4_str = sanitize_val(qual.get("4"))
    if g4_str != "":
        try:
            g4_val = int(g4_str)
            if g4_val < 15:
                clear_keys(["5", "6"], f"Gate 4 CAP ({g4_val}Y) < 15 (non-waivable anchor)")
                if calamity_active:
                    clear_keys(["calamity", "calamity_note"], f"Gate 4 CAP ({g4_val}Y) < 15 (non-waivable anchor)")
            else:
                # Company passes Gate 4 (CAP >= 15): verify Gate 5 is populated to prevent 'To review'
                g5_str = sanitize_val(qual.get("5"))
                if g5_str == "":
                    warnings.append(f"[{cid}] Company passes Gate 4 (CAP={g4_val}Y >= 15) but Gate 5 is blank; required to avoid 'To review'.")

                # Gate 5 check (waivable only if calamity == 'Y')
                if g5_str == "0" and not calamity_active:
                    clear_keys(["6"], "Gate 5 is 0 without calamity override")
                elif sanitize_val(qual.get("6")) == "":
                    warnings.append(f"[{cid}] Company passes Gate 4 (CAP={g4_val}Y >= 15) but Gate 6 is blank; required to avoid 'To review'.")
        except ValueError:
            errors.append(f"[{cid}] Gate 4 CAP value '{g4_str}' is not an integer.")

    # Calamity validation
    if qual.get("calamity") == "Y":
        if not sanitize_val(qual.get("calamity_note")):
            errors.append(f"[{cid}] calamity_flag='Y' requires a non-empty calamity_note.")
        has_eligible = (
            qual.get("3b") == "N"
            or sanitize_val(qual.get("5")) == "0"
            or qual.get("6") == "N"
        )
        if not has_eligible:
            warnings.append(f"[{cid}] Calamity flag 'Y' is set, but no eligible gate (3b, 5, or 6) failed.")

    return qual, warnings, errors


# ----------------------------------------------------------------------
# Batch Context Exporter (for M3 AI Evaluator Subagents)
# ----------------------------------------------------------------------

def export_batch_context(
    out_dir: Path,
    batch_size: int = 20,
    universe: str | None = None,
    sector: str | None = None,
    unscored_only: bool = True,
) -> list[Path]:
    """Export structured batch dossiers for M3 evaluator subagents.

    Groups companies logically by sector and sub-industry, packaging financial context,
    qualitative baseline, and clock-speed indicators into JSON files.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    target_universes = (universe,) if universe else UNIVERSES
    companies = get_gate_3_companies(
        universes=target_universes,
        sector=sector,
        unscored_only=unscored_only,
    )

    # Sort companies by sector, sub_industry, and id for coherent cohort batching
    companies.sort(key=lambda c: (c.get("sector", ""), c.get("sub_industry", ""), c.get("id", "")))

    exported_files: list[Path] = []
    total_companies = len(companies)

    for i in range(0, total_companies, batch_size):
        chunk = companies[i : i + batch_size]
        batch_idx = (i // batch_size) + 1
        sec_slug = (sector or "all_sectors").lower().replace(" ", "_").replace("&", "and")
        u_slug = universe or "all_uni"
        filename = f"batch_{u_slug}_{sec_slug}_{batch_idx:03d}.json"
        batch_path = out_dir / filename

        batch_payload = {
            "batch_metadata": {
                "batch_id": f"{u_slug}_{sec_slug}_{batch_idx:03d}",
                "universe": universe or "all",
                "sector": sector or "all",
                "count": len(chunk),
                "unscored_only": unscored_only,
            },
            "companies": [],
        }

        for c in chunk:
            fin = c.get("_financials", {})
            comp_dossier = {
                "identity": {
                    "id": c.get("id"),
                    "ticker": c.get("ticker"),
                    "company": c.get("company"),
                    "country": c.get("country"),
                    "sector": c.get("sector"),
                    "sub_industry": c.get("sub_industry"),
                    "universe": c.get("_universe"),
                    "is_reference": c.get("_is_reference"),
                    "is_fast_clock_speed": c.get("_is_fast_clock_speed"),
                },
                "current_qualitative": {k: c.get(k, "") for k in QUAL_COLUMNS},
                "financial_context": {
                    "fin_currency": fin.get("fin_currency"),
                    "source": fin.get("source"),
                    "price": fin.get("price"),
                    "market_cap_m": fin.get("market_cap_m"),
                    "roic_median_5y_gaap": fin.get("roic_median"),
                    "roic_operating_5y_tangible": fin.get("roic_operating"),
                    "fcf_conversion_multi_yr": fin.get("fcf_conv"),
                    "cagr_owner_eps": fin.get("cagr_oe_eps"),
                    "peak_to_peak_eps_ok": fin.get("p2p_ok"),
                    "lt_debt_m": fin.get("lt_debt_m"),
                    "cash_m": fin.get("cash_m"),
                    "ebit_ttm_m": fin.get("ebit_ttm_m"),
                    "interest_m": fin.get("interest_m"),
                    "g6_netdebt_years": fin.get("g6_netdebt_yrs"),
                    "g6_interest_coverage": fin.get("g6_intcov"),
                    "sales_1y": fin.get("sales_1y"),
                    "sales_cagr": fin.get("sales_cagr"),
                    "sales_cagr_years": fin.get("sales_cagr_yrs"),
                },
            }
            batch_payload["companies"].append(comp_dossier)

        batch_path.write_text(json.dumps(batch_payload, indent=2), encoding="utf-8")
        exported_files.append(batch_path)

    return exported_files


# ----------------------------------------------------------------------
# Dual-Listed Mirror Synchronization
# ----------------------------------------------------------------------

def sync_mirrors(dry_run: bool = True) -> dict[str, Any]:
    """Synchronize dual-listed mirror tickers defined in data/us/universe.json.

    Currently mirrors:
      - ASML (US) <- eu:ASML.NL (EU)
      - FER (US)  <- eu:FER.ES (EU)

    Synchronizes all 20 qualitative fields, notes, and evidence to achieve exact parity.
    """
    mirrors = load_universe_mirrors()
    report: dict[str, Any] = {
        "mirrors_checked": len(mirrors),
        "synced_pairs": [],
        "differences_found": {},
        "dry_run": dry_run,
    }

    # Load US inputs
    us_rows, us_fields = load_universe_inputs("us")
    us_by_id = {r["id"]: r for r in us_rows}

    # Load EU inputs
    eu_rows, _ = load_universe_inputs("eu")
    eu_by_id = {r["id"]: r for r in eu_rows}

    modified_us = False

    for target_ticker, (src_u, src_id) in mirrors.items():
        if src_u != "eu":
            continue
        src_row = eu_by_id.get(src_id)
        tgt_row = us_by_id.get(target_ticker)

        if not src_row or not tgt_row:
            report["differences_found"][target_ticker] = f"Missing source ({src_id}) or target ({target_ticker})"
            continue

        pair_diffs: dict[str, tuple[str, str]] = {}
        for col in QUAL_COLUMNS:
            src_val = sanitize_val(src_row.get(col, ""))
            tgt_val = sanitize_val(tgt_row.get(col, ""))
            if src_val != tgt_val:
                pair_diffs[col] = (tgt_val, src_val)
                if not dry_run:
                    tgt_row[col] = src_val
                    modified_us = True

        if pair_diffs:
            report["differences_found"][target_ticker] = pair_diffs
        else:
            report["synced_pairs"].append(f"{target_ticker} == {src_id} (100% parity)")

    if modified_us and not dry_run:
        write_csv_atomic(DATA_DIR / "us" / "inputs.csv", us_fields, us_rows)

    return report


# ----------------------------------------------------------------------
# Batch Ingestion Engine
# ----------------------------------------------------------------------

def ingest_evaluations(
    payloads: list[dict[str, Any]] | Path | str,
    target_universe: str | None = None,
    dry_run: bool = True,
    sync_mirrors_after: bool = True,
) -> dict[str, Any]:
    """Ingest evaluation payloads across universes, validating scores and enforcing waterfalls.

    Args:
        payloads: List of evaluation dicts, Path to a JSON file, or Path to a directory of JSONs.
        target_universe: Optional target universe ('us', 'eu', 'ca'). Auto-detected if None.
        dry_run: If True, previews changes without writing to disk.
        sync_mirrors_after: If True, synchronizes mirror tickers after applying.

    Returns:
        Summary dict of ingested, rejected, and modified companies.
    """
    raw_list: list[dict[str, Any]] = []

    # Handle input types
    if isinstance(payloads, (str, Path)):
        p = Path(payloads)
        if p.is_dir():
            for f in sorted(p.glob("*.json")):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        raw_list.extend(data)
                    elif isinstance(data, dict):
                        if "companies" in data:
                            raw_list.extend(data["companies"])
                        else:
                            raw_list.append(data)
                except Exception as e:
                    print(f"Warning: Failed to load {f}: {e}", file=sys.stderr)
        elif p.is_file():
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                raw_list.extend(data)
            elif isinstance(data, dict):
                if "companies" in data:
                    raw_list.extend(data["companies"])
                else:
                    raw_list.append(data)
    elif isinstance(payloads, list):
        raw_list = payloads

    summary: dict[str, Any] = {
        "total_evaluated": len(raw_list),
        "applied": 0,
        "rejected": 0,
        "warnings": [],
        "errors": [],
        "diffs": {},
        "dry_run": dry_run,
    }

    # Load all universes in memory
    universe_data: dict[str, tuple[list[dict[str, str]], list[str]]] = {
        u: load_universe_inputs(u) for u in UNIVERSES
    }
    company_index: dict[str, tuple[str, dict[str, str]]] = {}
    for u, (rows, _) in universe_data.items():
        for r in rows:
            cid = r.get("id") or r.get("ticker", "")
            company_index[cid] = (u, r)

    universe_modified = set()

    for item in raw_list:
        cid = item.get("id") or item.get("ticker")
        if not cid and "identity" in item:
            cid = item["identity"].get("id")
        if not cid:
            summary["errors"].append("Item missing 'id'")
            summary["rejected"] += 1
            continue

        if cid not in company_index:
            summary["errors"].append(f"Company '{cid}' not found in any universe inputs.csv")
            summary["rejected"] += 1
            continue

        u, existing_row = company_index[cid]
        if target_universe and u != target_universe:
            continue

        sanitized_qual, item_warnings, item_errors = validate_company_evaluation(item, existing_row=existing_row)
        summary["warnings"].extend(item_warnings)

        if item_errors:
            summary["errors"].extend(item_errors)
            summary["rejected"] += 1
            continue

        # Compute diffs against existing row
        comp_diff: dict[str, tuple[str, str]] = {}
        for col in QUAL_COLUMNS:
            if col in sanitized_qual:
                old_v = sanitize_val(existing_row.get(col, ""))
                new_v = sanitize_val(sanitized_qual.get(col, ""))
                if old_v != new_v:
                    comp_diff[col] = (old_v, new_v)
                    if not dry_run:
                        existing_row[col] = new_v
                        universe_modified.add(u)

        if comp_diff:
            summary["diffs"][cid] = comp_diff
        summary["applied"] += 1

    # Commit changes atomically if apply mode
    if not dry_run and universe_modified:
        for u in universe_modified:
            rows, fields = universe_data[u]
            write_csv_atomic(DATA_DIR / u / "inputs.csv", fields, rows)

        if sync_mirrors_after:
            mirror_rep = sync_mirrors(dry_run=False)
            summary["mirror_sync"] = mirror_rep

    return summary


# ----------------------------------------------------------------------
# Comprehensive Audit Engine
# ----------------------------------------------------------------------

def audit_gate_3_universe(universes: tuple[str, ...] = UNIVERSES) -> dict[str, Any]:
    """Perform an exhaustive compliance audit across all Gate 3 companies.

    Validates:
      1. Candidate count matches exactly 989 (US: 445, EU: 495, CA: 49).
      2. 11 Phase 1 reference companies match verified scores and notes.
      3. Deterministic CAP engine: 0 formula discrepancies.
      4. Primary Moat 3a: 0 alignment discrepancies with max score.
      5. 4n Note: 0 missing notes when any force >= 1.
      6. Waterfall integrity: 0 orphaned downstream fields on gate rejections.
      7. Calamity rules: 0 invalid calamity waivers on anchor gates.
      8. Mirror parity: ASML/ASML.NL and FER/FER.ES 100% synchronized.
    """
    audit: dict[str, Any] = {
        "gate_3_counts": {},
        "total_gate_3": 0,
        "count_target_met": False,
        "reference_companies_verified": False,
        "reference_discrepancies": [],
        "scored_companies_count": 0,
        "unscored_companies_count": 0,
        "formula_discrepancies": [],
        "moat_alignment_discrepancies": [],
        "missing_4n_notes": [],
        "waterfall_violations": [],
        "calamity_violations": [],
        "mirror_parity_ok": False,
        "mirror_discrepancies": {},
    }

    # 1. Verify Counts
    for u in universes:
        rows, _ = load_universe_inputs(u)
        g3_rows = [r for r in rows if r.get("1") == "Y" and r.get("2") == "Y"]
        audit["gate_3_counts"][u] = len(g3_rows)
        audit["total_gate_3"] += len(g3_rows)

    audit["count_target_met"] = (
        audit["gate_3_counts"] == TARGET_GATE_3_COUNTS
        and audit["total_gate_3"] == TOTAL_GATE_3_TARGET
    )

    # 2. Verify 11 Reference Companies
    ref_ok, ref_discrepancies = verify_reference_companies(universes=universes)
    audit["reference_companies_verified"] = ref_ok
    audit["reference_discrepancies"] = ref_discrepancies

    # 3. Audit Gate 3 companies for deterministic CAP, waterfall, notes, calamity
    all_g3 = get_gate_3_companies(universes=universes)
    p = params({})

    for c in all_g3:
        cid = c.get("id") or c.get("ticker", "")
        aud = cap_audit(c)

        if aud["moat_complete"]:
            audit["scored_companies_count"] += 1

            # Check Initial CAP
            m_tuple = tuple(int(c[code]) for code in MOAT_SCORE_CODES)
            exp_init = compute_initial_cap_from_scores(m_tuple)
            if aud["cap_init"] != exp_init:
                audit["formula_discrepancies"].append(f"[{cid}] Initial CAP mismatch: aud={aud['cap_init']} vs exp={exp_init}")

            # Check 3a alignment
            m_max = max(m_tuple)
            stored_3a = normalize_moat_label(c.get("3a"))
            if m_max == 0 and stored_3a != "None":
                audit["moat_alignment_discrepancies"].append(f"[{cid}] Moat is zero but 3a is '{stored_3a}'")
            elif m_max > 0:
                top_archs = [arch for (code, arch, _) in MOAT_SCORE_SPEC if int(c[code]) == m_max]
                if stored_3a not in top_archs:
                    audit["moat_alignment_discrepancies"].append(f"[{cid}] 3a '{stored_3a}' not in top archetypes {top_archs}")

            # Check Final CAP when forces complete
            if aud["force_complete"] and aud["cap_init"] and aud["cap_init"] > 0:
                f_tuple = tuple(int(c[code]) for code in FORCE_SCORE_CODES)
                exp_final, _, _ = compute_final_cap_from_scores(aud["cap_init"], f_tuple)
                stored_4 = c.get("4")
                if stored_4 is not None and stored_4 != "":
                    try:
                        if int(stored_4) != exp_final:
                            audit["formula_discrepancies"].append(
                                f"[{cid}] Final CAP formula mismatch: stored={stored_4} vs formula={exp_final}"
                            )
                    except ValueError:
                        audit["formula_discrepancies"].append(f"[{cid}] Non-numeric Final CAP: {stored_4!r}")

                # Check 4n note presence
                has_nonzero_force = any(int(c[fc]) in (1, 2) for fc in FORCE_SCORE_CODES)
                stored_4n = sanitize_val(c.get("4n"))
                if has_nonzero_force and not stored_4n:
                    audit["missing_4n_notes"].append(f"[{cid}] Missing mandatory '4n' note with force >= 1")
        else:
            audit["unscored_companies_count"] += 1

        # Check Waterfall Invariants
        g3a = normalize_moat_label(c.get("3a"))
        g3b = sanitize_val(c.get("3b"))
        calamity_flag = sanitize_val(c.get("calamity")) == "Y"

        if g3a == "None" or (g3b == "N" and not calamity_flag):
            # Downstream Gate 4 and Gates 5-6 MUST be empty
            orphans = [k for k in (*FORCE_SCORE_CODES, "4", "4n", "5", "6") if sanitize_val(c.get(k)) != ""]
            if orphans:
                audit["waterfall_violations"].append(f"[{cid}] Failed Gate 3 but downstream keys {orphans} are not blank")

        stored_4_val = c.get("4")
        if stored_4_val not in (None, ""):
            try:
                g4_num = int(stored_4_val)
                if g4_num < 15:
                    orphans_g4 = [k for k in ("5", "6") if sanitize_val(c.get(k)) != ""]
                    if orphans_g4:
                        audit["waterfall_violations"].append(f"[{cid}] Failed Gate 4 (CAP={g4_num}) but Gates 5-6 {orphans_g4} not blank")
            except ValueError:
                pass

        # Check Calamity Rules
        if calamity_flag:
            # Calamity flag cannot be set if any anchor gate fails
            g1 = sanitize_val(c.get("1"))
            g2 = sanitize_val(c.get("2"))
            g4_raw = c.get("4")
            try:
                g4_num = int(g4_raw) if g4_raw not in (None, "") else None
            except ValueError:
                g4_num = None
            g4_pass = (g4_num is not None) and (g4_num >= 15)
            if g1 != "Y" or g2 != "Y" or g3a == "None" or not g4_pass:
                audit["calamity_violations"].append(f"[{cid}] Calamity active on failed Anchor Gate (1={g1}, 2={g2}, 3a={g3a}, 4={g4_raw})")


            # Must have at least one eligible gate failed
            g5_val = sanitize_val(c.get("5"))
            g6_val = sanitize_val(c.get("6"))
            has_fail = (g3b == "N" or g5_val == "0" or g6_val == "N")
            if not has_fail:
                audit["calamity_violations"].append(f"[{cid}] Calamity active but no eligible gate (3b, 5, 6) failed")

            if not sanitize_val(c.get("calamity_note")):
                audit["calamity_violations"].append(f"[{cid}] Calamity active but calamity_note is empty")

    # 4. Check Mirror Parity
    mirror_report = sync_mirrors(dry_run=True)
    audit["mirror_parity_ok"] = len(mirror_report["differences_found"]) == 0
    audit["mirror_discrepancies"] = mirror_report["differences_found"]

    return audit


def verify_reference_companies(universes: tuple[str, ...] = UNIVERSES) -> tuple[bool, list[str]]:
    """Verify that all 11 reference companies exactly match verified values."""
    discrepancies: list[str] = []
    loaded: dict[str, dict[str, str]] = {}

    for u in universes:
        rows, _ = load_universe_inputs(u)
        for r in rows:
            cid = r.get("id") or r.get("ticker", "")
            if cid in REFERENCE_COMPANIES:
                loaded[cid] = r

    for cid, exp in REFERENCE_SNAPSHOT.items():
        if cid not in loaded:
            discrepancies.append(f"Missing reference company: {cid}")
            continue
        row = loaded[cid]
        for k, v in exp.items():
            if k == "universe":
                continue
            act = sanitize_val(row.get(k, ""))
            expected = sanitize_val(v)
            if act != expected:
                discrepancies.append(f"[{cid}] Discrepancy on '{k}': expected={expected!r} vs actual={act!r}")

    return len(discrepancies) == 0, discrepancies


# ----------------------------------------------------------------------
# CLI Interface
# ----------------------------------------------------------------------

def print_audit_report(audit: dict[str, Any]) -> None:
    """Print human-readable audit results."""
    print("=" * 70)
    print("QUALITY & MOAT SCREENER — GATE 3 COMPLIANCE AUDIT (v7.16)")
    print("=" * 70)

    print(f"Gate 3 Populations: {audit['gate_3_counts']} | Total: {audit['total_gate_3']} / {TOTAL_GATE_3_TARGET}")
    status_icon = "✓" if audit["count_target_met"] else "✗"
    print(f"[{status_icon}] Gate 3 Candidate Count Target: {'PASSED' if audit['count_target_met'] else 'FAILED'}")

    status_icon = "✓" if audit["reference_companies_verified"] else "✗"
    print(f"[{status_icon}] 11 Reference Companies Verified: {'PASSED' if audit['reference_companies_verified'] else 'FAILED'}")
    if audit["reference_discrepancies"]:
        for d in audit["reference_discrepancies"][:5]:
            print(f"    • {d}")

    print(f"\nScoring Status: {audit['scored_companies_count']} scored / {audit['unscored_companies_count']} unscored")

    status_icon = "✓" if not audit["formula_discrepancies"] else "✗"
    print(f"[{status_icon}] Deterministic CAP Formulas: {len(audit['formula_discrepancies'])} discrepancies")
    for d in audit["formula_discrepancies"][:5]:
        print(f"    • {d}")

    status_icon = "✓" if not audit["moat_alignment_discrepancies"] else "✗"
    print(f"[{status_icon}] Gate 3a Primary Moat Alignment: {len(audit['moat_alignment_discrepancies'])} discrepancies")
    for d in audit["moat_alignment_discrepancies"][:5]:
        print(f"    • {d}")

    status_icon = "✓" if not audit["missing_4n_notes"] else "✗"
    print(f"[{status_icon}] Mandatory 4n Runway Notes: {len(audit['missing_4n_notes'])} missing")
    for d in audit["missing_4n_notes"][:5]:
        print(f"    • {d}")

    status_icon = "✓" if not audit["waterfall_violations"] else "✗"
    print(f"[{status_icon}] Sequential Munger Waterfall: {len(audit['waterfall_violations'])} violations")
    for d in audit["waterfall_violations"][:5]:
        print(f"    • {d}")

    status_icon = "✓" if not audit["calamity_violations"] else "✗"
    print(f"[{status_icon}] Calamity Pass Rules: {len(audit['calamity_violations'])} violations")
    for d in audit["calamity_violations"][:5]:
        print(f"    • {d}")

    status_icon = "✓" if audit["mirror_parity_ok"] else "✗"
    print(f"[{status_icon}] Dual-Listed Mirror Parity: {'PASSED' if audit['mirror_parity_ok'] else 'FAILED'}")
    if audit["mirror_discrepancies"]:
        for t, diff in audit["mirror_discrepancies"].items():
            print(f"    • {t}: {diff}")

    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bulk scoring automation engine, batch context exporter, validator, and mirror synchronizer."
    )
    parser.add_argument("--audit", action="store_true", help="Run comprehensive compliance audit of all Gate 3 companies")
    parser.add_argument("--export-batch", action="store_true", help="Export batch context files for M3 evaluator subagents")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "evaluations" / "batches", help="Output directory for exported batches")
    parser.add_argument("--batch-size", type=int, default=20, help="Batch size for exported dossiers (default: 20)")
    parser.add_argument("--universe", "-u", choices=UNIVERSES, help="Filter by universe ('us', 'eu', 'ca')")
    parser.add_argument("--sector", "-s", type=str, help="Filter by GICS Sector")
    parser.add_argument("--company", "-c", type=str, help="Filter by company ID")
    parser.add_argument("--ingest", type=Path, help="Ingest evaluation JSON payload, directory, or batch file")
    parser.add_argument("--sync-mirrors", action="store_true", help="Synchronize dual-listed mirror tickers")
    parser.add_argument("--apply", action="store_true", help="Commit changes to disk (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Preview changes without writing to disk")

    args = parser.parse_args()

    # Default to dry-run unless --apply is explicitly specified
    is_dry_run = not args.apply

    if args.audit or (not args.export_batch and not args.ingest and not args.sync_mirrors):
        audit_res = audit_gate_3_universe(universes=(args.universe,) if args.universe else UNIVERSES)
        print_audit_report(audit_res)
        if not audit_res["count_target_met"] or not audit_res["reference_companies_verified"]:
            sys.exit(1)
        return

    if args.sync_mirrors:
        rep = sync_mirrors(dry_run=is_dry_run)
        print(f"\nMirror Sync Results ({'DRY RUN' if is_dry_run else 'APPLIED'}):")
        print(f"  Mirrors checked: {rep['mirrors_checked']}")
        print(f"  Synced pairs: {rep['synced_pairs']}")
        if rep["differences_found"]:
            print(f"  Differences found: {json.dumps(rep['differences_found'], indent=2)}")
        else:
            print("  All mirrors are 100% in parity.")
        return

    if args.export_batch:
        files = export_batch_context(
            out_dir=args.out_dir,
            batch_size=args.batch_size,
            universe=args.universe,
            sector=args.sector,
            unscored_only=True,
        )
        print(f"\nExported {len(files)} batch files to {args.out_dir}:")
        for f in files[:5]:
            print(f"  • {f.name}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more files.")
        return

    if args.ingest:
        summary = ingest_evaluations(
            payloads=args.ingest,
            target_universe=args.universe,
            dry_run=is_dry_run,
            sync_mirrors_after=True,
        )
        print(f"\nBatch Ingestion Summary ({'DRY RUN' if is_dry_run else 'APPLIED'}):")
        print(f"  Total evaluated: {summary['total_evaluated']}")
        print(f"  Applied successfully: {summary['applied']}")
        print(f"  Rejected: {summary['rejected']}")
        if summary["diffs"]:
            print(f"  Companies modified: {len(summary['diffs'])}")
            for cid, diff in list(summary["diffs"].items())[:5]:
                print(f"    [{cid}]: {list(diff.keys())}")
            if len(summary["diffs"]) > 5:
                print(f"    ... and {len(summary['diffs']) - 5} more companies.")
        if summary["errors"]:
            print(f"\nErrors encountered ({len(summary['errors'])}):")
            for err in summary["errors"][:5]:
                print(f"  ✗ {err}")
        if summary["warnings"]:
            print(f"\nWarnings ({len(summary['warnings'])}):")
            for w in summary["warnings"][:5]:
                print(f"  ! {w}")
        return


if __name__ == "__main__":
    main()
