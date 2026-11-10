"""Apply an independent agent's company evaluation JSON payload to data/<universe>/.

Validates the evaluation against the v6.23 framework rules, enforces the sequential
waterfall (clearing downstream fields after a failed gate), and updates:
- data/<universe>/inputs.csv (Qualitative gates 1-6, notes, evidence)
- data/<universe>/financials.csv (Quantitative overrides: peak_eps_est, g_est, g_implied, roic_est, fin_note)

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
DATA_DIR = ROOT / "data"

MOAT_TYPES = [
    "Toll booth / Switching costs",
    "Scale economies shared",
    "Irreplaceable infrastructure",
    "R&D super-thinkers / Intangibles",
    "None",
]
CAP_VALUES = [0, 5, 10, 15, 20, 30]
SCORE_VALUES = [0, 1, 2]

QUAL_KEY_MAP = {
    "gate_1": "1",
    "gate_2": "2",
    "gate_2_reason": "2r",
    "gate_3a_moat_archetype": "3a",
    "gate_3b_pricing_and_proof": "3b",
    "gate_3m_moat_note": "3m",
    "gate_4_runway_cap": "4",
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
    "3a": "3a",
    "3b": "3b",
    "3m": "3m",
    "4": "4",
    "5": "5",
    "6": "6",
}

FIN_KEY_MAP = {
    "peak_eps_est": "peak_eps_est",
    "g_est": "g_est",
    "g_implied": "g_implied",
    "g_exp": "g_implied",
    "roic_est": "roic_est",
    "fin_note": "fin_note",
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

    if qual:
        # Normalize calamity fields
        calamity = sanitize_val(qual.get("calamity"))
        if calamity not in ("", "Y"):
            warnings.append(f"Invalid calamity_flag '{calamity}' (expected 'Y' or null); cleared.")
            calamity = ""
        qual["calamity"] = calamity
        if calamity != "Y":
            if sanitize_val(qual.get("calamity_note")):
                warnings.append("Waterfall: cleared 'calamity_note' because calamity_flag is not 'Y'")
            qual["calamity_note"] = ""

        def clear_calamity(reason: str):
            if qual.get("calamity") or sanitize_val(qual.get("calamity_note")):
                warnings.append(f"Waterfall: cleared 'calamity'/'calamity_note' because {reason} (non-waivable)")
            qual["calamity"] = ""
            qual["calamity_note"] = ""

        # Enforce waterfall logic
        g1 = qual.get("1")
        g2 = qual.get("2")
        g3a = qual.get("3a")
        g3b = qual.get("3b")
        g4 = qual.get("4")
        g5 = qual.get("5")

        # Gate 1 check (never waivable)
        if g1 == "N":
            for k in ["2", "2r", "3a", "3b", "3m", "4", "5", "6"]:
                if qual.get(k):
                    warnings.append(f"Waterfall: scrubbed '{k}' because Gate 1 is 'N'")
                qual[k] = ""
            clear_calamity("Gate 1 is 'N'")
        elif g1 == "Y":
            # Gate 2 check (never waivable)
            if g2 == "N":
                for k in ["3a", "3b", "3m", "4", "5", "6"]:
                    if qual.get(k):
                        warnings.append(f"Waterfall: scrubbed '{k}' because Gate 2 is 'N'")
                    qual[k] = ""
                clear_calamity("Gate 2 is 'N'")
            elif g2 == "Y":
                qual["2r"] = ""
                cal_active = qual.get("calamity") == "Y"
                # Gate 3 check: 3a=='None' is never waivable; 3b=='N' is waivable only if calamity=='Y'
                if g3a == "None" or (g3b == "N" and not cal_active):
                    reason = "Gate 3a is 'None'" if g3a == "None" else "Gate 3b failed without calamity override"
                    for k in ["4", "5", "6"]:
                        if qual.get(k):
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
                                    if qual.get(k):
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

    # Normalize financials
    fin_raw = eval_data.get("quantitative_overrides", {})
    fin = {}
    for k, v in fin_raw.items():
        if k in FIN_KEY_MAP:
            fin[FIN_KEY_MAP[k]] = sanitize_val(v)

    return qual, fin, warnings


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
    fin_path = u_dir / "financials.csv"

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

    qual, fin, warnings = validate_and_waterfall(payload)
    for w in warnings:
        print(f"[{company_id}] {w}")

    if qual.get("calamity") == "Y" and not sanitize_val(qual.get("calamity_note")):
        print(f"Error: [{company_id}] calamity_flag='Y' requires a non-empty calamity_note.", file=sys.stderr)
        return False

    # Build input diff
    input_diff = {}
    for k, new_v in qual.items():
        if k in input_fieldnames:
            old_v = input_row.get(k, "")
            sanitized_new = sanitize_val(new_v)
            if old_v != sanitized_new:
                input_diff[k] = (old_v, sanitized_new)

    # Build financials diff
    fin_diff = {}
    fin_rows = read_csv(fin_path)
    fin_row = None
    if fin_rows:
        for r in fin_rows:
            if r.get("id") == company_id:
                fin_row = r
                break

    if fin and fin_row:
        fin_fieldnames = list(fin_rows[0].keys())
        for k, new_v in fin.items():
            if k in fin_fieldnames:
                old_v = fin_row.get(k, "")
                if old_v != new_v:
                    fin_diff[k] = (old_v, new_v)

    # Print summary
    print(f"\nEvaluation summary for {company_id} ({universe.upper()}):")
    verdict = payload.get("evaluation_metadata", {}).get("verdict")
    if verdict:
        print(f"Verdict: {verdict}")

    if not input_diff and not fin_diff:
        print("No changes required. Company data is already up-to-date.")
        return True

    if input_diff:
        print("\nQualitative Updates (inputs.csv):")
        for k, (old_v, new_v) in input_diff.items():
            print(f"  [{k}] {repr(old_v)} -> {repr(new_v)}")

    if fin_diff:
        print("\nQuantitative Overrides (financials.csv):")
        for k, (old_v, new_v) in fin_diff.items():
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
    if fin_diff and fin_row:
        for k, (_, new_v) in fin_diff.items():
            fin_row[k] = new_v
        write_csv(fin_path, list(fin_rows[0].keys()), fin_rows)
        print(f"\nSuccessfully updated {fin_path}")

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
