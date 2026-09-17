#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品種獨立頁 JSON-LD 後處理：把繼承自系列頁的 WebPage / BreadcrumbList / Product
三塊結構化數據改寫為品種頁自身（name/url 對齊 canonical，面包屑補第 4 級）。
冪等：重複執行結果一致。
"""
import os, re, glob, json, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLY = "--apply" in sys.argv

pages = sorted(glob.glob(os.path.join(SITE, "products/*/[a-z]*.html")) +
               glob.glob(os.path.join(SITE, "en/products/*/[a-z]*.html")))
pages = [p for p in pages if os.path.basename(os.path.dirname(p)) not in ("css", "js")]
pages = [p for p in pages if "/products/" in p.replace(os.sep, "/")]
changed = 0

for p in pages:
    h = open(p, encoding="utf-8").read()
    canon = re.search(r'rel="canonical" href="([^"]*)"', h).group(1)
    title = re.search(r'<title>(.*?)</title>', h, re.S).group(1)
    # 品種名 = 面包屑最後一級（aria-current）
    bc = re.findall(r'<nav class="breadcrumb"[^>]*>.*?</nav>', h, re.S)
    vname = None
    if bc:
        cur = re.findall(r'<li><span aria-current="page">([^<]*)</span></li>', bc[0])
        vname = cur[-1] if cur else None
    if not vname:
        continue

    # 從品種頁自己的麵包屑 nav 提取四級路徑
    crumbs = re.findall(r'<li><a href="[^"]*">([^<]*)</a></li>|\s*<li><span aria-current="page">([^<]*)</span></li>', bc[0]) if bc else []
    names = [a or b for a, b in crumbs]

    def sub_jsonld(m):
        block = m.group(1)
        try:
            data = json.loads(block)
        except Exception:
            return m.group(0)
        t = data.get("@type") if isinstance(data, dict) else None
        if t == "WebPage":
            data["name"] = title
            data["url"] = canon
        elif t == "BreadcrumbList":
            items = data.get("itemListElement", [])
            if items and items[-1].get("position") == len(items) and vname not in [i.get("name") for i in items]:
                items.append({"@type": "ListItem", "position": len(items) + 1,
                              "name": vname, "item": canon})
                data["itemListElement"] = items
        elif t == "Product":
            data["name"] = vname
            data["url"] = canon
        else:
            return m.group(0)
        return '<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False, indent=1)

    nh = re.sub(r'<script type="application/ld\+json">(.*?)</script>', sub_jsonld, h, flags=re.S)
    if nh != h:
        changed += 1
        if APPLY:
            open(p, "w", encoding="utf-8").write(nh)

print(("✅ " if APPLY else "🔍(dry-run) ") + f"JSON-LD 修正 {changed} 頁")
