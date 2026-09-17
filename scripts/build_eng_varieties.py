#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工程石材品種系列（製品類）生成器
================================
為「產品中心 › 工程石材 › 工程石材品種系列」一次性生成：

  落地頁  products/engineering-stone-varieties.html        (+ en/)
  詳情頁  products/engineering-stone-varieties/<slug>.html  (×18, + en/)

做法：以站內現有真實頁面為模板（保留完整 nav / footer / JSON-LD），
只替換 <head> 元信息與 <main-content> 主體，確保導航與結構一致。

圖片策略（Stone 2026-09-17 更新）：19 張 AI 場景主圖（18 系列 + 落地頁）已由
scripts/process_ev_heroes.py 生成並去水印，落盤 jpg+webp 雙格式；
本腳本以 <picture> 引用真實圖片（詳情頁 ../../ 與 ../../../，落地頁 ../ 與 ../../）。

用法：
  python3 scripts/build_eng_varieties.py          # dry-run（輸出到 /tmp）
  python3 scripts/build_eng_varieties.py --apply   # 正式寫入站點
"""
import os, re, sys, json

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLY = "--apply" in sys.argv
OUT_ROOT = SITE if APPLY else "/tmp/ev_preview"
NOW = "2026-09-17T14:00:00+08:00"

# ---------------- 模板 ----------------
ZH_DETAIL_TPL = os.path.join(SITE, "products/project-stone/qing-bluestone.html")
EN_DETAIL_TPL = os.path.join(SITE, "en/products/project-stone/qing-bluestone.html")
ZH_LAND_TPL = os.path.join(SITE, "products/project-stone.html")
EN_LAND_TPL = os.path.join(SITE, "en/products/project-stone.html")

# ---------------- 共享花崗岩（麻石）技術參數 ----------------
GRANITE_SPECS = [
    ("密度", "Density", "2.60 – 2.80 g/cm³", "ASTM C97"),
    ("吸水率", "Water Absorption", "≤ 0.50 %", "ASTM C97"),
    ("抗壓強度", "Compressive Strength", "120 – 260 MPa", "ASTM C170"),
    ("抗彎強度", "Flexural Strength", "8 – 20 MPa", "ASTM C880"),
    ("莫氏硬度", "Mohs Hardness", "6.0 – 7.0", "EN 14157"),
    ("放射性等級", "Radioactivity Class", "A 類 Class A", "GB 6566"),
    ("耐磨性", "Abrasion Resistance", "≤ 8.0 mm", "EN 14157"),
    ("耐凍融", "Frost Resistance", "50 次循環合格", "ASTM C666"),
]

# ---------------- 18 系列數據 ----------------
# 每系列：slug / zh{name,hk,en,intro,material,apps[]} / en{...} /
#         common_specs[(zh_label,en_label,value)×2] / items[×10]{zh,hk,en,zh_note,en_note}
SERIES = [
{
 "slug":"bollard-ball","idx":"01",
 "zh":{"name":"挡车石球","hk":"車檔石球","en":"Granite Bollard Ball",
  "intro":"以花崗岩（麻石）整料車削而成的球形車檔，用於人行道、廣場、停車場與公共設施入口，分隔人車、防範車輛誤闖，堅固耐撞、歷久不鏽。",
  "material":"選用高密度花崗岩（麻石）荒料整球車削，質地緻密、抗壓耐撞；表面常做火燒面或荔枝面處理以提升質感。麻石天然耐候、抗紫外線、不褪色，適合香港高溫多雨、臨海鹽霧的戶外環境長期使用。",
  "apps":[("🚧","公共設施入口","分隔人車、防車輛誤闖"),("🅿️","停車場與車道","界定行車動線"),("🏞️","廣場與園區","景觀與安全兼備"),("🏫","校園與醫院","守護行人安全"),("🏛️","文化地標","莊重且耐看"),("🌳","住宅社群","低調實用")]},
 "en":{"name":"Bollard Ball","hk":"Traffic Bollard Ball","en":"Granite Bollard Ball",
  "intro":"Solid-turned granite spheres used at building entrances, plazas, car parks and public facilities to separate pedestrians from vehicles — robust, impact-resistant and weatherproof.",
  "material":"Turned from solid high-density granite (麻石) blocks. Dense, compression-resistant and impact-proof; usually flamed or bush-hammered for texture. Granite is naturally weatherproof, UV-stable and non-fading — ideal for Hong Kong's hot, rainy, coastal climate.",
  "apps":[("🚧","Facility Entrances","Separate people and vehicles"),("🅿️","Car Parks & Driveways","Define traffic lines"),("🏞️","Plazas & Parks","Landscape + safety"),("🏫","Campuses & Hospitals","Protect pedestrians"),("🏛️","Cultural Landmarks","Dignified finish"),("🌳","Residential Estates","Low-key utility")]},
 "common_specs":[("常見規格 Common Sizes","Φ300 / Φ400 / Φ500 / Φ600 mm（可定制）"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 光面 Polished")],
 "items":[
  {"zh":"標準圓球","hk":"標準圓球","en":"Standard Sphere","zh_note":"最常見規格，Φ400–Φ600","en_note":"Most common Φ400–Φ600"},
  {"zh":"帶底座石球","hk":"連座石球","en":"Ball with Base","zh_note":"球+基座一體，防滾動","en_note":"Ball+plinth, anti-roll"},
  {"zh":"刻字石球","hk":"刻字石球","en":"Engraved Ball","zh_note":"球面陰刻/浮雕字","en_note":"Engraved/relief text"},
  {"zh":"半圓球（半球）","hk":"半球石球","en":"Half Sphere","zh_note":"貼地半球，防撞緩衝","en_note":"Ground half-sphere bumper"},
  {"zh":"橢圓球","hk":"橢圓石球","en":"Oval Sphere","zh_note":"橢圓造型，景觀用","en_note":"Oval form, landscape"},
  {"zh":"方柱頂球","hk":"方柱頂球","en":"Cube-top Ball","zh_note":"方柱+球組合","en_note":"Cube+ball combo"},
  {"zh":"穿孔鏈條球","hk":"穿鏈石球","en":"Chained Ball","zh_note":"預留穿孔，串不鏽鋼鏈","en_note":"Pre-drilled for chain"},
  {"zh":"矮墩球","hk":"矮墩球","en":"Low Dwarf Ball","zh_note":"低矮款，限制但不阻視線","en_note":"Low profile, sightline friendly"},
  {"zh":"組合球柱","hk":"組合球柱","en":"Ball Post Set","zh_note":"球+柱一體成型","en_note":"Ball+post monolith"},
  {"zh":"不鏽鋼鑲球","hk":"鋼石組合球","en":"Steel-inlaid Ball","zh_note":"麻石球鑲不鏽鋼環","en_note":"Granite+steel ring"}]
},
{
 "slug":"bollard-post","idx":"02",
 "zh":{"name":"挡车石柱","hk":"車檔柱","en":"Granite Bollard Post",
  "intro":"花崗岩（麻石）整料雕刻的立柱式車檔，用於限制車輛進入的行人區、廣場與設施入口，兼具防撞隔離與景觀裝飾功能。",
  "material":"採用高密度麻石整柱車削或雕刻，柱體筆直、頂帽可循羅馬/簡約等風格定制。麻石抗壓、耐撞、耐候，表面火燒/荔枝面防反光，適合香港戶外長期佈設。",
  "apps":[("🚷","行人專區","禁車區軟隔離"),("🏛️","古蹟與地標","風格協調"),("🌆","商場外廣場","安全與美觀"),("🏫","校園圍界","守護學童"),("🏥","醫院落客區","人車分流"),("🌳","私宅車道","低調防闖")]},
 "en":{"name":"Bollard Post","hk":"Traffic Bollard Post","en":"Granite Bollard Post",
  "intro":"Turned or carved granite posts that restrict vehicle access to pedestrian zones, plazas and entrances — combining impact resistance with decorative presence.",
  "material":"Solid high-density granite, turned or carved with Roman/plain caps. Compression-proof, impact-proof and weatherproof; flamed/bush-hammered faces cut glare — suited to Hong Kong outdoors.",
  "apps":[("🚷","Pedestrian Zones","Soft vehicle barrier"),("🏛️","Heritage Sites","Style match"),("🌆","Mall Plazas","Safety + beauty"),("🏫","Campuses","Protect children"),("🏥","Hospital Drop-offs","Separate flows"),("🌳","Private Driveways","Low-key guard")]},
 "common_specs":[("常見規格 Common Sizes","柱徑 Φ200–Φ300 mm；柱高 600–1200 mm"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 光面 Polished")],
 "items":[
  {"zh":"圓柱車檔","hk":"圓柱車檔","en":"Round Post","zh_note":"圓柱體，最通用","en_note":"Round, most versatile"},
  {"zh":"方柱車檔","hk":"方柱車檔","en":"Square Post","zh_note":"方正立柱，現代感","en_note":"Square, modern"},
  {"zh":"八角柱車檔","hk":"八角柱車檔","en":"Octagonal Post","zh_note":"八面柱，防撞面大","en_note":"8-face, big impact face"},
  {"zh":"帶頂帽柱","hk":"連帽柱","en":"Capped Post","zh_note":"頂部雕帽，莊重","en_note":"Carved cap, formal"},
  {"zh":"鏈條柱","hk":"穿鏈柱","en":"Chained Post","zh_note":"預留穿孔串鏈","en_note":"Chain-ready"},
  {"zh":"升降柱基座","hk":"升降柱基座","en":"Rising-post Base","zh_note":"配合電動升降柱","en_note":"For rising bollards"},
  {"zh":"矮柱","hk":"矮柱","en":"Low Post","zh_note":"低矮款，不阻視線","en_note":"Low, sightline clear"},
  {"zh":"高柱","hk":"高柱","en":"Tall Post","zh_note":"高款，強隔離","en_note":"Tall, strong barrier"},
  {"zh":"刻字柱","hk":"刻字柱","en":"Engraved Post","zh_note":"柱身陰刻字","en_note":"Engraved shaft"},
  {"zh":"組合柱","hk":"組合柱","en":"Composite Post","zh_note":"柱+球/燈組合","en_note":"Post+ball/light"}]
},
{
 "slug":"stone-balustrade","idx":"03",
 "zh":{"name":"石材栏杆扶手","hk":"石欄河（麻石欄杆）","en":"Stone Balustrade & Handrail",
  "intro":"花崗岩（麻石）欄杆扶手系統，含望柱、欄板、扶手與柱頭，適用於樓梯、平台、橋樑、陽台與園林步道，提供堅固導向與經典立面。",
  "material":"麻石欄杆由望柱、欄板與扶手榫接組裝，柱頭可雕抱鼓/羅馬/簡約等造型。石材自重穩、抗風壓、耐候不腐，表面火燒/荔枝面防滑，適合香港戶外樓梯與臨海步道。",
  "apps":[("🪜","樓梯與平台","安全導向扶手"),("🌉","橋樑與岸線","抗風壓欄河"),("🏞️","園林步道","古樸協調"),("🏠","陽台與露台","耐用圍護"),("🏛️","地標立面","莊重線條"),("⛲","水池與平台","防潮不腐")]},
 "en":{"name":"Stone Balustrade","hk":"Granite Railing","en":"Stone Balustrade & Handrail",
  "intro":"Granite balustrade systems — newel posts, infill panels, handrail and caps — for stairs, terraces, bridges, balconies and garden paths; solid guidance with a classic profile.",
  "material":"Mortise-joined granite: newels, panels and handrail, with drum/Roman/plain caps. Heavy, wind-loaded, weatherproof and non-rotting; flamed/bush-hammered for grip — ideal for HK outdoor stairs and seafront walks.",
  "apps":[("🪜","Stairs & Terraces","Safe guidance"),("🌉","Bridges & Quays","Wind-loaded rail"),("🏞️","Garden Paths","Rustic match"),("🏠","Balconies","Durable guard"),("🏛️","Landmark Facades","Formal lines"),("⛲","Pools & Decks","Rot-proof")]},
 "common_specs":[("常見規格 Common Sizes","欄板高 400–1100 mm；柱距 1000–1500 mm（可定制）"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 光面 Polished")],
 "items":[
  {"zh":"欄杆望柱","hk":"欄杆柱（望柱）","en":"Newel Post","zh_note":"欄杆主柱，承重","en_note":"Main load post"},
  {"zh":"欄板","hk":"欄板","en":"Infill Panel","zh_note":"柱間欄板","en_note":"Between-post panel"},
  {"zh":"扶手","hk":"扶手","en":"Handrail","zh_note":"頂部扶手條","en_note":"Top rail"},
  {"zh":"抱鼓石柱頭","hk":"抱鼓柱頭","en":"Drum Cap","zh_note":"傳統抱鼓造型","en_note":"Traditional drum cap"},
  {"zh":"羅馬柱頭","hk":"羅馬柱頭","en":"Roman Cap","zh_note":"西式雕花柱頭","en_note":"Roman carved cap"},
  {"zh":"簡約柱頭","hk":"簡約柱頭","en":"Plain Cap","zh_note":"現代平頂","en_note":"Plain modern cap"},
  {"zh":"彎位欄杆","hk":"彎位欄杆","en":"Curved Balustrade","zh_note":"弧線段欄杆","en_note":"Curved section"},
  {"zh":"樓梯欄杆","hk":"樓梯欄杆","en":"Stair Balustrade","zh_note":"踏步配套欄杆","en_note":"Stair-matched"},
  {"zh":"陽台欄杆","hk":"陽台欄杆","en":"Balcony Balustrade","zh_note":"低層圍護","en_note":"Low guard"},
  {"zh":"橋樑欄杆","hk":"橋樑欄河","en":"Bridge Balustrade","zh_note":"高承重合規","en_note":"High-load compliant"}]
},
{
 "slug":"engraved-name-stone","idx":"04",
 "zh":{"name":"刻字门牌石","hk":"門口石（刻字石）","en":"Engraved Entrance Stone",
  "intro":"花崗岩（麻石）門牌、招牌與題字景石，用於別墅、企業、園林與公共設施的識別與點題，陰刻/浮雕字經久清晰、風雨不褪。",
  "material":"選用色澤均一的麻石板材或自然景石，表面光面便於刻字、火燒/荔枝面顯質樸。石材不褪色、不腐、抗撞，適合香港戶外長期標識；字口可填漆或描金強化辨識。",
  "apps":[("🏡","別墅與住宅","門牌識別"),("🏢","企業總部","招牌題字"),("🏞️","園林景觀","點題刻石"),("🏛️","文化設施","落成名碑"),("🪨","廣場與公園","導視刻字"),("💒","宗教場所","莊重題字")]},
 "en":{"name":"Engraved Name Stone","hk":"Entrance Stone","en":"Engraved Entrance Stone",
  "intro":"Granite nameplates, signage and inscribed feature stones for villas, corporations, gardens and public facilities — incised/relief lettering stays sharp through weather.",
  "material":"Even-toned granite slab or natural boulder; polished for legibility, flamed/bush-hammered for rustic feel. Non-fading, non-rotting, impact-proof — ideal for HK outdoor signage; lettering can be painted or gilded.",
  "apps":[("🏡","Villas","Gate nameplate"),("🏢","HQ","Signage"),("🏞️","Gardens","Feature inscription"),("🏛️","Cultural","Commemorative"),("🪨","Plazas","Wayfinding"),("💒","Places of Worship","Formal text")]},
 "common_specs":[("常見規格 Common Sizes","平板 400×600–1200×800 mm；立石高 800–2000 mm"),("表面處理 Finish","光面 Polished（刻字）/ 火燒面 Flamed / 荔枝面 Bush-hammered")],
 "items":[
  {"zh":"平版門牌","hk":"平版門牌","en":"Flat Nameplate","zh_note":"平面刻字門牌","en_note":"Flat engraved plate"},
  {"zh":"立體字門牌","hk":"浮雕門牌","en":"Relief Nameplate","zh_note":"字體浮雕凸起","en_note":"Raised-letter plate"},
  {"zh":"鎮宅石","hk":"鎮宅石","en":"Guard Stone","zh_note":"園門側立石","en_note":"Gate-side stone"},
  {"zh":"公司招牌石","hk":"公司招牌石","en":"Corporate Sign","zh_note":"企業標識石刻","en_note":"Corporate logo stone"},
  {"zh":"別墅門牌","hk":"別墅門牌","en":"Villa Nameplate","zh_note":"住宅入口識別","en_note":"Residence ID"},
  {"zh":"園林刻字石","hk":"園林刻字石","en":"Garden Inscription","zh_note":"景石題字","en_note":"Inscribed boulder"},
  {"zh":"景石題字","hk":"景石題字","en":"Feature Inscription","zh_note":"自然石點題","en_note":"Natural-stone text"},
  {"zh":"奠基石","hk":"奠基石","en":"Foundation Stone","zh_note":"動工紀念刻石","en_note":"Groundbreaking stone"},
  {"zh":"落成紀念石","hk":"落成紀念石","en":"Commemorative Stone","zh_note":"竣工銘刻","en_note":"Completion plaque"},
  {"zh":"導視刻字石","hk":"導視刻字石","en":"Wayfinding Stone","zh_note":"園區指示石刻","en_note":"Directional stone"}]
},
{
 "slug":"carved-stone-pier","idx":"05",
 "zh":{"name":"石雕石墩","hk":"石墩（柱礎）","en":"Carved Stone Pier / Plinth",
  "intro":"花崗岩（麻石）雕刻的柱礎、門枕、抱鼓與景觀石墩，用於建築承托、圍牆收頭與園林點景，承重穩固、雕工精細、歷久彌新。",
  "material":"麻石質地均勻、便於雕刻，柱礎/門枕等承重件選高密度料確保承壓；表面可光面顯雕工或火燒/荔枝面顯質樸。石材耐候抗腐，適合香港戶外與半戶外佈設。",
  "apps":[("🏛️","古建與圍牆","柱礎承托"),("🚪","門樓與照壁","門枕抱鼓"),("🌳","園林點景","景觀石墩"),("🏺","花缽與燈座","基座承托"),("🪨","廣場收頭","圍牆端柱"),("🏠","別墅門廊","裝飾墩座")]},
 "en":{"name":"Carved Stone Pier","hk":"Stone Plinth","en":"Carved Stone Pier / Plinth",
  "intro":"Carved granite plinths, base stones, drum stones and landscape piers for structural support, wall ends and garden accents — load-bearing, finely carved, enduring.",
  "material":"Even granite, easy to carve; load parts use high-density stock for compression. Polished shows carving, flamed/bush-hammered shows rustic grain. Weatherproof and rot-proof for HK use.",
  "apps":[("🏛️","Heritage & Walls","Column base"),("🚪","Gateways","Drum stones"),("🌳","Gardens","Feature pier"),("🏺","Planters & Lamps","Base support"),("🪨","Plaza Ends","Wall terminal"),("🏠","Villa Porches","Decorative pier")]},
 "common_specs":[("常見規格 Common Sizes","方墩 300×300–800×800 mm；圓墩 Φ400–Φ1000 mm"),("表面處理 Finish","光面 Polished / 火燒面 Flamed / 荔枝面 Bush-hammered")],
 "items":[
  {"zh":"方形石墩","hk":"方石墩","en":"Square Pier","zh_note":"方整承重墩","en_note":"Square load pier"},
  {"zh":"圓形石墩","hk":"圓石墩","en":"Round Pier","zh_note":"圓整景觀墩","en_note":"Round feature pier"},
  {"zh":"柱礎石","hk":"柱礎石","en":"Column Base","zh_note":"梁柱承托礎","en_note":"Column plinth"},
  {"zh":"門枕石","hk":"門枕石","en":"Gate Pivot Stone","zh_note":"門軸承石","en_note":"Door-pivot stone"},
  {"zh":"抱鼓石","hk":"抱鼓石","en":"Drum Stone","zh_note":"門枕鼓形雕件","en_note":"Drum-shaped carving"},
  {"zh":"須彌座","hk":"須彌座","en":"Pedestal Base","zh_note":"多層線腳基座","en_note":"Moulded pedestal"},
  {"zh":"燈座石墩","hk":"燈座石墩","en":"Lamp Base","zh_note":"園林燈基座","en_note":"Lamp base"},
  {"zh":"花盆座","hk":"花缽座","en":"Planter Base","zh_note":"花缽承托","en_note":"Planter support"},
  {"zh":"水缽座","hk":"水缽座","en":"Basin Base","zh_note":"水景缽座","en_note":"Basin base"},
  {"zh":"景觀石墩","hk":"景觀石墩","en":"Landscape Pier","zh_note":"點景裝飾墩","en_note":"Accent pier"}]
},
{
 "slug":"flamed-paving","idx":"06",
 "zh":{"name":"火烧板地铺石","hk":"火燒面地鋪石","en":"Flamed Granite Paving Tile",
  "intro":"花崗岩（麻石）經火燒處理的戶外地鋪板材，表面粗糙防滑、色澤沉穩，適用於人行道、廣場、園路與車行區，耐磨抗壓、雨後不滑。",
  "material":"麻石板材經高溫火燒使表層礦物微爆形成均勻糙面，防滑且不易積水反光。石材密度高、抗壓耐磨，耐香港多雨與紫外線；厚度依荷載選 30/50 mm。",
  "apps":[("🚶","人行道","防滑安全"),("🏞️","園路與廣場","自然啞光"),("🅿️","車行區","承重耐磨"),("🏛️","地標鋪裝","莊重色調"),("🌳","住宅社群","低維護"),("🏫","校園戶外","耐走耐磨")]},
 "en":{"name":"Flamed Paving","hk":"Flamed Paving","en":"Flamed Granite Paving Tile",
  "intro":"Granite tiles flamed for a rough, slip-resistant outdoor surface — for footpaths, plazas, garden ways and drive zones; wear-proof, compression-proof, non-slip when wet.",
  "material":"Flame-treated granite gives an even matte non-slip face that sheds water and glare. Dense, compression-proof, UV-stable — thickness 30/50 mm by load.",
  "apps":[("🚶","Footpaths","Slip-safe"),("🏞️","Garden & Plaza","Matte tone"),("🅿️","Drive Zones","Load-wear"),("🏛️","Landmark Paving","Solemn tone"),("🌳","Estates","Low upkeep"),("🏫","Campuses","Heavy foot")]},
 "common_specs":[("常見規格 Common Sizes","300×300 / 400×400 / 600×300 / 600×600 mm；厚 30 / 50 mm"),("表面處理 Finish","火燒面 Flamed（主）/ 荔枝面 Bush-hammered")],
 "items":[
  {"zh":"300×300 方磚","hk":"300方磚","en":"300×300 Tile","zh_note":"小方格，園路","en_note":"Small grid, paths"},
  {"zh":"400×400 方磚","hk":"400方磚","en":"400×400 Tile","zh_note":"通用鋪裝","en_note":"General paving"},
  {"zh":"600×300 長磚","hk":"600×300長磚","en":"600×300 Tile","zh_note":"人字/錯縫","en_note":"Herringbone"},
  {"zh":"600×600 大磚","hk":"600方磚","en":"600×600 Tile","zh_note":"廣場大面","en_note":"Plaza large"},
  {"zh":"厚板 50mm","hk":"50厚板","en":"50mm Slab","zh_note":"車行承重","en_note":"Drive load"},
  {"zh":"收邊磚","hk":"收邊磚","en":"Edge Tile","zh_note":"邊界收口","en_note":"Border trim"},
  {"zh":"階磚","hk":"階磚","en":"Step Tile","zh_note":"平台階梯","en_note":"Terrace step"},
  {"zh":"斜坡磚","hk":"斜波磚","en":"Ramp Tile","zh_note":"無障礙坡","en_note":"Ramp piece"},
  {"zh":"異形切割磚","hk":"異形磚","en":"Cut Tile","zh_note":"弧形/拼花","en_note":"Curved/mosaic"},
  {"zh":"大板 600×900","hk":"大板","en":"600×900 Slab","zh_note":"大堂/廣場","en_note":"Lobby/plaza"}]
},
{
 "slug":"bushhammered-paving","idx":"07",
 "zh":{"name":"荔枝面地铺石","hk":"荔枝面地鋪石","en":"Bush-Hammered Granite Paving",
  "intro":"花崗岩（麻石）經荔枝錘處理的戶外地鋪板材，表面呈均勻點狀糙面、觸感細密防滑，色澤溫潤，適用人行道、園路、廣場與建築散水。",
  "material":"麻石板材以荔枝錘衝打形成細密均點糙面，比火燒面更細膩、防滑且不易藏污。石材抗壓耐磨、耐候，適合香港潮濕多雨戶外；厚度依荷載選 30/50 mm。",
  "apps":[("🚶","人行道","細密防滑"),("🏞️","園林步道","溫潤質感"),("🏛️","建築散水","協調立面"),("🅿️","車行區","承重耐磨"),("🌳","住宅社群","低維護"),("🏫","校園戶外","耐走耐磨")]},
 "en":{"name":"Bush-Hammered Paving","hk":"Bush-Hammered Paving","en":"Bush-Hammered Granite Paving",
  "intro":"Granite tiles bush-hammered into an even dotted matte face — fine, slip-resistant, stain-shedding; for footpaths, garden ways, plazas and building aprons.",
  "material":"Pneumatic-peened for a finer, denser non-slip face than flaming. Compression-proof, wear-proof, weatherproof — thickness 30/50 mm by load.",
  "apps":[("🚶","Footpaths","Fine grip"),("🏞️","Garden Ways","Warm grain"),("🏛️","Aprons","Facade match"),("🅿️","Drive Zones","Load-wear"),("🌳","Estates","Low upkeep"),("🏫","Campuses","Heavy foot")]},
 "common_specs":[("常見規格 Common Sizes","300×300 / 400×400 / 600×300 / 600×600 mm；厚 30 / 50 mm"),("表面處理 Finish","荔枝面 Bush-hammered（主）/ 火燒面 Flamed")],
 "items":[
  {"zh":"300×300 方磚","hk":"300方磚","en":"300×300 Tile","zh_note":"園路小格","en_note":"Path grid"},
  {"zh":"400×400 方磚","hk":"400方磚","en":"400×400 Tile","zh_note":"通用鋪裝","en_note":"General"},
  {"zh":"600×300 長磚","hk":"600×300長磚","en":"600×300 Tile","zh_note":"錯縫鋪","en_note":"Staggered"},
  {"zh":"600×600 大磚","hk":"600方磚","en":"600×600 Tile","zh_note":"廣場大面","en_note":"Plaza"},
  {"zh":"厚板 50mm","hk":"50厚板","en":"50mm Slab","zh_note":"車行承重","en_note":"Drive load"},
  {"zh":"收邊磚","hk":"收邊磚","en":"Edge Tile","zh_note":"邊界收口","en_note":"Border"},
  {"zh":"階磚","hk":"階磚","en":"Step Tile","zh_note":"平台階梯","en_note":"Step"},
  {"zh":"斜坡磚","hk":"斜波磚","en":"Ramp Tile","zh_note":"無障礙坡","en_note":"Ramp"},
  {"zh":"異形切割磚","hk":"異形磚","en":"Cut Tile","zh_note":"弧形拼花","en_note":"Curved"},
  {"zh":"大板 600×900","hk":"大板","en":"600×900 Slab","zh_note":"大堂廣場","en_note":"Lobby/plaza"}]
},
{
 "slug":"tactile-paving","idx":"08",
 "zh":{"name":"盲道石","hk":"導盲磚（盲人磚）","en":"Tactile Paving Stone",
  "intro":"花崗岩（麻石）觸覺引導鋪裝，含條紋導盲（行進）與圓點警示（停止），用於人行道、路口與公共設施，符合無障礙設計，雨後防滑、耐磨抗壓。",
  "material":"麻石觸覺磚以模具或火燒/雕刻成型條紋與圓點，觸感清晰、耐磨不磨平。石材密度高、抗壓、耐候，適合香港多雨戶外長期使用；常配黃/灰雙色引導。",
  "apps":[("🚶","人行道","條紋導引"),("🚦","路口與轉角","圓點警示"),("🏢","公共設施","無障礙動線"),("🚇","車站與口岸","安全引導"),("🏫","校園與醫院","守護視障"),("🌳","公園步道","連續引導")]},
 "en":{"name":"Tactile Paving","hk":"Tactile Paving","en":"Tactile Paving Stone",
  "intro":"Granite tactile guides — directional bars (travel) and warning dots (stop) — for footpaths, junctions and facilities; accessibility-compliant, slip-resistant when wet, wear-proof.",
  "material":"Moulded or carved granite bars/dots with clear, non-flattening tactile relief. Dense, compression-proof, weatherproof — yellow/grey dual colour for guidance in HK rain.",
  "apps":[("🚶","Footpaths","Directional bars"),("🚦","Junctions","Warning dots"),("🏢","Facilities","Accessible route"),("🚇","Stations","Safe guide"),("🏫","Campus/Hospital","Protect vision"),("🌳","Park Paths","Continuous guide")]},
 "common_specs":[("常見規格 Common Sizes","300×300 mm（條紋/圓點）；厚 20 / 30 mm"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 模具成型 Moulded")],
 "items":[
  {"zh":"條紋導盲磚","hk":"條紋導盲磚","en":"Directional Bar","zh_note":"直行引導","en_note":"Travel guide"},
  {"zh":"圓點警示磚","hk":"圓點警示磚","en":"Warning Dot","zh_note":"停止/轉向","en_note":"Stop/turn"},
  {"zh":"黃色警示磚","hk":"黃色警示磚","en":"Yellow Warning","zh_note":"高辨識警示","en_note":"Hi-vis warning"},
  {"zh":"灰色導盲磚","hk":"灰色導盲磚","en":"Grey Guide","zh_note":"低調引導","en_note":"Low-key guide"},
  {"zh":"帶坡磚","hk":"帶坡磚","en":"Ramp Tile","zh_note":"無障礙坡道","en_note":"Ramp piece"},
  {"zh":"轉角磚","hk":"轉角磚","en":"Corner Tile","zh_note":"路口轉向","en_note":"Junction turn"},
  {"zh":"路口磚","hk":"路口磚","en":"Junction Tile","zh_note":"斑馬線接續","en_note":"Crossing link"},
  {"zh":"厚板導盲","hk":"厚板導盲","en":"Thick Guide","zh_note":"車行臨邊","en_note":"Edge of drive"},
  {"zh":"異形收邊","hk":"異形收邊","en":"Cut Edge","zh_note":"弧形收口","en_note":"Curved trim"},
  {"zh":"不鏽鋼組合","hk":"鋼石組合","en":"Steel+Stone","zh_note":"金屬嵌條輔助","en_note":"Steel inlay aid"}]
},
{
 "slug":"cobblestone","idx":"09",
 "zh":{"name":"马蹄石（小方块石）","hk":"麻石小方石（卵石）","en":"Granite Cobblestone / Setts",
  "intro":"花崗岩（麻石）小方石與卵石，用於園路、廣場、車行與歷史街區鋪裝，質樸耐用、排水佳、可拼花，承載老香港街巷的經典麻石肌理。",
  "material":"麻石小方石經鑿面/火燒處理，棱角分明或圓潤，單塊獨立承重、整片咬合穩固。石材抗壓耐磨、耐候不滑，適合香港潮濕戶外與特色街區。",
  "apps":[("🏘️","歷史街區","經典麻石肌理"),("🚶","園路步道","質樸自然"),("🅿️","車行區","單塊承重"),("🏞️","廣場拼花","圖案鋪裝"),("🌳","住宅社群","低維護"),("⛲","水岸步道","防滑耐潮")]},
 "en":{"name":"Cobblestone","hk":"Granite Setts","en":"Granite Cobblestone / Setts",
  "intro":"Granite setts and cobbles for garden ways, plazas, drive zones and heritage streets — rustic, permeable, pattern-able; the classic Hong Kong granite texture.",
  "material":"Dressed or flamed granite setts, sharp or rounded, each independently load-bearing and interlocked as a field. Compression-proof, wear-proof, weatherproof and non-slip.",
  "apps":[("🏘️","Heritage Streets","Classic grain"),("🚶","Garden Paths","Rustic"),("🅿️","Drive Zones","Per-block load"),("🏞️","Plaza Patterns","Pattern lay"),("🌳","Estates","Low upkeep"),("⛲","Quay Walks","Wet-grip")]},
 "common_specs":[("常見規格 Common Sizes","100×100 / 90×90 / 100×200 mm；厚 50–80 mm"),("表面處理 Finish","鑿面 Dressed / 火燒面 Flamed / 圓角 Rounded")],
 "items":[
  {"zh":"100×100 小方石","hk":"100方石","en":"100×100 Setts","zh_note":"標準方格","en_note":"Std grid"},
  {"zh":"90×90 小方石","hk":"90方石","en":"90×90 Setts","zh_note":"緊密咬合","en_note":"Tight joint"},
  {"zh":"八角小方石","hk":"八角小石","en":"Octagon Setts","zh_note":"八角造型","en_note":"Octagon form"},
  {"zh":"圓角小方石","hk":"圓角小石","en":"Rounded Setts","zh_note":"圓潤不絆","en_note":"Rounded, no trip"},
  {"zh":"亂拼小石","hk":"亂拼小石","en":"Random Cobble","zh_note":"自然碎拼","en_note":"Random lay"},
  {"zh":"車行小方石","hk":"車行小石","en":"Drive Setts","zh_note":"加厚承重","en_note":"Thick load"},
  {"zh":"行人小方石","hk":"行人小石","en":"Pedestrian Setts","zh_note":"標準厚度","en_note":"Std thickness"},
  {"zh":"收邊小石","hk":"收邊小石","en":"Edge Setts","zh_note":"邊界收口","en_note":"Border trim"},
  {"zh":"異色拼花","hk":"異色拼花","en":"Two-tone Pattern","zh_note":"雙色圖案","en_note":"2-tone pattern"},
  {"zh":"厚版小石","hk":"厚版小石","en":"Thick Setts","zh_note":"重載區","en_note":"Heavy load"}]
},
{
 "slug":"crazy-paving","idx":"10",
 "zh":{"name":"冰裂纹碎拼石","hk":"冰裂紋碎拼石","en":"Irregular Flagstone / Crazy Paving",
  "intro":"花崗岩（麻石）自然面或機切的冰裂紋碎拼板材，用於園路、廣場、景牆與水岸，肌理靈動、排水自然、野趣盎然，契合香港園林與休閒空間。",
  "material":"麻石板材經自然面處理或機切多邊形，拼合呈冰裂紋。石材耐候、抗壓、不褪色，縫隙可填碎石或植草；適合香港戶外園景長期使用。",
  "apps":[("🏞️","園林步道","野趣肌理"),("🪨","景牆與旱景","自然面質"),("⛲","水岸平台","防滑耐潮"),("🏛️","廣場碎拼","圖案靈動"),("🌳","住宅社群","低維護"),("🏫","校園戶外","親自然")]},
 "en":{"name":"Crazy Paving","hk":"Irregular Flagstone","en":"Irregular Flagstone / Crazy Paving",
  "intro":"Natural or machine-cut granite crazy paving for garden ways, plazas, feature walls and quays — fluid texture, natural drainage, rustic charm for HK landscapes.",
  "material":"Natural-face or machine-cut polygonal granite laid in ice-crack pattern. Weatherproof, compression-proof, non-fading; joints filled with grit or planted — for HK outdoor use.",
  "apps":[("🏞️","Garden Paths","Rustic texture"),("🪨","Feature Walls","Natural face"),("⛲","Quay Decks","Wet-grip"),("🏛️","Plaza Crazy","Fluid pattern"),("🌳","Estates","Low upkeep"),("🏫","Campuses","Biophilic")]},
 "common_specs":[("常見規格 Common Sizes","多邊形碎塊 200–600 mm；厚 30 / 50 mm"),("表面處理 Finish","自然面 Natural / 火燒面 Flamed / 機切 Machine-cut")],
 "items":[
  {"zh":"自然面冰裂","hk":"自然面冰裂","en":"Natural Ice-crack","zh_note":"天然糙面","en_note":"Raw matte face"},
  {"zh":"機切冰裂","hk":"機切冰裂","en":"Machine-cut Ice","zh_note":"規整多邊","en_note":"Regular polygon"},
  {"zh":"大塊碎拼","hk":"大塊碎拼","en":"Large Flag","zh_note":"廣場大面","en_note":"Plaza large"},
  {"zh":"小塊碎拼","hk":"小塊碎拼","en":"Small Flag","zh_note":"園路細拼","en_note":"Path fine"},
  {"zh":"收邊冰裂","hk":"收邊冰裂","en":"Edge Ice","zh_note":"邊界收口","en_note":"Border trim"},
  {"zh":"圓角冰裂","hk":"圓角冰裂","en":"Rounded Ice","zh_note":"圓潤不絆","en_note":"Rounded edge"},
  {"zh":"黑白拼","hk":"黑白拼","en":"B/W Pattern","zh_note":"雙色圖案","en_note":"2-tone"},
  {"zh":"園路碎拼","hk":"園路碎拼","en":"Garden Crazy","zh_note":"步道鋪裝","en_note":"Path lay"},
  {"zh":"廣場碎拼","hk":"廣場碎拼","en":"Plaza Crazy","zh_note":"大面圖案","en_note":"Plaza pattern"},
  {"zh":"景牆碎拼","hk":"景牆碎拼","en":"Wall Crazy","zh_note":"立面粉拼","en_note":"Wall clad"}]
},
{
 "slug":"curb-stone","idx":"11",
 "zh":{"name":"路沿石（道牙石）","hk":"路緣石（石壆）","en":"Granite Curb Stone / Kerb",
  "intro":"花崗岩（麻石）路緣石與道牙，用於車行道、人行道、廣場與綠化帶邊界，分隔動線、保護路基、規整立面，抗壓耐磨、線條筆直。",
  "material":"麻石路緣石以高壓成型或整料鑿製，棱角分明、線條平直。石材抗壓、抗凍融、耐候，表面常做火燒/荔枝面；適合香港道路與公共空間長期使用。",
  "apps":[("🛣️","車行道邊","分隔人車"),("🚶","人行道邊","保護路基"),("🌳","綠化帶","界石收邊"),("🏞️","廣場與園區","線條規整"),("🅿️","停車場","動線界定"),("🏫","校園與醫院","安全邊界")]},
 "en":{"name":"Curb Stone","hk":"Granite Kerb","en":"Granite Curb Stone / Kerb",
  "intro":"Granite kerbs for carriageways, footpaths, plazas and green belts — separate flows, protect subgrade, straighten lines; compression-proof, wear-proof, true-edged.",
  "material":"Pressed or dressed granite with crisp straight lines. Compression-proof, frost-proof, weatherproof; flamed/bush-hammered face — for HK roads and public space.",
  "apps":[("🛣️","Carriageway","Separate flows"),("🚶","Footpath","Protect base"),("🌳","Green Belt","Edge stone"),("🏞️","Plaza/Park","Clean lines"),("🅿️","Car Park","Define lane"),("🏫","Campus/Hospital","Safe edge")]},
 "common_specs":[("常見規格 Common Sizes","1000×300×120 / 1000×250×100 mm（長×上寬×高，可定制）"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 光面 Polished")],
 "items":[
  {"zh":"立道牙（路緣石）","hk":"立路緣石","en":"Vertical Kerb","zh_note":"直立分隔","en_note":"Vertical divide"},
  {"zh":"平石","hk":"平石","en":"Lay-back Kerb","zh_note":"與路面齊平","en_note":"Flush with road"},
  {"zh":"路肩石","hk":"路肩石","en":"Channel Kerb","zh_note":"排水路肩","en_note":"Drain shoulder"},
  {"zh":"R型圓角道牙","hk":"R型圓角道牙","en":"Rounded Kerb","zh_note":"圓角防絆","en_note":"Rounded, no trip"},
  {"zh":"斜角道牙","hk":"斜角道牙","en":"Bevelled Kerb","zh_note":"斜角導水","en_note":"Bevel drain"},
  {"zh":"L型道牙","hk":"L型道牙","en":"L-type Kerb","zh_note":"擋邊兼收水","en_note":"Curb+drain"},
  {"zh":"帶排水孔道牙","hk":"排水孔道牙","en":"Drained Kerb","zh_note":"預留孔排水","en_note":"Pre-drilled drain"},
  {"zh":"轉角道牙","hk":"轉角道牙","en":"Corner Kerb","zh_note":"路口轉角","en_note":"Junction corner"},
  {"zh":"異型道牙","hk":"異型道牙","en":"Special Kerb","zh_note":"定制造型","en_note":"Custom shape"},
  {"zh":"樹池道牙","hk":"樹圈道牙","en":"Tree-ring Kerb","zh_note":"樹池收邊","en_note":"Tree ring"}]
},
{
 "slug":"curved-curb","idx":"12",
 "zh":{"name":"弯道石","hk":"彎位路緣石（曲線道牙）","en":"Curved Curb / Radius Kerb",
  "intro":"花崗岩（麻石）曲線路緣石，按半徑預彎成型，用於圓環、彎道、廣場弧線與景觀曲線，線條順暢、拼接密實，抗壓耐磨。",
  "material":"麻石曲線道牙以模具預彎或水刀/金剛線切割成弧，曲率準確、接縫密。石材耐候抗凍融，表面火燒/荔枝面；適合香港道路與園景弧線。",
  "apps":[("🔄","圓環與彎道","順暢弧線"),("🏞️","廣場弧線","線條優美"),("🌳","園景曲線","自然過渡"),("🅿️","車場弧邊","動線引導"),("🏫","校園步道","安全彎位"),("⛲","水岸曲線","防潮耐潮")]},
 "en":{"name":"Curved Curb","hk":"Radius Kerb","en":"Curved Curb / Radius Kerb",
  "intro":"Pre-radiused granite kerbs for roundabouts, bends, plaza arcs and landscape curves — smooth lines, tight joints, compression-proof and wear-proof.",
  "material":"Moulded or wire-cut granite to accurate radius, tight seams. Frost-proof, weatherproof, flamed/bush-hammered face — for HK road and garden arcs.",
  "apps":[("🔄","Roundabouts","Smooth arc"),("🏞️","Plaza Arc","Elegant line"),("🌳","Garden Curve","Natural transition"),("🅿️","Lot Arc","Lane guide"),("🏫","Campus Path","Safe bend"),("⛲","Quay Curve","Wet-proof")]},
 "common_specs":[("常見規格 Common Sizes","半徑 R500 / R1000 / R2000 mm；長×高 500×120 mm（可定制）"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 光面 Polished")],
 "items":[
  {"zh":"內彎道牙","hk":"內彎道牙","en":"Inner Curve","zh_note":"圓環內弧","en_note":"Inner arc"},
  {"zh":"外彎道牙","hk":"外彎道牙","en":"Outer Curve","zh_note":"圓環外弧","en_note":"Outer arc"},
  {"zh":"R500 小半徑","hk":"R500彎","en":"R500 Kerb","zh_note":"急彎小弧","en_note":"Tight arc"},
  {"zh":"R1000 半徑","hk":"R1000彎","en":"R1000 Kerb","zh_note":"通用中弧","en_note":"Mid arc"},
  {"zh":"R2000 大半徑","hk":"R2000彎","en":"R2000 Kerb","zh_note":"緩彎大弧","en_note":"Wide arc"},
  {"zh":"S彎道牙","hk":"S彎道牙","en":"S-curve Kerb","zh_note":"反向曲線","en_note":"Reverse curve"},
  {"zh":"圓角彎位","hk":"圓角彎位","en":"Fillet Curve","zh_note":"緩衝彎","en_note":"Ease bend"},
  {"zh":"收口彎位","hk":"收口彎位","en":"Taper Curve","zh_note":"弧線收口","en_note":"Arc taper"},
  {"zh":"坡道彎位","hk":"坡道彎位","en":"Ramp Curve","zh_note":"無障礙坡弧","en_note":"Ramp arc"},
  {"zh":"異型彎位","hk":"異型彎位","en":"Special Curve","zh_note":"定制曲線","en_note":"Custom curve"}]
},
{
 "slug":"tree-pit-stone","idx":"13",
 "zh":{"name":"树池石","hk":"樹池石（樹圈石）","en":"Tree Pit Stone / Tree Surround",
  "intro":"花崗岩（麻石）樹池圍石，用於人行道、廣場與園區樹穴收邊，保護樹根、規整立面、利於排水，堅固耐撞、與鋪裝協調。",
  "material":"麻石樹池石以整料鑿製或預製弧段拼合，棱角圓潤不絆腳。石材抗壓、耐候、抗凍融，表面火燒/荔枝面；適合香港戶外樹穴長期使用。",
  "apps":[("🌳","人行道樹穴","保護樹根"),("🏞️","廣場與園區","立面規整"),("🅿️","停車場綠帶","分隔緩衝"),("🚶","園路節點","收邊美觀"),("🏫","校園與醫院","安全圍護"),("⛲","水岸綠化","防潮耐潮")]},
 "en":{"name":"Tree Pit Stone","hk":"Tree Surround","en":"Tree Pit Stone / Tree Surround",
  "intro":"Granite tree-pit surrounds for street, plaza and park tree wells — protect roots, tidy lines, aid drainage; solid, impact-proof, matching the paving.",
  "material":"Dressed or pre-cast arc segments, rounded (trip-free) edges. Compression-proof, weatherproof, frost-proof, flamed/bush-hammered face — for HK outdoor wells.",
  "apps":[("🌳","Street Wells","Protect roots"),("🏞️","Plaza/Park","Tidy lines"),("🅿️","Lot Green","Buffer"),("🚶","Path Nodes","Neat edge"),("🏫","Campus/Hospital","Safe guard"),("⛲","Quay Green","Wet-proof")]},
 "common_specs":[("常見規格 Common Sizes","方圈 1000×1000 / 圓圈 Φ1000–Φ1500 mm；高 100–150 mm"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 光面 Polished")],
 "items":[
  {"zh":"方形樹池","hk":"方樹池","en":"Square Pit","zh_note":"方正樹圈","en_note":"Square ring"},
  {"zh":"圓形樹池","hk":"圓樹池","en":"Round Pit","zh_note":"圓整樹圈","en_note":"Round ring"},
  {"zh":"八角樹池","hk":"八角樹池","en":"Octagon Pit","zh_note":"八角造型","en_note":"Octagon form"},
  {"zh":"帶格柵樹池","hk":"連格柵樹池","en":"Grated Pit","zh_note":"配格柵透水","en_note":"With grate"},
  {"zh":"雙層樹池","hk":"雙層樹池","en":"Double Pit","zh_note":"高低雙圈","en_note":"Double ring"},
  {"zh":"收邊樹池","hk":"收邊樹池","en":"Edge Pit","zh_note":"與鋪裝齊","en_note":"Flush edge"},
  {"zh":"異型樹池","hk":"異型樹池","en":"Special Pit","zh_note":"定制造型","en_note":"Custom shape"},
  {"zh":"草地樹池","hk":"草地樹池","en":"Lawn Pit","zh_note":"草地收邊","en_note":"Lawn edge"},
  {"zh":"廣場樹池","hk":"廣場樹池","en":"Plaza Pit","zh_note":"大面陳列","en_note":"Plaza display"},
  {"zh":"組合樹池","hk":"組合樹池","en":"Composite Pit","zh_note":"樹池+坐凳","en_note":"Pit+bench"}]
},
{
 "slug":"coping-stone","idx":"14",
 "zh":{"name":"压顶石","hk":"壓頂石（笠帽石）","en":"Coping Stone / Wall Coping",
  "intro":"花崗岩（麻石）牆頂壓頂與笠帽石，用於矮牆、女兒牆、花槽、欄河與柱頂收頭，遮雨防滲、線條挺括，保護牆身、提升立面質感。",
  "material":"麻石壓頂石以整料鑿製，前緣常做滴水/斜角導水。石材抗壓、耐候、抗凍融，表面火燒/荔枝面或光面；適合香港多雨戶外收頭。",
  "apps":[("🧱","矮牆與女兒牆","遮雨收頭"),("🪴","花槽與欄河","挺括線條"),("🏛️","柱頂與牆頭","莊重收口"),("🏞️","園景牆身","保護牆身"),("🌳","住宅社群","低維護"),("⛲","水岸擋牆","防潮耐潮")]},
 "en":{"name":"Coping Stone","hk":"Wall Coping","en":"Coping Stone / Wall Coping",
  "intro":"Granite coping and capping for low walls, parapets, planters, balustrades and column tops — shed rain, crisp lines, protect masonry and lift the facade.",
  "material":"Dressed granite with drip/bevel front edge. Compression-proof, weatherproof, frost-proof, flamed/bush-hammered or polished — for HK rainy outdoor tops.",
  "apps":[("🧱","Walls/Parapets","Weather cap"),("🪴","Planters/Rails","Crisp line"),("🏛️","Column/Wall Top","Formal cap"),("🏞️","Garden Walls","Protect body"),("🌳","Estates","Low upkeep"),("⛲","Quay Walls","Wet-proof")]},
 "common_specs":[("常見規格 Common Sizes","長 600–1000 mm；出檐 50–80 mm；厚 50–80 mm"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 光面 Polished")],
 "items":[
  {"zh":"平牆壓頂","hk":"平牆壓頂","en":"Flat Coping","zh_note":"平直收頭","en_note":"Flat cap"},
  {"zh":"女兒牆壓頂","hk":"女兒牆壓頂","en":"Parapet Coping","zh_note":"屋面女兒牆","en_note":"Parapet top"},
  {"zh":"圓角壓頂","hk":"圓角壓頂","en":"Rounded Coping","zh_note":"圓潤前緣","en_note":"Rounded edge"},
  {"zh":"斜角壓頂","hk":"斜角壓頂","en":"Bevelled Coping","zh_note":"斜導水","en_note":"Bevel drain"},
  {"zh":"欄河壓頂","hk":"欄河壓頂","en":"Balustrade Coping","zh_note":"欄杆頂蓋","en_note":"Rail cap"},
  {"zh":"花槽壓頂","hk":"花槽壓頂","en":"Planter Coping","zh_note":"花槽收口","en_note":"Planter cap"},
  {"zh":"柱頂壓頂","hk":"柱頂壓頂","en":"Column Cap","zh_note":"柱頭笠帽","en_note":"Column cap"},
  {"zh":"收邊壓頂","hk":"收邊壓頂","en":"Edge Coping","zh_note":"轉角收口","en_note":"Corner cap"},
  {"zh":"異型壓頂","hk":"異型壓頂","en":"Special Coping","zh_note":"定制造型","en_note":"Custom shape"},
  {"zh":"厚版壓頂","hk":"厚版壓頂","en":"Thick Coping","zh_note":"重載收頭","en_note":"Heavy cap"}]
},
{
 "slug":"step-tread","idx":"15",
 "zh":{"name":"台阶踏步石","hk":"石級（踏步石）","en":"Granite Step Tread / Stair Tread",
  "intro":"花崗岩（麻石）室內外踏步與石級，用於大堂、平台、園林階梯與無障礙坡道，承重防滑、線條挺括、耐磨抗壓。",
  "material":"麻石踏步以整料鑿製，踏面常做防滑槽/火燒/荔枝面，踢腳可一體。石材抗壓耐磨、耐候，適合香港潮濕戶外階梯長期使用。",
  "apps":[("🪜","室外階梯","防滑安全"),("🏛️","大堂石級","莊重線條"),("🏞️","園林階梯","自然協調"),("♿","無障礙坡","平穩過渡"),("🏠","別墅門廊","耐用美觀"),("🏫","校園與醫院","重載耐磨")]},
 "en":{"name":"Step Tread","hk":"Stair Tread","en":"Granite Step Tread / Stair Tread",
  "intro":"Granite indoor/outdoor treads for lobbies, terraces, garden stairs and ramps — load-bearing, slip-resistant, crisp, wear-proof.",
  "material":"Dressed granite with anti-slip groove / flamed / bush-hammered tread, integral riser. Compression-proof, wear-proof, weatherproof — for HK wet outdoor stairs.",
  "apps":[("🪜","Outdoor Stairs","Slip-safe"),("🏛️","Lobby Treads","Formal line"),("🏞️","Garden Stairs","Natural match"),("♿","Ramps","Smooth transit"),("🏠","Villa Porches","Durable"),("🏫","Campus/Hospital","Heavy-wear")]},
 "common_specs":[("常見規格 Common Sizes","踏面 300–600 mm 深；踢腳高 150–200 mm；厚 40–60 mm"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 防滑槽 Grooved")],
 "items":[
  {"zh":"室內階磚","hk":"室內階磚","en":"Indoor Tread","zh_note":"光面室內","en_note":"Indoor polished"},
  {"zh":"室外踏步","hk":"室外踏步","en":"Outdoor Tread","zh_note":"火燒防滑","en_note":"Flamed grip"},
  {"zh":"防滑槽踏步","hk":"防滑槽踏步","en":"Grooved Tread","zh_note":"踏面刻槽","en_note":"Grooved face"},
  {"zh":"圓角踏步","hk":"圓角踏步","en":"Rounded Tread","zh_note":"圓潤前緣","en_note":"Rounded nosing"},
  {"zh":"帶踢腳踏步","hk":"連踢腳踏步","en":"Rise+Trade","zh_note":"踢踏一體","en_note":"Riser+tread"},
  {"zh":"坡道踏步","hk":"坡道踏步","en":"Ramp Tread","zh_note":"無障礙坡","en_note":"Ramp piece"},
  {"zh":"大堂階","hk":"大堂石級","en":"Lobby Stair","zh_note":"大面陳列","en_note":"Lobby large"},
  {"zh":"園林階","hk":"園林石級","en":"Garden Stair","zh_note":"自然協調","en_note":"Garden match"},
  {"zh":"異型踏步","hk":"異型踏步","en":"Special Tread","zh_note":"弧形/異形","en_note":"Curved/special"},
  {"zh":"厚版踏步","hk":"厚版踏步","en":"Thick Tread","zh_note":"重載階","en_note":"Heavy load"}]
},
{
 "slug":"stone-drain-grate","idx":"16",
 "zh":{"name":"石材水篦子地漏石","hk":"石水屜（去水石蓋）","en":"Stone Drain Grate / Floor Grate",
  "intro":"花崗岩（麻石）地漏與水篦子蓋板，用於廣場、園區、車行與建築散水的地表排水，承重防滑、不鏽不腐、與鋪裝協調。",
  "material":"麻石水篦以整料鑿孔或線切縫，栅條間距合規、承重達車行級。石材抗壓、耐候、抗凍融，表面火燒/荔枝面防滑；適合香港多雨戶外排水。",
  "apps":[("🌧️","廣場排水","地表收水"),("🅿️","車行區","重載格蓋"),("🏞️","園區散水","協調鋪裝"),("🏢","建築散水","防堵導水"),("🌳","住宅社群","低維護"),("⛲","水岸與池邊","防潮耐潮")]},
 "en":{"name":"Stone Drain Grate","hk":"Floor Grate","en":"Stone Drain Grate / Floor Grate",
  "intro":"Granite floor grates and drain covers for plaza, park, drive and building-apron surface drainage — load-bearing, slip-resistant, non-rusting, paving-matched.",
  "material":"Dressed or wire-cut granite with code-compliant bar spacing, drive-load rated. Compression-proof, weatherproof, frost-proof, flamed/bush-hammered grip — for HK rainy drainage.",
  "apps":[("🌧️","Plaza Drain","Surface collect"),("🅿️","Drive Zone","Load grate"),("🏞️","Park Apron","Match paving"),("🏢","Building Apron","Anti-clog"),("🌳","Estates","Low upkeep"),("⛲","Quay/Pool","Wet-proof")]},
 "common_specs":[("常見規格 Common Sizes","格蓋 300×300 / 500×500 mm；縫寬 15–25 mm（可定制）"),("表面處理 Finish","火燒面 Flamed / 荔枝面 Bush-hammered / 線切 Slot-cut")],
 "items":[
  {"zh":"直線水篦","hk":"直線水篦","en":"Linear Grate","zh_note":"長條直排","en_note":"Linear row"},
  {"zh":"格柵水篦","hk":"格柵水篦","en":"Grid Grate","zh_note":"井字格","en_note":"Grid pattern"},
  {"zh":"圓孔水篦","hk":"圓孔水篦","en":"Round-hole Grate","zh_note":"圓孔排水","en_note":"Round holes"},
  {"zh":"長條孔水篦","hk":"長條孔水篦","en":"Slot Grate","zh_note":"細長縫","en_note":"Slot gaps"},
  {"zh":"防滑水篦","hk":"防滑水篦","en":"Anti-slip Grate","zh_note":"糙面防絆","en_note":"Grip face"},
  {"zh":"園林水篦","hk":"園林水篦","en":"Garden Grate","zh_note":"低調收水","en_note":"Low-key"},
  {"zh":"車行水篦","hk":"車行水篦","en":"Drive Grate","zh_note":"重載格蓋","en_note":"Drive load"},
  {"zh":"收邊水篦","hk":"收邊水篦","en":"Edge Grate","zh_note":"邊界收口","en_note":"Border trim"},
  {"zh":"異型水篦","hk":"異型水篦","en":"Special Grate","zh_note":"定制造型","en_note":"Custom shape"},
  {"zh":"組合水篦","hk":"組合水篦","en":"Composite Grate","zh_note":"石+鋼組合","en_note":"Stone+steel"}]
},
{
 "slug":"curtain-wall-panel","idx":"17",
 "zh":{"name":"外墙干挂花岗岩板","hk":"外牆乾掛麻石板","en":"Granite Curtain Wall Panel",
  "intro":"花崗岩（麻石）幕牆幹掛板材，用於商廈、酒店、公共建築與車站外立面，背栓/開放式幹掛，平整挺括、耐候不褪色、維護成本低。",
  "material":"麻石幕牆板選高密度、色差小的料，背面開背栓孔或槽式幹掛，現場不濕貼。石材抗壓、耐紫外線、抗凍融，適合香港高溫多雨、臨海鹽霧的外牆。",
  "apps":[("🏢","商廈外立面","挺括平整"),("🏨","酒店與會所","高級質感"),("🚉","車站與口岸","耐久公共面"),("🏛️","公共建築","莊重立面"),("🏬","商場裙樓","低維護"),("🌉","橋樑與口岸","防潮耐潮")]},
 "en":{"name":"Curtain Wall Panel","hk":"Cladding Panel","en":"Granite Curtain Wall Panel",
  "intro":"Granite curtain-wall panels for offices, hotels, public buildings and stations — back-bolted/open dry-hung, flat, weatherproof, non-fading, low maintenance.",
  "material":"High-density, low-colour-variation granite with back-bolt holes or groove dry-hang (no wet stick). Compression-proof, UV-stable, frost-proof — for HK hot, rainy, coastal facades.",
  "apps":[("🏢","Office Facades","Flat plane"),("🏨","Hotels","Premium feel"),("🚉","Stations","Durable public"),("🏛️","Public Bldg","Formal face"),("🏬","Mall Podium","Low upkeep"),("🌉","Bridge/Port","Wet-proof")]},
 "common_specs":[("常見規格 Common Sizes","標準板 600×900 / 800×1200 mm；厚 25–30 mm（幹掛）"),("表面處理 Finish","光面 Polished / 火燒面 Flamed / 荔枝面 Bush-hammered")],
 "items":[
  {"zh":"標準幕牆板","hk":"標準幕牆板","en":"Std Panel","zh_note":"600×900 常規","en_note":"600×900 std"},
  {"zh":"大板幕牆","hk":"大板幕牆","en":"Large Panel","zh_note":"800×1200 大面","en_note":"800×1200 large"},
  {"zh":"防火級板材","hk":"防火級板","en":"Fire-rated Panel","zh_note":"背襯防火","en_note":"Fire-backed"},
  {"zh":"背栓式板","hk":"背栓式板","en":"Back-bolt Panel","zh_note":"背栓幹掛","en_note":"Back-bolt hung"},
  {"zh":"開放式幕牆","hk":"開放式幕牆","en":"Open-joint Wall","zh_note":"開縫透氣","en_note":"Open joint"},
  {"zh":"密縫幕牆","hk":"密縫幕牆","en":"Closed-joint Wall","zh_note":"密拼平整","en_note":"Tight joint"},
  {"zh":"柱面包板","hk":"柱面包板","en":"Column Clad","zh_note":"圓柱包覆","en_note":"Column wrap"},
  {"zh":"收邊包板","hk":"收邊包板","en":"Edge Clad","zh_note":"轉角收口","en_note":"Corner trim"},
  {"zh":"異型包柱","hk":"異型包柱","en":"Special Clad","zh_note":"曲面包覆","en_note":"Curved wrap"},
  {"zh":"厚板幕牆","hk":"厚板幕牆","en":"Thick Panel","zh_note":"重載/基層","en_note":"Heavy base"}]
},
{
 "slug":"mushroom-stone","idx":"18",
 "zh":{"name":"蘑菇石","hk":"蘑菇石（磊石）","en":"Mushroom Stone / Rustic Cladding",
  "intro":"花崗岩（麻石）蘑菇石（磊石）外牆裝飾板，表面中部凸起、邊緣薄收，質樸立體，用於別墅、圍牆、景牆與園林建築，自然野趣、耐候不褪。",
  "material":"麻石蘑菇石以整料鑿製或模具成型，中央隆起、四緣漸薄便於錯縫拼貼。石材抗壓、耐候、抗凍融，表面自然面/火燒；適合香港戶外立面與園景。",
  "apps":[("🏡","別墅與圍牆","質樸立面"),("🪨","景牆與旱景","立體肌理"),("🏞️","園林建築","自然野趣"),("🏛️","地標外飾","特色造型"),("🌳","住宅社群","低維護"),("⛲","水岸擋牆","防潮耐潮")]},
 "en":{"name":"Mushroom Stone","hk":"Rustic Cladding","en":"Mushroom Stone / Rustic Cladding",
  "intro":"Granite mushroom (rustic) cladding — raised centre, thin tapered edges — for villas, walls, feature walls and garden buildings; textured, weatherproof, non-fading.",
  "material":"Dressed or moulded granite, centre-bulged with thin tapered edges for staggered laying. Compression-proof, weatherproof, frost-proof, natural/flamed face — for HK outdoor cladding.",
  "apps":[("🏡","Villas/Walls","Rustic face"),("🪨","Feature Walls","3D texture"),("🏞️","Garden Bldg","Natural charm"),("🏛️","Landmark Trim","Feature form"),("🌳","Estates","Low upkeep"),("⛲","Quay Walls","Wet-proof")]},
 "common_specs":[("常見規格 Common Sizes","300×150 / 400×200 / 500×250 mm；厚 15–30 mm（中凸）"),("表面處理 Finish","自然面 Natural / 火燒面 Flamed / 機切 Machine-cut")],
 "items":[
  {"zh":"自然面蘑菇石","hk":"自然面蘑菇石","en":"Natural Mushroom","zh_note":"天然糙凸","en_note":"Raw bulge"},
  {"zh":"機切邊蘑菇石","hk":"機切邊蘑菇石","en":"Cut-edge Mushroom","zh_note":"邊緣規整","en_note":"Clean edge"},
  {"zh":"小塊蘑菇石","hk":"小塊蘑菇石","en":"Small Mushroom","zh_note":"細密拼貼","en_note":"Fine lay"},
  {"zh":"大塊蘑菇石","hk":"大塊蘑菇石","en":"Large Mushroom","zh_note":"大面陳列","en_note":"Large display"},
  {"zh":"圓角蘑菇石","hk":"圓角蘑菇石","en":"Rounded Mushroom","zh_note":"圓潤邊","en_note":"Rounded edge"},
  {"zh":"收邊蘑菇石","hk":"收邊蘑菇石","en":"Edge Mushroom","zh_note":"轉角收口","en_note":"Corner trim"},
  {"zh":"園林蘑菇石","hk":"園林蘑菇石","en":"Garden Mushroom","zh_note":"園景外飾","en_note":"Garden trim"},
  {"zh":"景牆蘑菇石","hk":"景牆蘑菇石","en":"Wall Mushroom","zh_note":"立面粉拼","en_note":"Wall clad"},
  {"zh":"異型蘑菇石","hk":"異型蘑菇石","en":"Special Mushroom","zh_note":"定制造型","en_note":"Custom shape"},
  {"zh":"組合蘑菇石","hk":"組合蘑菇石","en":"Composite Mushroom","zh_note":"混鋪圖案","en_note":"Mixed pattern"}]
},
]

# ---------------- 共享 CSS（占位圖框 + 表格 + 卡片） ----------------
SHARED_CSS = """
.ev-fields{width:100%;border-collapse:collapse;margin:10px 0 6px;background:#fff;border:1px solid rgba(201,168,76,.28);border-radius:12px;overflow:hidden;}
.ev-fields th,.ev-fields td{padding:13px 16px;text-align:left;vertical-align:top;border-bottom:1px solid rgba(201,168,76,.16);font-size:14.5px;}
.ev-fields tr:last-child td{border-bottom:none;}
.ev-fields th{width:30%;background:#fbf7ee;color:#1A1A2E;font-weight:600;white-space:nowrap;}
.ev-fields td b{color:#1A1A2E;}
.ev-fields td .ev-en{display:block;color:rgba(26,26,46,.6);font-size:12.5px;margin-top:2px;}
.ev-range{border:1px solid rgba(201,168,76,.28);border-radius:12px;overflow:hidden;margin:10px 0;}
.ev-range table{width:100%;border-collapse:collapse;}
.ev-range td{padding:11px 14px;border-bottom:1px solid rgba(201,168,76,.14);font-size:14px;vertical-align:top;}
.ev-range tr:last-child td{border-bottom:none;}
.ev-range td.ev-rn{width:42px;color:#C9A84C;font-weight:700;text-align:center;}
.ev-range td.ev-rz b{color:#1A1A2E;}
.ev-range td.ev-rz .ev-en{display:block;color:rgba(26,26,46,.6);font-size:12px;}
.ev-range td.ev-rnote{width:34%;color:rgba(26,26,46,.7);font-size:13px;}
"""

def esc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# ---------------- SEO-LD:auto 區塊（BreadcrumbList + Product / CollectionPage） ----------------
def build_seo_ld_auto(lang, is_landing, s):
    """生成全新的 SEO-LD:auto 區塊，替換模板中指向舊產品（qing-bluestone）的結構化資料。"""
    z = s[lang] if s else None
    home = "https://www.hsst.hk/"
    if lang == "zh":
        prod = "https://www.hsst.hk/products.html"
        cat_url = "https://www.hsst.hk/products/engineering-stone-varieties.html"
        cat_name = "工程石材品種系列"
        brand = "恆生石材科技有限公司"
        if is_landing:
            name = cat_name
            desc = "恆生石材工程石材品種系列：18 大類香港公共工程、路政、園林與住宅戶外花崗岩（麻石）製品型錄，耐候防滑、承重低維護。"
            url = cat_url
            crumbs = [("首頁", home), ("產品中心", prod), (cat_name, cat_url)]
        else:
            name = z["name"]
            desc = z["intro"]
            url = cat_url + "/" + s["slug"] + ".html"
            crumbs = [("首頁", home), ("產品中心", prod), (cat_name, cat_url), (z["name"], url)]
    else:
        prod = "https://www.hsst.hk/en/products.html"
        cat_url = "https://www.hsst.hk/en/products/engineering-stone-varieties.html"
        cat_name = "Engineering Stone Variety Series"
        brand = "HENGSHENG MARBLE S&T CO. LIMITED"
        if is_landing:
            name = cat_name
            desc = "HENGSHENG Engineering Stone Variety Series: 18 families of HK public-works, road, landscape and residential outdoor granite (麻石) products — weatherproof, slip-resistant, low-maintenance."
            url = cat_url
            crumbs = [("Home", home), ("Products", prod), (cat_name, cat_url)]
        else:
            name = z["name"]
            desc = z["intro"]
            url = cat_url + "/" + s["slug"] + ".html"
            crumbs = [("Home", home), ("Products", prod), (cat_name, cat_url), (z["name"], url)]
    bc = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": n + 1, "name": nm, "item": u}
            for n, (nm, u) in enumerate(crumbs)
        ],
    }
    blocks = ['<script type="application/ld+json">', json.dumps(bc, ensure_ascii=False, indent=1), "</script>"]
    if is_landing:
        cp = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": name, "url": url, "description": desc,
            "isPartOf": {"@type": "WebSite", "url": "https://www.hsst.hk", "name": brand},
        }
        blocks += ['<script type="application/ld+json">', json.dumps(cp, ensure_ascii=False, indent=1), "</script>"]
    else:
        prod_ld = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name, "url": url,
            "brand": {"@type": "Brand", "name": brand},
            "description": desc, "category": "Natural Stone",
            "image": "https://www.hsst.hk/images/products/engineering-stone-varieties/%s-hero.jpg" % s["slug"],
        }
        blocks += ['<script type="application/ld+json">', json.dumps(prod_ld, ensure_ascii=False, indent=1), "</script>"]
    return "<!-- SEO-LD:auto -->\n" + "\n".join(blocks) + "\n<!-- /SEO-LD:auto -->"

# ---------------- 詳情頁主體 ----------------
def build_detail_main(lang, s, prev_s, next_s):
    z = s[lang]
    L = "zh" if lang == "zh" else "en"
    crumbs = (("首頁","../../index.html"),("產品中心","../../products.html"),
              ("工程石材","../../products/engineering-stone-varieties.html"),(z["name"],None)) if lang=="zh" else \
             (("Home","../../../index.html"),("Products","../../../products.html"),
              ("Engineering Stone","../../../products/engineering-stone-varieties.html"),(z["name"],None))
    crumb = '<nav class="breadcrumb" aria-label="Breadcrumb"><ol>%s</ol></nav>' % "".join(
        ('<li><a href="%s">%s</a></li>' % (u,n)) if u else '<li><span aria-current="page">%s</span></li>' % n
        for n,u in crumbs)

    ip = "../../" if lang=="zh" else "../../../"
    pic = ('<picture><source srcset="%simages/products/engineering-stone-varieties/%s-hero.webp" type="image/webp"/>'
           '<img alt="%s" class="product-hero-bg" src="%simages/products/engineering-stone-varieties/%s-hero.jpg"/></picture>'
           ) % (ip, s["slug"], esc(z["name"]), ip, s["slug"])

    specs_rows = "".join(
        '<div class="spec-item"><div class="spec-item-left"><div class="spec-item-name">%s</div>%s</div>'
        '<div class="spec-item-right"><div class="spec-item-value">%s</div><div class="spec-item-meta">%s</div></div></div>'
        % (esc(zn), ('<span class="spec-item-name-en">%s</span>' % esc(en)) if lang=="zh" else '', esc(v), esc(std))
        for (zn, en, v, std) in GRANITE_SPECS)

    dims_rows = '<div class="specs-dimensions-wrap"><div class="specs-dimensions-grid">%s</div></div>' % "".join(
        '<div class="spec-dimension-card"><div class="spec-dimension-label">%s</div>'
        '<div class="spec-dimension-value">%s</div></div>' % (esc(lbl), esc(v).replace(" / ", "<br>"))
        for (lbl, v) in s["common_specs"])

    apps_cards = "".join(
        '<div class="application-card"><div class="application-card-icon">%s</div>'
        '<div class="app-card-title">%s</div><div class="app-card-desc">%s</div></div>' % (ic, esc(t), esc(d))
        for (ic, t, d) in z["apps"])

    items_rows = "".join(
        '<tr><td class="ev-rn">%d</td>'
        '<td class="ev-rz"><b>%s</b><span class="ev-en">%s · %s</span></td>'
        '<td class="ev-rnote">%s</td></tr>' % (i+1, esc(it["zh"]), esc(it["hk"]), esc(it["en"]), esc(it["zh_note"] if lang=="zh" else it["en_note"]))
        for i, it in enumerate(s["items"]))

    label_detail = "品種詳解 · 工程石材品種系列" if lang=="zh" else "Variety Detail · Engineering Stone Series"
    h2 = "%s · 樣本、技術參數與應用" % z["name"] if lang=="zh" else "%s — Samples, Technical Data & Applications" % z["name"]
    f1 = "產品名錄（四項對照）" if lang=="zh" else "Product Name Reference (4 fields)"
    f2 = "材料與工藝" if lang=="zh" else "Material & Craft"
    f3 = "技術參數" if lang=="zh" else "Technical Data"
    f4 = "應用場景" if lang=="zh" else "Applications"
    f5 = "可選表面處理工藝" if lang=="zh" else "Available Surface Finishes"
    f6 = "系列產品一覽（10 款）" if lang=="zh" else "Product Range (10 items)"
    spec_note = "* 以上數據為花崗岩（麻石）典型值範圍，具體批次可能略有差異。如需特定批次檢測報告，請聯繫我們。" if lang=="zh" else "* Values are typical granite (麻石) ranges; batches may vary slightly. Contact us for batch test reports."
    finishes = "火燒面 Flamed ／ 荔枝面 Bush-hammered ／ 光面 Polished ／ 亞光面 Honed ／ 噴砂面 Sandblasted ／ 剁斧面 Axe-cut" if lang=="zh" else "Flamed ／ Bush-hammered ／ Polished ／ Honed ／ Sandblasted ／ Axe-cut"

    pager = '<div class="var-pager-wrap">'
    if prev_s:
        pager += '<a class="var-pager prev" href="%s.html"><span>%s</span><b>%s</b></a>' % (prev_s["slug"], ("上一系列" if lang=="zh" else "Prev"), prev_s[lang]["name"])
    if next_s:
        pager += '<a class="var-pager next" href="%s.html"><span>%s</span><b>%s</b></a>' % (next_s["slug"], ("下一系列" if lang=="zh" else "Next"), next_s[lang]["name"])
    pager += '<a class="var-pager back" href="engineering-stone-varieties.html"><span>%s</span><b>%s</b></a></div>' % (("返回系列" if lang=="zh" else "Back"), ("工程石材品種系列" if lang=="zh" else "Engineering Stone Series"))

    hero = ('<section class="product-hero">%s'
            '<div class="product-hero-overlay"></div>'
            '<div class="product-hero-content">'
            '<span class="product-hero-badge">工程石材品種系列</span>'
            '<h1 class="product-hero-title">%s</h1>'
            '<p class="product-hero-subtitle">%s</p>'
            '<p class="product-hero-desc">%s</p>'
            '</div></section>') % (pic, esc(z["name"]), esc(z["en"]), esc(z["intro"][:90]+"…") if len(z["intro"])>90 else esc(z["intro"]))

    action = ('<section class="product-action-bar"><div class="container">'
              '<a href="%ssample-request.html" class="product-action-btn sample">📦 %s</a>'
              '<a href="%scontact.html" class="product-action-btn inquire">%s</a>'
              '</div></section>') % ("../../" if lang=="zh" else "../../../",
              "索取樣板" if lang=="zh" else "Request Samples",
              "../../" if lang=="zh" else "../../../",
              "立即諮詢" if lang=="zh" else "Inquire Now")

    detail = []
    detail.append('<section class="section-padding product-content-section border-top-light" id="variety-detail">')
    detail.append(' <div class="container">')
    detail.append('  <div class="product-section-title"><span class="label">%s</span><h2>%s</h2></div>' % (label_detail, h2))
    detail.append('  <div class="eng-var-body eng-var-page-body">')
    detail.append('   <p class="eng-var-desc">%s</p>' % esc(z["intro"]))
    detail.append(('   <div class="eng-variety-grid">'
                   '<figure class="granite-variety-card"><div class="granite-variety-img">'
                   '<picture><source srcset="%simages/products/engineering-stone-varieties/%s-hero.webp" type="image/webp"/>'
                   '<img alt="%s" loading="lazy" src="%simages/products/engineering-stone-varieties/%s-hero.jpg"/></picture></div>'
                   '<figcaption class="granite-variety-cap">%s</figcaption></figure></div>')
                  % (ip, s["slug"], esc(z["name"]), ip, s["slug"],
                     esc(z["name"] + (" · 產品場景一覽" if lang=="zh" else " · Product Scene"))))
    detail.append('   <h4 class="eng-var-subhead">%s <span>%s</span></h4>' % (f1, "4 Fields" if lang=="en" else "四項對照"))
    detail.append('   <table class="ev-fields"><tr><th>%s</th><td><b>%s</b><span class="ev-en">%s · %s</span></td></tr>' % ("產品內地名稱" if lang=="zh" else "Mainland CN Name", esc(z["name"]), esc(z["hk"]), esc(z["en"])))
    detail.append('   <tr><th>%s</th><td><b>%s</b><span class="ev-en">%s</span></td></tr>' % ("香港本地行業叫法" if lang=="zh" else "HK Local Trade Term", esc(z["hk"]), esc(z["en"])))
    detail.append('   <tr><th>%s</th><td><b>%s</b><span class="ev-en">%s</span></td></tr>' % ("外貿英文名稱" if lang=="zh" else "Export EN Name", esc(z["en"]), esc(z["name"])))
    detail.append('   <tr><th>%s</th><td>%s</td></tr></table>' % ("簡短商用產品簡介" if lang=="zh" else "Commercial Brief", esc(z["intro"])))
    detail.append('   <h4 class="eng-var-subhead">%s <span>%s</span></h4>' % (f2, "Material & Craft" if lang=="en" else "材料與工藝"))
    detail.append('   <p class="eng-var-desc">%s</p>' % esc(z["material"]))
    detail.append('   <h4 class="eng-var-subhead">%s <span>%s</span></h4>' % (f3, "Technical Data" if lang=="en" else "技術參數"))
    detail.append('   <div class="spec-grid">%s</div>' % specs_rows)
    detail.append('   <div class="spec-note">%s</div>' % spec_note)
    detail.append('   <h4 class="eng-var-subhead">%s <span>%s</span></h4>' % (f4, "Applications" if lang=="en" else "應用場景"))
    detail.append('   <div class="application-grid">%s</div>' % apps_cards)
    detail.append('   <div class="surface-treatment-section"><h5 class="surface-treatment-title">%s</h5>' % f5)
    detail.append('     <div class="surface-treatment-tags">%s</div></div>' % finishes)
    detail.append('   ' + dims_rows)
    detail.append('   <h4 class="eng-var-subhead">%s <span>%s</span></h4>' % (f6, "10 Items" if lang=="en" else "10 款"))
    detail.append('   <div class="ev-range"><table>%s</table></div>' % items_rows)
    detail.append('  </div>')
    detail.append('  ' + pager)
    detail.append(' </div>')
    detail.append('</section>')
    detail = "".join(detail)

    style = "<style>%s.breadcrumb{padding:14px 0 0;font-size:13px;}.breadcrumb ol{list-style:none;display:flex;align-items:center;gap:8px;margin:0;padding:0;flex-wrap:wrap;}</style>" % SHARED_CSS
    return style + crumb + hero + action + detail


def build_detail_page(lang, s, prev_s, next_s, tpl_path):
    h = open(tpl_path, encoding="utf-8").read()
    z = s[lang]
    L = "zh" if lang=="zh" else "en"
    base = "https://www.hsst.hk/products/engineering-stone-varieties"
    if lang=="zh":
        canon = "%s/%s.html" % (base, s["slug"]); alt_zh = canon; alt_en = "https://www.hsst.hk/en/products/engineering-stone-varieties/%s.html" % s["slug"]
        title = "%s · 工程石材品種系列 | 恆生石材科技有限公司" % z["name"]
        desc = z["intro"]
    else:
        canon = "https://www.hsst.hk/en/products/engineering-stone-varieties/%s.html" % s["slug"]
        alt_en = canon; alt_zh = "%s/%s.html" % (base, s["slug"])
        title = "%s — Engineering Stone Variety Series | HENGSHENG MARBLE S&T CO. LIMITED" % z["name"]
        desc = z["intro"]
    # head meta
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % esc(title), h, count=1, flags=re.S)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s\g<2>' % canon, h, count=1)
    h = re.sub(r'(<link rel="alternate" hreflang="zh-Hant" href=")[^"]*(")', r'\g<1>%s\g<2>' % alt_zh, h, count=1)
    h = re.sub(r'(<link rel="alternate" hreflang="en" href=")[^"]*(")', r'\g<1>%s\g<2>' % alt_en, h, count=1)
    h = re.sub(r'(<link rel="alternate" hreflang="x-default" href=")[^"]*(")', r'\g<1>%s\g<2>' % (alt_zh if lang=="zh" else alt_en), h, count=1)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(desc[:160]), h, count=1)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(title), h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(desc[:160]), h, count=1)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s\g<2>' % canon, h, count=1)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(title), h, count=1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(desc[:160]), h, count=1)
    # WebPage JSON-LD
    h = re.sub(r'<script type="application/ld\+json">\s*\{\s*"?@context"?:\s*"https://schema.org",\s*"?@type"?:\s*"WebPage".*?</script>',
               '<script type="application/ld+json">\n{\n "@context": "https://schema.org",\n "@type": "WebPage",\n "name": "%s",\n "url": "%s",\n "isPartOf": { "@type": "WebSite", "url": "https://www.hsst.hk", "name": "恆生石材科技有限公司" }\n}</script>' % (esc(title), canon),
               h, count=1, flags=re.S)
    # SEO-LD:auto 區塊（BreadcrumbList + Product）— 換成當前頁資料
    h = re.sub(r'<!-- SEO-LD:auto -->.*?<!-- /SEO-LD:auto -->',
               build_seo_ld_auto(lang, False, s), h, count=1, flags=re.S)
    # body region（保留 <section id="main-content"> 開標籤）
    i = h.find('<section id="main-content">')
    j = h.find('<section class="products-cta')
    assert i != -1 and j != -1, tpl_path
    main = build_detail_main(lang, s, prev_s, next_s)
    h = h[:i] + '<section id="main-content">\n' + main + "\n" + h[j:]
    return h


# ---------------- 落地頁主體 ----------------
def build_landing_main(lang):
    L = "zh"
    z = lang == "zh"
    crumbs = (("首頁","../index.html"),("產品中心","../products.html"),("工程石材品種系列",None)) if z else \
             (("Home","../../index.html"),("Products","../../products.html"),("Engineering Stone Series",None))
    crumb = '<nav class="breadcrumb" aria-label="Breadcrumb"><ol>%s</ol></nav>' % "".join(
        ('<li><a href="%s">%s</a></li>' % (u,n)) if u else '<li><span aria-current="page">%s</span></li>' % n for n,u in crumbs)

    hero_sub = "Engineering Stone Variety Series" if not z else "工程石材品種系列"
    intro_p = ("恆生石材「工程石材品種系列」聚焦香港公共工程、路政工程、園林工程與住宅戶外場景所需的花崗岩（麻石）製品，"
               "涵蓋車檔、欄杆、地鋪、路緣、樹池、壓頂、踏步、排水、幕牆與景牆等 18 大類。全系選用高密度麻石，"
               "耐候抗腐、防滑承重、易清潔低維護，契合香港高溫多雨、臨海鹽霧的戶外環境，為承建商、建築師與工程客戶提供一站式的製品型錄與定制加工。") if z else \
              ("HENGSHENG's Engineering Stone Variety Series covers granite (麻石) products for Hong Kong public works, road authority, landscape and residential outdoor use — "
               "18 families from bollards, balustrades, paving, kerbs, tree pits, coping, treads, drainage, curtain wall to feature cladding. All in dense granite: weatherproof, slip-resistant, load-bearing and low-maintenance, suited to Hong Kong's hot, rainy, coastal climate — a one-stop catalogue and fabrication source for contractors, architects and engineering clients.")
    ip = "../" if z else "../../"
    pic = ('<picture><source srcset="%simages/products/engineering-stone-varieties/landing-hero.webp" type="image/webp"/>'
           '<img alt="%s" class="product-hero-bg" src="%simages/products/engineering-stone-varieties/landing-hero.jpg"/></picture>'
           ) % (ip, "工程石材品種系列" if z else "Engineering Stone Variety Series", ip)

    hero = ('<section class="product-hero">%s<div class="product-hero-overlay"></div>'
            '<div class="product-hero-content"><span class="product-hero-badge">工程石材</span>'
            '<h1 class="product-hero-title">%s</h1><p class="product-hero-subtitle">%s</p>'
            '<p class="product-hero-desc">%s</p></div></section>') % (pic, "工程石材品種系列" if z else "Engineering Stone Variety Series", hero_sub, esc(intro_p[:120]+"…") if len(intro_p)>120 else esc(intro_p))

    action = ('<section class="product-action-bar"><div class="container">'
              '<a href="%ssample-request.html" class="product-action-btn sample">📦 %s</a>'
              '<a href="%scontact.html" class="product-action-btn inquire">%s</a></div></section>') % (
              "../" if z else "../../", "索取樣板" if z else "Request Samples", "../" if z else "../../", "立即諮詢" if z else "Inquire Now")

    cards = []
    for s in SERIES:
        v = s[lang]
        card = ('<a class="v2-series-card ev-card" href="engineering-stone-varieties/%s.html">'
                '<span class="vsc-img"><picture><source srcset="%simages/products/engineering-stone-varieties/%s-hero.webp" type="image/webp"/>'
                '<img alt="%s" loading="lazy" src="%simages/products/engineering-stone-varieties/%s-hero.jpg"/></picture></span>'
                '<span class="vsc-cap"><i>%s</i><b>%s</b>'
                '<span class="vsc-d">%s</span>'
                '<em class="vsc-go">%s</em></span></a>') % (
                s["slug"], ip, s["slug"], esc(v["name"]), ip, s["slug"],
                esc(v["en"]), esc(v["name"]), esc(v["intro"][:46]+"…") if len(v["intro"])>46 else esc(v["intro"]),
                "查看詳情 →" if z else "View details →")
        cards.append(card)
    grid = '<div class="v2-series-grid ev-grid">%s</div>' % "".join(cards)

    adv_title = "為何選用工程麻石製品" if z else "Why Granite (麻石) Engineering Products"
    adv_lead = "天然花崗岩（麻石）是香港戶外公共與景觀工程的首選材料：" if z else "Natural granite is the preferred stone for Hong Kong outdoor public & landscape works:"
    advs = [
        ("🛡️","耐候抗腐蝕","抗紫外線、抗鹽霧，不鏽不腐，長期戶外穩定","Weatherproof","UV & salt-spray resistant, non-rusting"),
        ("🚶","防滑安全","火燒/荔枝面糙面，雨後不滑，守護行人","Slip-safe","Flamed/bush-hammered grip when wet"),
        ("🏗️","承重抗壓","高密度麻石抗壓耐磨，達車行級荷載","Load-bearing","Compression-proof, drive-load rated"),
        ("🧽","易清潔低維護","不吸水不藏污，高壓沖洗即淨","Low upkeep","Non-absorbing, easy wash"),
        ("☀️","耐紫外線不褪色","天然色穩，歷久彌新","Non-fading","Stable natural colour"),
        ("🌧️","契合香港氣候","耐高溫多雨、臨海鹽霧戶外環境","HK climate","Hot, rainy, coastal ready"),
    ]
    adv_cards = "".join('<div class="application-card"><div class="application-card-icon">%s</div><div class="app-card-title">%s</div><div class="app-card-desc">%s</div></div>' % (ic, esc(t if z else te), esc(d if z else de)) for (ic,t,te,d,de) in advs)

    intro_sec = ('<section class="section-padding product-content-section border-top-light" id="series-intro">'
                 '<div class="container"><div class="product-section-title"><span class="label">%s</span><h2>%s</h2></div>'
                 '<p class="eng-var-desc">%s</p>%s'
                 '<div class="surface-treatment-section" style="margin-top:18px"><h5 class="surface-treatment-title">%s</h5>'
                 '<div class="surface-treatment-tags"><span class="surface-treatment-tag">火燒面 Flamed</span><span class="surface-treatment-tag">荔枝面 Bush-hammered</span><span class="surface-treatment-tag">光面 Polished</span><span class="surface-treatment-tag">亞光面 Honed</span><span class="surface-treatment-tag">噴砂面 Sandblasted</span><span class="surface-treatment-tag">剁斧面 Axe-cut</span></div></div>'
                 '</div></section>') % (
        "工程石材品種系列" if z else "Engineering Stone Variety Series",
        "18 大類戶外麻石製品型錄" if z else "18 Families of Outdoor Granite Products",
        esc(intro_p), grid,
        "通用表面處理工藝" if z else "Common Surface Finishes")

    adv_sec = ('<section class="section-padding product-content-section border-top-light" id="why-granite">'
               '<div class="container"><div class="product-section-title"><span class="label">%s</span><h2>%s</h2></div>'
               '<p class="eng-var-desc">%s</p><div class="application-grid">%s</div></div></section>') % (
        "工程石材" if z else "Engineering Stone", adv_title, esc(adv_lead), adv_cards)

    style = ("<style>%s.breadcrumb{padding:14px 0 0;font-size:13px;}.breadcrumb ol{list-style:none;display:flex;align-items:center;gap:8px;margin:0;padding:0;flex-wrap:wrap;}"
             ".ev-card .vsc-img{display:block;}.ev-grid{grid-template-columns:repeat(3,1fr);}@media(max-width:900px){.ev-grid{grid-template-columns:repeat(2,1fr);}}@media(max-width:560px){.ev-grid{grid-template-columns:1fr;}}"
             "body.premium .v2-series-card .vsc-go{opacity:1;transform:none;display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border:1px solid #C9A84C;border-radius:999px;background:#fff;color:#1A1A2E;}</style>") % SHARED_CSS
    return style + crumb + hero + action + intro_sec + adv_sec


def build_landing_page(lang, tpl_path):
    h = open(tpl_path, encoding="utf-8").read()
    z = lang == "zh"
    base = "https://www.hsst.hk/products/engineering-stone-varieties"
    if z:
        canon = base + ".html"; alt_en = "https://www.hsst.hk/en/products/engineering-stone-varieties.html"; alt_zh = canon
        title = "工程石材品種系列 | 恆生石材科技有限公司"
        desc = "恆生石材工程石材品種系列：18 大類香港公共工程、路政、園林與住宅戶外花崗岩（麻石）製品型錄，耐候防滑、承重低維護。"
    else:
        canon = "https://www.hsst.hk/en/products/engineering-stone-varieties.html"; alt_zh = base + ".html"; alt_en = canon
        title = "Engineering Stone Variety Series | HENGSHENG MARBLE S&T CO. LIMITED"
        desc = "HENGSHENG Engineering Stone Variety Series: 18 families of HK public-works, road, landscape and residential outdoor granite (麻石) products — weatherproof, slip-resistant, low-maintenance."
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % esc(title), h, count=1, flags=re.S)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s\g<2>' % canon, h, count=1)
    h = re.sub(r'(<link rel="alternate" hreflang="zh-Hant" href=")[^"]*(")', r'\g<1>%s\g<2>' % alt_zh, h, count=1)
    h = re.sub(r'(<link rel="alternate" hreflang="en" href=")[^"]*(")', r'\g<1>%s\g<2>' % alt_en, h, count=1)
    h = re.sub(r'(<link rel="alternate" hreflang="x-default" href=")[^"]*(")', r'\g<1>%s\g<2>' % (alt_zh if z else alt_en), h, count=1)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(desc), h, count=1)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(title), h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(desc), h, count=1)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s\g<2>' % canon, h, count=1)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(title), h, count=1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', r'\g<1>%s\g<2>' % esc(desc), h, count=1)
    h = re.sub(r'<script type="application/ld\+json">\s*\{\s*"?@context"?:\s*"https://schema.org",\s*"?@type"?:\s*"WebPage".*?</script>',
               '<script type="application/ld+json">\n{\n "@context": "https://schema.org",\n "@type": "WebPage",\n "name": "%s",\n "url": "%s",\n "isPartOf": { "@type": "WebSite", "url": "https://www.hsst.hk", "name": "恆生石材科技有限公司" }\n}</script>' % (esc(title), canon),
               h, count=1, flags=re.S)
    # SEO-LD:auto 區塊（BreadcrumbList + CollectionPage）— 換成當前頁資料
    h = re.sub(r'<!-- SEO-LD:auto -->.*?<!-- /SEO-LD:auto -->',
               build_seo_ld_auto(lang, True, None), h, count=1, flags=re.S)
    # body region（保留 <section id="main-content"> 開標籤）
    i = h.find('<section id="main-content">')
    j = h.find('<section class="products-cta')
    assert i != -1 and j != -1, tpl_path
    main = build_landing_main(lang)
    h = h[:i] + '<section id="main-content">\n' + main + "\n" + h[j:]
    return h


# ---------------- 可複製內容稿 ----------------
def build_content_doc(lang):
    z = lang == "zh"
    if z:
        html_lang = "zh-Hant"
        title = "工程石材品種系列（18 大類 · 可複製內容稿）"
        sub = "恆生石材科技有限公司｜花崗岩（麻石）戶外製品型錄｜公共工程 / 路政工程 / 園林工程 / 住宅戶外"
    else:
        html_lang = "en"
        title = "Engineering Stone Variety Series (18 families · copy-ready)"
        sub = "HENGSHENG MARBLE S&T CO. LIMITED | Granite outdoor product catalogue | Public / Road / Landscape / Residential"
    css = ('body{font-family:-apple-system,"PingFang TC","Noto Sans TC",sans-serif;max-width:1100px;margin:0 auto;padding:28px;color:#1A1A2E;line-height:1.7;}'
           'h1{font-size:26px;border-bottom:3px solid #C9A84C;padding-bottom:10px;}h2{font-size:20px;margin-top:34px;color:#1A1A2E;}'
           '.blk{border:1px solid #e6e0d2;border-radius:12px;padding:18px 20px;margin:14px 0;background:#fffdf8;}'
           'table{width:100%;border-collapse:collapse;margin:8px 0;font-size:14px;}th,td{border:1px solid #e6e0d2;padding:8px 10px;vertical-align:top;text-align:left;}'
           'th{background:#fbf7ee;width:22%;}caption{font-weight:700;text-align:left;padding:6px 0;color:#8a7d5e;}'
           '.en{color:#777;font-size:12.5px;}.note{color:#666;font-size:12.5px;}')
    out = []
    out.append('<!DOCTYPE html><html lang="%s"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>%s</title><style>%s</style></head><body>' % (html_lang, title, css))
    out.append('<h1>%s</h1><p class="note">%s</p>' % (title, sub))
    for s in SERIES:
        v = s[lang]
        out.append('<h2>%s. %s <span class="en">/ %s</span></h2>' % (s["idx"], esc(v["name"]), esc(v["en"])))
        out.append('<div class="blk">')
        out.append('<table><caption>%s</caption>' % ("四項對照（4 fields）" if z else "Four-field reference"))
        out.append('<tr><th>%s</th><td>%s</td></tr>' % ("產品內地名稱" if z else "Mainland CN name", esc(v["name"])))
        out.append('<tr><th>%s</th><td>%s</td></tr>' % ("香港本地行業叫法" if z else "HK local trade term", esc(v["hk"])))
        out.append('<tr><th>%s</th><td>%s</td></tr>' % ("外貿英文名稱" if z else "Export EN name", esc(v["en"])))
        out.append('<tr><th>%s</th><td>%s</td></tr>' % ("簡短商用產品簡介" if z else "Commercial brief", esc(v["intro"])))
        out.append('</table>')
        out.append('<p><b>%s</b> %s</p>' % ("材料與工藝：" if z else "Material & craft: ", esc(v["material"])))
        out.append('<p><b>%s</b></p><div class="ev-range"><table>' % ("系列產品一覽（10 款）：" if z else "Product range (10 items):"))
        for i, it in enumerate(s["items"]):
            out.append('<tr><td class="ev-rn">%d</td><td><b>%s</b> <span class="en">%s · %s</span></td><td class="note">%s</td></tr>' % (
                i+1, esc(it["zh"]), esc(it["hk"]), esc(it["en"]), esc(it["zh_note"] if z else it["en_note"])))
        out.append('</table></div>')
        out.append('</div>')
    out.append('</body></html>')
    return "".join(out)


def main():
    import shutil
    os.makedirs(OUT_ROOT, exist_ok=True)
    # 落地頁
    zh_land = build_landing_page("zh", ZH_LAND_TPL)
    en_land = build_landing_page("en", EN_LAND_TPL)
    # 詳情頁
    n = len(SERIES)
    created = 0
    for k, s in enumerate(SERIES):
        prev_s = SERIES[k-1] if k > 0 else None
        next_s = SERIES[k+1] if k < n-1 else None
        zh_d = build_detail_page("zh", s, prev_s, next_s, ZH_DETAIL_TPL)
        en_d = build_detail_page("en", s, prev_s, next_s, EN_DETAIL_TPL)
        if APPLY:
            d1 = os.path.join(SITE, "products/engineering-stone-varieties"); d2 = os.path.join(SITE, "en/products/engineering-stone-varieties")
            os.makedirs(d1, exist_ok=True); os.makedirs(d2, exist_ok=True)
            open(os.path.join(d1, s["slug"]+".html"), "w", encoding="utf-8").write(zh_d)
            open(os.path.join(d2, s["slug"]+".html"), "w", encoding="utf-8").write(en_d)
            open(os.path.join(SITE, "products/engineering-stone-varieties.html"), "w", encoding="utf-8").write(zh_land)
            open(os.path.join(SITE, "en/products/engineering-stone-varieties.html"), "w", encoding="utf-8").write(en_land)
        created += 2
    # 可複製稿
    doc_zh = build_content_doc("zh"); doc_en = build_content_doc("en")
    if APPLY:
        outdir = "/Users/stone/WorkBuddy/2026-09-05-23-03-06"
        open(os.path.join(outdir, "engineering-stone-varieties-content-zh.html"), "w", encoding="utf-8").write(doc_zh)
        open(os.path.join(outdir, "engineering-stone-varieties-content-en.html"), "w", encoding="utf-8").write(doc_en)
    print(("✅ " if APPLY else "🔍(dry-run) ") + "落地頁 2 + 詳情頁 %d + 可複製稿 2" % created)
    if not APPLY:
        # 寫入 /tmp 供校驗
        open("/tmp/ev_preview/landing-zh.html","w",encoding="utf-8").write(zh_land)
        open("/tmp/ev_preview/landing-en.html","w",encoding="utf-8").write(en_land)
        open("/tmp/ev_preview/doc-zh.html","w",encoding="utf-8").write(doc_zh)
        for k,s in enumerate(SERIES):
            open("/tmp/ev_preview/%s-zh.html"%(s["slug"]),"w",encoding="utf-8").write(build_detail_page("zh",s,SERIES[k-1] if k>0 else None,SERIES[k+1] if k<n-1 else None,ZH_DETAIL_TPL))


if __name__ == "__main__":
    main()
