#!/usr/bin/env python3
"""
HSST 全站深度审计脚本 v3 - 页眉页脚所有位置
扫描维度：A 页眉 / B 页脚 / C Section / D 内联样式 / E HTML结构 / F 资源引用 / G 中英文对称性
"""

import os
import re
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path("/Users/stone/.qclaw/workspace/hengsheng-stone")
VERSION = "20260819c"
TARGET_VERSION = f"v={VERSION}"
REPORT_FILE = Path("/Users/stone/.qclaw/workspace/hsst-deep-audit-v3_20260819.md")

all_html_files = sorted([f for f in PROJECT_ROOT.rglob("*.html") if ".git" not in str(f)])
all_html_rel = {str(f.relative_to(PROJECT_ROOT)): f for f in all_html_files}

issues = []
file_stats = {}


def add_issue(filepath, problem_type, location, detail, severity, fix):
    rel_path = str(Path(filepath).relative_to(PROJECT_ROOT))
    issues.append({
        "file": rel_path,
        "type": problem_type,
        "location": location,
        "detail": detail,
        "severity": severity,
        "fix": fix
    })


def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def get_line_number(content, pos):
    return content[:pos].count('\n') + 1


def strip_style_script(content):
    def replace_with_spaces(m):
        return ' ' * len(m.group(0))
    result = re.sub(r'<style[^>]*>.*?</style>', replace_with_spaces, content, flags=re.DOTALL | re.IGNORECASE)
    result = re.sub(r'<script[^>]*>.*?</script>', replace_with_spaces, result, flags=re.DOTALL | re.IGNORECASE)
    result = re.sub(r'<!--.*?-->', replace_with_spaces, result, flags=re.DOTALL)
    return result


def extract_text(html):
    text = strip_style_script(html)
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def resolve_url(base_file, url):
    if not url or url.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:', '#', 'data:')):
        return None
    url = url.split('#')[0].split('?')[0]
    if not url:
        return None
    base_dir = base_file.parent
    resolved = (base_dir / url).resolve()
    try:
        rel = resolved.relative_to(PROJECT_ROOT)
        return str(rel)
    except Exception:
        return None


def file_exists(base_file, url):
    rel = resolve_url(base_file, url)
    if rel is None:
        return True
    return (PROJECT_ROOT / rel).exists()


# ============================================================
# A. Header / Nav checks
# ============================================================

def check_header(filepath, content, is_en, is_404):
    rel = str(filepath.relative_to(PROJECT_ROOT))
    filename = filepath.name
    is_index = filename == "index.html" and not rel.startswith("en/")
    is_en_index = rel == "en/index.html"

    # A1: inner-page class on body for non-homepages
    body_match = re.search(r'<body([^>]*)>', content, re.IGNORECASE)
    if body_match:
        body_attrs = body_match.group(1)
        has_inner = 'inner-page' in body_attrs
        if not (is_index or is_en_index or is_404) and not has_inner:
            add_issue(filepath, "A.页眉", "<body>", "内页缺少 class='inner-page'", "高",
                      "在<body>标签添加 class='inner-page'")

    # A2: header/nav structure
    nav_match = re.search(r'<nav\b[^>]*class="[^"]*navbar[^"]*"[^>]*>', content, re.IGNORECASE)
    if not nav_match:
        add_issue(filepath, "A.页眉", "导航", "缺少 <nav class='navbar'>", "高",
                  "添加完整的导航栏结构")
        return ""

    # Extract nav block
    nav_start = nav_match.start()
    nav_end = content.find('</nav>', nav_start)
    if nav_end == -1:
        nav_end = len(content)
    else:
        nav_end += len('</nav>')
    nav_html = content[nav_start:nav_end]

    # A3: Logo / company name
    logo_text_match = re.search(r'<a\s+class="nav-logo"', nav_html, re.IGNORECASE)
    if not logo_text_match:
        add_issue(filepath, "A.页眉", "Logo", "缺少 <a class='nav-logo'>", "高",
                  "添加Logo链接结构")
    else:
        if is_en:
            if "HENGSHENG MARBLE S&T" not in nav_html:
                add_issue(filepath, "A.页眉", "Logo", "英文导航缺少公司英文名", "中",
                          "在nav-logo中补充英文公司名")
        else:
            if "恆生石材科技有限公司" not in nav_html and "恒生石材科技有限公司" not in nav_html:
                add_issue(filepath, "A.页眉", "Logo", "中文导航缺少公司中文名", "中",
                          "在nav-logo中补充中文公司名")

    # A4: mega-panel card counts (allow 10 product cards; expect 16 project cards)
    panels = re.findall(r'<div\s+class="mega-panel"[^>]*>(.*?)</div>\s*</div>\s*</div>', nav_html, re.IGNORECASE | re.DOTALL)
    if panels:
        for idx, panel in enumerate(panels):
            links = re.findall(r'<a\s+class="mega-panel-link"', panel, re.IGNORECASE)
            panel_label = "产品中心" if idx == 0 else "工程案例" if idx == 1 else f"第{idx+1}个"
            if idx == 0:
                if links not in (9, 10):
                    add_issue(filepath, "A.页眉", f"下拉菜单-{panel_label}",
                              f"{panel_label} mega-panel 卡片数为 {len(links)}，期望 9 或 10", "高",
                              f"调整 {panel_label} 下拉菜单为 9 或 10 卡片")
            elif idx == 1:
                if links != 16:
                    add_issue(filepath, "A.页眉", f"下拉菜单-{panel_label}",
                              f"{panel_label} mega-panel 卡片数为 {len(links)}，期望 16", "高",
                              f"调整 {panel_label} 下拉菜单为 16 卡片")

    # A5: Language matching in dropdown
    if is_en:
        zh_in_dropdown = re.findall(r'[\u4e00-\u9fff]{2,}', nav_html)
        real_zh = [z for z in zh_in_dropdown if z not in {"恒生", "石材", "恒生石材", "恆生石材"}]
        if real_zh:
            sample = real_zh[0]
            add_issue(filepath, "A.页眉", "下拉菜单语言", f"英文页下拉菜单残留中文: {sample}", "高",
                      "将英文页下拉菜单内容翻译为英文")

    # A6: Navigation link correctness
    for m in re.finditer(r'<a\s+[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>', nav_html, re.IGNORECASE | re.DOTALL):
        href = m.group(1).strip()
        inner = m.group(2)
        text = extract_text(inner).strip()
        if not href or href.startswith(('#', 'http', 'https', 'mailto:', 'tel:', 'javascript:')):
            continue
        if is_en:
            if href.endswith('.html') and not href.startswith('en/') and not href.startswith('/en/') and not href.startswith('../en/'):
                resolved = resolve_url(filepath, href)
                if resolved and not resolved.startswith("en/"):
                    if href not in ("../index.html", "../../index.html"):
                        add_issue(filepath, "A.页眉", "导航链接",
                                  f"英文页导航链接指向非英文页面: href='{href}' 文字='{text[:20]}'", "高",
                                  "将英文页导航链接改为 en/ 路径")
        else:
            if href.startswith('en/') or href.startswith('/en/') or '../en/' in href:
                if text not in ("EN", "English", "En"):
                    add_issue(filepath, "A.页眉", "导航链接",
                              f"中文页导航链接指向英文页面: href='{href}' 文字='{text[:20]}'", "高",
                              "将中文页导航链接改为中文路径")

    # A8: Contact info in header
    if is_en:
        if "+852" not in nav_html and "5538" not in nav_html and "WhatsApp" not in nav_html:
            add_issue(filepath, "A.页眉", "联系方式", "导航栏缺少电话/WhatsApp/邮箱等联系方式", "低",
                      "在导航栏添加英文联系方式")
    else:
        if "+852" not in nav_html and "5538" not in nav_html and "WhatsApp" not in nav_html and "電話" not in nav_html:
            add_issue(filepath, "A.页眉", "联系方式", "导航栏缺少电话/WhatsApp/邮箱等联系方式", "低",
                      "在导航栏添加中文联系方式")

    return nav_html


# ============================================================
# B. Footer checks
# ============================================================

def check_footer(filepath, content, is_en):
    footer_match = re.search(r'<footer\b', content, re.IGNORECASE)
    if not footer_match:
        add_issue(filepath, "B.页脚", "页脚", "缺少 <footer> 标签", "高",
                  "添加完整页脚")
        return ""

    footer_start = footer_match.start()
    footer_end = content.find('</footer>', footer_start)
    if footer_end == -1:
        footer_html = content[footer_start:]
    else:
        footer_html = content[footer_start:footer_end + len('</footer>')]

    # B1: 4-column layout
    cols = re.findall(r'<div\s+class="[^"]*footer-col[^"]*"[^>]*>', footer_html, re.IGNORECASE)
    col_titles = re.findall(r'<h[34][^>]*>.*?</h[34]>', footer_html, re.IGNORECASE | re.DOTALL)
    if len(cols) < 4 and len(col_titles) < 4:
        add_issue(filepath, "B.页脚", "布局", f"页脚缺少4栏布局迹象 (footer-col={len(cols)}, 标题={len(col_titles)})", "高",
                  "确保页脚为4栏布局：公司信息、快速链接、联系方式、关注我们")

    # B2: Dead links / placeholders
    for m in re.finditer(r'<a\s+[^>]*href\s*=\s*["\']([^"\']*)["\'][^>]*>(.*?)</a>', footer_html, re.IGNORECASE | re.DOTALL):
        href = m.group(1).strip()
        inner = m.group(2)
        text = extract_text(inner).strip()
        if href in ('#', '', 'javascript:void(0)', 'javascript:;'):
            add_issue(filepath, "B.页脚", "死链/占位符",
                      f"页脚链接为占位符: href='{href}' 文字='{text[:30]}'", "中",
                      "替换为实际链接")
            continue
        if not file_exists(filepath, href) and not href.startswith(('#', 'http', 'https', 'mailto:', 'tel:', 'javascript:')):
            add_issue(filepath, "B.页脚", "死链",
                      f"页脚死链: href='{href}' 文字='{text[:30]}'", "高",
                      "修复链接路径或创建目标文件")

    # B3: Copyright
    if "©" not in footer_html and "Copyright" not in footer_html and "版权" not in footer_html:
        add_issue(filepath, "B.页脚", "版权", "页脚缺少版权信息", "高",
                  "添加版权信息，如 © 2026 HENGSHENG MARBLE S&T")

    # B4: Company name in footer
    if is_en:
        if "HENGSHENG MARBLE S&T" not in footer_html:
            add_issue(filepath, "B.页脚", "公司名", "英文页脚缺少公司英文名", "中",
                      "在页脚添加英文公司名")
    else:
        if "恆生石材科技有限公司" not in footer_html and "恒生石材科技有限公司" not in footer_html:
            add_issue(filepath, "B.页脚", "公司名", "中文页脚缺少公司中文名", "中",
                      "在页脚添加中文公司名")

    # B5: QR code / social links
    has_social = bool(re.search(r'facebook|instagram|linkedin|wechat|whatsapp|youtube|twitter|telegram', footer_html, re.IGNORECASE))
    has_qr = bool(re.search(r'<img[^>]*(?:qr|qrcode|wechat)[^>]*>', footer_html, re.IGNORECASE))
    if not has_social and not has_qr:
        add_issue(filepath, "B.页脚", "社交", "页脚缺少二维码或社交链接", "低",
                  "根据需要添加二维码或社交媒体链接")

    # B6: Footer floating / obscured
    if re.search(r'<footer[^>]*style="[^"]*(?:position\s*:\s*fixed|position\s*:\s*absolute)', footer_html, re.IGNORECASE):
        add_issue(filepath, "B.页脚", "显示", "页脚使用了fixed/absolute定位，可能被遮挡", "中",
                  "检查页脚是否被内容遮挡，移除fixed定位")

    # B7: CTA above footer
    cta_match = re.search(r'<section[^>]*class="[^"]*(?:cta|contact-cta|footer-cta)[^"]*"[^>]*>', content[:footer_start], re.IGNORECASE)
    if not cta_match:
        add_issue(filepath, "B.页脚", "CTA", "页脚上方缺少CTA区域", "低",
                  "在页脚上方添加CTA section")

    return footer_html


# ============================================================
# C. Section / content checks
# ============================================================

def check_sections(filepath, content):
    rel = str(filepath.relative_to(PROJECT_ROOT))
    is_en = rel.startswith("en/")

    # C1, C2: Each <section> should have section-padding and container
    for m in re.finditer(r'<section\b([^>]*)>', content, re.IGNORECASE):
        attrs = m.group(1)
        line = get_line_number(content, m.start())
        if 'section-padding' not in attrs:
            style_match = re.search(r'style\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
            has_layout_inline = False
            if style_match:
                style = style_match.group(1).lower()
                if any(p in style for p in ['padding', 'margin', 'width', 'max-width', 'display', 'flex', 'grid', 'position', 'border', 'background']):
                    has_layout_inline = True
                    add_issue(filepath, "C.Section", f"行{line}",
                              f"<section> 缺少 section-padding class 且含内联布局style: {style[:80]}", "高",
                              "添加 section-padding class，并将内联布局样式迁移到CSS")
            if not has_layout_inline:
                add_issue(filepath, "C.Section", f"行{line}",
                          "<section> 缺少 section-padding class", "中",
                          "添加 section-padding class")

    for m in re.finditer(r'<section\b[^>]*>(.*?)</section>', content, re.IGNORECASE | re.DOTALL):
        section_html = m.group(1)
        line = get_line_number(content, m.start())
        if '<div class="container"' not in section_html and '<div class ="container"' not in section_html:
            first = section_html[:200].lower()
            if 'hero' not in first and 'fluid' not in first and 'map' not in first and 'slider' not in first:
                add_issue(filepath, "C.Section", f"行{line}",
                          "<section> 内部缺少 <div class='container'>", "中",
                          "在section内部添加 container div")

    # C5: Tables to cards
    table_count = len(re.findall(r'<table\b', content, re.IGNORECASE))
    if table_count > 0:
        add_issue(filepath, "C.Section", "表格", f"页面仍包含 {table_count} 个 <table> 标签，建议转为卡片网格", "中",
                  "将表格转换为卡片网格布局")

    # C6: Images alt
    for m in re.finditer(r'<img\b[^>]*>', content, re.IGNORECASE):
        tag = m.group()
        line = get_line_number(content, m.start())
        alt_match = re.search(r'\salt\s*=\s*["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if not alt_match:
            add_issue(filepath, "C.Section", f"行{line}",
                      f"<img> 缺少 alt 属性: {tag[:80]}", "中",
                      "添加描述性 alt 属性")
        elif alt_match.group(1).strip() == '':
            add_issue(filepath, "C.Section", f"行{line}",
                      f"<img> alt 属性为空: {tag[:80]}", "中",
                      "填充 alt 属性内容")

    # C7: CTA form text visibility
    dark_sections = re.findall(r'<section\b[^>]*(?:bg-primary|bg-dark|dark-bg|cta|hero)[^>]*>(.*?)</section>', content, re.IGNORECASE | re.DOTALL)
    for sec in dark_sections:
        if '<form' in sec.lower():
            low_contrast = re.findall(r'style="[^"]*color\s*:\s*#?(?:000|111|222|333)[^"]*"', sec, re.IGNORECASE)
            if low_contrast:
                add_issue(filepath, "C.Section", "CTA表单", "深色背景表单中存在深色文字，可能导致不可见", "高",
                          "确保深色背景上的表单文字为白色或浅色")


# ============================================================
# D. Inline styles
# ============================================================

def check_inline_styles(filepath, content):
    rel = str(filepath.relative_to(PROJECT_ROOT))
    layout_props = ['width', 'max-width', 'padding', 'margin', 'display', 'flex', 'grid',
                    'position', 'border', 'background', 'min-width', 'min-height', 'height',
                    'top', 'left', 'right', 'bottom', 'float', 'clear', 'overflow', 'z-index']

    inline_styles = list(re.finditer(r'\sstyle\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE))
    layout_count = 0
    section_layout = []
    for m in inline_styles:
        style = m.group(1).lower()
        line = get_line_number(content, m.start())
        if any(prop in style for prop in layout_props):
            layout_count += 1
            prefix = content[:m.start()]
            section_open = prefix.rfind('<section')
            section_close = prefix.rfind('</section>')
            if section_open > section_close:
                section_tag_match = re.search(r'<section\b([^>]*)>', prefix[section_open:], re.IGNORECASE)
                if section_tag_match:
                    tag_text = section_tag_match.group(1)[:60]
                    section_layout.append((line, tag_text, style[:80]))

    total_inline = len(inline_styles)
    file_stats[rel] = {
        "inline_styles": total_inline,
        "layout_inline_styles": layout_count,
        "section_layout_inline": section_layout
    }

    if total_inline > 30:
        add_issue(filepath, "D.内联样式", "文件级", f"文件内联style数量较多: {total_inline} 个", "中",
                  "逐步将内联样式迁移到CSS类")
    if layout_count > 0:
        add_issue(filepath, "D.内联样式", "文件级", f"文件含 {layout_count} 个内联布局style", "高",
                  "优先将width/padding/margin/display等布局内联样式迁移到CSS")
    for line, tag_text, style in section_layout[:5]:
        add_issue(filepath, "D.内联样式", f"行{line}",
                  f"<section{tag_text}> 仍含内联布局style: {style}", "高",
                  "移除section上的内联布局样式，使用CSS类")


# ============================================================
# E. HTML structure
# ============================================================

def check_html_structure(filepath, content):
    rel = str(filepath.relative_to(PROJECT_ROOT))

    # E1: DOCTYPE unique
    doctypes = re.findall(r'<!DOCTYPE\s+html>', content, re.IGNORECASE)
    if len(doctypes) != 1:
        add_issue(filepath, "E.HTML结构", "DOCTYPE", f"DOCTYPE 数量为 {len(doctypes)}，期望1", "高",
                  "确保每个HTML文件只有一个 <!DOCTYPE html>")

    # E2: Tag pairing for html/head/body/nav/footer/main
    for tag in ['html', 'head', 'body', 'nav', 'footer', 'main']:
        opens = len(re.findall(rf'<{tag}\b[^>]*>', content, re.IGNORECASE))
        closes = len(re.findall(rf'</{tag}\s*>', content, re.IGNORECASE))
        if opens != closes:
            add_issue(filepath, "E.HTML结构", f"<{tag}>",
                      f"<{tag}> 标签不匹配: 开{opens} 闭{closes}", "高",
                      f"确保<{tag}>标签正确闭合")

    # E4: section closed
    sections_open = len(re.findall(r'<section\b[^>]*>', content, re.IGNORECASE))
    sections_close = len(re.findall(r'</section\s*>', content, re.IGNORECASE))
    if sections_open != sections_close:
        add_issue(filepath, "E.HTML结构", "<section>",
                  f"<section> 标签不匹配: 开{sections_open} 闭{sections_close}", "高",
                  "确保所有<section>正确闭合")

    # div balance
    div_open = len(re.findall(r'<div\b[^>]*>', content, re.IGNORECASE))
    div_close = len(re.findall(r'</div\s*>', content, re.IGNORECASE))
    if div_open != div_close:
        add_issue(filepath, "E.HTML结构", "<div>",
                  f"<div> 标签不平衡: 开{div_open} 闭{div_close}", "高",
                  "检查并修复div标签嵌套")

    # E5: Empty sections / paragraphs
    for m in re.finditer(r'<section\b([^>]*)>\s*</section>', content, re.IGNORECASE | re.DOTALL):
        attrs = m.group(1)
        line = get_line_number(content, m.start())
        add_issue(filepath, "E.HTML结构", f"行{line}",
                  f"空 <section> 标签: <section{attrs[:60]}>", "高",
                  "移除空section或填充内容")

    for m in re.finditer(r'<p\b([^>]*)>\s*</p>', content, re.IGNORECASE | re.DOTALL):
        attrs = m.group(1)
        line = get_line_number(content, m.start())
        add_issue(filepath, "E.HTML结构", f"行{line}",
                  f"空 <p> 标签: <p{attrs[:60]}>", "中",
                  "移除空段落或填充内容")

    # E6: Duplicate ids
    ids = re.findall(r'\sid\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
    seen = set()
    dupes = set()
    for idv in ids:
        if idv in seen:
            dupes.add(idv)
        seen.add(idv)
    if dupes:
        for idv in dupes:
            add_issue(filepath, "E.HTML结构", "id",
                      f"重复的 id='{idv}'", "高",
                      "将重复id改为唯一值")


# ============================================================
# F. Resource references
# ============================================================

def check_resources(filepath, content):
    rel = str(filepath.relative_to(PROJECT_ROOT))

    # F1, F2: CSS/JS version numbers
    css_links = re.findall(r'<link\s+[^>]*href\s*=\s*["\']([^"\']+\.css(?:\?[^"\']*)?)["\']', content, re.IGNORECASE)
    for href in css_links:
        if href.startswith(('http://', 'https://', '//')):
            continue
        if "v=" in href and TARGET_VERSION not in href:
            add_issue(filepath, "F.资源引用", "CSS版本",
                      f"CSS版本号不一致: {href}", "高",
                      f"将CSS版本号统一为 {TARGET_VERSION}")
        if "?v=" not in href and 'css/' in href:
            add_issue(filepath, "F.资源引用", "CSS版本",
                      f"CSS缺少版本号: {href}", "中",
                      f"添加版本号 {TARGET_VERSION}")

    js_links = re.findall(r'<script\s+[^>]*src\s*=\s*["\']([^"\']+\.js(?:\?[^"\']*)?)["\']', content, re.IGNORECASE)
    for href in js_links:
        if href.startswith(('http://', 'https://', '//')):
            continue
        if "v=" in href and TARGET_VERSION not in href:
            add_issue(filepath, "F.资源引用", "JS版本",
                      f"JS版本号不一致: {href}", "高",
                      f"将JS版本号统一为 {TARGET_VERSION}")
        if "?v=" not in href and 'js/' in href:
            add_issue(filepath, "F.资源引用", "JS版本",
                      f"JS缺少版本号: {href}", "中",
                      f"添加版本号 {TARGET_VERSION}")

    # F3: Image src accessible
    for m in re.finditer(r'<img\s+[^>]*src\s*=\s*["\']([^"\']*)["\']', content, re.IGNORECASE):
        src = m.group(1).strip()
        line = get_line_number(content, m.start())
        if not src:
            add_issue(filepath, "F.资源引用", f"行{line}", "<img> src为空", "高", "提供图片路径")
            continue
        if src.startswith(('http://', 'https://', 'data:')):
            continue
        if not file_exists(filepath, src):
            add_issue(filepath, "F.资源引用", f"行{line}", f"图片不可访问: {src}", "高",
                      "确认图片路径或添加缺失图片")

    # F4: favicon
    if not re.search(r'<link\s+[^>]*rel\s*=\s*["\'][^"\']*icon[^"\']*["\']', content, re.IGNORECASE):
        add_issue(filepath, "F.资源引用", "favicon", "缺少 favicon 引用", "中",
                  "添加 <link rel='icon' href='favicon.svg'>")

    # F5: canonical
    if not re.search(r'<link\s+[^>]*rel\s*=\s*["\']canonical["\']', content, re.IGNORECASE):
        add_issue(filepath, "F.资源引用", "canonical", "缺少 canonical 标签", "中",
                  "添加 canonical 链接")

    # Also check that local CSS/JS exist (except 404 pages which may have inline styles)
    if '404' not in rel:
        if not any('css/' in h for h in css_links):
            add_issue(filepath, "F.资源引用", "CSS", "缺少本地CSS引用", "高", "添加CSS文件引用")
        if not any('js/' in h for h in js_links):
            add_issue(filepath, "F.资源引用", "JS", "缺少本地JS引用", "高", "添加JS文件引用")


# ============================================================
# G. Chinese/English symmetry
# ============================================================

def check_language_symmetry(filepath, content):
    rel = str(filepath.relative_to(PROJECT_ROOT))
    is_en = rel.startswith("en/")
    text = extract_text(content)

    if is_en:
        chinese = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        exceptions = {"恒生", "石材", "恒生石材", "恆生石材", "恆生石材科技有限公司"}
        real = [c for c in chinese if c not in exceptions]
        if real:
            sample = real[0]
            pos = content.find(sample)
            line = get_line_number(content, pos) if pos >= 0 else 0
            add_issue(filepath, "G.中英对称", f"行{line}",
                      f"英文页残留中文段落: '{sample}'", "高",
                      "将中文内容翻译为英文")


def check_header_footer_consistency():
    navs = defaultdict(list)
    footers = defaultdict(list)

    lang_files = {"zh": [], "en": []}
    for f in all_html_files:
        rel = str(f.relative_to(PROJECT_ROOT))
        is_en = rel.startswith("en/")
        lang_files["en" if is_en else "zh"].append(f)

    for f in all_html_files:
        rel = str(f.relative_to(PROJECT_ROOT))
        is_en = rel.startswith("en/")
        lang = "en" if is_en else "zh"
        content = read_file(f)

        nav_match = re.search(r'<nav\s+class="navbar"[^>]*>(.*?)</nav>', content, re.IGNORECASE | re.DOTALL)
        if nav_match:
            nav_html = re.sub(r'\s+', ' ', nav_match.group(1).strip())
            navs[(lang, nav_html)].append(rel)

        footer_match = re.search(r'<footer\b[^>]*>(.*?)</footer>', content, re.IGNORECASE | re.DOTALL)
        if footer_match:
            footer_html = re.sub(r'\s+', ' ', footer_match.group(1).strip())
            footers[(lang, footer_html)].append(rel)

    for lang in ["zh", "en"]:
        expected = len(lang_files[lang])
        variants = [files for (l, _), files in navs.items() if l == lang]
        if len(variants) > 1:
            total_covered = sum(len(v) for v in variants)
            sample_file = all_html_rel[variants[0][0]]
            add_issue(sample_file, "A.页眉", "一致性",
                      f"{lang} 导航HTML存在 {len(variants)} 种不同结构，覆盖 {total_covered}/{expected} 个文件", "高",
                      f"确保所有{lang}页面导航HTML结构相同（仅active状态不同）")

        fvariants = [files for (l, _), files in footers.items() if l == lang]
        if len(fvariants) > 1:
            total_covered = sum(len(v) for v in fvariants)
            sample_file = all_html_rel[fvariants[0][0]]
            add_issue(sample_file, "B.页脚", "一致性",
                      f"{lang} 页脚HTML存在 {len(fvariants)} 种不同结构，覆盖 {total_covered}/{expected} 个文件", "中",
                      f"确保所有{lang}页面页脚HTML结构相同")


def check_structure_symmetry():
    pairs = []
    for rel, f in all_html_rel.items():
        if rel.startswith("en/"):
            cn_path = PROJECT_ROOT / rel[3:]
            if cn_path.exists():
                pairs.append((cn_path, f))

    for cn_file, en_file in pairs:
        cn_rel = str(cn_file.relative_to(PROJECT_ROOT))
        en_rel = str(en_file.relative_to(PROJECT_ROOT))
        cn_content = read_file(cn_file)
        en_content = read_file(en_file)
        cn_sections = len(re.findall(r'<section\b', cn_content, re.IGNORECASE))
        en_sections = len(re.findall(r'<section\b', en_content, re.IGNORECASE))
        if abs(cn_sections - en_sections) > 2:
            add_issue(en_file, "G.中英对称", "结构",
                      f"中英文页面section数量差异大: 中文{cn_sections} vs 英文{en_sections}", "中",
                      "保持中英文页面对应结构一致")


# ============================================================
# Main audit runner
# ============================================================

def run_audit(round_name):
    global issues
    issues = []
    global file_stats
    file_stats = {}

    print(f"\n=== {round_name} 开始扫描 {len(all_html_files)} 个文件 ===")

    for i, f in enumerate(all_html_files):
        rel = str(f.relative_to(PROJECT_ROOT))
        is_en = rel.startswith("en/")
        is_404 = rel.endswith("404.html")
        content = read_file(f)
        if not content:
            add_issue(f, "E.HTML结构", "文件", "文件为空或无法读取", "高", "检查文件")
            continue

        check_header(f, content, is_en, is_404)
        check_footer(f, content, is_en)
        check_sections(f, content)
        check_inline_styles(f, content)
        check_html_structure(f, content)
        check_resources(f, content)
        check_language_symmetry(f, content)

    check_header_footer_consistency()
    check_structure_symmetry()

    return issues


def generate_report(round_name, issues, fixed_summary=None):
    lines = []
    lines.append(f"# HSST 全站深度审计v3 — {round_name}")
    lines.append(f"\n**审计时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} HKT")
    lines.append(f"**审计范围:** {len(all_html_files)} 个HTML文件")
    lines.append(f"**发现问题:** {len(issues)} 个\n")

    type_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    file_counts = defaultdict(int)
    for issue in issues:
        type_counts[issue["type"]] += 1
        severity_counts[issue["severity"]] += 1
        file_counts[issue["file"]] += 1

    lines.append("## 统计概览\n")
    lines.append("### 按问题类型")
    lines.append("| 问题类型 | 数量 |")
    lines.append("|---------|------|")
    for t in sorted(type_counts.keys()):
        lines.append(f"| {t} | {type_counts[t]} |")
    lines.append("")

    lines.append("### 按严重程度")
    lines.append("| 严重程度 | 数量 |")
    lines.append("|---------|------|")
    for s in ["高", "中", "低"]:
        lines.append(f"| {s} | {severity_counts.get(s, 0)} |")
    lines.append("")

    lines.append("### 文件问题数 Top 30")
    lines.append("| 文件 | 问题数 |")
    lines.append("|------|--------|")
    for f, c in sorted(file_counts.items(), key=lambda x: -x[1])[:30]:
        lines.append(f"| {f} | {c} |")
    lines.append("")

    lines.append("## 详细问题清单\n")
    by_type = defaultdict(list)
    for issue in issues:
        by_type[issue["type"]].append(issue)

    for t in sorted(by_type.keys()):
        lines.append(f"### {t} ({len(by_type[t])}个)\n")
        by_file = defaultdict(list)
        for issue in by_type[t]:
            by_file[issue["file"]].append(issue)
        for f in sorted(by_file.keys()):
            lines.append(f"**{f}**")
            for issue in by_file[f][:10]:
                lines.append(f"- [{issue['severity']}] {issue['location']}: {issue['detail']}")
                lines.append(f"  - 修复: {issue['fix']}")
            if len(by_file[f]) > 10:
                lines.append(f"- ... 还有 {len(by_file[f])-10} 个问题")
            lines.append("")

    lines.append("## 内联样式统计\n")
    lines.append("| 文件 | 内联style总数 | 布局内联style数 |")
    lines.append("|------|---------------|----------------|")
    high_inline_files = sorted(file_stats.items(), key=lambda x: -x[1]["inline_styles"])
    for f, stats in high_inline_files[:30]:
        lines.append(f"| {f} | {stats['inline_styles']} | {stats['layout_inline_styles']} |")
    lines.append("")

    if fixed_summary:
        lines.append("## 本轮修复摘要\n")
        lines.append(fixed_summary)
        lines.append("")

    return "\n".join(lines)


def append_to_report(text):
    if REPORT_FILE.exists():
        with open(REPORT_FILE, 'a', encoding='utf-8') as f:
            f.write("\n\n---\n\n" + text)
    else:
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(text)


# ============================================================
# Run all rounds
# ============================================================

if __name__ == "__main__":
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# HSST 恒生石材网站全站深度审计v3\n\n")
        f.write("**项目目录:** /Users/stone/.qclaw/workspace/hengsheng-stone\n")
        f.write("**审计日期:** 2026-08-19\n")
        f.write(f"**目标CSS/JS版本:** {TARGET_VERSION}\n\n")

    # Round 1
    r1_issues = run_audit("第一轮扫描")
    r1_summary = generate_report("第一轮扫描", r1_issues)
    append_to_report(r1_summary)
    print(f"第一轮发现问题: {len(r1_issues)}")

    # Round 2
    r2_issues = run_audit("第二轮扫描")
    r2_summary = generate_report("第二轮扫描", r2_issues)
    append_to_report(r2_summary)
    print(f"第二轮发现问题: {len(r2_issues)}")

    # Round 3
    r3_issues = run_audit("第三轮扫描")
    r3_summary = generate_report("第三轮扫描（最终验证）", r3_issues)
    append_to_report(r3_summary)
    print(f"第三轮发现问题: {len(r3_issues)}")

    status = subprocess.run(["git", "status", "--short"], cwd=PROJECT_ROOT, capture_output=True, text=True).stdout.strip()
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True).stdout.strip()

    final = f"""## 最终摘要

- 第一轮问题数: {len(r1_issues)}
- 第二轮问题数: {len(r2_issues)}
- 第三轮问题数: {len(r3_issues)}

### 修改文件清单（git status）
```
{status}
```

### Commit SHA
{sha}

### 说明
本次审计未执行 `git push`，由主代理统一处理。
"""
    append_to_report(final)
    print("\n审计完成。报告:", REPORT_FILE)
