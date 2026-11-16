"""v7.16 migration: add Gate 3/4 CAP audit columns to inputs.csv and normalize legacy 3a moat labels
into the 4 canonical archetypes across US, EU, and CA.

Usage:
    python3 screener/migrations/migrate_v7_16_cap_engine.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from screener.config import MOAT_TYPES  # noqa: E402
from screener.data import DATA_DIR, input_fields, load_universe, universe_keys, write_csv  # noqa: E402

# Companies legitimately operating Nick Sleep's 'Scale economies shared' model (passing unit-cost scale
# efficiencies back into lower customer prices / fees to compound volume).
NICK_SLEEP_SCALE_SHARED_IDS = {
    # Club, discount, off-price, fast-fashion, convenience & grocery scale retailers
    "COST", "WMT", "AMZN", "TJX", "ROST", "ITX.ES", "DOL.CA", "DG", "DLTR",
    "ATD.CA", "KR", "L.CA", "MRU.CA", "WN.CA", "AD.NL", "AXFO.SE", "CA.FR",
    "JMT.PT", "KESKOB.FI", "SBRY.GB", "TSCO.GB", "HWDN.GB", "KGF.GB",
    # Direct low-cost insurers, low-fee digital brokers/payments & passive ETF scale leaders
    "PGR", "ADM.GB", "IBKR", "SCHW", "AZA.SE", "SAVE.SE", "FBK.IT", "WISE.GB", "ADYEN.NL",
    "BLK", "AMUN.FR",
    # Low-cost carrier models
    "LUV", "EZJ.GB", "RYA.IE",
}

# Former 'R&D super-thinkers / Intangibles' names whose primary moat is static brand, heritage, IP library,
# regulatory license, or distribution network rather than active R&D frontier engineering.
INTANGIBLE_BRAND_OR_ASSET_IDS = {
    "RACE.IT", "IT", "SLB",
}
INTANGIBLE_SECTORS_FROM_RD = {
    "Communication Services",
    "Consumer Staples",
    "Financials",
}
INTANGIBLE_SUBINDUSTRIES_FROM_RD = {
    "Apparel, Accessories & Luxury Goods",
    "Apparel, Accessories & Luxury Goods (mapped)",
    "Footwear",
    "Restaurants",
    "Construction & Engineering",
    "Construction & Engineering (mapped)",
    "Trading Companies & Distributors",
    "Trading Companies & Distributors (mapped)",
}


def map_canonical_3a(row: dict) -> str | None:
    raw = row.get("3a")
    if raw is None or str(raw).strip() == "":
        return None
    s = str(raw).strip()
    if s == "None":
        return "None"
    if s in MOAT_TYPES and s != "Scale economies shared":
        return s
    if s == "Toll booth / Switching costs":
        return "Toll booth & switching costs"
    if s == "Irreplaceable infrastructure":
        return "Irreplaceable infrastructure & intangibles"

    cid = str(row.get("id") or "").strip()
    sec = str(row.get("sector") or "").strip()
    sub = str(row.get("sub_industry") or "").strip()

    if s in ("R&D super-thinkers / Intangibles", "R&D super-thinkers"):
        if cid == "IT":
            return "Toll booth & switching costs"
        if cid in INTANGIBLE_BRAND_OR_ASSET_IDS or sec in INTANGIBLE_SECTORS_FROM_RD or sub in INTANGIBLE_SUBINDUSTRIES_FROM_RD:
            return "Irreplaceable infrastructure & intangibles"
        return "R&D & innovation leadership"

    if s == "Scale economies shared":
        if cid in NICK_SLEEP_SCALE_SHARED_IDS:
            return "Scale economies shared"
        return "Irreplaceable infrastructure & intangibles"

    raise ValueError(f"Unrecognized legacy 3a value {s!r} on {cid}")


def main() -> None:
    transitions: Counter[tuple[str, str]] = Counter()
    final_counts: Counter[str] = Counter()

    for u in universe_keys():
        meta = load_universe(u)
        rows = meta["companies"]
        fields = input_fields(meta)
        changed = 0
        for r in rows:
            old_3a = r.get("3a")
            new_3a = map_canonical_3a(r)
            if old_3a != new_3a:
                transitions[(str(old_3a), str(new_3a))] += 1
                r["3a"] = new_3a
                changed += 1
            if new_3a is not None:
                assert new_3a in MOAT_TYPES, f"Non-canonical 3a {new_3a!r} on {r.get('id')}"
                final_counts[new_3a] += 1
        write_csv(DATA_DIR / u / "inputs.csv", fields, rows)
        print(f"{u}: wrote {len(rows)} rows with {len(fields)} columns ({changed} 3a labels updated)")

    print("\n3a Transition Summary:")
    for (o, n), cnt in transitions.most_common():
        print(f"  {o!r} -> {n!r}: {cnt}")

    print("\nCanonical 3a Distribution Across All Universes:")
    for k, cnt in final_counts.most_common():
        print(f"  {k}: {cnt}")


if __name__ == "__main__":
    main()
