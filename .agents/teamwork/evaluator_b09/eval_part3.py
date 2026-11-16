"""Evaluation definitions for Batch 09 companies (part 3: companies 41 to 65)."""

PART_3 = {
    "CAT": {
        "3_tb": 1, "3_ia": 2, "3_se": 1, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "3m": "Unrivaled global dealer network (150+ independent dealers, 2,700 locations, $20B+ dealer equity) delivering guaranteed 24-48 hour machine uptime anywhere on earth. Massive machine installed base generates high-margin captive aftermarket parts and Cat Financial services. Operating margins expand to 19-21% and 10-year median GAAP ROIC is 16.1% (>25-30% in 2023-2025). Proven pricing power covering raw steel and wage inflation across multiple cycles.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 1, "4_sub": 0,
        "4n": "Initial CAP 30Y reduced by -10Y for heavy machinery rivalry with Komatsu and emerging market OEMs (4_riv=1), mining fleet buyer procurement leverage (4_buy=1), and powertrain transition capex alongside steel/labor input costs (4_sup=1) yielding Final CAP 20Y.",
        "5": 2,
        "6": "Y",
        "note": "Passes all 6 gates. Global undisputed hegemon in construction and mining equipment. Moat anchored by an unreplicable independent global dealer network with $20B+ invested capital, ensuring parts and service availability that competitors cannot match. Transformed through-cycle profitability under Jim Umpleby's O&E operating model, raising trough margins from 6% to 14%. Pristine industrial balance sheet with net cash, interest coverage >18x, and aggressive share repurchases. [5-10Y g: global infrastructure & mining replacement volume 2.0% + premium equipment pricing 2.0% + services/aftermarket mix 1.5% - cyclical downturn drag 0.5% + net share repurchases 2.0%]",
        "evidence": "10-year median GAAP ROIC is 16.1%, rising above 25% in recent years. Industrial operations generated $10B+ in annual operating cash flow with FCF conversion near 100%. Machinery, Energy & Transportation (ME&T) holds net cash, with total consolidated debt primarily residing in high-quality Cat Financial receivables. Long-term capital allocation is exemplary, returning substantially all ME&T free cash flow via dividends and share buybacks ($30B+ returned over five years)."
    },
    "CMI": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 1,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Global diesel engine design and manufacturing leadership, extensive independent distributor network, and long-standing OEM truck integration (Paccar, Navistar). However, commercial diesel engine manufacturing is cyclical and capital-intensive, facing multi-billion-dollar R&D/capex burdens for zero-emission powertrains (Accelera hydrogen/battery unit generating heavy operating losses). Through-cycle ROIC is constrained by OEM buyer power and cyclical truck volumes.",
        "note": "Fails Gate 3b (Proof of Moat & ROIC, REJECT). World leader in commercial diesel engines, but business is exposed to cyclical truck build rates, heavy capital intensity, and multi-billion-dollar powertrain decarbonization investments (Accelera unit running substantial operating losses). Consolidated returns on capital and margins fluctuate sharply with commercial vehicle cycles, lacking invariant pricing power.",
        "evidence": "Consolidated operating margins range between 8% and 11% across freight cycles. The Accelera clean tech division absorbs hundreds of millions in annual operating losses ($400M+ annually) with uncertain payback horizons. OEM truck makers (Paccar, Daimler Truck) increasingly develop proprietary engines, capping Cummins' long-term pricing power and volume."
    },
    "PCAR": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Premium heavy-duty commercial truck manufacturing (Kenworth, Peterbilt, DAF) with outstanding build quality, high resale values, and loyal dealer network. However, Class 8 commercial truck manufacturing is inherently cyclical; freight downturns trigger deep order cancellations and pricing concessions, while consolidated multi-cycle GAAP ROIC is diluted by financial services to ~11-14% with peak-to-trough volatility.",
        "note": "Fails Gate 3b (ROIC & Pricing Power, REJECT). Exceptional truck manufacturer with legendary operational discipline and premium brand equity (Kenworth, Peterbilt). However, commercial vehicle manufacturing is subject to severe 25-40% peak-to-trough order swings and fleet buyer price pressure during freight recessions, preventing invariant pricing power above inflation across the full cycle.",
        "evidence": "10-year median GAAP ROIC is ~16.5% during economic expansions, but drops sharply during freight downcycles. Commercial truck demand is highly volatile, driven by fleet operator profitability and diesel prices. PACCAR Financial carries substantial debt to finance customer truck purchases, exposing the business to credit cycle fluctuations."
    },
    "WAB": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "3m": "Locomotive manufacturing and freight rail braking systems, positive train control (PTC), and digital solutions. Strong rail equipment installed base across North American Class I railroads. However, 5-year median GAAP ROIC is only 6.9% (operating tangible ROIC ~20%), heavily diluted by $9B+ in goodwill and intangibles from the GE Transportation acquisition, failing the 12% GAAP ROIC hurdle.",
        "note": "Fails Gate 3b (ROIC < 12%, REJECT). Leading freight rail equipment and locomotive manufacturer benefiting from North American Class I rail installed base. However, multi-cycle GAAP ROIC has averaged only ~7-8%, severely depressed by $9B+ in goodwill and intangible assets from the 2019 GE Transportation merger, failing the 12% Munger moat threshold.",
        "evidence": "5-year median GAAP ROIC is 6.9% (GAAP operating margins 14-17%). Class I railroad customers (Union Pacific, BNSF, CSX, Norfolk Southern) exercise substantial buyer bargaining power and cyclically park locomotives during freight downturns, constraining pricing power and fleet replacement capex."
    },
    "ALO.FR": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Global rail transport manufacturer (TGV high-speed trains, regional trains, signaling). However, rail rolling stock manufacturing suffers from fixed-price contract overrun liabilities, low operating margins (3-5%), and massive goodwill impairments following the value-destructive Bombardier Transportation acquisition, keeping multi-cycle GAAP ROIC below 4%.",
        "note": "Fails Gate 3b (ROIC < 12%, REJECT). French rail equipment manufacturer severely damaged by the 2021 Bombardier Transportation acquisition. Heavy legacy problem contracts, negative free cash flows, low operating margins (~4-5%), and emergency capital increases (€1B rights issue in 2024) demonstrate the complete absence of pricing power and economic moat.",
        "evidence": "5-year median GAAP ROIC is just 3.4%. Massive working capital outflows and contractual execution delays on inherited Bombardier contracts forced a €1B emergency equity rights issue and €1B hybrid bond offering in 2024 to defend investment grade status. Rolling stock assembly remains a low-margin, politically dictated government procurement business."
    },
    "DTG.DE": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "World's largest commercial vehicle manufacturer by revenue (Freightliner, Mercedes-Benz, Western Star, Fuso). Premier market share in North American Class 8 trucks (~40% share). However, consolidated through-cycle GAAP ROIC hovers around 8-9%, constrained by European commercial vehicle margin softness, heavy powertrain transition capex, and extreme freight cycle volatility.",
        "note": "Fails Gate 3b (ROIC < 12%, REJECT). Global commercial vehicle market share leader, but through-cycle consolidated GAAP ROIC averages only ~8.7%, failing the 12% threshold. Commercial truck manufacturing is structurally burdened by cyclical fleet procurement downturns, European labor rigidity, and dual-powertrain R&D/capex requirements.",
        "evidence": "Since the late 2021 spinoff from Daimler AG, consolidated GAAP ROIC has averaged 8.7%. While North America (Freightliner) delivers double-digit adjusted EBIT margins, Mercedes-Benz European trucks have struggled with low single-digit margins. The business faces multi-billion-euro dual investments in diesel efficiency and zero-emission (battery/hydrogen) technologies."
    },
    "EPI A.SE": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Installed base of proprietary underground mining drill rigs driving ~68% recurring aftermarket parts, consumables, and digital automation services with high customer switching costs. Empirically proven by 5-year median GAAP ROIC of 26.6% (tangible operating ROIC >40%), operating margins consistently 19-22%, and resilient cash generation through mining capex cycles.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for mining equipment duopoly rivalry with Sandvik (4_riv=1), mining house procurement concentration (4_buy=1), and battery-electric/autonomous mining fleet transition risks (4_sub=1) yielding Final CAP 15Y.",
        "5": 2,
        "6": "Y",
        "note": "Passes all 6 gates. Global pure-play leader in underground hard-rock mining equipment and infrastructure automation. Spun from Atlas Copco with identical owner-operator engineering culture. Over two-thirds of revenue generated from mission-critical aftermarket parts, rock drilling consumables, and digital tele-remote automation services. 26%+ multi-year ROIC, ~100% FCF conversion, and fortress balance sheet with net debt/NI ~1.2x. [5-10Y g: mining ore-body extraction volume 2.5% + aftermarket consumables pricing 2.0% + automation/electrification mix 2.5% - cyclical timing drag 0.5% + net share repurchases 0.5%]",
        "evidence": "5-year median GAAP ROIC of 26.6% and tangible operating ROIC of 42.8%. Operating margins consistently ~19-22%. Free cash flow conversion normalized to 98-101% in 2024-2025. Aftermarket represents ~68% of sales, insulating cash generation from mining capex cycles. Net debt / NI stands at ~1.2x with interest coverage >13.9x."
    },
    "FLS.DK": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "3m": "Installed base of minerals processing flowsheet equipment creates an aftermarket service anchor, but returns have been diluted by cyclical original equipment pricing, lumpiness, and historical EPC project execution, keeping multi-cycle GAAP ROIC well below 12%.",
        "note": "Fails Gate 3b (ROIC & Pricing Power, REJECT). FLSmidth has successfully transformed into a pure-play mining flowsheet and aftermarket provider by divesting its cement division, but multi-cycle GAAP ROIC has averaged just 3-6% over the last five years, failing the 12% hurdle. Returns are not suppressed by a temporary calamity but by structural capital intensity, acquisition goodwill, and cyclical mining capex exposure.",
        "evidence": "Consolidated GAAP ROIC ranged between 2.3% and 5.6% from 2022 to 2024, rising toward ~9% in 2025 on continuing operations post-cement carveout. Group EBIT margins averaged 5-9% prior to 2025. While mining service revenues account for over 60% of continuing sales, large past acquisitions (TK Mining for €325m) and competitive pressure in capital equipment have kept multi-cycle returns well below cost of capital."
    },
    "HIAB.FI": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "3m": "Strong brand recognition in loader cranes (HIAB) and truck-mounted forklifts (MOFFETT) backed by service networks, but high exposure to cyclical construction and trucking capex, along with duopolistic rivalry with Palfinger, limits pricing power and leaves multi-cycle standalone GAAP ROIC unproven above 12% across full recessions.",
        "note": "Fails Gate 3b (ROIC & Pricing Power, REJECT). Spun out as the core remnant of Cargotec following the Kalmar demerger and MacGregor sale, Hiab owns premium niche brands (HIAB, MOFFETT), but heavy exposure to cyclical construction and trucking fleet capex limits sustained pricing power above inflation, and historical multi-cycle group GAAP ROIC across full downturns fails the 12% hurdle.",
        "evidence": "Hiab division generates €1.55B sales with ~13% comparable EBIT margins and high operative ROCE on localized assembly capital, but historical Cargotec group GAAP ROIC averaged 7-10% across prior cycles. The business faces steep order-intake contractions during commercial vehicle downturns (e.g. 2023-2024 orders dipped >15%) and competes aggressively against global market share leader Palfinger (25-35% share) where switching costs for fleet operators are limited at replacement cycles."
    },
    "IVG.IT": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Sub-scale European commercial truck and bus manufacturer competing against global heavyweights (Volvo, Daimler Truck, Traton). Lacks economic moat, scale advantages, or pricing power, evidenced by thin 3-5% EBIT margins and structurally sub-hurdle multi-cycle ROIC in the 3-6% range.",
        "note": "Fails Gate 3b (ROIC & Pricing Power, REJECT). Sub-scale commercial vehicle and powertrain manufacturer with low single-digit operating margins (3-5%) and multi-cycle GAAP ROIC well below the 12% hurdle. Lacks meaningful scale or pricing power against larger peers Daimler Truck, Volvo, and Traton.",
        "evidence": "GAAP ROIC has hovered between 2.6% and 8.7% since the 2022 demerger from CNH Industrial, averaging under 6%. EBIT margins of 3.7-5.8% reflect commoditized truck assembly economics and high cyclicality without the scale to fund transition capex profitably."
    },
    "METSO.FI": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Dominant global installed base in minerals processing (grinding mills, crushers, flotation cells) with 55%+ of revenue from proprietary aftermarket wear parts and field services providing high customer switching costs and pricing power above inflation.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for minerals processing rivalry with FLSmidth and Weir (4_riv=1), mining house procurement pressure (4_buy=1), and tailings/grinding technology transitions (4_sub=1) yielding Final CAP 15Y.",
        "5": 1,
        "6": "N",
        "note": "Fails Gate 6 (FCF Conversion, REJECT). Dominant mining flowsheet and wear-parts supplier with resilient 15%+ median ROIC and high aftermarket exposure, but multi-year cash conversion is only ~60% of net income due to structural working capital absorption in inventories and project receivables across cyclical swings.",
        "evidence": "While Metso boasts a 15.4% median GAAP ROIC and strong mineral processing market positions, 4-year cumulative Owner FCF (€951m) represents just 59.6% of GAAP Net Income (€1,596m), severely missing the 80% hurdle. Severe working capital drains in 2022-2023 (€376m and €449m) reflect heavy inventory and receivable cycles intrinsic to heavy mining equipment."
    },
    "VOLV B.SE": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Extensive global dealer and service network across commercial trucking and heavy equipment with strong total-cost-of-ownership (TCO) brand reputation, but cyclical truck replacement cycles and aggressive price discounting during freight downturns constrain pricing power, keeping consolidated GAAP ROIC in the 8-11% range.",
        "note": "Fails Gate 3b (ROIC & Pricing Power, REJECT). Premier global commercial truck and heavy equipment OEM, but consolidated multi-cycle GAAP ROIC (including financial services) hovers at 8-11%, below the 12% threshold. Extreme cyclicality in freight fleets and fleet capex deferrals during downturns preclude sustained pricing power above inflation.",
        "evidence": "Consolidated multi-cycle ROIC averages 8-11% across full cycles due to financial services leverage and cyclical troughs (e.g. 2020 ROCE dipped to 10.4%). While Industrial Operations delivers strong peak-cycle margins (11-14%), truck deliveries are subject to 20-30% cyclical contractions and multi-billion-euro dual powertrain (diesel and zero-emission) transition capex."
    },
    "WEIR.GB": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Global market leadership in severe-abrasion slurry pumps (Warman) and ground-engaging tools (ESCO) where proprietary metallurgy and mission-critical mine-site installed base drive ~70% recurring aftermarket revenue with exceptional pricing power.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for slurry pump and ground-engaging tools rivalry with Metso (4_riv=1), mining customer procurement pressure (4_buy=1), and mineral processing tailings technology evolution (4_sub=1) yielding Final CAP 15Y.",
        "5": 1,
        "6": "N",
        "note": "Fails Gate 6 (Peace-of-Mind Balance Sheet, REJECT). World-class mining slurry pump and wear-parts franchise (Warman, ESCO) with 70%+ recurring aftermarket revenue and high FCF conversion, but the £657m debt-funded acquisition of Micromine pushed LT debt to 6.18x NI and net debt to 4.12x NI, breaching the <= 4.0x balance sheet threshold.",
        "evidence": "While 4-year median GAAP ROIC is 12.4% and cumulative Owner FCF conversion is outstanding at 122.6% (£1,226m FCF on £1,000m NI), gross debt surged from £934.5m in 2024 to £1,526.5m in 2025 following the debt-funded Micromine transaction. LT debt / NI stands at 6.18x and net debt / NI is 4.12x, while interest coverage compressed to 5.75x, violating the <=4.0x balance sheet hurdle."
    },
    "BR": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Unassailable two-sided network effect and regulatory switching costs as the SEC-mandated proxy clearinghouse handling >80% of US beneficial share votes. 15.2% 5-year median GAAP ROIC, >100% tangible ROIC, and 98%+ client revenue retention. Annual fee updates consistently match or exceed inflation.",
        "4_ent": 0, "4_riv": 0, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for SEC proxy fee schedule reviews and custodian/broker-dealer contract negotiations (4_buy=1), yielding Final CAP 20Y.",
        "5": 1,
        "6": "Y",
        "note": "Passes all 6 gates. The indispensable regulatory plumbing of corporate governance, handling >80% of US beneficial shareholder proxy voting under SEC rules. Deeply embedded enterprise workflow across broker-dealers and custodians results in 98%+ recurring client retention. Low capital intensity enables >100% FCF conversion, supported by a conservative balance sheet with net debt/NI ~2.2x and interest coverage >8.7x. [5-10Y g: equity position & fund volume 4.0% + recurring fee pricing 2.0% + digital wealth/capital markets mix 2.0% - regulatory fee review drag 0.5% + net share repurchases 1.0%]",
        "evidence": "10-year median GAAP ROIC is 15.2%, with operating tangible ROIC well in excess of 100%. Recurring fee revenue grew at an 8% CAGR over the last decade with client revenue retention consistently between 97% and 99%. FY2025 FCF reached $872M on $841M net income (103.6% conversion). Total debt of $3.25B is serviced easily by $1.3B EBIT (8.75x interest coverage)."
    },
    "AMS.ES": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Global distribution system (GDS) two-sided network connecting hundreds of airlines with hundreds of thousands of travel agencies (~40%+ global market share) combined with mission-critical Altéa Passenger Service System (PSS) powering airline reservations, inventory, and departure control with near-zero customer churn. Demonstrated 5-year median GAAP ROIC of 17.5% and tangible ROIC >50%.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 0,
        "4n": "Initial CAP 25Y reduced by -5Y for GDS rivalry with Sabre (4_riv=1) and airline customer bargaining power / NDC direct-distribution pushes (4_buy=1) yielding Final CAP 20Y.",
        "5": 2,
        "6": "Y",
        "note": "Passes all 6 gates. The premier global airline distribution and passenger service software duopolist. Exceptional two-sided network effects in GDS combined with unassailable switching costs in Altéa PSS (contract terms 10+ years, zero voluntary migrations to in-house IT). Post-COVID travel normalization demonstrated pricing power and operating leverage with EBITDA margins returning to >40%. Pristine balance sheet with net debt/NI <1.7x and interest coverage >13.5x. [5-10Y g: global air passenger volume 3.5% + transaction fee pricing 1.5% + hospitality & airport IT mix 2.0% - airline direct NDC drag 1.0% + share repurchases 1.0%]",
        "evidence": "5-year median GAAP ROIC is 17.5% (rebounding past 19% in 2024-2025). Altéa and Navitaire process over 2 billion passengers boarded annually. Free cash flow conversion consistently exceeds 100% of Net Income (€1.2B-€1.3B FCF in 2024-2025). Net debt was reduced from €3.0B post-pandemic to €1.8B by 2025, bringing net debt / EBITDA to ~0.9x with interest coverage of 13.5x."
    },
    "CPRT": {
        "3_tb": 2, "3_ia": 2, "3_se": 1, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "Unassailable two-sided network effect connecting auto insurance carriers with global vehicle dismantlers/rebuilders (750k+ buyers across 190+ countries) coupled with an irreplaceable, environmentally permitted physical yard footprint (250+ locations, 18,000+ acres). 10-year median GAAP ROIC is 31.6% with operating margins near 40% and zero customer churn among major auto insurers.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for salvage auction rivalry with IAA/RB Global (4_riv=1), auto insurer procurement concentration (4_buy=1), and long-term autonomous crash-avoidance technology substitution risk (4_sub=1) yielding Final CAP 20Y.",
        "5": 2,
        "6": "Y",
        "note": "Passes all 6 gates. The global hegemon in salvage vehicle auction services. Combines an irreplaceable physically zoned and environmentally permitted 18,000-acre yard network with an unassailable global two-sided buyer network (VB3 auction platform), maximizing vehicle salvage recovery for auto insurers. Beneficiary of vehicle complexity, sensors, and battery costs driving higher total-loss rates. Debt-free balance sheet with >$3B in net cash/dry powder and 30%+ multi-year ROIC. [5-10Y g: total loss vehicle volume 4.0% + auction fee realization 2.5% + international buyer expansion 2.0% - vehicle longevity/EV repairability drag 0.5% + share repurchases 0.5%]",
        "evidence": "10-year median GAAP ROIC is 31.6% (operating margins consistently 38-41%). Zero funded debt with cash and short-term investments exceeding $3.2B. Owner FCF conversion averages ~95-100% despite continuous aggressive land purchases. Willis Johnson and Jay Adair have executed an Outsider capital allocation playbook, reinvesting cash flow into permanent, zoned real estate that competitors cannot replicate."
    },
    "CTAS": {
        "3_tb": 1, "3_ia": 2, "3_se": 1, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "Y",
        "3m": "Unrivaled route density across North America (~11,000 local routes, 450+ facilities) delivering the lowest unit cost per stop in corporate uniform rental and facility services. Multi-year contracts, automated laundry infrastructure, and weekly direct customer contact generate high switching costs. 10-year median GAAP ROIC is 25.9% with operating margins expanding to >21% and unbroken pricing power above inflation.",
        "4_ent": 0, "4_riv": 1, "4_buy": 0, "4_sup": 1, "4_sub": 1,
        "4n": "Initial CAP 30Y reduced by -10Y for route-based rivalry with Aramark and UniFirst (4_riv=1), route driver labor and fleet fuel costs (4_sup=1), and workplace casualization / remote work substitution headwinds (4_sub=1) yielding Final CAP 20Y.",
        "5": 2,
        "6": "Y",
        "note": "Passes all 6 gates. The undisputed market leader in corporate uniform rental and facility services with unrivaled route density. Route density creates a powerful cost moat and customer lock-in across 1M+ businesses, enabling consistent annual price increases above inflation. 40+ consecutive years of dividend increases, 25%+ multi-year ROIC, and fortress balance sheet with net debt/NI ~1.4x and interest coverage ~22x. [5-10Y g: new customer penetration 3.5% + cross-selling facility/first aid 2.5% + pricing power 2.0% - macro employment drag 0.5% + share repurchases 1.5%]",
        "evidence": "10-year median GAAP ROIC is 25.9% (operating ROIC >60% on tangible assets). Operating margins have steadily expanded from 15.5% in 2015 to >21.5% in 2025. Free cash flow conversion consistently approaches 100% of Net Income. Total debt of $3.5B is supported by $2.3B EBITDA, yielding net debt / EBITDA of ~1.1x and interest coverage of 22.3x."
    },
    "LDOS": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Largest pure-play IT and technical services contractor to the US federal government, intelligence agencies, and Department of Defense. Top-secret cleared personnel and federal contract vehicles provide entry barriers, but government contracting is characterized by competitive RFP rebids every 3-5 years, federal cost-accounting standards capping profit margins (6-8%), and 5-year median GAAP ROIC of 10.8%, below the 12% hurdle.",
        "note": "Fails Gate 3b (ROIC < 12%, REJECT). Premier US government IT and defense contractor with critical mission expertise and cleared personnel. However, government procurement dynamics cap operating margins at 7-8.5%, contracts are subject to protest and rebids, and heavy goodwill from past acquisitions keeps 5-year median GAAP ROIC below the 12% Munger threshold.",
        "evidence": "10-year median GAAP ROIC is 10.8% (GAAP operating margins 7.0-8.5%). B2G cost-plus and fixed-price incentive contracts face rigorous federal audit and procurement oversight that structurally prevent excess economic profits. Federal budget continuing resolutions introduce revenue volatility."
    },
    "AYV.FR": {
        "3_tb": 0, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Irreplaceable infrastructure & intangibles",
        "3b": "N",
        "3m": "Global corporate vehicle fleet management and operational leasing (merger of ALD Automotive and LeasePlan). Operates a fleet of ~3.4 million vehicles. However, vehicle leasing is essentially a commodity financing business exposed to interest-rate spreads, used car residual value collapses, and bank regulatory capital costs, resulting in a multi-cycle GAAP ROIC of ~4-5%, failing the 12% hurdle.",
        "note": "Fails Gate 3b (ROIC < 12%, REJECT). Leading European full-service vehicle fleet management and leasing company (ALD LeasePlan). Despite global fleet scale, vehicle leasing is fundamentally a balance-sheet-heavy financial spread business exposed to residual value volatility on electric vehicles and borrowing costs, keeping multi-cycle GAAP ROIC well below 5%.",
        "evidence": "5-year median GAAP ROIC is ~4.0%. The business carries massive debt to fund its vehicle fleet (balance sheet total assets >€70B, majority funded by bank debt and debt securities). Used EV price drops in 2023-2024 resulted in severe residual value write-downs and margin compression."
    },
    "ELIS.FR": {
        "3_tb": 1, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "3m": "Circular services in textile, hygiene, and facility rental across Europe and Latin America. Route density and industrial laundry plants provide operational scale, but heavy debt from historical acquisitions (Berendsen) and high capital expenditures for textile replacement keep 5-year median GAAP ROIC at 5.4%, well below the 12% hurdle.",
        "note": "Fails Gate 3b (ROIC < 12%, REJECT). European leader in flat linen, workwear, and hygiene services. Route density provides local operational efficiency, but high textile replacement capex, heavy debt load (€3.2B net debt), and European wage/energy inflation depress multi-cycle GAAP ROIC to ~5-6%, failing Gate 3b.",
        "evidence": "5-year median GAAP ROIC is 5.4% (operating margin 13-15%). Operating profits are heavily absorbed by textile amortization and net financial expense (€160M+ annually). Net debt stands at ~€3.2B (~2.0x EBITDA), leaving through-cycle capital returns far below the 12% threshold."
    },
    "ISS.DK": {
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "None",
        "3b": "N",
        "3m": "Global integrated facility services (cleaning, catering, technical services, workplace management). Facility management is a highly competitive, labor-intensive service business characterized by low switching costs, thin operating margins (3.5-4.5%), and periodic contract turnover, completely lacking a durable economic moat.",
        "note": "Fails Gate 3 (3a=None, 3b=N, REJECT). Danish multinational facility services provider operating in cleaning and workplace support. Thin operating margins (~4%), high staff turnover, wage inflation, and aggressive enterprise client procurement rebids preclude pricing power and keep through-cycle ROIC below the 12% threshold.",
        "evidence": "Operating margins consistently hover between 3.5% and 4.5%. 5-year median GAAP ROIC is ~11.3% (and negative during restructuring years). Integrated facility service contracts are frequently re-tendered on price by corporate clients, resulting in zero pricing power."
    },
    "MTO.GB": {
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "None",
        "3b": "N",
        "3m": "UK facilities management and professional services provider (cleaning, security, engineering maintenance). B2B facility service contracts are awarded via competitive procurement tenders with limited pricing power, operating margins of 3.5-5.0%, and zero structural switching barriers.",
        "note": "Fails Gate 3 (3a=None, 3b=N, REJECT). UK facilities management provider operating in competitive building cleaning, security, and maintenance services. B2B service contracts face regular competitive rebidding, limiting operating margins to ~4-5% and preventing the establishment of an enduring economic moat.",
        "evidence": "Operating margins average 3.5-4.8% on £4.5B+ of revenue. While recent cash generation has improved under post-turnaround management, facilities management is an inherently contestable market where corporate and public sector clients switch providers for small basis-point savings."
    },
    "SRP.GB": {
        "3_tb": 0, "3_ia": 0, "3_se": 0, "3_rd": 0,
        "3a": "None",
        "3b": "N",
        "3m": "International public services contractor providing defense, justice, immigration, and transport services to governments. Operates in B2G markets facing sovereign monopsony buyers, political scrutiny, capped margin structures (5-6%), and 5-year median GAAP ROIC below the 12% hurdle.",
        "note": "Fails Gate 3b (ROIC < 12%, REJECT). International public services outsourcing contractor facing sovereign monopsony buyers, periodic competitive re-tenders, razor-thin operating margins (~5.1-5.7%), and sub-hurdle multi-cycle GAAP ROIC (~9.5-10.2%) lacking structural pricing power.",
        "evidence": "Serco's underlying operating margin hovers between 5.1% and 5.7% (FY2023-2025). 5-year median GAAP ROIC is ~9.5-10.2%, persistently below the 12% quality threshold. B2G contracts across defense, justice, and citizen services are subject to competitive rebidding, political scrutiny, and capped margin structures that prevent excess economic returns."
    },
    "AME": {
        "3_tb": 2, "3_ia": 1, "3_se": 0, "3_rd": 0,
        "3a": "Toll booth & switching costs",
        "3b": "Y",
        "3m": "High customer switching costs and prohibitive qualification/recertification barriers (FAA, FDA, ISO) across aerospace, medtech, and laboratory testing lock in customers, enabling steady 2-3% pricing power above inflation with zero churn. 10-year median GAAP ROIC of 13.1-14.1% and operating margins expanding from 20.6% in 2016 to 25.8% in 2025 confirm moat durability against customer consolidation or industrial cyclicality.",
        "4_ent": 0, "4_riv": 1, "4_buy": 1, "4_sup": 0, "4_sub": 1,
        "4n": "Initial CAP 25Y reduced by -10Y for niche instrumentation rivalry with Fortive and Roper (4_riv=1), aerospace/medtech OEM procurement pressure (4_buy=1), and technological evolution in sensing/testing architectures (4_sub=1) yielding Final CAP 15Y.",
        "5": 1,
        "6": "Y",
        "note": "Passes all 6 gates. Premier niche instrumentation and precision electromechanical compounder with unassailable switching costs across aerospace, medtech, and automation. High pricing power demonstrated by consistent 2-3% annual price increases with zero churn. Highly resilient across all 5 macrotrends with negligible capex needs (<2% of sales) and fortress balance sheet (interest coverage >20x, net debt/EBITDA <0.8x). [5-10Y g: organic volume 3.0% + niche pricing power 2.5% + bolt-on M&A reinvestment 2.5% - cost/integration drag 0.5% + share repurchases 1.0%]",
        "evidence": "10-year median GAAP ROIC of 14.1% and operating ROIC >200% on tangible capital. Unbroken 10-year Owner EPS CAGR of 10.96% ($2.69 in 2016 to $7.67 in 2025) demonstrating pristine peak-to-peak compounding through the 2020 pandemic. FCF conversion averages 107.6% of net income with capex under 1.8% of sales ($130M on $7.4B revenue). Highly disciplined M&A playbook proven by rapid deleveraging following the $1.9B Paragon Medical acquisition, reducing net debt to 0.42x annual net income by 2025. Interest coverage stands at 20.9x."
    },
    "BE": {
        "3_tb": 1, "3_ia": 0, "3_se": 0, "3_rd": 1,
        "3a": "Toll booth & switching costs",
        "3b": "N",
        "3m": "Proprietary solid oxide fuel cell (SOFC) stack intellectual property (400+ patents) and long-term on-site service/maintenance contracts create switching costs, but economic returns are structurally depressed by high stack refurbishment/replacement expenses and competitive displacement risks from gas turbines, reciprocating engines, and grid interconnections.",
        "note": "Fails Gate 3b (ROIC < 12%, REJECT). While Bloom Energy captures strong 'speed-to-power' tailwinds from AI data centres and C&I customers facing multi-year grid interconnect queues, it fails to demonstrate empirical moat proof or economic profitability. 5-year median GAAP ROIC is negative (-27.4%), burdened by cumulative net losses since inception (accumulated deficit of ~$3.99B through FY2025), high periodic stack replacement costs, and chronic reliance on convertible debt offerings and equity dilution.",
        "evidence": "10-year and 5-year median GAAP ROIC is negative (-27.4%), failing the 12% capital efficiency hurdle. Despite top-line revenue scaling to $2.02B (FY25), Bloom continues to generate GAAP net losses (-$88.4M in FY25), with GAAP operating margins remaining in low single digits (1.5% in FY24, 3.6% in FY25). Accumulated deficit stood at $3.99B at the end of FY25. Capital structure features heavy use of convertible senior notes (e.g., 2.5% Green Notes due 2025, 3.0% Green Notes due 2029) and repeated debt-for-equity exchanges to manage debt maturities and liquidity."
    }
}
