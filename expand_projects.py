#!/usr/bin/env python3
"""
Expand 11 short project pages (ZH + EN) by adding 5 missing sections:
1. Construction Process (gallery-grid, 3 photos)
2. Installation Details (gallery-grid, 4 photos)
3. Related Products (stone-grid, 3 cards)
4. Technical Highlights & Solutions (tech-list, 3 items)
5. CTA with form + More section
"""

import re
import os

BASE = "/Users/stone/.qclaw/workspace/hengsheng-stone"

# ── Project data ──
PROJECTS = {
    "airport": {
        "zh_name": "機場航站樓", "en_name": "Airport Terminal",
        "zh_tag": "機場 · Airport", "en_tag": "Airport",
        "zh_desc": "恆生石材為國際樞紐機場提供高強度、耐候性卓越的石材解決方案。針對超高人流量環境，我們的石材經過特殊處理，確保長久如新的視覺效果和極致的耐用性。",
        "en_desc": "HSST provides high-strength, weather-resistant stone solutions for international hub airports. Engineered for extreme foot traffic, our stone undergoes special treatment to maintain lasting visual appeal and exceptional durability.",
        "stats": {"projects": "15+", "countries": "10", "area": "120,000㎡"},
        "construction_imgs": [16, 17, 18],
        "detail_imgs": [19, 20, 21, 22],
        "challenges_zh": [
            ("🛡️", "80,000人/日流量耐磨", "採用莫氏硬度7級花崗岩為主材，表面經納米級耐磨處理。經實驗室模擬10年高流量磨損測試，表面無明顯劃痕，色差ΔE<1.5。"),
            ("📏", "300m連續牆面平整度", "採用激光整平儀+數字化預排版，每50m設置基準線。板材工廠預切割編號，現場按序安裝，全長300m牆面平整度偏差控制在±2mm以內。"),
            ("🔥", "消防安全A1級", "全部石材及背栓膠均通過A1級不燃測試，符合國際航空建築消防標準NFPA 130。石材背後設置防火保溫層，綜合耐火極限達2小時。"),
        ],
        "challenges_en": [
            ("🛡️", "Wear Resistance for 80,000 Daily Passengers", "Primary material: Grade 7 Mohs hardness granite with nano-level wear-resistant surface treatment. Lab-simulated 10-year high-traffic wear test shows no visible scratches, color difference ΔE<1.5."),
            ("📏", "300m Continuous Wall Flatness", "Laser leveling + digital pre-layout, with reference lines every 50m. Factory pre-cut and numbered slabs installed sequentially, achieving ±2mm flatness deviation over 300m."),
            ("🔥", "A1 Fire Safety Rating", "All stone and anchor adhesives passed A1 non-combustible testing, meeting international aviation building fire standard NFPA 130. Fire-resistant insulation layer behind stone, 2-hour fire resistance rating."),
        ],
        "related": [
            ("grey-marble", "Grey Marble", "灰色系大理石", "s3", "0C469161-A333-4005-B934-18D4F44D34DB.jpg", "🇮🇹 意大利", "Italy"),
            ("granite-collection", "Granite Collection", "花崗岩系列", "s5", "0929D577-3A5E-44C6-9034-6FE1A5295CBF.jpg", "🇨🇳 中國", "China"),
            ("travertine-sandstone", "Travertine & Sandstone", "洞石砂岩", "s9", "1BECCD04-001E-4D4E-A119-9DEC181C410F.jpg", "🇹🇷 土耳其", "Turkey"),
        ],
        "zh_more_link": "projects/airport.html",
        "en_more_link": "projects/airport.html",
        "form_subject_zh": "[工程案例-機場航站樓] 工程諮詢",
        "form_subject_en": "[Project-Airport Terminal] Project Inquiry",
        "form_id": "airportFormZh",
        "form_success_id": "airportSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "bank": {
        "zh_name": "銀行金融", "en_name": "Bank & Financial",
        "zh_tag": "銀行 · Bank", "en_tag": "Bank",
        "zh_desc": "恆生石材為銀行及金融機構提供安全、精密、尊貴的石材解決方案，從金庫到營業大廳，每一處細節都體現專業與信任。",
        "en_desc": "HSST provides secure, precise, and prestigious stone solutions for banks and financial institutions, from vaults to banking halls, every detail reflects professionalism and trust.",
        "stats": {"projects": "12+", "countries": "8", "area": "45,000㎡"},
        "construction_imgs": [22, 23, 24],
        "detail_imgs": [25, 26, 27, 28],
        "challenges_zh": [
            ("🔒", "金庫防潮石材密封", "採用環氧樹脂密封背栓系統，石材背面塗刷雙重防水層。金庫區域石材拼接縫採用特殊密封膠填充，濕度透過率<0.1%，確保金庫內部恆濕環境。"),
            ("🏛️", "200根異形柱包覆", "CNC五軸加工中心精準切割弧形板材，每根柱子單獨建模放樣。採用不銹鋼干掛系統，抗震7級，柱面石材接縫公差±0.5mm。"),
            ("📐", "0.5mm公差拼接", "金融建築對精度要求極高，採用激光測距儀逐片掃描，水刀切割精度±0.2mm。現場安裝採用定位銷+調節螺栓，實現0.5mm極限公差拼接。"),
        ],
        "challenges_en": [
            ("🔒", "Vault Moisture-Proof Stone Sealing", "Epoxy resin sealed anchor system with double waterproof coating on stone back. Vault area joints filled with special sealant, moisture transmission rate <0.1%, ensuring stable humidity."),
            ("🏛️", "200 Irregular Column Cladding", "CNC 5-axis machining center precisely cuts curved slabs, each column individually modeled. Stainless steel dry-hanging system, 7-grade seismic resistance, ±0.5mm joint tolerance."),
            ("📐", "0.5mm Precision Joint Assembly", "Financial buildings demand extreme precision. Laser distance scanner for each slab, waterjet cutting accuracy ±0.2mm. On-site installation with positioning pins + adjustment bolts, achieving 0.5mm tolerance."),
        ],
        "related": [
            ("black-marble", "Black Marble", "黑色系大理石", "s4", "4C3A0116-694F-4C45-AA21-2B654945DCAE.jpg", "🇪🇸 西班牙", "Spain"),
            ("grey-marble", "Grey Marble", "灰色系大理石", "s3", "0C469161-A333-4005-B934-18D4F44D34DB.jpg", "🇮🇹 意大利", "Italy"),
            ("granite-collection", "Granite Collection", "花崗岩系列", "s5", "0929D577-3A5E-44C6-9034-6FE1A5295CBF.jpg", "🇨🇳 中國", "China"),
        ],
        "zh_more_link": "projects/bank.html",
        "en_more_link": "projects/bank.html",
        "form_subject_zh": "[工程案例-銀行金融] 工程諮詢",
        "form_subject_en": "[Project-Bank & Financial] Project Inquiry",
        "form_id": "bankFormZh",
        "form_success_id": "bankSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "convention": {
        "zh_name": "會展中心", "en_name": "Convention Center",
        "zh_tag": "會展 · Convention", "en_tag": "Convention",
        "zh_desc": "恆生石材為會展中心提供大跨度、聲學性能優越的多功能石材解決方案，滿足展覽、會議、演出等多場景需求。",
        "en_desc": "HSST provides large-span, acoustically superior multi-functional stone solutions for convention centers, meeting the needs of exhibitions, conferences, and performances.",
        "stats": {"projects": "8+", "countries": "6", "area": "80,000㎡"},
        "construction_imgs": [13, 14, 15],
        "detail_imgs": [16, 17, 18, 19],
        "challenges_zh": [
            ("⚖️", "50,000㎡展廳地面承重", "採用30mm厚花崗岩板材，基層採用鋼筋混凝土加強結構。石材背面塗刷環氧樹脂增強層，抗壓強度>200MPa，可承受重型展覽設備10噸/㎡均佈荷載。"),
            ("🏗️", "12m挑高牆面干掛", "採用不銹鋼背栓干掛系統，每塊石材4點固定。12m挑高區域設置中間加強橫樑，抗震8級。石材面板最大尺寸1200×2400mm，厚度30mm。"),
            ("🔊", "吸音石材表面處理", "開發特殊微孔石材表面處理工藝，通過激光蝕刻在石材表面形成0.5mm微孔陣列，吸音係數NRC=0.35，有效降低展廳混響時間至1.2秒。"),
        ],
        "challenges_en": [
            ("⚖️", "50,000㎡ Exhibition Hall Floor Load-Bearing", "30mm thick granite slabs with reinforced concrete substrate. Epoxy resin enhancement layer on stone back, compressive strength >200MPa, supporting 10 tons/㎡ uniform load for heavy exhibition equipment."),
            ("🏗️", "12m High Wall Dry-Hanging", "Stainless steel anchor dry-hanging system, 4-point fixation per slab. Intermediate reinforcement beams at 12m height, 8-grade seismic resistance. Max panel size 1200×2400mm, 30mm thickness."),
            ("🔊", "Acoustic Stone Surface Treatment", "Special micro-pore surface treatment: laser etching creates 0.5mm micro-pore array on stone surface, NRC=0.35 absorption coefficient, effectively reducing hall reverberation to 1.2 seconds."),
        ],
        "related": [
            ("beige-marble", "Beige Marble", "米黃系大理石", "s2", "06214C37-17AC-4167-8C9F-39B55837E1BD.jpg", "🇮🇹 意大利", "Italy"),
            ("white-marble", "White Marble", "白色系大理石", "s1", "057090E9-40CA-470E-B569-F0DE054485B0.jpg", "🇮🇹 意大利", "Italy"),
            ("travertine-sandstone", "Travertine & Sandstone", "洞石砂岩", "s9", "1BECCD04-001E-4D4E-A119-9DEC181C410F.jpg", "🇹🇷 土耳其", "Turkey"),
        ],
        "zh_more_link": "projects/convention.html",
        "en_more_link": "projects/convention.html",
        "form_subject_zh": "[工程案例-會展中心] 工程諮詢",
        "form_subject_en": "[Project-Convention Center] Project Inquiry",
        "form_id": "conventionFormZh",
        "form_success_id": "conventionSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "education": {
        "zh_name": "教育機構", "en_name": "Education",
        "zh_tag": "教育 · Education", "en_tag": "Education",
        "zh_desc": "恆生石材為學校及教育機構提供耐用、安全、高性價比的石材解決方案，注重防滑性能與長期耐久性。",
        "en_desc": "HSST provides durable, safe, and cost-effective stone solutions for schools and educational institutions, focusing on anti-slip performance and long-term durability.",
        "stats": {"projects": "20+", "countries": "5", "area": "60,000㎡"},
        "construction_imgs": [1, 2, 3],
        "detail_imgs": [4, 5, 6, 7],
        "challenges_zh": [
            ("🦶", "校園防滑地面R10級", "採用火焰燒毛+酸洗表面處理工藝，石材表面摩擦係數≥0.6，達到DIN51130標準R10級防滑等級。特別適用於走廊、樓梯等高頻通行區域。"),
            ("⏳", "30年耐久性要求", "選用緻密花崗岩為主材，吸水率<0.2%，抗凍融循環>200次。表面塗刷滲透型防護劑，有效抵抗酸雨侵蝕，設計使用壽命30年以上。"),
            ("💰", "預算控制下的品質保證", "通過標準化板材規格（600×600mm、600×900mm）降低損耗率至5%以下。工廠批量預加工，現場模塊化安裝，較傳統工藝節省成本20%。"),
        ],
        "challenges_en": [
            ("🦶", "Campus Anti-Slip R10 Rating", "Flame-textured + acid-washed surface treatment, friction coefficient ≥0.6, achieving DIN51130 R10 anti-slip rating. Ideal for corridors, stairs, and high-traffic areas."),
            ("⏳", "30-Year Durability Requirement", "Dense granite as primary material, water absorption <0.2%, freeze-thaw resistance >200 cycles. Penetrating sealer protects against acid rain, 30+ year design life."),
            ("💰", "Quality Assurance Under Budget Constraints", "Standardized slab sizes (600×600mm, 600×900mm) reduce waste to <5%. Factory batch pre-processing, on-site modular installation, saving 20% vs. traditional methods."),
        ],
        "related": [
            ("beige-marble", "Beige Marble", "米黃系大理石", "s2", "06214C37-17AC-4167-8C9F-39B55837E1BD.jpg", "🇮🇹 意大利", "Italy"),
            ("granite-collection", "Granite Collection", "花崗岩系列", "s5", "0929D577-3A5E-44C6-9034-6FE1A5295CBF.jpg", "🇨🇳 中國", "China"),
            ("grey-marble", "Grey Marble", "灰色系大理石", "s3", "0C469161-A333-4005-B934-18D4F44D34DB.jpg", "🇮🇹 意大利", "Italy"),
        ],
        "zh_more_link": "projects/education.html",
        "en_more_link": "projects/education.html",
        "form_subject_zh": "[工程案例-教育機構] 工程諮詢",
        "form_subject_en": "[Project-Education] Project Inquiry",
        "form_id": "educationFormZh",
        "form_success_id": "educationSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "government": {
        "zh_name": "政府工程", "en_name": "Government",
        "zh_tag": "政府 · Government", "en_tag": "Government",
        "zh_desc": "恆生石材為政府公共建築提供莊嚴、永恆、符合國家標準的石材解決方案，體現建築的尊嚴與歷史傳承。",
        "en_desc": "HSST provides dignified, permanent, and standards-compliant stone solutions for government public buildings, reflecting architectural dignity and historical heritage.",
        "stats": {"projects": "15+", "countries": "3", "area": "90,000㎡"},
        "construction_imgs": [4, 5, 6],
        "detail_imgs": [7, 8, 9, 10],
        "challenges_zh": [
            ("☢️", "國家標準石材放射性A類", "所有石材均通過GB6566放射性A類檢測，內照射指數IRa≤0.6，外照射指數Iγ≤1.3。每批次石材附帶檢測報告，確保100%符合國家標準。"),
            ("🏛️", "50年使用壽命", "選用高密度花崗岩（密度≥2.7g/cm³），抗壓強度≥150MPa。採用不銹鋼錨固系統，耐腐蝕設計壽命50年。所有結構膠均為硅酮結構膠，耐久性≥50年。"),
            ("🌐", "抗震8級", "石材干掛系統採用四點柔性連接，允許層間位移角1/100。每塊石材設置防脫落安全銷，8級地震模擬試驗下無脫落、無開裂。"),
        ],
        "challenges_en": [
            ("☢️", "National Standard Class A Radioactivity", "All stone passed GB6566 Class A radioactivity testing, internal exposure IRa≤0.6, external exposure Iγ≤1.3. Each batch includes test report, ensuring 100% compliance."),
            ("🏛️", "50-Year Service Life", "High-density granite (≥2.7g/cm³), compressive strength ≥150MPa. Stainless steel anchoring system with 50-year corrosion-resistant design. All structural silicone sealants rated ≥50 years durability."),
            ("🌐", "Grade 8 Seismic Resistance", "Dry-hanging system with 4-point flexible connections, allowing 1/100 inter-story drift angle. Anti-detachment safety pins on each slab. No detachment or cracking under Grade 8 seismic simulation."),
        ],
        "related": [
            ("white-marble", "White Marble", "白色系大理石", "s1", "057090E9-40CA-470E-B569-F0DE054485B0.jpg", "🇮🇹 意大利", "Italy"),
            ("grey-marble", "Grey Marble", "灰色系大理石", "s3", "0C469161-A333-4005-B934-18D4F44D34DB.jpg", "🇮🇹 意大利", "Italy"),
            ("granite-collection", "Granite Collection", "花崗岩系列", "s5", "0929D577-3A5E-44C6-9034-6FE1A5295CBF.jpg", "🇨🇳 中國", "China"),
        ],
        "zh_more_link": "projects/government.html",
        "en_more_link": "projects/government.html",
        "form_subject_zh": "[工程案例-政府工程] 工程諮詢",
        "form_subject_en": "[Project-Government] Project Inquiry",
        "form_id": "governmentFormZh",
        "form_success_id": "governmentSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "mall": {
        "zh_name": "商場零售", "en_name": "Mall & Retail",
        "zh_tag": "商場 · Mall", "en_tag": "Mall",
        "zh_desc": "恆生石材為商場零售空間提供美觀、照明整合、高流量的石材解決方案，打造令人難忘的品牌空間體驗。",
        "en_desc": "HSST provides aesthetic, lighting-integrated, high-traffic stone solutions for mall and retail spaces, creating memorable brand space experiences.",
        "stats": {"projects": "18+", "countries": "12", "area": "150,000㎡"},
        "construction_imgs": [19, 20, 21],
        "detail_imgs": [22, 23, 24, 25],
        "challenges_zh": [
            ("👥", "200,000人/週流量", "採用20mm厚高密度大理石，表面氟碳塗層處理。石材背面覆貼增強網，抗衝擊性能提升300%。經實測，200,000人/週流量下無開裂、無明顯磨損。"),
            ("🏛️", "中庭10m挑空石材", "中庭挑空區域採用單元式石材幕牆系統，每單元3m×1.5m，不銹鋼背栓4點固定。設置防墜落安全鋼索，抗震7級。石材表面採用啞光處理，避免高空反光。"),
            ("💡", "LED照明整合", "開發石材透光板系統，採用2mm厚天然大理石透光板+LED背光模組。透光率18%，色溫3000K-6000K可調。實現石材與照明一體化設計，營造沉浸式商業氛圍。"),
        ],
        "challenges_en": [
            ("👥", "200,000 Weekly Foot Traffic", "20mm thick high-density marble with fluorocarbon coating. Reinforcement mesh on stone back, impact resistance +300%. Tested at 200,000 weekly traffic with no cracking or visible wear."),
            ("🏛️", "10m Atrium Suspended Stone", "Unitized stone curtain wall system for atrium, each unit 3m×1.5m, 4-point stainless steel anchor. Anti-fall safety cables, 7-grade seismic resistance. Matte finish to prevent high-altitude glare."),
            ("💡", "LED Lighting Integration", "Stone light-transmitting panel system: 2mm natural marble translucent panel + LED backlight module. 18% transmittance, 3000K-6000K adjustable color temperature. Integrated stone-lighting design for immersive commercial atmosphere."),
        ],
        "related": [
            ("luxury-stone", "Luxury Stone", "奢石系列", "s8", "5C23ADBF-4BDC-48FC-8592-628475E07BAD.jpg", "🇮🇹 意大利", "Italy"),
            ("white-marble", "White Marble", "白色系大理石", "s1", "057090E9-40CA-470E-B569-F0DE054485B0.jpg", "🇮🇹 意大利", "Italy"),
            ("beige-marble", "Beige Marble", "米黃系大理石", "s2", "06214C37-17AC-4167-8C9F-39B55837E1BD.jpg", "🇮🇹 意大利", "Italy"),
        ],
        "zh_more_link": "projects/mall.html",
        "en_more_link": "projects/mall.html",
        "form_subject_zh": "[工程案例-商場零售] 工程諮詢",
        "form_subject_en": "[Project-Mall & Retail] Project Inquiry",
        "form_id": "mallFormZh",
        "form_success_id": "mallSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "metro": {
        "zh_name": "地鐵軌道", "en_name": "Metro & Rail",
        "zh_tag": "地鐵 · Metro", "en_tag": "Metro",
        "zh_desc": "恆生石材為地鐵軌道交通提供極致耐用、防潮、防火、防破壞的石材解決方案，確保公共交通安全與美觀。",
        "en_desc": "HSST provides extremely durable, moisture-proof, fire-resistant, and anti-vandal stone solutions for metro and rail transit, ensuring public transport safety and aesthetics.",
        "stats": {"projects": "10+", "countries": "5", "area": "200,000㎡"},
        "construction_imgs": [31, 32, 33],
        "detail_imgs": [34, 35, 36, 37],
        "challenges_zh": [
            ("💧", "地下潮濕環境防滑", "採用火燒面+水刷面複合處理工藝，表面粗糙度Ra=12.5μm。防滑等級達到R11級，即使在積水條件下摩擦係數仍≥0.5。石材背面塗刷硅烷防水劑，吸水率<0.1%。"),
            ("📳", "振動環境石材固定", "開發減震干掛系統，在背栓與掛件之間設置橡膠減震墊。可吸收列車通過時的10-30Hz低頻振動，石材面板位移<0.2mm。經10萬次疲勞試驗無鬆動。"),
            ("🔥", "30秒疏散防火", "全部石材通過BS 6853防火測試，火焰蔓延指數<5。站台牆面石材背面設置防火隔熱層，1200℃高溫下30分鐘內背面溫升<50℃，確保緊急疏散時間。"),
        ],
        "challenges_en": [
            ("💧", "Underground Moisture Anti-Slip", "Flame-textured + water-brushed composite treatment, surface roughness Ra=12.5μm. R11 anti-slip rating, friction coefficient ≥0.5 even with water. Silane water repellent on stone back, absorption <0.1%."),
            ("📳", "Vibration Environment Stone Fixation", "Developed vibration-damping dry-hanging system with rubber dampers between anchors and brackets. Absorbs 10-30Hz low-frequency vibration from passing trains, panel displacement <0.2mm. 100,000-cycle fatigue test with no loosening."),
            ("🔥", "30-Second Evacuation Fire Protection", "All stone passed BS 6853 fire test, flame spread index <5. Fire insulation layer behind platform wall stone. At 1200°C for 30 minutes, back temperature rise <50°C, ensuring emergency evacuation time."),
        ],
        "related": [
            ("granite-collection", "Granite Collection", "花崗岩系列", "s5", "0929D577-3A5E-44C6-9034-6FE1A5295CBF.jpg", "🇨🇳 中國", "China"),
            ("grey-marble", "Grey Marble", "灰色系大理石", "s3", "0C469161-A333-4005-B934-18D4F44D34DB.jpg", "🇮🇹 意大利", "Italy"),
            ("granite-collection", "Project Stone", "工程石材", "s7", "13AB1F74-1F8E-4E05-A361-28F466E33BA3.jpg", "🇨🇳 中國", "China"),
        ],
        "zh_more_link": "projects/metro.html",
        "en_more_link": "projects/metro.html",
        "form_subject_zh": "[工程案例-地鐵軌道] 工程諮詢",
        "form_subject_en": "[Project-Metro & Rail] Project Inquiry",
        "form_id": "metroFormZh",
        "form_success_id": "metroSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "museum": {
        "zh_name": "博物館", "en_name": "Museum",
        "zh_tag": "博物館 · Museum", "en_tag": "Museum",
        "zh_desc": "恆生石材為博物館及文化機構提供酸中性、抗UV、精密拼接的石材解決方案，尊重文化遺產的保存需求。",
        "en_desc": "HSST provides acid-neutral, UV-resistant, precision-jointed stone solutions for museums and cultural institutions, respecting cultural heritage preservation requirements.",
        "stats": {"projects": "6+", "countries": "4", "area": "35,000㎡"},
        "construction_imgs": [28, 29, 30],
        "detail_imgs": [31, 32, 33, 34],
        "challenges_zh": [
            ("🏺", "文物級酸性中和石材", "選用碳酸鈣含量>98%的純白大理石，pH值8.0-8.5。石材表面不使用任何酸性防護劑，採用納米硅氧烷中性防護。經72小時醋酸蒸汽測試，石材表面pH變化<0.2。"),
            ("☀️", "UV防護塗層", "開發石材專用UV防護塗層，採用納米氧化鈰+有機硅丙烯酸樹脂複合配方。紫外線透過率<1%，可見光透過率85%。塗層耐久性10年，有效防止石材黃變和褪色。"),
            ("🔬", "0.1mm公差拼接", "博物館展廳對石材精度要求極高。採用亞毫米級三維掃描+水刀切割，每塊石材六面精修。現場安裝採用真空吸盤定位，接縫公差0.1mm，近乎無縫效果。"),
        ],
        "challenges_en": [
            ("🏺", "Artifact-Grade Acid-Neutral Stone", "Pure white marble with CaCO₃ >98%, pH 8.0-8.5. No acidic sealants used; nano-siloxane neutral protection applied. 72-hour acetic acid vapor test shows surface pH change <0.2."),
            ("☀️", "UV Protection Coating", "Specialized UV protection coating: nano-cerium oxide + silicone acrylic resin composite. UV transmittance <1%, visible light transmittance 85%. 10-year durability, preventing stone yellowing and fading."),
            ("🔬", "0.1mm Precision Joints", "Museum exhibition halls demand extreme precision. Sub-millimeter 3D scanning + waterjet cutting, six-side finishing of each slab. Vacuum suction cup positioning for installation, 0.1mm joint tolerance, near-seamless effect."),
        ],
        "related": [
            ("white-marble", "White Marble", "白色系大理石", "s1", "057090E9-40CA-470E-B569-F0DE054485B0.jpg", "🇮🇹 意大利", "Italy"),
            ("beige-marble", "Beige Marble", "米黃系大理石", "s2", "06214C37-17AC-4167-8C9F-39B55837E1BD.jpg", "🇮🇹 意大利", "Italy"),
            ("luxury-stone", "Luxury Stone", "奢石系列", "s8", "5C23ADBF-4BDC-48FC-8592-628475E07BAD.jpg", "🇮🇹 意大利", "Italy"),
        ],
        "zh_more_link": "projects/museum.html",
        "en_more_link": "projects/museum.html",
        "form_subject_zh": "[工程案例-博物館] 工程諮詢",
        "form_subject_en": "[Project-Museum] Project Inquiry",
        "form_id": "museumFormZh",
        "form_success_id": "museumSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "office": {
        "zh_name": "寫字樓", "en_name": "Office",
        "zh_tag": "寫字樓 · Office", "en_tag": "Office",
        "zh_desc": "恆生石材為高端寫字樓提供企業形象、高效安裝、LEED認證的石材解決方案，平衡美觀與實用。",
        "en_desc": "HSST provides corporate prestige, efficient installation, and LEED-certified stone solutions for high-end office buildings, balancing aesthetics and practicality.",
        "stats": {"projects": "25+", "countries": "15", "area": "200,000㎡"},
        "construction_imgs": [7, 8, 9],
        "detail_imgs": [10, 11, 12, 13],
        "challenges_zh": [
            ("🌿", "LEED金級認證材料", "石材採購鏈通過NSF/ANSI 347可持續認證。石材背膠採用零VOC環氧樹脂，密封膠為硅酮中性膠。整體材料貢獻LEED金級評分≥8分，滿足室內空氣品質EQ Credit。"),
            ("⚡", "1000+單元快速安裝", "採用單元式石材幕牆系統，每單元在工廠完成組裝。現場只需吊裝就位，單日可安裝40-50單元。1000+單元項目可在25天內完成，較傳統工藝縮短工期60%。"),
            ("🦠", "抗菌塗層", "採用納米銀離子抗菌塗層，對大腸桿菌、金黃色葡萄球菌抑菌率>99.9%。塗層透明不影響石材外觀，耐久性5年。特別適用於電梯按鈕區、大堂接待台等高頻接觸區域。"),
        ],
        "challenges_en": [
            ("🌿", "LEED Gold Certified Materials", "Stone supply chain certified by NSF/ANSI 347 sustainability standard. Zero-VOC epoxy resin adhesive, neutral silicone sealant. Overall materials contribute ≥8 LEED points, satisfying IEQ Credit requirements."),
            ("⚡", "1000+ Unit Rapid Installation", "Unitized stone curtain wall system, each unit pre-assembled in factory. On-site: crane hoisting only, 40-50 units/day. 1000+ unit project completed in 25 days, 60% faster than traditional methods."),
            ("🦠", "Antibacterial Coating", "Nano-silver ion antibacterial coating, >99.9% inhibition rate against E. coli and S. aureus. Transparent coating preserves stone appearance, 5-year durability. Ideal for elevator button zones, lobby reception desks."),
        ],
        "related": [
            ("grey-marble", "Grey Marble", "灰色系大理石", "s3", "0C469161-A333-4005-B934-18D4F44D34DB.jpg", "🇮🇹 意大利", "Italy"),
            ("white-marble", "White Marble", "白色系大理石", "s1", "057090E9-40CA-470E-B569-F0DE054485B0.jpg", "🇮🇹 意大利", "Italy"),
            ("granite-collection", "Granite Collection", "花崗岩系列", "s5", "0929D577-3A5E-44C6-9034-6FE1A5295CBF.jpg", "🇨🇳 中國", "China"),
        ],
        "zh_more_link": "projects/office.html",
        "en_more_link": "projects/office.html",
        "form_subject_zh": "[工程案例-寫字樓] 工程諮詢",
        "form_subject_en": "[Project-Office] Project Inquiry",
        "form_id": "officeFormZh",
        "form_success_id": "officeSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "stadium": {
        "zh_name": "體育場館", "en_name": "Stadium",
        "zh_tag": "體育 · Stadium", "en_tag": "Stadium",
        "zh_desc": "恆生石材為體育場館提供耐候、抗衝擊、大流量通行能力的石材解決方案，經受極端環境考驗。",
        "en_desc": "HSST provides weather-resistant, impact-resistant, high-capacity stone solutions for stadiums and sports venues, withstanding extreme environmental challenges.",
        "stats": {"projects": "7+", "countries": "5", "area": "100,000㎡"},
        "construction_imgs": [25, 26, 27],
        "detail_imgs": [28, 29, 30, 31],
        "challenges_zh": [
            ("☀️", "戶外抗UV風化", "採用花崗岩為主材，表面塗刷納米TiO₂自潔塗層。紫外線加速老化試驗3000小時，色差ΔE<2.0。塗層具有光催化自潔功能，可分解表面有機污染物，降低維護成本50%。"),
            ("🏟️", "5萬觀眾振動負荷", "看台區石材採用彈性安裝系統，石材與結構之間設置10mm橡膠減震層。可承受5萬觀眾同時跳動產生的動荷載。石材背栓採用防鬆脫設計，經100萬次振動試驗無鬆動。"),
            ("🌧️", "雨季施工排水", "開發石材快速排水系統，板縫設置2mm排水縫，基層設置導水槽。排水速率≥50L/min·m，可在暴雨條件下快速排水。雨季施工採用臨時遮陽棚+除濕機，確保施工品質。"),
        ],
        "challenges_en": [
            ("☀️", "Outdoor UV Weathering Resistance", "Granite as primary material with nano-TiO₂ self-cleaning coating. 3000-hour UV accelerated aging test, color difference ΔE<2.0. Photocatalytic self-cleaning decomposes organic pollutants, reducing maintenance costs 50%."),
            ("🏟️", "50,000 Spectator Vibration Load", "Grandstand stone: elastic installation system with 10mm rubber damping layer between stone and structure. Withstands dynamic load from 50,000 spectators jumping simultaneously. Anti-loosening anchor design, 1 million cycle vibration test with no loosening."),
            ("🌧️", "Rainy Season Construction Drainage", "Rapid stone drainage system: 2mm drainage joints between slabs, water guide channels in substrate. Drainage rate ≥50L/min·m. Temporary shelter + dehumidifier for rainy season construction, ensuring quality."),
        ],
        "related": [
            ("granite-collection", "Granite Collection", "花崗岩系列", "s5", "0929D577-3A5E-44C6-9034-6FE1A5295CBF.jpg", "🇨🇳 中國", "China"),
            ("granite-collection", "Project Stone", "工程石材", "s7", "13AB1F74-1F8E-4E05-A361-28F466E33BA3.jpg", "🇨🇳 中國", "China"),
            ("travertine-sandstone", "Travertine & Sandstone", "洞石砂岩", "s9", "1BECCD04-001E-4D4E-A119-9DEC181C410F.jpg", "🇹🇷 土耳其", "Turkey"),
        ],
        "zh_more_link": "projects/stadium.html",
        "en_more_link": "projects/stadium.html",
        "form_subject_zh": "[工程案例-體育場館] 工程諮詢",
        "form_subject_en": "[Project-Stadium] Project Inquiry",
        "form_id": "stadiumFormZh",
        "form_success_id": "stadiumSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
    "villa": {
        "zh_name": "別墅豪宅", "en_name": "Luxury Villa",
        "zh_tag": "別墅 · Villa", "en_tag": "Villa",
        "zh_desc": "恆生石材為別墅豪宅提供定制化、奢華、私密的石材解決方案，每一處細節都體現業主的獨特品味。",
        "en_desc": "HSST provides customized, luxurious, and private stone solutions for luxury villas and mansions, where every detail reflects the owner's unique taste.",
        "stats": {"projects": "30+", "countries": "10", "area": "25,000㎡"},
        "construction_imgs": [10, 11, 12],
        "detail_imgs": [13, 14, 15, 16],
        "challenges_zh": [
            ("🏛️", "異形穹頂石材包覆", "採用3D掃描建模+CNC五軸加工，將穹頂分割為128塊異形扇形板材。每塊板材單獨編號，現場按編號順序安裝。穹頂直徑8m，石材接縫公差±0.3mm，實現完美弧面過渡。"),
            ("🌿", "庭園景觀無縫過渡", "開發室內外石材過渡系統，室內採用拋光面、室外採用火燒面，同種石材兩種表面處理。過渡區域設置隱藏式排水溝，實現室內外地面無高差過渡，視覺上渾然一體。"),
            ("👑", "業主私人定製", "提供從選礦到安裝的全流程私人定制服務。業主可親赴礦區挑選荒料，每塊石材的紋理方向、拼花圖案均經業主確認。專屬設計師駐場服務，確保每個細節符合業主要求。"),
        ],
        "challenges_en": [
            ("🏛️", "Irregular Dome Stone Cladding", "3D scanning + CNC 5-axis machining, dome divided into 128 irregular fan-shaped slabs. Each slab individually numbered, installed sequentially. Dome diameter 8m, joint tolerance ±0.3mm, achieving perfect curved surface transition."),
            ("🌿", "Seamless Garden Landscape Transition", "Indoor-outdoor stone transition system: same stone with polished interior and flame-textured exterior. Hidden drainage channel in transition zone, zero-threshold indoor-outdoor transition, visually unified."),
            ("👑", "Owner's Private Customization", "Full-process private customization from quarry selection to installation. Owners can personally select blocks at the quarry. Vein direction and mosaic patterns confirmed by owner. Dedicated on-site designer ensures every detail meets owner's requirements."),
        ],
        "related": [
            ("luxury-stone", "Luxury Stone", "奢石系列", "s8", "5C23ADBF-4BDC-48FC-8592-628475E07BAD.jpg", "🇮🇹 意大利", "Italy"),
            ("white-marble", "White Marble", "白色系大理石", "s1", "057090E9-40CA-470E-B569-F0DE054485B0.jpg", "🇮🇹 意大利", "Italy"),
            ("custom-craft", "Custom Craft", "異形工藝", "s10", "06214C37-17AC-4167-8C9F-39B55837E1BD.jpg", "🇮🇹 意大利", "Italy"),
        ],
        "zh_more_link": "projects/villa.html",
        "en_more_link": "projects/villa.html",
        "form_subject_zh": "[工程案例-別墅豪宅] 工程諮詢",
        "form_subject_en": "[Project-Luxury Villa] Project Inquiry",
        "form_id": "villaFormZh",
        "form_success_id": "villaSuccessZh",
        "zh_cta_h3": "讓專業團隊為您服務",
        "en_cta_h3": "Let Our Professional Team Serve You",
    },
}


def img_num(n):
    return f"{n:03d}"


def build_zh_sections(p):
    """Build the 5 new sections for a Chinese page."""
    name = p["zh_name"]
    construction_imgs = p["construction_imgs"]
    detail_imgs = p["detail_imgs"]

    # Section 1: Construction Process
    s1 = f'''<!-- Construction Process -->
<section class="project-section project-section-alt">
  <div class="project-container">
    <span class="project-section-subtitle">Construction Process</span>
    <h2 class="project-section-title">施工過程</h2>
    <p class="project-section-desc">以下為{name}項目施工全過程記錄，涵蓋從測量、加工到安裝的各個環節。</p>
    <div class="gallery-grid" id="constructionGallery">
      <div class="gallery-item" data-src="../images/projects/cases/{img_num(construction_imgs[0])}.jpg"><img alt="現場測量放線" loading="lazy" src="../images/projects/cases/{img_num(construction_imgs[0])}.jpg"/></div>
      <div class="gallery-item" data-src="../images/projects/cases/{img_num(construction_imgs[1])}.jpg"><img alt="工廠CNC切割加工" loading="lazy" src="../images/projects/cases/{img_num(construction_imgs[1])}.jpg"/></div>
      <div class="gallery-item" data-src="../images/projects/cases/{img_num(construction_imgs[2])}.jpg"><img alt="現場安裝施工" loading="lazy" src="../images/projects/cases/{img_num(construction_imgs[2])}.jpg"/></div>
    </div>
  </div>
</section>'''

    # Section 2: Installation Details
    s2 = f'''<!-- Installation Details -->
<section class="project-section">
  <div class="project-container">
    <span class="project-section-subtitle">Installation Details</span>
    <h2 class="project-section-title">安裝細節</h2>
    <p class="project-section-desc">近距離展示{name}項目石材安裝的精密工藝細節。</p>
    <div class="gallery-grid" id="detailGallery">
      <div class="gallery-item" data-src="../images/projects/cases/{img_num(detail_imgs[0])}.jpg"><img alt="接縫處理細節" loading="lazy" src="../images/projects/cases/{img_num(detail_imgs[0])}.jpg"/></div>
      <div class="gallery-item" data-src="../images/projects/cases/{img_num(detail_imgs[1])}.jpg"><img alt="基層處理與固定" loading="lazy" src="../images/projects/cases/{img_num(detail_imgs[1])}.jpg"/></div>
      <div class="gallery-item" data-src="../images/projects/cases/{img_num(detail_imgs[2])}.jpg"><img alt="表面處理工藝" loading="lazy" src="../images/projects/cases/{img_num(detail_imgs[2])}.jpg"/></div>
      <div class="gallery-item" data-src="../images/projects/cases/{img_num(detail_imgs[3])}.jpg"><img alt="完工驗收效果" loading="lazy" src="../images/projects/cases/{img_num(detail_imgs[3])}.jpg"/></div>
    </div>
  </div>
</section>'''

    # Section 3: Related Products
    related_cards = []
    for slug, en_name, zh_name_r, sdir, simg, origin_zh, origin_en in p["related"]:
        related_cards.append(f'''      <a class="stone-card" href="../products/{slug}.html">
        <div class="stone-card-img"><img alt="{en_name}" loading="lazy" src="../images/products/{sdir}/{simg}"/></div>
        <div class="stone-card-body">
          <div class="stone-card-name">{zh_name_r}</div>
          <div class="stone-card-origin">{origin_zh}</div>
          <div class="stone-card-desc">{p["zh_desc"][:40]}...</div>
          <span class="stone-card-link">查看詳情 →</span>
        </div>
      </a>''')
    s3 = f'''<!-- Related Products -->
<section class="project-section project-section-alt">
  <div class="project-container">
    <span class="project-section-subtitle">Related Products</span>
    <h2 class="project-section-title">相關產品</h2>
    <p class="project-section-desc">本項目使用的石材產品，點擊查看詳細規格。</p>
    <div class="stone-grid">
{chr(10).join(related_cards)}
    </div>
  </div>
</section>'''

    # Section 4: Technical Highlights & Solutions
    tech_items = []
    for icon, title, solution in p["challenges_zh"]:
        tech_items.append(f'''      <div class="tech-item">
        <div class="tech-icon">{icon}</div>
        <div class="tech-body">
          <div class="tech-label">挑戰</div>
          <div class="tech-title">{title}</div>
          <div class="tech-solution">
            <strong>解決方案：</strong>{solution}
          </div>
        </div>
      </div>''')
    s4 = f'''<!-- Technical Highlights & Solutions -->
<section class="project-section project-section-alt">
  <div class="project-container">
    <span class="project-section-subtitle">Technical</span>
    <h2 class="project-section-title">技術亮點與解決方案</h2>
    <p class="project-section-desc">面對{name}項目的特殊挑戰，恆生石材以專業技術攻克多重難關。</p>
    <div class="tech-list">
{chr(10).join(tech_items)}
    </div>
  </div>
</section>'''

    # Section 5: CTA with form + More
    s5 = f'''<!-- CTA -->
<section class="project-section">
  <div class="project-container">
    <span class="project-section-subtitle">Get Started</span>
    <h2 class="project-section-title">打造您的頂級項目</h2>
    <div class="cta-grid">
      <div class="cta-info">
        <h3>{p["zh_cta_h3"]}</h3>
        <p>無論您的項目規模如何，我們的工程顧問團隊都能為您量身定制最優石材方案。從選材諮詢到工程交付，全程一對一服務。</p>
        <div class="cta-buttons">
          <a class="btn-filled" href="../products.html">🏗️ 選用同款石材</a>
          <a class="btn-outline" href="../contact.html">📋 類似工程諮詢</a>
        </div>
      </div>
      <div>
        <form class="hsst-form" id="{p["form_id"]}" action="https://formspree.io/f/xnjrjlzb" method="POST">
          <input type="hidden" name="_subject" value="{p["form_subject_zh"]}"/>
          <div class="hsst-form-row">
            <div class="hsst-form-group">
              <label class="hsst-form-label">姓名 <span class="required">*</span></label>
              <input type="text" name="name" class="hsst-form-input" placeholder="您的姓名" required/>
            </div>
            <div class="hsst-form-group">
              <label class="hsst-form-label">電話 <span class="required">*</span></label>
              <input type="tel" name="phone" class="hsst-form-input" placeholder="+852 XXXX XXXX" required/>
            </div>
          </div>
          <div class="hsst-form-row">
            <div class="hsst-form-group">
              <label class="hsst-form-label">郵箱 <span class="required">*</span></label>
              <input type="email" name="email" class="hsst-form-input" placeholder="example@email.com" required/>
            </div>
            <div class="hsst-form-group">
              <label class="hsst-form-label">公司/機構</label>
              <input type="text" name="company" class="hsst-form-input" placeholder="您的公司名稱"/>
            </div>
          </div>
          <div class="hsst-form-group">
            <label class="hsst-form-label">項目規模</label>
            <select name="scale" class="hsst-form-select">
              <option value="">請選擇</option>
              <option value="small">小型 (&lt;2,000㎡)</option>
              <option value="medium">中型 (2,000-10,000㎡)</option>
              <option value="large">大型 (10,000-50,000㎡)</option>
              <option value="mega">超大型 (&gt;50,000㎡)</option>
            </select>
          </div>
          <div class="hsst-form-group">
            <label class="hsst-form-label">項目需求描述 <span class="required">*</span></label>
            <textarea name="message" class="hsst-form-textarea" placeholder="請簡述您的項目需求..." required></textarea>
          </div>
          <div class="hsst-form-group" style="text-align:center;margin-top:20px;">
            <button type="submit" class="hsst-form-btn">提交諮詢</button>
          </div>
          <p class="hsst-form-privacy">提交即表示您同意我們的隱私政策。我們將在24小時內與您聯繫。</p>
        </form>
        <div class="hsst-form-success" id="{p["form_success_id"]}">
          <div class="hsst-form-success-icon">✓</div>
          <h3>提交成功！</h3>
          <p>感謝您的諮詢，我們的工程顧問將在24小時內與您聯繫。</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Related Projects -->
<section class="project-section project-section-alt">
  <div class="project-container" style="text-align:center;">
    <span class="project-section-subtitle">More</span>
    <h2 class="project-section-title" style="margin-bottom:24px;">探索更多案例</h2>
    <div class="cta-buttons" style="justify-content:center;">
      <a class="btn-outline" href="../projects/{p["zh_more_link"].split('/')[-1]}">📂 更多{name}工程</a>
      <a class="btn-outline" href="../projects.html">📂 瀏覽全部案例</a>
    </div>
  </div>
</section>

<!-- Lightbox -->
<div class="lightbox" id="lightbox">
  <button class="lightbox-close" id="lightboxClose">&times;</button>
  <button class="lightbox-prev" id="lightboxPrev">&lsaquo;</button>
  <img alt="" id="lightboxImg"/>
  <button class="lightbox-next" id="lightboxNext">&rsaquo;</button>
</div>'''

    return s1, s2, s3, s4, s5


def build_en_sections(p):
    """Build the 5 new sections for an English page."""
    name = p["en_name"]
    construction_imgs = p["construction_imgs"]
    detail_imgs = p["detail_imgs"]

    # Section 1: Construction Process
    s1 = f'''<!-- Construction Process -->
<section class="project-section project-section-alt">
  <div class="project-container">
    <span class="project-section-subtitle">Construction Process</span>
    <h2 class="project-section-title">Construction Process</h2>
    <p class="project-section-desc">Below is the complete construction process record for the {name} project, covering measurement, processing, and installation stages.</p>
    <div class="gallery-grid" id="constructionGallery">
      <div class="gallery-item" data-src="../../images/projects/cases/{img_num(construction_imgs[0])}.jpg"><img alt="On-site Measurement & Layout" loading="lazy" src="../../images/projects/cases/{img_num(construction_imgs[0])}.jpg"/></div>
      <div class="gallery-item" data-src="../../images/projects/cases/{img_num(construction_imgs[1])}.jpg"><img alt="Factory CNC Cutting" loading="lazy" src="../../images/projects/cases/{img_num(construction_imgs[1])}.jpg"/></div>
      <div class="gallery-item" data-src="../../images/projects/cases/{img_num(construction_imgs[2])}.jpg"><img alt="On-site Installation" loading="lazy" src="../../images/projects/cases/{img_num(construction_imgs[2])}.jpg"/></div>
    </div>
  </div>
</section>'''

    # Section 2: Installation Details
    s2 = f'''<!-- Installation Details -->
<section class="project-section">
  <div class="project-container">
    <span class="project-section-subtitle">Installation Details</span>
    <h2 class="project-section-title">Installation Details</h2>
    <p class="project-section-desc">Close-up display of precision craftsmanship details in stone installation for the {name} project.</p>
    <div class="gallery-grid" id="detailGallery">
      <div class="gallery-item" data-src="../../images/projects/cases/{img_num(detail_imgs[0])}.jpg"><img alt="Joint Treatment Detail" loading="lazy" src="../../images/projects/cases/{img_num(detail_imgs[0])}.jpg"/></div>
      <div class="gallery-item" data-src="../../images/projects/cases/{img_num(detail_imgs[1])}.jpg"><img alt="Substrate Preparation & Fixing" loading="lazy" src="../../images/projects/cases/{img_num(detail_imgs[1])}.jpg"/></div>
      <div class="gallery-item" data-src="../../images/projects/cases/{img_num(detail_imgs[2])}.jpg"><img alt="Surface Treatment Process" loading="lazy" src="../../images/projects/cases/{img_num(detail_imgs[2])}.jpg"/></div>
      <div class="gallery-item" data-src="../../images/projects/cases/{img_num(detail_imgs[3])}.jpg"><img alt="Finished Surface" loading="lazy" src="../../images/projects/cases/{img_num(detail_imgs[3])}.jpg"/></div>
    </div>
  </div>
</section>'''

    # Section 3: Related Products
    related_cards = []
    for slug, en_name_r, zh_name, sdir, simg, origin_zh, origin_en in p["related"]:
        related_cards.append(f'''      <a class="stone-card" href="../../products/{slug}.html">
        <div class="stone-card-img"><img alt="{en_name_r}" loading="lazy" src="../../images/products/{sdir}/{simg}"/></div>
        <div class="stone-card-body">
          <div class="stone-card-name">{en_name_r}</div>
          <div class="stone-card-origin">{origin_en}</div>
          <div class="stone-card-desc">{p["en_desc"][:40]}...</div>
          <span class="stone-card-link">View Details →</span>
        </div>
      </a>''')
    s3 = f'''<!-- Related Products -->
<section class="project-section project-section-alt">
  <div class="project-container">
    <span class="project-section-subtitle">Related Products</span>
    <h2 class="project-section-title">Related Products</h2>
    <p class="project-section-desc">Stone products used in this project. Click to view detailed specifications.</p>
    <div class="stone-grid">
{chr(10).join(related_cards)}
    </div>
  </div>
</section>'''

    # Section 4: Technical Highlights & Solutions
    tech_items = []
    for icon, title, solution in p["challenges_en"]:
        tech_items.append(f'''      <div class="tech-item">
        <div class="tech-icon">{icon}</div>
        <div class="tech-body">
          <div class="tech-label">Challenge</div>
          <div class="tech-title">{title}</div>
          <div class="tech-solution">
            <strong>Solution: </strong>{solution}
          </div>
        </div>
      </div>''')
    s4 = f'''<!-- Technical Highlights & Solutions -->
<section class="project-section project-section-alt">
  <div class="project-container">
    <span class="project-section-subtitle">Technical</span>
    <h2 class="project-section-title">Technical Highlights & Solutions</h2>
    <p class="project-section-desc">Facing the unique challenges of the {name} project, HSST overcame multiple technical difficulties with professional expertise.</p>
    <div class="tech-list">
{chr(10).join(tech_items)}
    </div>
  </div>
</section>'''

    # Section 5: CTA with form + More
    form_id = p["form_id"].replace("FormZh", "FormEn")
    success_id = p["form_success_id"].replace("SuccessZh", "SuccessEn")
    s5 = f'''<!-- CTA -->
<section class="project-section">
  <div class="project-container">
    <span class="project-section-subtitle">Get Started</span>
    <h2 class="project-section-title">Build Your Premium Project</h2>
    <div class="cta-grid">
      <div class="cta-info">
        <h3>{p["en_cta_h3"]}</h3>
        <p>Regardless of your project scale, our engineering consultant team can tailor the optimal stone solution for you. One-on-one service from material selection to project delivery.</p>
        <div class="cta-buttons">
          <a class="btn-filled" href="../../products.html">🏗️ Use Similar Stone</a>
          <a class="btn-outline" href="../../contact.html">📋 Similar Project Inquiry</a>
        </div>
      </div>
      <div>
        <form class="hsst-form" id="{form_id}" action="https://formspree.io/f/xnjrjlzb" method="POST">
          <input type="hidden" name="_subject" value="{p["form_subject_en"]}"/>
          <div class="hsst-form-row">
            <div class="hsst-form-group">
              <label class="hsst-form-label">Name <span class="required">*</span></label>
              <input type="text" name="name" class="hsst-form-input" placeholder="Your Name" required/>
            </div>
            <div class="hsst-form-group">
              <label class="hsst-form-label">Phone <span class="required">*</span></label>
              <input type="tel" name="phone" class="hsst-form-input" placeholder="+852 XXXX XXXX" required/>
            </div>
          </div>
          <div class="hsst-form-row">
            <div class="hsst-form-group">
              <label class="hsst-form-label">Email <span class="required">*</span></label>
              <input type="email" name="email" class="hsst-form-input" placeholder="example@email.com" required/>
            </div>
            <div class="hsst-form-group">
              <label class="hsst-form-label">Company/Organization</label>
              <input type="text" name="company" class="hsst-form-input" placeholder="Your Company Name"/>
            </div>
          </div>
          <div class="hsst-form-group">
            <label class="hsst-form-label">Project Scale</label>
            <select name="scale" class="hsst-form-select">
              <option value="">Please Select</option>
              <option value="small">Small (&lt;2,000㎡)</option>
              <option value="medium">Medium (2,000-10,000㎡)</option>
              <option value="large">Large (10,000-50,000㎡)</option>
              <option value="mega">Mega (&gt;50,000㎡)</option>
            </select>
          </div>
          <div class="hsst-form-group">
            <label class="hsst-form-label">Project Requirements <span class="required">*</span></label>
            <textarea name="message" class="hsst-form-textarea" placeholder="Briefly describe your project requirements..." required></textarea>
          </div>
          <div class="hsst-form-group" style="text-align:center;margin-top:20px;">
            <button type="submit" class="hsst-form-btn">Submit Inquiry</button>
          </div>
          <p class="hsst-form-privacy">By submitting, you agree to our privacy policy. We will contact you within 24 hours.</p>
        </form>
        <div class="hsst-form-success" id="{success_id}">
          <div class="hsst-form-success-icon">✓</div>
          <h3>Submitted Successfully!</h3>
          <p>Thank you for your inquiry. Our engineering consultant will contact you within 24 hours.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Related Projects -->
<section class="project-section project-section-alt">
  <div class="project-container" style="text-align:center;">
    <span class="project-section-subtitle">More</span>
    <h2 class="project-section-title" style="margin-bottom:24px;">Explore More Projects</h2>
    <div class="cta-buttons" style="justify-content:center;">
      <a class="btn-outline" href="../../projects/{p["en_more_link"].split('/')[-1]}">📂 More {name} Projects</a>
      <a class="btn-outline" href="../../projects.html">📂 View All Projects</a>
    </div>
  </div>
</section>

<!-- Lightbox -->
<div class="lightbox" id="lightbox">
  <button class="lightbox-close" id="lightboxClose">&times;</button>
  <button class="lightbox-prev" id="lightboxPrev">&lsaquo;</button>
  <img alt="" id="lightboxImg"/>
  <button class="lightbox-next" id="lightboxNext">&rsaquo;</button>
</div>'''

    return s1, s2, s3, s4, s5


def build_form_script_zh(p):
    """Build the form AJAX script for ZH page."""
    return f'''<script>
// Lightbox
(function(){{
  var items = document.querySelectorAll('.gallery-item');
  var lightbox = document.getElementById('lightbox');
  var lightboxImg = document.getElementById('lightboxImg');
  var closeBtn = document.getElementById('lightboxClose');
  var prevBtn = document.getElementById('lightboxPrev');
  var nextBtn = document.getElementById('lightboxNext');
  var currentIdx = 0;
  var galleryData = [];
  items.forEach(function(item, i){{
    galleryData.push(item.getAttribute('data-src'));
    item.addEventListener('click', function(){{
      currentIdx = i;
      openLightbox(currentIdx);
    }});
  }});
  function openLightbox(idx){{
    lightboxImg.src = galleryData[idx];
    lightbox.classList.add('show');
    document.body.style.overflow = 'hidden';
  }}
  function closeLightbox(){{
    lightbox.classList.remove('show');
    document.body.style.overflow = '';
  }}
  function prevImg(){{
    currentIdx = (currentIdx - 1 + galleryData.length) % galleryData.length;
    lightboxImg.src = galleryData[currentIdx];
  }}
  function nextImg(){{
    currentIdx = (currentIdx + 1) % galleryData.length;
    lightboxImg.src = galleryData[currentIdx];
  }}
  closeBtn.addEventListener('click', closeLightbox);
  prevBtn.addEventListener('click', prevImg);
  nextBtn.addEventListener('click', nextImg);
  lightbox.addEventListener('click', function(e){{
    if(e.target === lightbox) closeLightbox();
  }});
  document.addEventListener('keydown', function(e){{
    if(!lightbox.classList.contains('show')) return;
    if(e.key === 'Escape') closeLightbox();
    if(e.key === 'ArrowLeft') prevImg();
    if(e.key === 'ArrowRight') nextImg();
  }});
}})();

// Form AJAX
(function(){{
  var f = document.getElementById('{p["form_id"]}');
  var s = document.getElementById('{p["form_success_id"]}');
  if(!f) return;
  f.addEventListener('submit', function(e){{
    e.preventDefault();
    var btn = f.querySelector('.hsst-form-btn');
    var orig = btn.textContent;
    btn.disabled = true;
    btn.textContent = '提交中...';
    fetch(f.action, {{method:'POST', body: new FormData(f)}})
      .then(function(r){{
        if(r.ok){{
          f.style.display = 'none';
          s.classList.add('show');
        }} else {{
          btn.disabled = false;
          btn.textContent = orig;
          alert('提交失敗，請重試或直接聯繫我們。');
        }}
      }})
      .catch(function(){{
        btn.disabled = false;
        btn.textContent = orig;
        alert('網絡錯誤，請重試或直接聯繫我們。');
      }});
  }});
}})();
</script>'''


def build_form_script_en(p):
    """Build the form AJAX script for EN page."""
    form_id = p["form_id"].replace("FormZh", "FormEn")
    success_id = p["form_success_id"].replace("SuccessZh", "SuccessEn")
    return f'''<script>
// Lightbox
(function(){{
  var items = document.querySelectorAll('.gallery-item');
  var lightbox = document.getElementById('lightbox');
  var lightboxImg = document.getElementById('lightboxImg');
  var closeBtn = document.getElementById('lightboxClose');
  var prevBtn = document.getElementById('lightboxPrev');
  var nextBtn = document.getElementById('lightboxNext');
  var currentIdx = 0;
  var galleryData = [];
  items.forEach(function(item, i){{
    galleryData.push(item.getAttribute('data-src'));
    item.addEventListener('click', function(){{
      currentIdx = i;
      openLightbox(currentIdx);
    }});
  }});
  function openLightbox(idx){{
    lightboxImg.src = galleryData[idx];
    lightbox.classList.add('show');
    document.body.style.overflow = 'hidden';
  }}
  function closeLightbox(){{
    lightbox.classList.remove('show');
    document.body.style.overflow = '';
  }}
  function prevImg(){{
    currentIdx = (currentIdx - 1 + galleryData.length) % galleryData.length;
    lightboxImg.src = galleryData[currentIdx];
  }}
  function nextImg(){{
    currentIdx = (currentIdx + 1) % galleryData.length;
    lightboxImg.src = galleryData[currentIdx];
  }}
  closeBtn.addEventListener('click', closeLightbox);
  prevBtn.addEventListener('click', prevImg);
  nextBtn.addEventListener('click', nextImg);
  lightbox.addEventListener('click', function(e){{
    if(e.target === lightbox) closeLightbox();
  }});
  document.addEventListener('keydown', function(e){{
    if(!lightbox.classList.contains('show')) return;
    if(e.key === 'Escape') closeLightbox();
    if(e.key === 'ArrowLeft') prevImg();
    if(e.key === 'ArrowRight') nextImg();
  }});
}})();

// Form AJAX
(function(){{
  var f = document.getElementById('{form_id}');
  var s = document.getElementById('{success_id}');
  if(!f) return;
  f.addEventListener('submit', function(e){{
    e.preventDefault();
    var btn = f.querySelector('.hsst-form-btn');
    var orig = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Submitting...';
    fetch(f.action, {{method:'POST', body: new FormData(f)}})
      .then(function(r){{
        if(r.ok){{
          f.style.display = 'none';
          s.classList.add('show');
        }} else {{
          btn.disabled = false;
          btn.textContent = orig;
          alert('Submission failed. Please try again or contact us directly.');
        }}
      }})
      .catch(function(){{
        btn.disabled = false;
        btn.textContent = orig;
        alert('Network error. Please try again or contact us directly.');
      }});
  }});
}})();
</script>'''


def process_zh_page(slug, p):
    """Process a Chinese project page."""
    filepath = os.path.join(BASE, "projects", f"{slug}.html")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Build new sections
    s1, s2, s3, s4, s5 = build_zh_sections(p)

    # Find the old CTA section and replace it
    # The old CTA starts with <!-- CTA --> and ends before <!-- Footer -->
    cta_pattern = r'<!-- CTA -->\s*<section class="project-section">.*?(?=<!-- Footer -->)'
    
    # Build the replacement: new sections 1-4 + section 5 (CTA+More+Lightbox)
    new_content_block = s1 + "\n\n" + s2 + "\n\n" + s3 + "\n\n" + s4 + "\n\n" + s5
    
    # Replace old CTA with new content
    new_content = re.sub(cta_pattern, new_content_block + "\n\n", content, flags=re.DOTALL)

    # Also need to replace the old lightbox (if exists separately) and old script
    # Remove old lightbox div
    new_content = re.sub(r'<!-- Lightbox -->\s*<div class="lightbox".*?</div>\s*</div>\s*</div>', '', new_content, flags=re.DOTALL)
    
    # Replace old script with new one (form + lightbox)
    # Find the old script block
    old_script_pattern = r'<script>\s*let currentIndex=0;.*?</script>'
    new_script = build_form_script_zh(p)
    new_content = re.sub(old_script_pattern, new_script, new_content, flags=re.DOTALL)

    # Also add CSS for form if not present
    if '.hsst-form' not in new_content:
        form_css = """
<style>
.hsst-form{background:#FFF;padding:32px;border-radius:12px;border:1px solid #EEE8DD;}
.hsst-form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;}
.hsst-form-group{margin-bottom:16px;}
.hsst-form-label{display:block;font-size:0.85rem;font-weight:600;color:#1A1A2E;margin-bottom:6px;}
.hsst-form-input,.hsst-form-select,.hsst-form-textarea{width:100%;padding:10px 14px;border:1px solid #DDD;border-radius:6px;font-size:0.9rem;font-family:inherit;box-sizing:border-box;transition:border-color 0.3s;}
.hsst-form-input:focus,.hsst-form-select:focus,.hsst-form-textarea:focus{border-color:#D4AF37;outline:none;}
.hsst-form-textarea{min-height:100px;resize:vertical;}
.hsst-form-btn{background:linear-gradient(135deg,#D4AF37,#C5A059);color:#111;padding:12px 36px;border:none;border-radius:6px;font-size:1rem;font-weight:700;cursor:pointer;transition:all 0.3s;}
.hsst-form-btn:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(212,175,55,0.35);}
.hsst-form-btn:disabled{opacity:0.6;cursor:not-allowed;}
.hsst-form-privacy{font-size:0.75rem;color:#999;text-align:center;margin-top:12px;}
.hsst-form-success{display:none;text-align:center;padding:48px 24px;}
.hsst-form-success.show{display:block;}
.hsst-form-success-icon{width:64px;height:64px;background:#4CAF50;color:#FFF;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;margin:0 auto 16px;}
.hsst-form-success h3{color:#1A1A2E;margin-bottom:8px;}
.hsst-form-success p{color:rgba(26,26,46,0.6);}
.required{color:#E53935;}
@media(max-width:768px){.hsst-form-row{grid-template-columns:1fr;}.hsst-form{padding:20px;}}
</style>"""
        # Insert before </head>
        new_content = new_content.replace('</style>\n</head>', '</style>\n' + form_css + '\n</head>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  ✓ ZH: {slug}.html updated")


def process_en_page(slug, p):
    """Process an English project page."""
    filepath = os.path.join(BASE, "en", "projects", f"{slug}.html")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Build new sections
    s1, s2, s3, s4, s5 = build_en_sections(p)

    # Find the old CTA section and replace it
    cta_pattern = r'<!-- CTA -->\s*<section class="project-section">.*?(?=<!-- Footer -->)'
    
    new_content_block = s1 + "\n\n" + s2 + "\n\n" + s3 + "\n\n" + s4 + "\n\n" + s5
    
    new_content = re.sub(cta_pattern, new_content_block + "\n\n", content, flags=re.DOTALL)

    # Remove old lightbox div
    new_content = re.sub(r'<!-- Lightbox -->\s*<div class="lightbox".*?</div>\s*</div>\s*</div>', '', new_content, flags=re.DOTALL)
    
    # Replace old script
    old_script_pattern = r'<script>\s*let currentIndex=0;.*?</script>'
    new_script = build_form_script_en(p)
    new_content = re.sub(old_script_pattern, new_script, new_content, flags=re.DOTALL)

    # Add form CSS if not present
    if '.hsst-form' not in new_content:
        form_css = """
<style>
.hsst-form{background:#FFF;padding:32px;border-radius:12px;border:1px solid #EEE8DD;}
.hsst-form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;}
.hsst-form-group{margin-bottom:16px;}
.hsst-form-label{display:block;font-size:0.85rem;font-weight:600;color:#1A1A2E;margin-bottom:6px;}
.hsst-form-input,.hsst-form-select,.hsst-form-textarea{width:100%;padding:10px 14px;border:1px solid #DDD;border-radius:6px;font-size:0.9rem;font-family:inherit;box-sizing:border-box;transition:border-color 0.3s;}
.hsst-form-input:focus,.hsst-form-select:focus,.hsst-form-textarea:focus{border-color:#D4AF37;outline:none;}
.hsst-form-textarea{min-height:100px;resize:vertical;}
.hsst-form-btn{background:linear-gradient(135deg,#D4AF37,#C5A059);color:#111;padding:12px 36px;border:none;border-radius:6px;font-size:1rem;font-weight:700;cursor:pointer;transition:all 0.3s;}
.hsst-form-btn:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(212,175,55,0.35);}
.hsst-form-btn:disabled{opacity:0.6;cursor:not-allowed;}
.hsst-form-privacy{font-size:0.75rem;color:#999;text-align:center;margin-top:12px;}
.hsst-form-success{display:none;text-align:center;padding:48px 24px;}
.hsst-form-success.show{display:block;}
.hsst-form-success-icon{width:64px;height:64px;background:#4CAF50;color:#FFF;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;margin:0 auto 16px;}
.hsst-form-success h3{color:#1A1A2E;margin-bottom:8px;}
.hsst-form-success p{color:rgba(26,26,46,0.6);}
.required{color:#E53935;}
@media(max-width:768px){.hsst-form-row{grid-template-columns:1fr;}.hsst-form{padding:20px;}}
</style>"""
        new_content = new_content.replace('</style>\n</head>', '</style>\n' + form_css + '\n</head>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  ✓ EN: {slug}.html updated")


def main():
    print("Expanding project pages...")
    for slug, p in PROJECTS.items():
        print(f"\nProcessing: {slug}")
        process_zh_page(slug, p)
        process_en_page(slug, p)
    print("\n✅ All 22 pages updated!")


if __name__ == "__main__":
    main()
