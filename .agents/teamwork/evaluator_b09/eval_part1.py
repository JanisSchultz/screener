"""Evaluation definitions for Batch 09 companies (part 1: companies 1 to 20)."""

PART_1 = {
    "KNIN.CH": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Kuehne+Nagel is the global #1 ocean freight forwarder and a top-3 air forwarder with scale economies shared and proprietary digital routing platforms (Seaexplorer). However, enterprise shippers face low switching costs and routinely tender shipping lanes across competing forwarders, leaving K+N as a price-taking intermediary without independent pricing power >= inflation across the freight cycle.",
        "note": "Fails Gate 3b (ROIC & Pricing Power, REJECT). Kuehne+Nagel is an asset-light global forwarding leader with high return on equity and stable anchor ownership by Klaus-Michael Kühne. However, third-party logistics forwarding is structurally intermediated and subject to frequent customer RFQs; EBIT halved from 2022 peaks as global ocean/air freight spreads normalized, confirming that margins are market-driven rather than protected by proprietary pricing power.",
        "evidence": "Group revenue declined from CHF 39.4B (2022) to CHF 23.8B (2023) and EBIT fell ~50% from CHF 3.76B to CHF 1.90B as abnormal pandemic supply-chain surcharges vanished. Core Sea and Air logistics volumes are re-tendered regularly by corporate customers on commodity freight rates with negligible customer lock-in."
    },
    "ADP.FR": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "3m": "Groupe ADP operates an unreplicable infrastructure monopoly across the Greater Paris air basin (Paris-CDG, Paris-Orly, and Le Bourget). Physical runway slot scarcity and environmental restrictions prevent competing hub development. Under its dual-till regulatory model, non-aeronautical retail (Extime Paris luxury duty-free JV with Lagardère) exercises exceptional unregulated pricing power over high-spending intercontinental travelers, while aeronautical charges adjust via economic regulation agreements.",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for airline hub bargaining power and French ART regulatory tariff friction (4_buy=1) and unionized airport labor alongside terminal construction supplier pressure (4_sup=1) yielding Final CAP 20Y.",
        "5": 0,
        "6": "",
        "note": "Fails Gate 5 (Management & Capital Allocation, Score = 0, REJECT). Paris CDG and Orly are irreplaceable national infrastructure assets, but Groupe ADP is 50.6% owned by the French State and suffers from acute capital allocation and governance pathologies: recurring regulatory conflict with ART over allowed aeronautical charges, bureaucratic inertia, and value-destructive international M&A (GMR Airports in India, TAV in Turkey) that loaded the balance sheet with €8.5B+ in net debt (>13x net income) and caused large impairment charges (€330M in 2024).",
        "evidence": "State-dominated corporate governance has directed massive capital into speculative overseas airport stakes (GMR in India, TAV in Turkey) instead of disciplined per-share compounding. Net financial debt reached €8.57B at year-end 2024 against normalized net income of €638M (and reported net income of €342M, hit by a €330M merger charge on Indian assets), depressing consolidated ROIC to ~5-7%."
    },
    "AENA.ES": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "3m": "Aena holds an unreplicable national spatial monopoly over 46 Spanish airports handling >99% of Spanish commercial air passenger traffic. High entry barriers (land acquisition, airspace constraints, environmental permitting) make competitive entry impossible. Pricing power is anchored by DORA regulatory inflation indexation on aeronautical tariffs and multi-year retail concession contracts with CPI-indexed Minimum Annual Guarantees (MAG). 5-year median ROIC of 16.5% proves moat durability. Main erosion risks stem from 5-year DORA regulatory resets and airline lobbying against tariff increases.",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 1, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for airline/DORA regulatory tariff resets (4_buy=1), airport operational/security contractor wage inflation (4_sup=1), and high-speed rail AVE substitution on domestic intercity corridors (4_sub=1) yielding Final CAP 15Y.",
        "5": 1,
        "6": "Y",
        "note": "Passes all 6 gates. Unreplicable statutory monopoly operating the entire Spanish commercial airport network, benefiting from Spain's structural status as the world's #2 tourist destination. Aeronautical tariffs protected by DORA inflation indexation, while commercial retail concessions (duty-free, F&B) deliver high-margin non-aero profit with minimum annual guarantees. 16.5% median ROIC, 98% FCF conversion, and net debt amortizing comfortably below 3.0x earnings. [5-10Y g: passenger volume 2.5% + DORA aero tariff indexation 1.0% + commercial retail spend per passenger 2.0% - environmental/energy capex drag 0.5% + dividend payout 0.0%]",
        "evidence": "Aena operates 46 airports in Spain plus international terminals (London Luton, Northeast Brazil). In 2024-2025, passenger traffic reached all-time records exceeding 300M passengers. EBITDA margins exceed 58%, and Owner FCF generation reached €2.1B+ on net income of €1.9B (FCF conversion >100%). Net debt stands at €5.6B (down from €7.4B in 2021), representing ~2.6x Owner Earnings with interest coverage >9.4x."
    },
    "FHZN.CH": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "3m": "Single-hub airport concession for Zurich-Kloten with commercial real estate (The Circle) and retail integration. Hub carrier Swiss International Air Lines represents ~55% of passenger traffic. High local land constraints and Swiss infrastructure standards protect the physical hub, while non-aero real estate and commercial retail provide inflation-linked rental income.",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 1, "4_sub": 2,
        "4n": "Initial CAP 20Y reduced to 5Y under Fatal-Flaw Cap due to severe terminal environmental noise restrictions, southern German flight path bans, and dense high-speed rail substitution across central Europe (4_sub=2), alongside Lufthansa/Swiss buyer concentration (4_buy=1) and Swiss labor costs (4_sup=1).",
        "5": "",
        "6": "",
        "note": "Fails Gate 4 (CAP = 5, REJECT). While Zurich Airport is an entrenched spatial asset in Switzerland, its structural runway is severely truncated by external constraints: stringent noise abatement flight bans from southern Germany restricting approach corridors, strict local aircraft movement caps, high-speed rail substitution across central Europe (4_sub=2), and large capital outlays for international concessions (Noida Airport in India) that dilute group return stability.",
        "evidence": "Zurich Airport operates under a cantonal concession expiring in 2051. While operating margins on airport operations and The Circle retail reach 35-40%, flight movement volumes are structurally capped by strict noise curfews (23:00 to 06:00) and persistent diplomatic disputes with Germany over approach sectors. Concession capex commitments in Noida, India commit substantial capital outside Switzerland."
    },
    "ALLE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Architectural specification lock-in via MasterFormat spec-writers, institutional master key systems embedded in schools, hospitals, and commercial facilities. Schlage, Von Duprin, and LCN command premier brand loyalty among locksmiths and contractors with multi-decade replacement lifecycles. 10-year median GAAP ROIC is 22.8% (tangible ROIC >68%) with consistent 2-4% pricing power above inflation.",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for commercial access control and institutional security rivalry with ASSA ABLOY and dormakaba (4_riv=1), yielding Final CAP 20Y.",
        "5": 1,
        "6": "Y",
        "note": "Passes all 6 gates. Global leader in mechanical and electronic access solutions with deep architectural specification moats (MasterFormat Division 08) and high-margin institutional replacement cycles (Von Duprin, Schlage, LCN). High pricing power demonstrated across multiple cycles with operating margins expanding from 18% to >22%. Fortress balance sheet with net debt/NI ~1.7x and interest coverage ~11.5x. [5-10Y g: commercial non-res renovation volume 2.0% + electronic access adoption 2.5% + spec-in pricing power 2.0% - residential cyclical drag 0.5% + share repurchases 1.5%]",
        "evidence": "10-year median GAAP ROIC is 22.8%, tangible operating ROIC exceeds 68%. Gross margins consistently 42-45% and operating margins 20-23%. FCF conversion averaged 95-100% of Net Income ($500M-$600M FCF annually). Total debt of $2.1B against $1.2B TTM EBITDA and $570M Net Income yields net debt/NI of 1.7x and interest coverage of 11.5x. Institutional non-residential channels represent >75% of profits, insulating cash flow from residential housing volatility."
    },
    "AOS": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Leading North American manufacturer of residential and commercial water heaters and boilers. Strong contractor and plumber relationships, wholesale distribution channel lock-in, and reliable Lindy brand reputation. 10-year median GAAP ROIC is 34.6% with operating margins near 18-19%. Primary erosion threats include customer concentration at Ferguson, regulatory shifts toward heat pumps, and persistent property deflation in China.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced by -10Y for wholesale distributor concentration at Ferguson (4_buy=1), intensifying domestic/China competition (4_riv=1), and regulatory DOE heat-pump technology transition risks favoring HVAC OEMs (4_sub=1) yielding Final CAP 10Y.",
        "5": "",
        "6": "",
        "note": "Fails Gate 4 (CAP = 10, REJECT). High returns on capital (median ROIC >30%) in North American replacement water heating are offset by structural competitive headwinds: heavy customer concentration at Ferguson (~35% of sales, 4_buy=1), persistent property deflation and domestic pricing pressure in China (4_riv=1), and regulatory DOE efficiency standards accelerating the shift to heat-pump water heaters where global HVAC/appliance OEMs hold scale advantages (4_sub=1).",
        "evidence": "10-year median GAAP ROIC of 34.6% and operating margins of 18-19%. However, North American wholesale revenue is heavily dependent on Ferguson (~35% of total sales). China revenue (historically 25-30% of sales) has suffered sustained declines due to Chinese real estate contraction and aggressive local competition from Haier and Midea. The 2029 DOE efficiency standards mandate heat-pump technology for electric storage water heaters, opening the market to HVAC incumbents (Rheem, Daikin, Carrier)."
    },
    "CARR": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "3m": "Global commercial and residential HVAC installed base, direct service branch network, and recognized Carrier brand name. However, extensive portfolio reshaping (€12B Viessmann acquisition alongside divestitures of Access Solutions and Industrial Fire) added massive goodwill and debt, while 5-year median GAAP ROIC of 11.7% falls below the 12% Munger moat hurdle. European heat pump demand has suffered sharp post-subsidy contractions.",
        "note": "Fails Gate 3b (ROIC < 12% & Proof of Moat, REJECT). Carrier completed a massive portfolio reshaping (acquiring Viessmann Climate Solutions for €12B and divesting Access Solutions, Commercial Refrigeration, and Industrial Fire), but 5-year median GAAP ROIC is ~11.7% (below the 12% hurdle), burdened by heavy goodwill/intangibles (€12B Viessmann deal) and cyclical residential heat pump weakness in Europe. Lacks invariant pricing power across cycles.",
        "evidence": "Reported GAAP ROIC has averaged 11.7% over 5 years. The €12B acquisition of Viessmann closed in January 2024 right as European heat pump subsidies waned, leading to volume contractions in Germany and Central Europe. Total debt surged to over $14B post-deal, and while divestitures funded partial debt reduction, through-cycle ROIC remains below the 12% cost of capital threshold."
    },
    "JCI": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Metasys building automation systems, proprietary controls, and massive commercial building installed base create high customer switching costs. Empirical proof: commercial building solutions generate solid operating margins (10-14%) and strong pricing power on service contracts. Primary erosion threats include open-protocol smart building software and commercial HVAC rivalry.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for commercial HVAC/controls rivalry with Trane and Honeywell (4_riv=1), commercial real estate buyer procurement pressure (4_buy=1), and cloud-native open-protocol smart building substitution (4_sub=1) yielding Final CAP 15Y.",
        "5": 1,
        "6": "N",
        "note": "Fails Gate 6 (Peace-of-Mind Balance Sheet & ROIC, REJECT). Pure-play commercial building solutions provider with premier installed base (York, Metasys), but 10-year GAAP ROIC has averaged only 8.6% burdened by $17B+ of legacy goodwill. Total debt remains elevated at $9.9B ($8.6B LT debt vs $1.7B net income, LT debt / NI ~5.1x exceeding the <=4.0x ceiling), and management chose to deploy $5.0B of net proceeds from the Bosch divestiture into an accelerated share repurchase rather than debt reduction.",
        "evidence": "Following the August 2025 close of the $8.1B sale ($5.0B net cash proceeds) of its Residential & Light Commercial HVAC unit to Bosch, Johnson Controls operates as a pure-play commercial building solutions provider with ~$23B in continuing revenue and solid operating margins (10-14%). However, 10-year GAAP ROIC has averaged 7-10% (median 9.2%) weighed down by $17B+ of goodwill and intangibles dating from the 2016 Tyco merger. Balance sheet remains overleveraged with total debt of $9.9B ($8.6B long-term debt) against FY25 net income of $1.7B (LT debt / NI ~5.1x, exceeding the <=4.0x maximum). Management directed the $5.0B net proceeds from the Bosch sale into an accelerated share repurchase rather than deleveraging, failing Gate 6."
    },
    "LII": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Direct-to-dealer (D2D) distribution model bypasses independent two-step wholesalers for ~75% of sales, embedding high switching costs via Lennox Premier Dealer certification, proprietary diagnostic tools, warranty handling, and co-op marketing. 10-year median ROIC is ~28% with operating margins near 17-18%. Primary erosion threat is private equity contractor consolidation demanding multi-brand wholesale sourcing.",
        "4_ent": 0, "4_riv": 1, "4_buy": 2, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 20Y reduced to 5Y under Fatal-Flaw Cap due to private equity consolidation of independent residential HVAC contractors dismantling the direct-to-dealer captive distribution moat (4_buy=2), alongside commercial HVAC rivalry (4_riv=1) and residential financing sensitivity (4_sub=1).",
        "5": "",
        "6": "",
        "note": "Fails Gate 4 (CAP = 5, REJECT). While Lennox achieves high returns on capital via its proprietary direct-to-dealer network, structural runway is limited. Capital Goods base-rate persistence is Tier 3 (10-15Y). The rapid private equity consolidation of independent residential HVAC contractors directly threatens Lennox's captive dealer moat by shifting procurement to multi-brand wholesale distributors (Watsco, Ferguson). Exiting Europe leaves Lennox >90% dependent on mature North American residential replacement cycles, with high-ticket consumer financing vulnerable to structural interest rates.",
        "evidence": "10-year median ROIC of 28.5% with operating margins of 17-18% and FCF of $640M-$785M. Revenue splits ~65% Home Comfort Solutions (Residential) and ~35% Building Climate Solutions (Commercial); ~75% replacement / 25% new construction. However, Lennox is pure-play North American without global scale, competing against Daikin, Carrier, and Trane. Private equity rollups of local HVAC dealers aggregate buying power away from proprietary direct-to-dealer networks."
    },
    "TT": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Massive proprietary installed base in commercial HVAC, mission-critical Tracer building automation controls, and company-owned direct technician service network create high customer switching costs. Empirically proven by 5-year median ROIC of ~18.5% (ROIC >20% in 2024-2025), robust gross margins, and consistent positive pricing realization (+3-5% annually) driving operating margins from 14% to >18%. Primary erosion threats include low-end residential HVAC commoditization and competition from Asian OEMs in ductless split systems.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for commercial HVAC/chiller rivalry (4_riv=1), enterprise customer procurement power (4_buy=1), and regulatory refrigerant transition/Asian OEM split competition (4_sub=1) yielding Final CAP 15Y.",
        "5": 1,
        "6": "Y",
        "note": "Passes all 6 gates. Global leader in commercial HVAC and climate solutions with powerful switching costs anchored by installed base and direct service network. Active beneficiary of AI data center thermal cooling demand and secular building decarbonization/energy efficiency. Clean balance sheet with net debt/NI ~1.2x and interest coverage ~17.5x. [5-10Y g: commercial & data center volume 3.5% + equipment pricing 2.0% + services & controls mix 2.0% - regulatory refrigerant/tariff drag 0.5% + share repurchases 1.5%]",
        "evidence": "10-year median ROIC ~18.5% with 2024-2025 ROIC >20%. FY2024 revenue $19.8B (+12%), FCF $2.8B (109% conversion); FY2025 revenue $21.3B (+7.5%), operating income $3.97B, net income $2.94B, FCF conversion 98%. Total debt of $4.6B (net debt ~$3.5B) against $2.94B net income yields net debt/NI of 1.19x and interest coverage of 17.5x. Pure-play climate leader benefiting from mission-critical commercial HVAC, data center cooling, and transport refrigeration (Thermo King)."
    },
    "ASSA B.SE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Spec-in key systems installed base and decentralized acquisition machine. Unrivaled global scale in mechanical and digital access solutions (HID, Yale, effeff). Proven pricing power covering raw metal and wage inflation across multiple cycles. 5-year median GAAP ROIC is 12.5% and operating tangible ROIC exceeds 100% due to serial acquisition intangibles.",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for commercial access control and smart lock rivalry with Allegion and dormakaba (4_riv=1), yielding Final CAP 20Y.",
        "5": 2,
        "6": "Y",
        "note": "Passes all 6 gates. Global leader in physical and electromechanical access solutions with an unassailable installed base in master key systems, architectural spec-in, and HID electronic credentials. Over two-thirds of revenue driven by resilient aftermarket maintenance and replacement. Proven pricing power across multiple inflationary cycles with multi-year FCF conversion >100%. [5-10Y g: aftermarket volume 2.0% + smart access mix 2.0% + pricing power 2.0% + bolt-on M&A 2.0% - restructuring drag 0.5% + buybacks 0.5%]",
        "evidence": "5-year median GAAP ROIC of 12.5% with tangible operating ROIC >100% due to capital-light assembly and large acquisition intangibles. Owner FCF conversion averaged 119.6% from 2022 to 2025 (FY2025 FCF of 18.6B SEK on 14.7B SEK net income). Net debt / NI sits at 3.07x with 6.98x interest coverage (EBIT 23.1B SEK vs 3.3B SEK interest), easily meeting the <4.0x leverage and >5.0x coverage thresholds."
    },
    "BEAN.CH": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 2,
        "3a": "R&D & innovation leadership",
        "3b": "Y",
        "3m": "Decades of actuator precision engineering and distributor/OEM spec-in. Actuators are a minuscule cost component of building systems but carry catastrophic failure costs, cementing extreme customer loyalty and price insensitivity. Demonstrated multi-year median GAAP ROIC >32% and tangible ROIC >34%.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for building automation OEM rivalry (4_riv=1), HVAC OEM buyer procurement concentration (4_buy=1), and technological transition to data center liquid cooling architectures (4_sub=1) yielding Final CAP 20Y.",
        "5": 2,
        "6": "Y",
        "note": "Passes all 6 gates. Global undisputed hegemon in HVAC damper actuators and control valves. Unbeatable consumer surplus and installer trust: devices represent <2% of building HVAC capex but prevent millions in system downtime, resulting in supreme pricing power. Massive secular tailwinds from data-center liquid cooling and building decarbonization mandates. Pristine debt-free net cash balance sheet with >32% median ROIC. [5-10Y g: volume 5.0% + price 2.0% + data center cooling mix 2.0% - R&D/capex drag 0.5% + buybacks/dividends 0.0%]",
        "evidence": "Multi-cycle GAAP ROIC consistently exceeds 27-36% (median 32.4%), with operating tangible ROIC of 34.2%. Owner EPS grew at a 13.9% CAGR from 2022 to 2025 (reaching 14.77 CHF peak in 2025). Long-term debt is 0.0 CHF against 100.6m CHF in cash, with EBIT / Interest coverage >270x."
    },
    "GEBN.CH": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Installer loyalty and decades-evolved training ecosystem. Over 50% European market share in concealed cisterns. Behind-the-wall water damage risk creates insurmountable installer switching costs and pricing power. Multi-year median GAAP ROIC is 30.7% with tangible ROIC of 89.5% and sustained EBITDA margins above 30%.",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for European sanitary and ceramic competitor rivalry (4_riv=1), yielding Final CAP 20Y.",
        "5": 2,
        "6": "Y",
        "note": "Passes all 6 gates. Unrivaled European sanitary market hegemon (~50% share in concealed cisterns). Moat anchored by deep plumber installer loyalty, 29 specialized training academies, 50-year spare parts guarantees, and severe behind-the-wall leak liabilities that deter substitution. Maintained 30%+ EBITDA margins and >100% FCF conversion throughout the severe 2022-2025 European construction downturn. Fortress balance sheet with net debt <0.9x NI and interest coverage of 27x. [5-10Y g: European renovation volume 1.5% + pre-wall system penetration 1.5% + pricing power 2.0% - raw material/energy drag 0.5% + share repurchases 0.5%]",
        "evidence": "5-year median GAAP ROIC is 30.7% with operating tangible ROIC of 89.5%. Multi-year Owner FCF conversion averaged 107.0% (FY2025 FCF of 703.5m CHF on 597.8m CHF net income). Net debt is 505.2m CHF (0.84x NI) with 27.3x interest coverage (EBIT 762.5m CHF vs interest 27.9m CHF)."
    },
    "KRX.IE": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Brand strength, architectural spec-in, and proprietary formulation IP (QuadCore). Significant freight-radius barriers and local factory footprint insulate regional market shares in insulated panels and boards. Proven pricing power demonstrated by expanding gross margins despite volatile chemical (MDI) input costs. 5-year median GAAP ROIC is 14.0% with tangible ROIC of 31.9%.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -5Y for insulation competitor rivalry (4_riv=1) and commercial contractor procurement pressure (4_buy=1) yielding Final CAP 15Y.",
        "5": 1,
        "6": "Y",
        "note": "Passes all 6 gates. Global pioneer and market leader in advanced high-performance insulation boards and building envelope systems. Secular beneficiary of stringent global building efficiency mandates and AI data center building envelopes. Proven pricing power covering volatile chemical input costs with 14%+ multi-year ROIC and ~100% FCF conversion. Pristine balance sheet with net debt/NI at 1.6x and interest coverage >13x. [5-10Y g: commercial/industrial insulation volume 3.0% + building energy efficiency regulations 2.0% + pricing power 1.5% + bolt-on M&A 1.5% - construction cyclical drag 1.0% + buybacks/dividends 0.5%]",
        "evidence": "5-year median GAAP ROIC is 14.0% with tangible operating ROIC of 31.9%. Owner EPS compounded at 9.4% CAGR from 2022 to 2025. Owner FCF conversion averaged 96.3% over 4 years (FY2025 FCF of €580.4m on €616.9m net income). Net debt / NI stands at 1.57x with interest coverage of 13.9x (EBIT €889.3m vs interest €64.0m), well within safe balance sheet parameters."
    },
    "NIBE B.SE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "3m": "Heat pump manufacturing and installer distribution channels. However, European heat pump subsidy rollbacks, dealer inventory destocking, and aggressive competition from Asian HVAC conglomerates (Daikin, Panasonic) triggered severe margin erosion. EBIT collapsed >60% and through-cycle ROIC dropped below the 12% hurdle, demonstrating lack of independent pricing power without state subsidies.",
        "note": "Fails Gate 3b (ROIC < 12% & Pricing Power, REJECT). Swedish heat pump and climate solutions manufacturer suffered a severe margin and earnings collapse in 2023-2025 following European subsidy rollbacks, dealer destocking, and predatory Asian OEM entry (Daikin, Panasonic). EBIT plunged >60%, multi-cycle ROIC dropped below the 12% threshold, and NIBE proved to be a cyclical price-taker unable to sustain pricing above inflation without massive volume loss.",
        "evidence": "Operating profit collapsed from 5.3B SEK in 2022 to under 2.0B SEK in 2024-2025. Group ROCE fell from 17% to ~5-7%, breaching the 12% quality threshold. Heavy inventory buildups required deep production cuts and restructuring charges, proving that margins were artificially elevated by temporary government energy subsidies rather than protected by a durable economic moat."
    },
    "ROCK B.DK": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Stone wool insulation manufacturing infrastructure, energy-intensive cupola furnaces, and brand recognition. However, stone wool faces intense cross-material competition from glass wool, EPS, and polyurethane panels. High natural gas and electricity intensity make margins cyclical and cost-driven, lacking independent pricing power >= inflation across the full construction cycle.",
        "note": "Fails Gate 3b (Proof of Moat & Pricing Power, REJECT). Danish stone wool insulation manufacturer operating energy-intensive melting furnaces. While stone wool benefits from non-combustibility in fire safety regulations, product substitution from glass wool (Saint-Gobain) and foam insulation (Kingspan) is prevalent, and margins are heavily dictated by energy input costs and cyclical European residential construction rather than proprietary pricing power.",
        "evidence": "Operating margins fluctuate sharply with European energy prices and building construction cycles (ranging from 9% to 15%). While 5-year median GAAP ROIC touched ~16% during post-pandemic supply shortages, incremental returns on capital and pricing power fail to protect margins when natural gas or construction volumes normalize. Lacks high switching costs or unreplicable distribution moats."
    },
    "SGO.FR": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Extensive building materials manufacturing and light construction distribution network across Europe and North America (CertainTeed, Gyproc, Weber). However, heavy exposure to commoditized merchant distribution and low-margin building materials keeps consolidated 10-year GAAP ROIC below the 12% hurdle.",
        "note": "Fails Gate 3b (ROIC < 12%, REJECT). French multinational building materials manufacturer and distributor. Despite restructuring and portfolio rationalization under the 'Grow & Impact' plan, multi-cycle consolidated GAAP ROIC has averaged only 6-8%, falling far short of the 12% Munger moat hurdle. The business remains structurally burdened by commoditized merchant distribution, capital-intensive manufacturing, and intense price competition in plasterboard and glass.",
        "evidence": "10-year median GAAP ROIC is ~7.5%, never consistently exceeding 12% across economic cycles. Operating margins hover in the 8-11% range. The capital intensity of glass and gypsum manufacturing combined with merchant distribution working capital ties up massive capital without delivering excess economic returns."
    },
    "FDXF": {
        "3_tb": 0, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "3m": "Unrivaled physical LTL network scale with ~400 service centers, dense cross-dock infrastructure, and unmatched revenue leadership (~$9B). Moat is maintained through disciplined 4.9-5.9% annual General Rate Increases (GRIs). 5-year median GAAP ROIC is 36.0% (benefiting from Yellow's collapse). Primary erosion threats include driver wage inflation, mandatory fleet decarbonization capex under EPA/CARB, and carrier rivalry against Old Dominion, Saia, and XPO.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 20Y reduced by -10Y for LTL carrier rivalry with Old Dominion and XPO (4_riv=1), enterprise shipper freight rate negotiation (4_buy=1), and driver labor scarcity alongside fleet transition capex (4_sup=1) yielding Final CAP 10Y.",
        "5": "",
        "6": "",
        "note": "Fails Gate 4 (CAP = 10, REJECT). While FedEx Freight is the largest North American LTL carrier by revenue (~$9B) with an unreplicable ~400-terminal footprint and strong pricing discipline (4.9-5.9% annual GRIs), it faces severe secular macrotrend headwinds: persistent demographic truck driver shortages and wage inflation (Macrotrend 2, 4_sup=1), mandatory fleet decarbonization capex under EPA/CARB rules (Macrotrend 4, 4_sup=1), carrier rivalry against Old Dominion, Saia, XPO (4_riv=1), and a heavy post-spin balance sheet with negative equity resulting from a pre-spin debt dividend to parent FedEx. These structural labor, fleet transition, and competitive forces cap predictable runway at 10 years, failing Gate 4.",
        "evidence": "Revenues reached ~$9.1B in FY24 before softening to ~$8.6B in FY25 amidst an extended freight recession. Reported operating margin contracted from 19.3% in FY24 to 6.3% in FY25 ($540M operating income), with Owner FCF swinging negative (-$225M) after capex of ~$765M. Long-term debt post-separation stands at $4.26B against TTM net income of $655M, yielding negative book equity of -$497M due to pre-spin dividend recapitalization."
    },
    "JBHT": {
        "3_tb": 0, "3_ia": 1, "3_se": 1, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Scale economies shared in North American domestic intermodal (>100k containers) and private fleet replacement (DCS). However, JBHT lacks independent pricing power; intermodal must maintain a discount to highway trucking, making JBHT a price-taker during freight downturns when overcapacity triggers aggressive spot discounting.",
        "note": "Fails Gate 3b (Pricing Power & Proof of Moat, REJECT). North American intermodal and dedicated transportation leader with scale economies shared, but lacks invariant pricing power across the cycle. Intermodal rates must price at a discount to over-the-road trucking; during freight recessions and capacity gluts, JBHT becomes a cyclical price-taker, causing severe margin compression (operating margin fell from 9.4% in 2022 to 6.9% in 2024) and dragging trough ROIC below the 12% hurdle (11.2% in 2024).",
        "evidence": "10-year median ROIC is ~13.8%, but cyclical: 21.6% in 2022 (freight peak), 14.6% in 2023, 11.2% in 2024 (below 12% hurdle), and 12.4% in 2025. Operating margins compressed from 9.4% in 2022 to 6.9% in 2024. Intermodal (JBI, ~47% of revenue) and Dedicated (DCS, ~32% of revenue) provide operating scale and multi-year contract stability, but brokerage (ICS) and truckload (JBT) are exposed to brutal spot rate competition. CapEx cycles for container and tractor fleet replacement create lumpy FCF (-$118M in 2023, +$618M in 2024, +$948M in 2025). Net debt of ~$1.0B is manageable (EBIT interest coverage >10x), but structural inability to price above inflation in freight downcycles fails Gate 3b."
    },
    "ODFL": {
        "3_tb": 1, "3_ia": 2, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "3m": "Self-reinforcing network density and irreplaceable physical terminal footprint (250+ owned/zoned cross-dock service centers) create massive scale advantages. Unmatched service execution (99% on-time delivery, 0.1% cargo claims ratio vs industry average 1.5%) drives durable pricing power (revenue per cwt up 4-6% p.a. across all freight cycles). 5-year median GAAP ROIC is 32.7% (24.4% in 2025 trough) with best-in-class operating ratio (70-75% vs 85-95% for peers). Erosion threats from freight recessions or price wars are blunted by ODFL's premium service brand and low-cost non-union structure.",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for LTL peer rivalry (4_riv=1) and truck driver labor/fleet replacement costs (4_sup=1) yielding Final CAP 20Y.",
        "5": 2,
        "6": "Y",
        "note": "Passes all 6 gates. The undisputed premier less-than-truckload (LTL) motor carrier in North America with an unreplicable nationwide terminal network, 99% on-time delivery, industry-leading operating ratio, net-cash balance sheet, and proven pricing power above inflation across freight cycles. Beneficiary of supply chain reshoring and insulated from AI disruption. [5-10Y g: LTL tonnage market share gains 3.0% + revenue per cwt pricing 3.5% + terminal density reinvestment 1.0% - cyclical/cost drag 0.5% + share repurchases 1.0%]",
        "evidence": "10-year track record of industry-leading capital efficiency: 10-year GAAP and Tangible ROIC averaged >27% (peak 40.1% in 2022, trough 24.4% in 2025). Operating ratio consistently outperforms unionized and non-union peers by 800-1500 bps (75.2% in FY2025, improving to 71.5% in Q3 2026). Pristine balance sheet with essentially zero debt ($20M total debt vs $120M cash) and negligible interest expense. Outstanding capital allocation discipline demonstrated by walking away from overpriced Yellow terminal bidding in 2023, preserving balance sheet strength while continuing counter-cyclical network capex and share repurchases. Owner FCF conversion consistently near or above 100% of Net Income."
    }
}
