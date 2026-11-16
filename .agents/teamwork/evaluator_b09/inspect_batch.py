import json

with open("evaluations/batches/batch_09.json") as f:
    batch = json.load(f)

print(f"Batch ID: {batch.get('batch_metadata', {}).get('batch_id')}")
print(f"Total count: {len(batch.get('companies', []))}")

for i, c in enumerate(batch["companies"]):
    ident = c["identity"]
    cur = c["current_qualitative"]
    fin = c.get("financial_context", {})
    cid = ident.get("id", "")
    comp = ident.get("company", "")
    sub = ident.get("sub_industry", "")
    g1 = cur.get("1", "")
    g2 = cur.get("2", "")
    g3b = cur.get("3b", "")
    g4_leg = cur.get("4", "")
    g5 = cur.get("5", "")
    g6 = cur.get("6", "")
    roic_gaap = fin.get("roic_median_5y_gaap", "")
    roic_tang = fin.get("roic_operating_5y_tangible", "")
    fcf_conv = fin.get("fcf_conversion_multi_yr", "")
    int_cov = fin.get("g6_interest_coverage", "")
    net_debt = fin.get("g6_netdebt_years", "")
    fc = ident.get("is_fast_clock_speed", False)
    m3m = cur.get("3m", "")[:100]
    note = cur.get("note", "")[:100]

    print(f"[{i+1:02d}] {cid:10s} | {comp[:22]:22s} | {sub[:25]:25s} | 3b={g3b} | G4_leg={g4_leg:2s} | 5={g5:1s} | 6={g6:1s} | Fast={str(fc):5s} | ROIC={roic_gaap[:6]:6s} | Tang={roic_tang[:6]:6s}")
