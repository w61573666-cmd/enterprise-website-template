#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恒生石材（hsst.hk）「產品中心」三處清單全站同步器
================================================
數據源：data/products-manifest.json

同步三處（全部按 manifest 的 series 順序重排）：
  ① 導航「產品中心」下拉  …  <div class="mega-panel"> > .mega-panel-grid
     （12 個系列 + navExtra 企業頁，共 14 條）
  ② 頁腳「產品業務矩陣」 …  <ul class="ft-matrix-grid">（僅 12 個系列）
  ③ 「全部系列」卡片牆    …  <div class="v2-series-grid">（僅 12 個系列，
     存在於 products.html / en/products.html）

相對路徑規則（實測全站慣例）：
  depth = 檔案相對於站點根目錄的目錄層數
  langRoot = 0（zh，站點根＝語言根）／1（en，語言根是 en/ 這一層）
  連結前綴 href_prefix  = '../' * max(0, depth - langRoot)
      → en/ 內頁的內部連結以「語言根」為基準，所以 en/products.html 用 products/x.html
  資源前綴 asset_prefix = '../' * depth
      → 圖片/樣式一律以真實檔案位置為基準，所以 en/products.html 用 ../images/…

用法：
  python3 scripts/sync-products.py            # 寫入
  python3 scripts/sync-products.py --check    # 只檢查不寫入
"""
import os, re, sys, json, html as htmllib

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(SITE, "data", "products-manifest.json")
CHECK = "--check" in sys.argv

# ---------- 定位用的正則（只在內容層替換，絕不動結構標籤） ----------
RE_PANEL = re.compile(
    r'(<div class="mega-panel">\s*<div class="mega-panel-grid">)(.*?)(</div>\s*</div>\s*</div>)', re.S)
RE_MATRIX = re.compile(r'(<ul class="ft-matrix-grid">)(.*?)(</ul>)', re.S)
RE_WALL = re.compile(r'(<div class="v2-series-grid">)(.*?)(</div>)', re.S)

# 結構計數守衛：這些 token 的數量在同步前後必須完全一致
GUARDS = ['class="nav-dropdown"', 'class="mega-panel"', 'class="mega-panel-grid"',
          'class="mega-panel-link"', 'class="ft-matrix"', 'class="ft-matrix-grid"',
          'class="footer', 'class="nav-links"', '</html>', '<script']


def esc(t):
    """輸出 HTML 轉義（manifest 裡存原文，& 一律轉 &amp;，渲染結果不變）"""
    return htmllib.escape(str(t), quote=False)


def href_prefix(depth, lang):
    """內部連結前綴：以「語言根」為基準（en 頁面的語言根是 en/，故少一層）"""
    return "../" * max(0, depth - (1 if lang == "en" else 0))


def asset_prefix(depth):
    """圖片/樣式前綴：以真實檔案位置為基準"""
    return "../" * depth


def lang_of(rel):
    return "en" if rel.split(os.sep)[0] == "en" else "zh"


def verify_links(block, rel, problems, what):
    """把區塊裡的相對連結/資源逐條落到檔案系統上驗證存在——防止前綴算錯"""
    base = os.path.dirname(rel)
    urls = re.findall(r'(?:href|src|srcset)="([^"]+)"', block)
    for u in urls:
        if u.startswith(("http://", "https://", "//", "#", "mailto:", "tel:", "data:")):
            continue
        target = os.path.normpath(os.path.join(base, u.split("?")[0]))
        if not os.path.exists(os.path.join(SITE, target)):
            problems.append(f"{rel}: {what} 連結指向不存在的檔案 → {u}")


# ---------- 三個區塊的生成 ----------

def build_nav_grid(items, lang, hp):
    blocks = []
    for it in items:
        blocks.append(
            '        <a class="mega-panel-link" href="%s%s">\n'
            '         <div class="mega-panel-text">\n'
            '          <strong>\n'
            '           %s\n'
            '          </strong>\n'
            '          <span>\n'
            '           %s\n'
            '          </span>\n'
            '         </div>\n'
            '        </a>' % (hp, it["href"], esc(it["nav"][lang]), esc(it["navSub"][lang]))
        )
    return "\n" + "\n".join(blocks) + "\n       "


def build_matrix(items, lang, hp):
    lis = ['        <li><a href="%s%s">%s</a></li>' % (hp, it["href"], esc(it["footer"][lang]))
           for it in items]
    return "\n" + "\n".join(lis) + "\n     "


def build_wall(items, lang, ap, defaults):
    cards = []
    for it in items:
        c = it["card"][lang]
        slug = it["slug"]
        go = c.get("go") or defaults["cardGo"][lang]
        cards.append(
            '<a class="v2-series-card" href="products/%s.html">'
            '<span class="vsc-img"><picture>'
            '<source srcset="%simages/series-cards/%s-card.webp" type="image/webp"/>'
            '<img alt="%s" loading="lazy" src="%simages/series-cards/%s-card.jpg"/>'
            '</picture></span>'
            '<span class="vsc-cap"><i>%s</i><b>%s</b>'
            '<span class="vsc-d">%s</span>'
            '<em class="vsc-go">%s</em></span></a>'
            % (slug, ap, slug, esc(c["alt"]), ap, slug,
               esc(c["i"]), esc(c["b"]), esc(c["d"]), esc(go))
        )
    return "\n" + "\n".join(cards) + "\n"


# ---------- ④ products 頁的「系列數」文案與結構化資料 ----------
# 這兩頁本來寫死「10 大系列 / 十一個主流系列 / TEN SIGNATURE COLLECTIONS」，
# 系列數一變就說謊。這裡改成由 manifest 的 series 長度即時推導。
CN_DIGIT = "零一二三四五六七八九"
EN_ONES = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
           "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
           "Seventeen", "Eighteen", "Nineteen"]
EN_TENS = {2: "Twenty", 3: "Thirty", 4: "Forty", 5: "Fifty", 6: "Sixty", 7: "Seventy",
           8: "Eighty", 9: "Ninety"}


def cn_num(n):
    if n < 10:
        return CN_DIGIT[n]
    if n < 20:
        return "十" + (CN_DIGIT[n - 10] if n > 10 else "")
    t, o = divmod(n, 10)
    return CN_DIGIT[t] + "十" + (CN_DIGIT[o] if o else "")


def en_num(n):
    if n < 20:
        return EN_ONES[n]
    t, o = divmod(n, 10)
    return EN_TENS[t] + ("-" + EN_ONES[o] if o else "")


# (正則, 替換模板)
# REQUIRED：products 兩頁的版面文案，每條必須恰好命中 1 次，否則報錯（禁止靜默漏改）
# OPTIONAL：全站掃描，命中 0 次也正常（例如 projects/catalog.html 的「十大系列應用版圖」）
COUNT_RULES_REQUIRED = {
    "zh": [
        (r"\d+\s*大主流石材系列", "{n} 大主流石材系列"),
        (r"<b>\d+\+?</b><span>主流石材系列</span>", "<b>{n}+</b><span>主流石材系列</span>"),
        (r"\b[A-Z]+ SIGNATURE COLLECTIONS", "{ENUP} SIGNATURE COLLECTIONS"),
    ],
    "en": [
        (r"\b[A-Z][a-z]+ signature series", "{en} signature series"),
        (r"<b>\d+</b><span>Stone Series</span>", "<b>{n}</b><span>Stone Series</span>"),
        (r"\b[A-Z]+ SIGNATURE COLLECTIONS", "{ENUP} SIGNATURE COLLECTIONS"),
        (r"\b[A-Za-z]+ collections, over", "{enl} collections, over"),
    ],
}

COUNT_RULES_OPTIONAL = {
    "zh": [
        (r"[一二三四五六七八九十]+大系列", "{cn}大系列"),
        (r"[一二三四五六七八九十]+個主流系列", "{cn}個主流系列"),
    ],
    "en": [
        (r"\bTen series\b", "{en} series"),
        (r"\bten series\b", "{enl} series"),
        (r"\bEleven series\b", "{en} series"),
        (r"\beleven series\b", "{enl} series"),
    ],
}

# 結構化資料裡的系列清單也要跟著變
JSONLD_RULES = {
    "zh": (r'"name": "恆生石材產品中心[^"]*"',
           '"name": "恆生石材產品中心，{cn}大系列天然石材：{series_zh}"'),
    "en": (r'"name": "HENGSHENG MARBLE S&amp;T CO\. LIMITED product center[^"]*"',
           '"name": "HENGSHENG MARBLE S&amp;T CO. LIMITED product center — {n} series of natural stone"'),
}


def apply_rules(html, rules, tok, problems, rel, label, exact=True):
    for pat, tpl in rules:
        want = tpl.format(**tok).replace("\\", "\\\\")
        new, cnt = re.subn(pat, want, html)
        if exact and cnt != 1:
            problems.append(f"{rel}: {label} /{pat}/ 命中 {cnt} 次（應為 1）")
        else:
            html = new
    return html


def count_tokens(n, series):
    return {"n": n, "cn": cn_num(n), "en": en_num(n), "enl": en_num(n).lower(),
            "ENUP": en_num(n).upper(), "series_zh": "、".join(s["short"] for s in series)}


def sync_page_copy(html, lang, n, series, problems, rel):
    tok = count_tokens(n, series)
    html = apply_rules(html, COUNT_RULES_REQUIRED[lang], tok, problems, rel, "系列數文案", exact=True)
    pat, tpl = JSONLD_RULES[lang]
    want = tpl.format(**tok)
    new, cnt = re.subn(pat, want.replace("\\", "\\\\"), html)
    if cnt != 1:
        problems.append(f"{rel}: JSON-LD 系列清單命中 {cnt} 次（應為 1）")
    else:
        html = new
    return html


def main():
    mf = json.load(open(MANIFEST, encoding="utf-8"))
    series, extra, defaults = mf["series"], mf.get("navExtra", []), mf["defaults"]
    nav_items = series + extra
    print(f"manifest: {len(series)} 系列 + {len(extra)} navExtra = 下拉 {len(nav_items)} 條")

    # 資料自檢
    slugs = [s["slug"] for s in series]
    assert len(set(slugs)) == len(slugs), "series slug 有重複"
    for s in series:
        for k in ("slug", "href", "nav", "navSub", "footer", "card"):
            assert k in s, (s.get("slug"), "缺欄位", k)
        assert os.path.exists(os.path.join(SITE, s["href"])), f"系列頁不存在: {s['href']}"
        for ext in ("jpg", "webp"):
            p = os.path.join(SITE, "images", "series-cards", f"{s['slug']}-card.{ext}")
            assert os.path.exists(p), f"封面圖不存在: {p}"
    for e in extra:
        assert os.path.exists(os.path.join(SITE, e["href"])), f"navExtra 頁不存在: {e['href']}"

    htmls = []
    for root, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in (".git", ".workbuddy", "node_modules")]
        for f in files:
            if f.endswith(".html"):
                htmls.append(os.path.relpath(os.path.join(root, f), SITE))
    htmls.sort()

    stats = dict(pages=0, nav=0, matrix=0, wall=0, skipped=[])
    problems = []

    for rel in htmls:
        path = os.path.join(SITE, rel)
        orig = open(path, encoding="utf-8").read()
        depth = rel.count(os.sep)
        lang = lang_of(rel)
        hp, ap = href_prefix(depth, lang), asset_prefix(depth)

        # 三處都不存在 → 校驗頁/404 之類的 stub，跳過
        if 'class="mega-panel-grid"' not in orig and 'class="ft-matrix-grid"' not in orig:
            stats["skipped"].append(rel)
            continue

        html = orig
        before = {g: html.count(g) for g in GUARDS}

        # ① 導航下拉
        hits = list(RE_PANEL.finditer(html))
        prod = [m for m in hits if "products/white-marble.html" in m.group(2)]
        if len(prod) != 1:
            problems.append(f"{rel}: 產品中心 mega-panel 命中 {len(prod)} 個（應為 1）")
        else:
            m = prod[0]
            blk = build_nav_grid(nav_items, lang, hp)
            verify_links(blk, rel, problems, "導航下拉")
            html = html[:m.start()] + m.group(1) + blk + m.group(3) + html[m.end():]
            stats["nav"] += 1

        # ② 頁腳業務矩陣
        hits = list(RE_MATRIX.finditer(html))
        if len(hits) != 1:
            problems.append(f"{rel}: ft-matrix-grid 命中 {len(hits)} 個（應為 1）")
        else:
            m = hits[0]
            blk = build_matrix(series, lang, hp)
            verify_links(blk, rel, problems, "頁腳矩陣")
            html = html[:m.start()] + m.group(1) + blk + m.group(3) + html[m.end():]
            stats["matrix"] += 1

        # ③ 全部系列卡片牆（只有 products 頁有）
        hits = list(RE_WALL.finditer(html))
        if len(hits) == 1:
            m = hits[0]
            blk = build_wall(series, lang, ap, defaults)
            verify_links(blk, rel, problems, "卡片牆")
            html = html[:m.start()] + m.group(1) + blk + m.group(3) + html[m.end():]
            stats["wall"] += 1
            # ④ 這一頁的「系列數」文案 + JSON-LD 系列清單
            html = sync_page_copy(html, lang, len(series), series, problems, rel)
        elif len(hits) > 1:
            problems.append(f"{rel}: v2-series-grid 命中 {len(hits)} 個")

        # 守衛：結構 token 數量不得變化
        after = {g: html.count(g) for g in GUARDS}
        for g in GUARDS:
            if before[g] != after[g]:
                problems.append(f"{rel}: 結構守衛 '{g}' 由 {before[g]} → {after[g]}")

        # 全站可選規則：系列數文案（products 頁之外也可能出現，如工程目錄頁）
        html = apply_rules(html, COUNT_RULES_OPTIONAL[lang], count_tokens(len(series), series),
                           problems, rel, "全站系列數", exact=False)

        # 結果校驗
        if html.count('class="mega-panel-link"') and "products/white-marble.html" in html:
            pass
        pm = [m for m in RE_PANEL.finditer(html) if "products/white-marble.html" in m.group(2)]
        if len(pm) == 1:
            got = re.findall(r'<a class="mega-panel-link" href="[^"]*?((?:products/)?[a-z-]+\.html)"', pm[0].group(2))
            if len(got) != len(nav_items):
                problems.append(f"{rel}: 下拉條數 {len(got)} ≠ {len(nav_items)}")
        mm = RE_MATRIX.finditer(html)
        for m in mm:
            n = m.group(2).count("<li>")
            if n != len(series):
                problems.append(f"{rel}: 頁腳矩陣 {n} 條 ≠ {len(series)}")

        if html != orig:
            if not CHECK:
                open(path, "w", encoding="utf-8").write(html)
            stats["pages"] += 1

    print(f"\n變更頁面 {stats['pages']} / 共 {len(htmls)} 個 HTML")
    print(f"  · 導航下拉同步 {stats['nav']} 頁")
    print(f"  · 頁腳矩陣同步 {stats['matrix']} 頁")
    print(f"  · 卡片牆同步   {stats['wall']} 頁")
    print(f"  · 跳過(無導航/頁腳) {len(stats['skipped'])}: {stats['skipped']}")
    if problems:
        print(f"\n❌ 發現 {len(problems)} 個問題：")
        for p in problems[:40]:
            print("   -", p)
        sys.exit(1)
    print("\n✅ 三處清單完全一致，結構守衛全數通過" + ("（--check 未寫入）" if CHECK else ""))


if __name__ == "__main__":
    main()
