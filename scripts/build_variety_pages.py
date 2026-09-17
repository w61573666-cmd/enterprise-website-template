#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
產品中心「品種獨立頁」生成器
============================
把 12 個系列頁（×2 語言）裡的手風琴品種（eng-var）拆成獨立頁面：

  生成  products/<series>/<variety>.html        （74 頁）
        en/products/<series>/<variety>.html     （74 頁）
  改造  系列頁：品種卡只留縮圖+名稱，「查看詳情」變為連結；
        移除內聯 body 與手風琴 JS；更新欄目引導文案。

⚠️ 一次性遷移腳本：系列頁的 eng-var-body 被搬走後，本腳本不可重跑
   （會提取不到內容而拒絕執行）。品種內容以系列頁為唯一來源。
"""
import os, re, sys, glob, json

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLY = "--apply" in sys.argv
NOW = "2026-09-17T12:00:00+08:00"

MF = json.load(open(os.path.join(SITE, "data/products-manifest.json"), encoding="utf-8"))
SERIES = {s["slug"]: s for s in MF["series"]}


# ---------------- 相對路徑整體 +1 層 ----------------
def _pref_url(u, by):
    if by <= 0:
        return u
    return "../" * by + u


def shift(html, by=1):
    """把塊內所有相對 href/src/srcset 加 by 層 ../；絕對路徑/錨點/外鏈不動"""
    def fix_srcset(v):
        parts = []
        for cand in v.split(","):
            cand = cand.strip()
            if not cand:
                continue
            tok = cand.split()[0]
            if tok.startswith(("http:", "https:", "/", "#", "mailto:", "tel:", "data:")):
                parts.append(cand)
            else:
                parts.append(_pref_url(tok, by) + (" " + " ".join(cand.split()[1:]) if len(cand.split()) > 1 else ""))
        return ", ".join(parts)

    def repl(m):
        attr, val = m.group(1), m.group(2)
        if val.startswith(("http:", "https:", "/", "#", "mailto:", "tel:", "data:")):
            return m.group(0)
        if attr == "srcset":
            return '%s="%s"' % (attr, fix_srcset(val))
        return '%s="%s"' % (attr, _pref_url(val, by))

    return re.sub(r'\b(href|src|srcset)="([^"]+)"', repl, html)


def div_block(html, start):
    """從 start（指向一個 <div ...>）起做 div 配平，返回 (含起訖的塊, 內部, 結束位置)"""
    i = start
    depth = 0
    while True:
        m = re.compile(r'<div\b|</div>', re.S).search(html, i)
        if not m:
            raise ValueError("div 不配平")
        if m.group(0) == "<div":
            depth += 1
        else:
            depth -= 1
        i = m.end()
        if depth == 0:
            break
    block = html[start:i]
    inner = block[block.find(">") + 1: block.rfind("</div>")]
    return block, inner, i


# ---------------- 解析系列頁 ----------------
def parse_series(path):
    h = open(path, encoding="utf-8").read()
    lst = h.find('<div class="eng-vars-list">')
    assert lst != -1, path
    vars_ = []
    for m in re.finditer(r'<article class="eng-var" id="([a-z0-9-]+)">', h):
        vid = m.group(1)
        a = m.start()
        nxt = h.find('<article class="eng-var"', a + 10)
        seg_end = nxt if nxt != -1 else h.find('</div>\n </div>\n </section>', a)
        if seg_end == -1:
            seg_end = h.find('</section>', a)
        seg = h[a:seg_end]
        body_i = seg.find('<div class="eng-var-body"')
        assert body_i != -1, (path, vid)
        _, body_inner, _bend = div_block(seg, body_i)
        name_m = re.search(
            r'<h3 class="eng-var-name"><span class="eng-var-idx">([^<]*)</span>([^<]*)(?:<span class="eng-var-name-en">([^<]*)</span>)?</h3>',
            seg)
        assert name_m, (path, vid)
        media_m = re.search(r'<span class="eng-var-media">\s*<picture>.*?src="([^"]+)"', seg, re.S)
        assert media_m, (path, vid)
        desc_m = re.search(r'<p class="eng-var-desc">([^<]*)</p>', body_inner)
        vars_.append(dict(
            vid=vid, idx=name_m.group(1).strip(),
            name=name_m.group(2).strip(), sub=(name_m.group(3) or "").strip(),
            media=media_m.group(1),
            desc=(desc_m.group(1).strip() if desc_m else ""),
            body=body_inner.strip(),
        ))
    # 系列級信息
    hero = dict(
        bg=re.search(r'<section class="product-hero">\s*<picture>.*?src="([^"]+)"', h, re.S).group(1),
        title=re.search(r'<h1 class="product-hero-title">([^<]*)</h1>', h).group(1),
        sub=re.search(r'<p class="product-hero-subtitle">([^<]*)</p>', h).group(1),
    )
    return h, vars_, hero


# ---------------- 生成品種頁 ----------------
IIFE = re.compile(r'<script>\s*\(function \(\)\s*\{\s*var list = document\.querySelector\(\'\.eng-vars-list\'\);.*?</script>', re.S)


def build_variety_page(series_html, series_slug, var, all_vars, lang):
    s = SERIES[series_slug]
    dirurl = "%s/%s.html" % (series_slug, var["vid"])          # 系列頁相對路徑（同層）
    selfurl = "%s/%s.html" % (series_slug, var["vid"])         # 本頁相對系列目錄
    if lang == "zh":
        canon = "https://www.hsst.hk/products/%s" % selfurl
        alt_zh = canon
        alt_en = "https://www.hsst.hk/en/products/%s" % selfurl
    else:
        canon = "https://www.hsst.hk/en/products/%s" % selfurl
        alt_en = canon
        alt_zh = "https://www.hsst.hk/products/%s" % selfurl

    if lang == "zh":
        title = "%s · %s品種 | 恆生石材科技有限公司" % (var["name"], s["nav"]["zh"])
        desc = (var["desc"][:110] + "…") if len(var["desc"]) > 110 else var["desc"]
        label_detail = "品種詳解"
        crumbs = [("首頁", "../../index.html"), ("產品中心", "../../products.html"),
                  (s["nav"]["zh"], "../%s.html" % series_slug), (var["name"], None)]
        back_label, prev_l, next_l = "返回系列", "上一品種", "下一品種"
        detail_h2 = "%s · 樣本、技術參數與應用" % var["name"]
        cta_txt = "查看詳情"
    else:
        title = "%s — %s Varieties | HENGSHENG MARBLE S&T CO. LIMITED" % (var["name"], s["nav"]["en"])
        d_en = var["desc"] if not re.search(r'[\u4e00-\u9fff]', var["desc"]) else s["nav"]["en"] + " variety — samples, technical data and applications."
        desc = (d_en[:110] + "…") if len(d_en) > 110 else d_en
        label_detail = "Variety Details"
        crumbs = [("Home", "../../index.html"), ("Products", "../../products.html"),
                  (s["nav"]["en"], "../%s.html" % series_slug), (var["name"], None)]
        back_label, prev_l, next_l = "Back to series", "Previous", "Next"
        detail_h2 = "%s — Samples, Technical Data & Applications" % var["name"]
        cta_txt = "View details"

    html = series_html

    # ---- <head> 元信息改寫 ----
    html = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title.replace("&", "&amp;"), html, count=1, flags=re.S)
    html = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s\g<2>' % canon, html, count=1)
    html = re.sub(r'(<link rel="alternate" hreflang="zh-Hant" href=")[^"]*(")', r'\g<1>%s\g<2>' % alt_zh, html, count=1)
    html = re.sub(r'(<link rel="alternate" hreflang="en" href=")[^"]*(")', r'\g<1>%s\g<2>' % alt_en, html, count=1)
    html = re.sub(r'(<link rel="alternate" hreflang="x-default" href=")[^"]*(")',
                  r'\g<1>%s\g<2>' % (alt_zh if lang == "zh" else alt_en), html, count=1)
    html = re.sub(r'(<meta name="description" content=")[^"]*(")', r'\g<1>%s\g<2>' % desc.replace("&", "&amp;"), html, count=1)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")', r'\g<1>%s\g<2>' % title.replace("&", "&amp;"), html, count=1)
    html = re.sub(r'(<meta property="og:description" content=")[^"]*(")', r'\g<1>%s\g<2>' % desc.replace("&", "&amp;"), html, count=1)
    html = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s\g<2>' % canon, html, count=1)

    # ---- 主體替換：hero → 品種 hero；varieties 區 → 品種詳解；中間系列區塊刪除 ----
    hero_bg = var["media"]
    idx = html.find('<section class="product-hero">')
    cta_i = html.find('<section class="products-cta')
    foot_i = html.find('<footer class="footer')
    assert idx != -1 and cta_i != -1 and foot_i != -1, series_slug

    cta_block = html[cta_i:foot_i]
    # 去 CTA 塊後面附帶的隱藏 SEO 關鍵詞段（footer 前的所有內容僅保留 CTA 本身）
    cta_end = cta_block.find("</section>") + len("</section>")
    cta_block = cta_block[:cta_end]

    footer_block = html[foot_i: html.find("</body>")]
    top = html[:idx]

    def find_var(v):
        return next(x for x in all_vars if x["vid"] == v["vid"])

    pi = all_vars.index(var)
    prev_v = all_vars[pi - 1] if pi > 0 else None
    next_v = all_vars[pi + 1] if pi < len(all_vars) - 1 else None
    pagers = []
    if prev_v:
        pagers.append('<a class="var-pager prev" href="%s.html"><span>%s</span><b>%s</b></a>'
                      % (prev_v["vid"], prev_l, prev_v["name"]))
    if next_v:
        pagers.append('<a class="var-pager next" href="%s.html"><span>%s</span><b>%s</b></a>'
                      % (next_v["vid"], next_l, next_v["name"]))
    pager_html = '<div class="var-pager-wrap">%s<a class="var-pager back" href="../%s.html"><span>%s</span><b>%s</b></a></div>' % (
        "".join(pagers), series_slug, back_label, s["nav"][lang] if lang in ("zh", "en") else "")

    crumb = '<nav class="breadcrumb" aria-label="Breadcrumb"><ol>%s</ol></nav>' % "".join(
        ('<li><a href="%s">%s</a></li>' % (u, n)) if u else '<li><span aria-current="page">%s</span></li>' % n
        for n, u in crumbs)

    hero = '''<section class="product-hero">
<picture><source srcset="%s" type="image/webp"/><img alt="%s" class="product-hero-bg" src="%s"/></picture>
<div class="product-hero-overlay"></div>
<div class="product-hero-content">
<span class="product-hero-badge">%s</span>
<h1 class="product-hero-title">%s</h1>
<p class="product-hero-subtitle">%s</p>
<p class="product-hero-desc">%s</p>
</div></section>''' % (_pref_url(var["media"].replace(".jpg", ".webp"), 1), var["name"],
                       _pref_url(var["media"], 1), s["nav"][lang], var["name"], var["sub"],
                       (var["desc"][:90] + "…") if len(var["desc"]) > 90 else var["desc"])

    action = ('<section class="product-action-bar"><div class="container">'
              '<a href="%ssample-request.html" class="product-action-btn sample">📦 %s</a>'
              '<a href="%scontact.html" class="product-action-btn inquire">%s</a>'
              '</div></section>') % (
        "../../" if lang == "zh" else "../../",
        "索取樣板" if lang == "zh" else "Request Samples",
        "../../",
        "立即諮詢" if lang == "zh" else "Inquire Now")

    detail = '''<section class="section-padding product-content-section border-top-light" id="variety-detail">
 <div class="container">
  <div class="product-section-title">
   <span class="label">%s · %s</span>
   <h2>%s</h2>
  </div>
  <div class="eng-var-body eng-var-page-body">
%s
  </div>
%s
 </div>
</section>''' % (label_detail, s["nav"][lang], detail_h2,
                 shift(var["body"], 1), pager_html)

    page_style = '''<style>
.eng-var-page-body{background:#fff;border:1px solid rgba(201,168,76,.28);border-radius:16px;padding:30px 34px;box-shadow:0 10px 30px rgba(26,26,46,.06);}
.eng-var-page-body > p:first-child{margin-top:0;}
@media (max-width:700px){.eng-var-page-body{padding:20px 16px;border-radius:12px;}}
.var-pager-wrap{display:flex;gap:12px;margin-top:30px;flex-wrap:wrap;}
.var-pager{flex:1;min-width:150px;display:flex;flex-direction:column;gap:4px;padding:14px 18px;border:1px solid rgba(201,168,76,.4);border-radius:12px;background:#fff;text-decoration:none;transition:border-color .25s,transform .25s;}
.var-pager span{font-size:12px;color:rgba(26,26,46,.55);}
.var-pager b{font-size:15px;color:#1A1A2E;}
.var-pager:hover{border-color:#C9A84C;transform:translateY(-2px);}
.var-pager.next{text-align:right;}
.breadcrumb{padding:14px 0 0;font-size:13px;}
.breadcrumb ol{list-style:none;display:flex;align-items:center;gap:8px;margin:0;padding:0;flex-wrap:wrap;}
</style>'''

    middle = page_style + crumb + hero + action + detail
    # 只有 top/cta/footer 是深度 1（系列頁）的內容，需要 +1；
    # middle（crumbs/hero/action/detail/pager）已按深度 2 寫好，不可再 shift
    top = shift(top, 1)
    cta_block = shift(cta_block, 1)
    footer_block = shift(footer_block, 1)
    html = top + middle + cta_block + "\n" + footer_block + "</body>"
    return html


# ---------------- 改造系列頁 ----------------
CTA_RE = re.compile(r'<span class="eng-var-cta" aria-hidden="true">(.*?)</span>\s*</div>', re.S)


def rebuild_series_page(path, vars_):
    h = open(path, encoding="utf-8").read()
    series_slug = os.path.basename(path)[:-5]
    for var in vars_:
        a = h.find('<article class="eng-var" id="%s">' % var["vid"])
        assert a != -1, (path, var["vid"])
        nxt = h.find('<article class="eng-var"', a + 10)
        seg_end = nxt if nxt != -1 else h.find('</section>', a)
        seg = h[a:seg_end]
        new_seg = seg
        # ① 去掉 head 的按鈕語義
        new_seg = re.sub(r'<div class="eng-var-head" role="button" tabindex="0" aria-expanded="false" aria-controls="eng-panel-%s">' % var["vid"],
                         '<div class="eng-var-head">', new_seg)
        # ② CTA 變連結（相對本系列頁：<series>/<vid>.html）
        link = '%s/%s.html' % (series_slug, var["vid"])
        m = re.search(r'<span class="eng-var-cta" aria-hidden="true">(.*?)</span>', new_seg, re.S)
        assert m, (path, var["vid"])
        inner = m.group(1)
        inner = re.sub(r'<span class="eng-var-cta-txt">[^<]*</span>',
                       '<span class="eng-var-cta-txt">%s</span>' % ("查看詳情" if "/en/" not in path else "View details"),
                       inner)
        new_seg = new_seg[:m.start()] + '<a class="eng-var-cta" href="%s" aria-label="%s">%s</a>' % (link, var["name"], inner) + new_seg[m.end():]
        # ③ 刪除內聯 body
        bi = new_seg.find('<div class="eng-var-body"')
        assert bi != -1, (path, var["vid"])
        _, _, bend = div_block(new_seg, bi)
        new_seg = new_seg[:bi] + new_seg[bend:]
        h = h[:a] + new_seg + h[seg_end:]
    # ④ 移除手風琴 JS
    h2 = IIFE.sub("", h)
    assert h2 != h, path
    h = h2
    # ⑤ 欄目引導文案
    h = h.replace("即可展開該品種的樣本圖、技術參數與適用場景", "即可進入該品種獨立頁面，查看樣本圖、技術參數與適用場景")
    h = h.replace("Click a variety below to expand its samples, technical data and applications.",
                  "Click any variety to open its dedicated page with samples, technical data and applications.")
    h = h.replace("點擊下方任一品種，即可展開", "點擊下方任一品種，即可進入")
    return h


def main():
    changed_pages, created = 0, 0
    for lang, tpl in (("zh", "products/%s.html"), ("en", "en/products/%s.html")):
        for slug in [s["slug"] for s in MF["series"]]:
            path = os.path.join(SITE, tpl % slug)
            if not os.path.exists(path):
                print("  ⚠️ 缺少", path)
                continue
            h, vars_, hero = parse_series(path)
            assert vars_, path
            # 生成品種頁
            for var in vars_:
                out_dir = os.path.join(SITE, tpl % slug)  # products/<slug>/../
                d = os.path.dirname(path)
                out = os.path.join(d, slug, var["vid"] + ".html")
                page = build_variety_page(h, slug, var, vars_, lang)
                assert 'eng-var-page-body' in page
                if APPLY:
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    open(out, "w", encoding="utf-8").write(page)
                created += 1
            # 改造系列頁
            nh = rebuild_series_page(path, vars_)
            if APPLY and nh != h:
                open(path, "w", encoding="utf-8").write(nh)
            changed_pages += 1
            print("  %-14s %d 品種" % (slug, len(vars_)))
    print(("✅ " if APPLY else "🔍(dry-run) ") + f"改造系列頁 {changed_pages} 個；品種頁 {created} 個")
    if not APPLY:
        print("加 --apply 正式寫入")


if __name__ == "__main__":
    main()
