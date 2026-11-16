"""Apply an independent agent's company evaluation JSON payload to data/<universe>/.

Validates the evaluation against the framework rules, enforces the sequential
waterfall (clearing downstream fields after a failed gate), and updates:
- data/<universe>/inputs.csv (Qualitative gates 1-6, notes, evidence)
Quantitative inputs come only from the statements (v7.6): a `quantitative_overrides` block is ignored with a warning.

Usage:
    python3 screener/apply_evaluation.py --input result.json
    python3 screener/apply_evaluation.py --input result.json --dry-run
    cat result.json | python3 screener/apply_evaluation.py -
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.config import (  # noqa: E402
    CAP_VALUES,
    FORCE_SCORE_CODES,
    LEGACY_MOAT_ALIASES,
    MOAT_SCORE_CODES,
    MOAT_SCORE_SPEC,
    MOAT_TYPES,
    SCORE_VALUES,
)
from screener.gates import (  # noqa: E402
    compute_final_cap_from_scores,
    compute_initial_cap_from_scores,
)

DATA_DIR = ROOT / "data"

QUAL_KEY_MAP = {
    "gate_1": "1",
    "gate_2": "2",
    "gate_2_reason": "2r",
    "gate_3_moat_toll_booth": "3_tb",
    "gate_3_moat_infrastructure": "3_ia",
    "gate_3_moat_scale_shared": "3_se",
    "gate_3_moat_rd": "3_rd",
    "gate_3a_moat_archetype": "3a",
    "gate_3b_pricing_and_proof": "3b",
    "gate_3m_moat_note": "3m",
    "gate_4_force_entrants": "4_ent",
    "gate_4_force_rivalry": "4_riv",
    "gate_4_force_buyers": "4_buy",
    "gate_4_force_suppliers": "4_sup",
    "gate_4_force_substitution": "4_sub",
    "gate_4_runway_cap": "4",
    "gate_4n_runway_note": "4n",
    "gate_5_management_score": "5",
    "gate_6_cash_and_balance_sheet": "6",
    "calamity_flag": "calamity",
    "calamity": "calamity",
    "calamity_note": "calamity_note",
    "note": "note",
    "evidence": "evidence",
    "1": "1",
    "2": "2",
    "2r": "2r",
    "3_tb": "3_tb",
    "3_ia": "3_ia",
    "3_se": "3_se",
    "3_rd": "3_rd",
    "3a": "3a",
    "3b": "3b",
    "3m": "3m",
    "4_ent": "4_ent",
    "4_riv": "4_riv",
    "4_buy": "4_buy",
    "4_sup": "4_sup",
    "4_sub": "4_sub",
    "4": "4",
    "4n": "4n",
    "5": "5",
    "6": "6",
}



def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def find_company_universe(company_id: str) -> tuple[str, Path] | None:
    for u_dir in sorted(DATA_DIR.iterdir()):
        if u_dir.is_dir() and (u_dir / "inputs.csv").exists():
            rows = read_csv(u_dir / "inputs.csv")
            for r in rows:
                if r.get("id") == company_id:
                    return u_dir.name, u_dir
    return None


def sanitize_val(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()



def validate_and_waterfall(eval_data: dict) -> tuple[dict, dict, list[str]]:
    warnings = []
    qual_raw = eval_data.get("qualitative", {})
    if not qual_raw:
        # Check top-level
        qual_raw = {k: v for k, v in eval_data.items() if k in QUAL_KEY_MAP}

    # Normalize qualitative keys
    qual = {}
    for k, v in qual_raw.items():
        if k in QUAL_KEY_MAP:
            target_key = QUAL_KEY_MAP[k]
            qual[target_key] = v

    # Normalize calamity fields only when the payload speaks about them (a full qualitative evaluation, or explicit
    # calamity keys) — a sandbox payload carrying only gate_4_runway_cap must not wipe an existing calamity flag.
    if qual and ("calamity" in qual or "calamity_note" in qual or "1" in qual):
        calamity = sanitize_val(qual.get("calamity"))
        if calamity not in ("", "Y"):
            warnings.append(f"Invalid calamity_flag '{calamity}' (expected 'Y' or null); cleared.")
            calamity = ""
        qual["calamity"] = calamity
        if calamity != "Y":
            if sanitize_val(qual.get("calamity_note")):
                warnings.append("Waterfall: cleared 'calamity_note' because calamity_flag is not 'Y'")
            qual["calamity_note"] = ""

    if qual:
        def clear_calamity(reason: str):
            if qual.get("calamity") or sanitize_val(qual.get("calamity_note")):
                warnings.append(f"Waterfall: cleared 'calamity'/'calamity_note' because {reason} (non-waivable)")
            qual["calamity"] = ""
            qual["calamity_note"] = ""

        def _parse_subscore(code: str) -> int | None:
            raw = qual.get(code)
            if raw is None or raw == "":
                return None
            if isinstance(raw, bool):
                warnings.append(f"Invalid score '{raw}' for '{code}' (expected 0, 1, or 2); cleared.")
                qual[code] = ""
                return None
            try:
                iv = int(raw)
                if iv == float(raw) and iv in SCORE_VALUES:
                    qual[code] = iv
                    return iv
            except (ValueError, TypeError):
                pass
            warnings.append(f"Invalid score '{raw}' for '{code}' (expected 0, 1, or 2); cleared.")
            qual[code] = ""
            return None

        # Normalize legacy 3a aliases if supplied
        raw_3a = sanitize_val(qual.get("3a"))
        if raw_3a in LEGACY_MOAT_ALIASES:
            mapped_3a = LEGACY_MOAT_ALIASES[raw_3a]
            warnings.append(f"Normalized legacy Gate 3a label '{raw_3a}' -> '{mapped_3a}'")
            qual["3a"] = mapped_3a

        # Parse Gate 3 Moat & Gate 4 Force sub-scores when present
        m_vals = {c: _parse_subscore(c) for c in MOAT_SCORE_CODES}
        f_vals = {c: _parse_subscore(c) for c in FORCE_SCORE_CODES}
        m_count = sum(1 for v in m_vals.values() if v is not None)
        f_count = sum(1 for v in f_vals.values() if v is not None)

        if 0 < m_count < len(MOAT_SCORE_CODES):
            warnings.append(f"Incomplete Gate 3 moat sub-scores ({m_count}/4 provided); all 4 (3_tb, 3_ia, 3_se, 3_rd) are required.")
        if 0 < f_count < len(FORCE_SCORE_CODES):
            warnings.append(f"Incomplete Gate 4 force sub-scores ({f_count}/5 provided); all 5 (4_ent..4_sub) are required.")

        cap_init_det: int | None = None
        if m_count == len(MOAT_SCORE_CODES):
            m_tuple = tuple(m_vals[c] for c in MOAT_SCORE_CODES)  # type: ignore[misc]
            cap_init_det = compute_initial_cap_from_scores(m_tuple)
            m_max = max(m_tuple)
            cur_3a = sanitize_val(qual.get("3a"))
            if m_max == 0:
                if cur_3a and cur_3a != "None":
                    warnings.append(f"Deterministic Gate 3a: overwrote '{cur_3a}' with 'None' because all 4 moat scores are 0.")
                qual["3a"] = "None"
            else:
                top_archs = [arch for (code, arch, _) in MOAT_SCORE_SPEC if m_vals[code] == m_max]
                if cur_3a not in top_archs:
                    chosen = top_archs[0]
                    if cur_3a:
                        warnings.append(f"Deterministic Gate 3a: aligned '{cur_3a}' -> '{chosen}' to match max moat score ({m_max}).")
                    qual["3a"] = chosen

        if m_count == len(MOAT_SCORE_CODES) and f_count == len(FORCE_SCORE_CODES) and cap_init_det and cap_init_det > 0:
            f_tuple = tuple(f_vals[c] for c in FORCE_SCORE_CODES)  # type: ignore[misc]
            cap_det, _, _ = compute_final_cap_from_scores(cap_init_det, f_tuple)
            supplied_4 = sanitize_val(qual.get("4"))
            if supplied_4 and supplied_4 != str(cap_det):
                warnings.append(
                    f"Deterministic Gate 4 CAP: overwrote manual CAP '{supplied_4}' with formula-computed {cap_det}Y "
                    f"(Initial CAP {cap_init_det}Y adjusted by Gate 4 Force scores)."
                )
            qual["4"] = cap_det

        # Validate standalone/legacy CAP value if present
        if sanitize_val(qual.get("4")) != "":
            try:
                g4_chk = int(qual["4"])
                if g4_chk not in CAP_VALUES:
                    warnings.append(f"Invalid Gate 4 CAP '{qual['4']}' (allowed: {CAP_VALUES}); cleared.")
                    qual["4"] = ""
            except (ValueError, TypeError):
                warnings.append(f"Invalid Gate 4 CAP '{qual['4']}' (allowed: {CAP_VALUES}); cleared.")
                qual["4"] = ""

        # Enforce waterfall logic
        g1 = qual.get("1")
        g2 = qual.get("2")
        g3a = qual.get("3a")
        g3b = qual.get("3b")
        g4 = qual.get("4")
        g5 = qual.get("5")

        g3_all_keys = [*MOAT_SCORE_CODES, "3a", "3b", "3m"]
        g4_all_keys = [*FORCE_SCORE_CODES, "4", "4n"]

        # Gate 1 check (never waivable)
        if g1 == "N":
            for k in ["2", "2r", *g3_all_keys, *g4_all_keys, "5", "6"]:
                if sanitize_val(qual.get(k)) != "":
                    warnings.append(f"Waterfall: scrubbed '{k}' because Gate 1 is 'N'")
                qual[k] = ""
            clear_calamity("Gate 1 is 'N'")
        elif g1 == "Y":
            # Gate 2 check (never waivable)
            if g2 == "N":
                for k in [*g3_all_keys, *g4_all_keys, "5", "6"]:
                    if sanitize_val(qual.get(k)) != "":
                        warnings.append(f"Waterfall: scrubbed '{k}' because Gate 2 is 'N'")
                    qual[k] = ""
                clear_calamity("Gate 2 is 'N'")
            elif g2 == "Y":
                qual["2r"] = ""
                cal_active = qual.get("calamity") == "Y"
                # Gate 3 check: 3a=='None' is never waivable; 3b=='N' is waivable only if calamity=='Y'
                if g3a == "None" or (g3b == "N" and not cal_active):
                    reason = "Gate 3a is 'None'" if g3a == "None" else "Gate 3b failed without calamity override"
                    for k in [*g4_all_keys, "5", "6"]:
                        if sanitize_val(qual.get(k)) != "":
                            warnings.append(f"Waterfall: scrubbed '{k}' because {reason}")
                        qual[k] = ""
                    clear_calamity(reason)
                elif g3a in MOAT_TYPES and g3a != "None" and (g3b == "Y" or (g3b == "N" and cal_active)):
                    # Gate 4 check (never waivable)
                    if g4 is not None and g4 != "":
                        try:
                            g4_num = int(g4)
                            if g4_num < 15:
                                for k in ["5", "6"]:
                                    if sanitize_val(qual.get(k)) != "":
                                        warnings.append(f"Waterfall: scrubbed '{k}' because Gate 4 (CAP={g4_num}) < 15")
                                    qual[k] = ""
                                clear_calamity(f"Gate 4 (CAP={g4_num}) < 15")
                            else:
                                # Gate 5 check (waivable if calamity=='Y')
                                if g5 is not None and g5 != "":
                                    g5_num = int(g5)
                                    if g5_num == 0 and not cal_active:
                                        if qual.get("6"):
                                            warnings.append("Waterfall: scrubbed Gate 6 because Gate 5 is 0 without calamity override")
                                        qual["6"] = ""
                        except ValueError:
                            pass

        if qual.get("calamity") == "Y":
            has_eligible_fail = (
                qual.get("3b") == "N"
                or sanitize_val(qual.get("5")) == "0"
                or qual.get("6") == "N"
            )
            if not has_eligible_fail:
                warnings.append("Calamity flag 'Y' is set, but no eligible gate (3b, 5, or 6) failed.")

    # v7.6: no analyst overrides — quantitative inputs come only from the statements
    if eval_data.get("quantitative_overrides"):
        warnings.append("quantitative_overrides ignored: the valuation uses statement data only (no analyst overrides).")

    return qual, {}, warnings


def apply_evaluation(payload: dict, universe: str | None = None, dry_run: bool = False) -> bool:
    company_id = payload.get("id") or payload.get("ticker")
    if not company_id:
        print("Error: Missing 'id' in evaluation payload.", file=sys.stderr)
        return False

    # Locate universe directory
    if universe:
        u_dir = DATA_DIR / universe
        if not u_dir.exists():
            print(f"Error: Specified universe directory not found: {u_dir}", file=sys.stderr)
            return False
    else:
        found = find_company_universe(company_id)
        if not found:
            print(f"Error: Company '{company_id}' not found in any universe in data/.", file=sys.stderr)
            return False
        universe, u_dir = found

    inputs_path = u_dir / "inputs.csv"

    inputs_rows = read_csv(inputs_path)
    if not inputs_rows:
        print(f"Error: Empty or missing {inputs_path}", file=sys.stderr)
        return False
    input_fieldnames = list(inputs_rows[0].keys())

    # Find company in inputs.csv
    input_row = None
    for r in inputs_rows:
        if r.get("id") == company_id:
            input_row = r
            break

    if input_row is None:
        print(f"Error: Company '{company_id}' not found in {inputs_path}", file=sys.stderr)
        return False

    qual, _, warnings = validate_and_waterfall(payload)
    for w in warnings:
        print(f"[{company_id}] {w}")

    if qual.get("calamity") == "Y" and not sanitize_val(qual.get("calamity_note")):
        print(f"Error: [{company_id}] calamity_flag='Y' requires a non-empty calamity_note.", file=sys.stderr)
        return False

    has_nonzero_force = any(
        sanitize_val(qual.get(fc)) in ("1", "2") for fc in FORCE_SCORE_CODES
    )
    if has_nonzero_force and not sanitize_val(qual.get("4n")):
        print(
            f"Error: [{company_id}] non-zero Gate 4 competitive force score(s) require a non-empty gate_4n_runway_note ('4n').",
            file=sys.stderr,
        )
        return False

    # Build input diff
    input_diff = {}
    for k, new_v in qual.items():
        if k in input_fieldnames:
            old_v = input_row.get(k, "")
            sanitized_new = sanitize_val(new_v)
            if old_v != sanitized_new:
                input_diff[k] = (old_v, sanitized_new)

    # Print summary
    print(f"\nEvaluation summary for {company_id} ({universe.upper()}):")
    verdict = payload.get("evaluation_metadata", {}).get("verdict")
    if verdict:
        print(f"Verdict: {verdict}")

    if not input_diff:
        print("No changes required. Company data is already up-to-date.")
        return True

    if input_diff:
        print("\nQualitative Updates (inputs.csv):")
        for k, (old_v, new_v) in input_diff.items():
            print(f"  [{k}] {repr(old_v)} -> {repr(new_v)}")

    if dry_run:
        print("\n[DRY RUN] No files written.")
        return True

    # Apply qualitative changes if any
    if input_diff:
        for k, (_, new_v) in input_diff.items():
            input_row[k] = new_v
        write_csv(inputs_path, input_fieldnames, inputs_rows)
        print(f"\nSuccessfully updated {inputs_path}")

    # Apply financial changes if any
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", "-i", help="Path to JSON evaluation file (or '-' for stdin)")
    parser.add_argument("--universe", "-u", choices=["us", "eu", "ca"], help="Target universe (auto-detected if omitted)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--rebuild", action="store_true", help="Run build.py after applying changes")
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    if args.input == "-":
        payload = json.load(sys.stdin)
    else:
        p = Path(args.input)
        if not p.exists():
            sys.exit(f"File not found: {p}")
        with p.open(encoding="utf-8") as f:
            payload = json.load(f)

    success = apply_evaluation(payload, universe=args.universe, dry_run=args.dry_run)
    if not success:
        sys.exit(1)
    if args.rebuild and not args.dry_run:
        print("\nRebuilding HTML cockpit...")
        cmd = ["python3", str(ROOT / "build.py")]
        if args.universe:
            cmd.append(args.universe)
        subprocess.run(cmd)


if __name__ == "__main__":
    main()
