"""Generate evaluated batch_12 JSON matching v7.16 qualitative specification."""
import json
import os
import sys
from pathlib import Path

# Add screener root to sys.path
screener_root = Path(__file__).resolve().parent.parent.parent.parent
if str(screener_root) not in sys.path:
    sys.path.insert(0, str(screener_root))

from screener.apply_evaluation import validate_and_waterfall
from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores

BATCH_INPUT_PATH = screener_root / "evaluations" / "batches" / "batch_12.json"
OUTPUT_PATH = screener_root / "evaluations" / "completed" / "batch_12_evaluated.json"

# (m_scores, 3a_label, 3b_gate, f_scores, 4n_note, 5_score, 6_gate, calamity_flag)
EVAL_SPECS = {
    # 37 Gate 3 Fails
    'ANET': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'CIEN': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'CSCO': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'FFIV': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'LITE': ((0, 0, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'ERIC B.SE': ((1, 0, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'NOKIA.FI': ((0, 0, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'COHR': ((0, 0, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'GLW': ((0, 1, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'ZBRA': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'FLEX': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'JBL': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'ATS.AT': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'CTSH': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'GIB.A.CA': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'IBM': ((1, 1, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'CAP.FR': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'REY.IT': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'SOP.FR': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'AKAM': ((1, 1, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'GDDY': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'TER': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'AIXA.DE': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'COTN.CH': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'SOI.FR': ((1, 0, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'TPRO.IT': ((1, 0, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'AMD': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'FSLR': ((0, 1, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'INTC': ((1, 1, 0, 0), 'Irreplaceable infrastructure & intangibles', 'N', None, '', '', '', ''),
    'MCHP': ((1, 0, 0, 0), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'MRVL': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'MU': ((0, 1, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'ON': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'QCOM': ((1, 0, 0, 2), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'SWKS': ((1, 0, 0, 1), 'R&D & innovation leadership', 'N', None, '', '', '', ''),
    'ALAB': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),
    'IFX.DE': ((1, 0, 0, 1), 'Toll booth & switching costs', 'N', None, '', '', '', ''),

    # 28 Gate 3 Passes
    'MSI': ((2, 1, 0, 0), 'Toll booth & switching costs', 'Y', (0, 1, 0, 0, 1), 'Initial CAP 25Y reduced by -5Y for stable public safety rivalry (4_riv=1) and cellular broadband/LMR coexistence clock speed (4_sub=1).', 1, 'Y', ''),
    'APH': ((2, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 0, 0, 1), 'Initial CAP 25Y reduced by -5Y for connector market rivalry (4_riv=1) and high-speed copper-to-optical transition clock speed (4_sub=1).', 2, 'Y', ''),
    'KEYS': ((1, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 2), 'Initial CAP 20Y capped at 5Y due to severe substitution risk from virtual simulation/AI automated testing (4_sub=2) and cyclical buyer/rivalry pressure (4_riv=1, 4_buy=1).', '', '', ''),
    'ROP': ((2, 0, 0, 0), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 2), 'Initial CAP 20Y capped at 5Y due to terminal substitution risk from agentic AI automating professional services seat-based software (4_sub=2) alongside buyer seat compression (4_buy=1) and rivalry (4_riv=1).', '', '', ''),
    'TDY': ((1, 1, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 20Y reduced by -10Y for digital imaging rivalry (4_riv=1), defense/commercial buyer consolidation (4_buy=1), and sensor technology substitution clock speed (4_sub=1).', '', '', ''),
    'HEXA B.SE': ((2, 1, 0, 0), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 25Y reduced by -10Y for metrology peer rivalry (4_riv=1), auto/aero buyer power (4_buy=1), and 3D computer-vision substitution clock speed (4_sub=1).', 1, 'N', ''),
    'HLMA.GB': ((1, 0, 0, 2), 'R&D & innovation leadership', 'Y', (0, 1, 0, 0, 1), 'Initial CAP 25Y reduced by -5Y for niche instrument rivalry (4_riv=1) and medical/safety sensing technology clock speed (4_sub=1).', 2, 'Y', ''),
    'IFCN.CH': ((1, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 2, 0, 1), 'Initial CAP 20Y capped at 5Y due to fatal flaw customer concentration and China trade embargo exposure (4_buy=2), with semicap rivalry (4_riv=1) and tech clock speed (4_sub=1).', '', '', ''),
    'TEL': ((2, 1, 0, 0), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 25Y reduced by -10Y for connector rivalry (4_riv=1), auto OEM buyer leverage (4_buy=1), and EV architecture clock speed (4_sub=1).', 1, 'Y', ''),
    'ACN': ((2, 0, 0, 0), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 2), 'Initial CAP 20Y capped at 5Y due to severe terminal substitution of billable-hour IT consulting and coding by cognitive AI agents (4_sub=2) alongside client fee pressure (4_buy=1) and rivalry (4_riv=1).', '', '', ''),
    'IT': ((2, 1, 0, 0), 'Toll booth & switching costs', 'Y', (0, 0, 1, 0, 2), 'Initial CAP 25Y capped at 10Y due to terminal substitution risk from enterprise AI search and autonomous vendor synthesis agents (4_sub=2) and client seat-compression pressure (4_buy=1).', '', '', ''),
    'VRSN': ((2, 0, 0, 0), 'Toll booth & switching costs', 'Y', (0, 0, 1, 0, 1), 'Initial CAP 20Y reduced by -5Y for ICANN contractual price-cap regulation (4_buy=1) and app/social web navigation substitution clock speed (4_sub=1).', 2, 'Y', ''),
    'SHOP': ((2, 0, 0, 0), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 2), 'Initial CAP 20Y capped at 5Y due to severe substitution risk from AI autonomous agentic shopping bypassing storefronts (4_sub=2) and intense commerce rivalry (4_riv=1, 4_buy=1).', '', '', ''),
    'AMAT': ((2, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 25Y reduced by -10Y for semicap peer rivalry (4_riv=1), fab buyer concentration (4_buy=1), and semiconductor node transition clock speed (4_sub=1).', 1, 'Y', ''),
    'KLAC': ((2, 1, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 30Y reduced by -10Y for metrology rivalry (4_riv=1), concentrated fab buyer power (4_buy=1), and semiconductor technology clock speed (4_sub=1).', 2, 'Y', ''),
    'LRCX': ((2, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 25Y reduced by -10Y for etch/deposition rivalry (4_riv=1), memory buyer concentration (4_buy=1), and semiconductor equipment clock speed (4_sub=1).', 2, 'Y', ''),
    'Q': ((1, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 2, 0, 1), 'Initial CAP 20Y capped at 5Y due to acute geopolitical concentration in Taiwan/China fab customers (4_buy=2), alongside chemical formulation rivalry (4_riv=1) and semiconductor clock speed (4_sub=1).', '', '', ''),
    'ASM.NL': ((2, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 0, 0, 1), 'Initial CAP 25Y reduced by -5Y for ALD equipment peer rivalry (4_riv=1) and semiconductor technology clock speed (4_sub=1).', 2, 'Y', ''),
    'BESI.NL': ((1, 0, 0, 2), 'R&D & innovation leadership', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 25Y reduced by -10Y for packaging equipment rivalry (4_riv=1), OSAT/foundry buyer concentration (4_buy=1), and packaging technology clock speed (4_sub=1).', 2, 'N', ''),
    'MYCR.SE': ((2, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 25Y reduced by -10Y for SMT equipment rivalry (4_riv=1), display panel buyer concentration (4_buy=1), and display tech clock speed (4_sub=1).', 1, 'Y', ''),
    'VACN.CH': ((2, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 0, 0, 1), 'Initial CAP 25Y reduced by -5Y for niche valve rivalry (4_riv=1) and semiconductor node transition clock speed (4_sub=1).', 1, 'Y', ''),
    'ADI': ((2, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 0, 0, 1), 'Initial CAP 25Y reduced by -5Y for analog duopoly rivalry (4_riv=1) and semiconductor technology clock speed (4_sub=1).', 1, 'Y', ''),
    'AVGO': ((2, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 25Y reduced by -10Y for networking silicon rivalry (4_riv=1), hyperscaler/enterprise buyer leverage (4_buy=1), and AI architecture clock speed (4_sub=1).', 1, 'Y', ''),
    'MPWR': ((1, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 2, 0, 1), 'Initial CAP 20Y capped at 5Y due to monopsonistic GPU customer leverage and dual-sourcing reallocation (4_buy=2), alongside PMIC rivalry (4_riv=1) and semiconductor clock speed (4_sub=1).', '', '', ''),
    'NVDA': ((2, 0, 0, 2), 'Toll booth & switching costs', 'Y', (1, 1, 1, 1, 1), 'Initial CAP 30Y reduced by -15Y for full-spectrum semiconductor frictions: custom ASIC entrant threat (4_ent=1), GPU peer rivalry (4_riv=1), Cloud Titan buyer concentration (4_buy=1), TSMC/HBM supplier bottlenecks (4_sup=1), and rapid AI model clock speed (4_sub=1).', 2, 'N', ''),
    'NXPI': ((2, 0, 0, 0), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 20Y reduced by -10Y for automotive MCU peer rivalry (4_riv=1), auto OEM buyer pressure (4_buy=1), and zonal architecture/Chinese substitution clock speed (4_sub=1).', '', '', ''),
    'TXN': ((2, 1, 0, 0), 'Toll booth & switching costs', 'Y', (0, 1, 0, 0, 1), 'Initial CAP 25Y reduced by -5Y for analog duopoly rivalry (4_riv=1) and semiconductor technology clock speed (4_sub=1).', 2, 'N', 'Y'),
    'ARM': ((2, 0, 0, 1), 'Toll booth & switching costs', 'Y', (0, 1, 1, 0, 1), 'Initial CAP 25Y reduced by -10Y for RISC-V/x86 architecture rivalry (4_riv=1), licensee buyer consolidation (4_buy=1), and open-source ISA substitution clock speed (4_sub=1).', 1, 'N', '')
}


def main():
    with open(BATCH_INPUT_PATH, "r", encoding="utf-8") as f:
        batch_raw = json.load(f)

    companies = batch_raw["companies"]
    print(f"Loaded {len(companies)} companies from {BATCH_INPUT_PATH}")
    assert len(companies) == 65

    evaluated_list = []
    total_warnings = 0

    for c in companies:
        cid = c["identity"]["id"]
        u = c["identity"]["universe"]
        cq = c["current_qualitative"]

        if cid not in EVAL_SPECS:
            raise KeyError(f"Missing evaluation spec for company: {cid}")

        m_scores, a3, g3b, f_scores, f_note, g5, g6, cal = EVAL_SPECS[cid]

        raw_qual = {
            "1": "Y",
            "2": "Y",
            "2r": "",
            "3_tb": m_scores[0],
            "3_ia": m_scores[1],
            "3_se": m_scores[2],
            "3_rd": m_scores[3],
            "3a": a3,
            "3b": g3b,
            "3m": cq.get("3m", ""),
            "4_ent": f_scores[0] if f_scores else "",
            "4_riv": f_scores[1] if f_scores else "",
            "4_buy": f_scores[2] if f_scores else "",
            "4_sup": f_scores[3] if f_scores else "",
            "4_sub": f_scores[4] if f_scores else "",
            "4": "",
            "4n": f_note,
            "5": g5,
            "6": g6,
            "calamity": cal,
            "calamity_note": cq.get("calamity_note", "") if cal == "Y" else "",
            "note": cq.get("note", ""),
            "evidence": cq.get("evidence", "")
        }

        if f_scores:
            cap_init = compute_initial_cap_from_scores(m_scores)
            cap_final, _, _ = compute_final_cap_from_scores(cap_init, f_scores)
            raw_qual["4"] = cap_final

        # Strict validation and waterfall cleaning
        validated_qual, _, warnings = validate_and_waterfall({"id": cid, "qualitative": raw_qual})
        if warnings:
            print(f"[{cid}] Waterfall warnings: {warnings}")
            total_warnings += len(warnings)

        # Build final object
        evaluated_list.append({
            "id": cid,
            "universe": u,
            "qualitative": validated_qual
        })

    print(f"Processed {len(evaluated_list)} companies with {total_warnings} total warnings.")
    assert len(evaluated_list) == 65
    assert total_warnings == 0

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(evaluated_list, f, indent=2)

    print(f"Successfully wrote evaluated array to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
