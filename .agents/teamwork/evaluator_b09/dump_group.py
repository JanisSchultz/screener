import sys
import json

start = int(sys.argv[1])
end = int(sys.argv[2])

with open("evaluations/batches/batch_09.json") as f:
    batch = json.load(f)

for i in range(start, min(end, len(batch["companies"]))):
    c = batch["companies"][i]
    ident = c["identity"]
    cur = c["current_qualitative"]
    fin = c.get("financial_context", {})
    cid = ident.get("id")
    comp = ident.get("company")
    sub = ident.get("sub_industry")
    print(f"[{i+1}] {cid} | {comp} | {sub}")
    print(f"  3a: {cur.get('3a')} | 3b: {cur.get('3b')} | 4: {cur.get('4')} | 5: {cur.get('5')} | 6: {cur.get('6')}")
    print(f"  Financials: GAAP ROIC={fin.get('roic_median_5y_gaap')} | Tang={fin.get('roic_operating_5y_tangible')} | FCF Conv={fin.get('fcf_conversion_multi_yr')}")
    print(f"              Debt={fin.get('lt_debt_m')} | Cash={fin.get('cash_m')} | EBIT={fin.get('ebit_ttm_m')} | IntCov={fin.get('g6_interest_coverage')} | NetDebtYrs={fin.get('g6_netdebt_years')}")
    print(f"  3m: {cur.get('3m')}")
    print(f"  4n: {cur.get('4n')}")
    print(f"  Note: {cur.get('note')}")
    print(f"  Evidence: {cur.get('evidence')}")
    print("=" * 80)
