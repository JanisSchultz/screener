import json

with open("evaluations/batches/batch_09.json") as f:
    batch = json.load(f)

for i, c in enumerate(batch["companies"]):
    ident = c["identity"]
    cur = c["current_qualitative"]
    fin = c.get("financial_context", {})
    cid = ident.get("id")
    print(f"=== [{i+1}] {cid} | {ident.get('company')} | {ident.get('sector')} | {ident.get('sub_industry')} ===")
    print(f"Current G1={cur.get('1')} G2={cur.get('2')} 3a={cur.get('3a')} 3b={cur.get('3b')} G4={cur.get('4')} G5={cur.get('5')} G6={cur.get('6')} Cal={cur.get('calamity')}")
    print(f"Financials: GAAP ROIC={fin.get('roic_median_5y_gaap')} | Tangible={fin.get('roic_operating_5y_tangible')} | FCF conv={fin.get('fcf_conversion_multi_yr')}")
    print(f"            Debt={fin.get('lt_debt_m')} | Cash={fin.get('cash_m')} | EBIT={fin.get('ebit_ttm_m')} | IntCov={fin.get('g6_interest_coverage')} | NetDebtYrs={fin.get('g6_netdebt_years')}")
    print(f"3m: {cur.get('3m')}")
    print(f"4n: {cur.get('4n')}")
    print(f"note: {cur.get('note')}")
    print(f"evidence: {cur.get('evidence')}")
    print()
