#!/usr/bin/env python3
"""
HSST 全站深度审计脚本 v3
- 修正了CSS花括号误报
- 修正了HTML标签闭合检查（处理重复标签、嵌套div等）
- 修正了<a>标签空内容检查（考虑子元素文本）
- 修正了<usd>等假阳性标签检测
- 更精准的内容完整性检查
"""

import os
import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path("/Users/stone/.qclaw/workspace/hengsheng-stone")

all_html_files = sorted(PROJECT_ROOT.rglob("*.html"))
all_html_files = [f for f in all_html_files if ".git" not in str(f)]

# Build set of all existing files
all_image_files = set()
all_video_files = set()
for f in PROJECT_ROOT.rglob("*"):
    if f.is_file() and ".git" not in str(f):
        rel = str(f.relative_to(PROJECT_ROOT))
        if rel.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico')):
            all_image_files.add(rel)
        if rel.lower().endswith(('.mp4', '.webm', '.ogg', '.mov', '.avi')):
            all_video_files.add(rel)

all_html_rel = set()
for f in all_html_files:
    all_html_rel.add(str(f.relative_to(PROJECT_ROOT)))

issues = []

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
    except:
        return ""

def get_line_number(content, pos):
    return content[:pos].count('\n') + 1

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
    except:
        return None

def check_file_exists(base_file, url):
    rel = resolve_url(base_file, url)
    if rel is None:
        return True
    return (PROJECT_ROOT / rel).exists()

def strip_style_script(content):
    """Replace <style> and <script> blocks with equal-length spaces to preserve line numbers."""
    def replace_with_spaces(m):
        return ' ' * len(m.group(0))
    result = re.sub(r'<style[^>]*>.*?</style>', replace_with_spaces, content, flags=re.DOTALL | re.IGNORECASE)
    result = re.sub(r'<script[^>]*>.*?</script>', replace_with_spaces, result, flags=re.DOTALL | re.IGNORECASE)
    return result

def extract_all_text(content):
    """Extract all visible text including from nested elements."""
    text_content = strip_style_script(content)
    text_content = re.sub(r'<!--.*?-->', '', text_content, flags=re.DOTALL)
    # Repeatedly remove tags until no more tags
    prev = None
    while prev != text_content:
        prev = text_content
        text_content = re.sub(r'<[^>]+>', ' ', text_content)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    return text_content

# ===== Check 1: Placeholder text =====

REAL_PLACEHOLDERS = [
    (r'Lorem ipsum', 'Lorem ipsum占位文字'),
    (r'\bTODO\b', 'TODO标记'),
    (r'\bTBD\b', 'TBD标记'),
    (r'待补充', '待补充标记'),
    (r'待完善', '待完善标记'),
    (r'待填写', '待填写标记'),
    (r'暂无内容', '暂无内容'),
    (r'内容待填', '内容待填'),
    (r'示例文字', '示例文字'),
    (r'测试文字', '测试文字'),
    (r'\{pagename\}', '模板变量{pagename}'),
    (r'\{page_name\}', '模板变量{page_name}'),
    (r'\{title\}', '模板变量{title}'),
    (r'\{content\}', '模板变量{content}'),
]

def check_placeholders(filepath, content):
    text_content = strip_style_script(content)
    for pattern, desc in REAL_PLACEHOLDERS:
        for m in re.finditer(pattern, text_content, re.IGNORECASE):
            line = get_line_number(content, m.start())
            add_issue(filepath, "缺失文字", f"行{line}",
                f"占位符文字: {desc} '{m.group()}'", "高",
                f"替换占位符为实际内容")

# ===== Check 2: Empty alt attributes =====

def check_alt_attributes(filepath, content):
    for m in re.finditer(r'<img[^>]*>', content, re.IGNORECASE):
        tag = m.group()
        line = get_line_number(content, m.start())
        alt_match = re.search(r'\salt\s*=\s*["\']([^"\']*)["\']', tag, re.IGNORECASE)
        if not alt_match:
            add_issue(filepath, "缺失文字", f"行{line}",
                f"img标签缺少alt属性: {tag[:80]}", "中",
                "添加描述性的alt属性")
        elif alt_match.group(1).strip() == '':
            add_issue(filepath, "缺失文字", f"行{line}",
                f"img标签alt属性为空: {tag[:80]}", "中",
                "填充alt属性内容")

# ===== Check 3: Image src checks =====

def check_image_srcs(filepath, content):
    for m in re.finditer(r'<img[^>]*src\s*=\s*["\']([^"\']*)["\'][^>]*>', content, re.IGNORECASE):
        src = m.group(1)
        line = get_line_number(content, m.start())
        if not src or src.strip() == '':
            add_issue(filepath, "缺失图片", f"行{line}",
                "img标签src为空", "高",
                "提供有效的图片路径")
            continue
        if src.startswith(('data:', 'http://', 'https://')):
            continue
        if not check_file_exists(filepath, src):
            add_issue(filepath, "缺失图片", f"行{line}",
                f"图片文件不存在: src='{src}'", "高",
                f"确认图片路径是否正确，或添加缺失的图片文件")

# ===== Check 4: CSS background-image checks =====

def check_css_background_images(filepath, content):
    for m in re.finditer(r'background-image\s*:\s*url\(["\']?([^"\')\s]+)["\']?\)', content, re.IGNORECASE):
        url = m.group(1)
        line = get_line_number(content, m.start())
        if url.startswith(('data:', 'http://', 'https://')):
            continue
        if not check_file_exists(filepath, url):
            add_issue(filepath, "缺失图片", f"行{line}",
                f"CSS背景图片不存在: url('{url}')", "高",
                f"确认背景图片路径是否正确")

# ===== Check 5: Empty elements =====

def check_empty_elements(filepath, content):
    text_content = strip_style_script(content)
    
    # Empty headings (h1-h6)
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        for m in re.finditer(rf'<{tag}([^>]*)>\s*</{tag}>', text_content, re.IGNORECASE):
            line = get_line_number(content, m.start())
            add_issue(filepath, "缺失文字", f"行{line}",
                f"<{tag}>标签无文字内容", "高",
                f"填充<{tag}>标题文字")
    
    # Empty <button>
    for m in re.finditer(r'<button([^>]*)>\s*</button>', text_content, re.IGNORECASE):
        line = get_line_number(content, m.start())
        add_issue(filepath, "缺失文字", f"行{line}",
            f"<button>标签无文字内容", "高",
            "添加按钮文字")
    
    # Empty <p> with class
    for m in re.finditer(r'<p([^>]*)>\s*</p>', text_content, re.IGNORECASE):
        attrs = m.group(1).strip()
        line = get_line_number(content, m.start())
        if 'class' in attrs.lower():
            add_issue(filepath, "缺失文字", f"行{line}",
                f"<p>标签有class但无文字内容", "中",
                "填充段落文字内容或移除空标签")
    
    # Empty <section> with class
    for m in re.finditer(r'<section([^>]*)>\s*</section>', text_content, re.IGNORECASE):
        attrs = m.group(1).strip()
        line = get_line_number(content, m.start())
        if 'class' in attrs.lower():
            add_issue(filepath, "内容不完整", f"行{line}",
                f"<section>标签有class但完全无内容", "中",
                "填充section内容或移除空标签")

# ===== Check 6: Links =====

def check_links(filepath, content):
    for m in re.finditer(r'<a[^>]*href\s*=\s*["\']([^"\']*)["\'][^>]*>(.*?)</a>', content, re.IGNORECASE | re.DOTALL):
        href = m.group(1)
        inner_html = m.group(2)
        # Extract ALL text from inner HTML (including nested elements)
        link_text = extract_all_text(inner_html).strip()
        line = get_line_number(content, m.start())
        
        if href == '':
            add_issue(filepath, "HTML结构", f"行{line}",
                f"链接href为空: 文字='{link_text[:30]}'", "高",
                "提供有效的href")
            continue
        
        if href == '#':
            continue
        
        if href.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:')):
            continue
        
        clean_href = href.split('#')[0].split('?')[0]
        if clean_href and not check_file_exists(filepath, href):
            add_issue(filepath, "HTML结构", f"行{line}",
                f"死链(目标文件不存在): href='{href}' 文字='{link_text[:30]}'", "高",
                f"修复链接路径或创建目标文件")
        
        # Only flag empty link text if there are no child elements either
        if not link_text and not re.search(r'<(?:img|svg|i\b|span)', inner_html, re.IGNORECASE):
            add_issue(filepath, "缺失文字", f"行{line}",
                f"<a>标签有href但无文字内容也无图片: href='{href}'", "高",
                "添加链接文字或图标")

# ===== Check 7: Content completeness =====

def check_content_completeness(filepath, content):
    text_content = strip_style_script(content)
    
    # Sections with heading but no paragraph text
    for m in re.finditer(r'<section[^>]*>(.*?)</section>', text_content, re.IGNORECASE | re.DOTALL):
        section_content = m.group(1)
        line = get_line_number(content, m.start())
        
        headings = re.findall(r'<h[1-6][^>]*>.*?</h[1-6]>', section_content, re.IGNORECASE | re.DOTALL)
        paragraphs = re.findall(r'<p[^>]*>.*?</p>', section_content, re.IGNORECASE | re.DOTALL)
        
        # Check for text in divs with text-related classes
        text_divs = re.findall(r'<div[^>]*class="[^"]*(?:content|text|desc|body|info|detail|description|card-body|modal-text)[^"]*"[^>]*>.*?</div>', section_content, re.IGNORECASE | re.DOTALL)
        
        # Check for list items
        list_items = re.findall(r'<li[^>]*>.*?</li>', section_content, re.IGNORECASE | re.DOTALL)
        
        # Check for table cells
        table_cells = re.findall(r'<td[^>]*>.*?</td>', section_content, re.IGNORECASE | re.DOTALL)
        
        if headings and not paragraphs and not text_divs and not list_items and not table_cells:
            # Check for other text-bearing elements
            other_text = re.findall(r'<(?:blockquote|figcaption|caption)[^>]*>', section_content, re.IGNORECASE)
            if not other_text:
                heading_text = extract_all_text(headings[0]).strip()
                if heading_text and len(heading_text) > 2:
                    add_issue(filepath, "内容不完整", f"行{line}",
                        f"section只有标题'{heading_text[:40]}'无正文段落", "中",
                        "添加正文段落内容")

def check_tables(filepath, content):
    text_content = strip_style_script(content)
    for m in re.finditer(r'<td([^>]*)>\s*</td>', text_content, re.IGNORECASE):
        line = get_line_number(content, m.start())
        add_issue(filepath, "内容不完整", f"行{line}",
            "表格单元格(td)为空", "中",
            "填充表格单元格数据或使用占位符样式")
    
    for m in re.finditer(r'<th([^>]*)>\s*</th>', text_content, re.IGNORECASE):
        line = get_line_number(content, m.start())
        add_issue(filepath, "内容不完整", f"行{line}",
            "表头单元格(th)为空", "高",
            "填充表头标题")

# ===== Check 8: Chinese/English symmetry =====

def get_paired_files():
    pairs = []
    for f in all_html_files:
        rel = str(f.relative_to(PROJECT_ROOT))
        if rel.startswith("en/"):
            cn_path = PROJECT_ROOT / rel[3:]
            if cn_path.exists():
                pairs.append((cn_path, f))
    return pairs

def check_cn_en_symmetry():
    pairs = get_paired_files()
    for cn_file, en_file in pairs:
        cn_content = read_file(cn_file)
        en_content = read_file(en_file)
        
        cn_text = extract_all_text(cn_content)
        en_text = extract_all_text(en_content)
        
        # Chinese text in English pages
        cn_chars_in_en = re.findall(r'[\u4e00-\u9fff]+', en_text)
        if cn_chars_in_en:
            exceptions = {'恒生石材', '恒生', '石材'}
            real_cn = [c for c in cn_chars_in_en if c not in exceptions]
            if real_cn:
                for cn_word in list(set(real_cn))[:10]:
                    pos = en_content.find(cn_word)
                    if pos >= 0:
                        line = get_line_number(en_content, pos)
                        add_issue(en_file, "中英不对称", f"行{line}",
                            f"英文页残留中文: '{cn_word}'", "高",
                            f"将'{cn_word}'翻译为英文")
        
        # Content length asymmetry
        cn_len = len(cn_text)
        en_len = len(en_text)
        if cn_len > 100 and en_len > 100:
            ratio = en_len / cn_len
            if ratio < 0.4:
                add_issue(en_file, "中英不对称", "全文",
                    f"英文页内容明显少于中文页 (中文{cn_len}字符 vs 英文{en_len}字符, 比例{ratio:.1%})", "中",
                    "补充英文页内容，使其与中文页对称")
            elif ratio > 2.5:
                add_issue(cn_file, "中英不对称", "全文",
                    f"中文页内容明显少于英文页 (中文{cn_len}字符 vs 英文{en_len}字符, 比例{ratio:.1%})", "中",
                    "补充中文页内容，使其与英文页对称")

# ===== Check 9: HTML structure (improved v3) =====

def check_html_structure(filepath, content):
    VOID_ELEMENTS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                      'link', 'meta', 'param', 'source', 'track', 'wbr'}
    
    # First, remove script and style blocks entirely to avoid parsing their contents
    # Use space replacement to preserve line numbers
    def replace_with_spaces(m):
        return ' ' * len(m.group(0))
    clean_content = re.sub(r'<script[^>]*>.*?</script>', replace_with_spaces, content, flags=re.DOTALL | re.IGNORECASE)
    clean_content = re.sub(r'<style[^>]*>.*?</style>', replace_with_spaces, clean_content, flags=re.DOTALL | re.IGNORECASE)
    # Also remove comments
    clean_content = re.sub(r'<!--.*?-->', replace_with_spaces, clean_content, flags=re.DOTALL)
    
    # Also remove content that looks like tags but is actually text (e.g. '<USD 50/sqm')
    # These are patterns like < followed by uppercase letters followed by space/digit (not valid HTML tags)
    # We'll handle this by filtering out non-HTML tag matches in the parser below
    
    tag_re = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)(/?)>', re.DOTALL)
    
    # Valid HTML tag names (lowercase). Any tag name not in this set is likely text content misidentified as a tag.
    VALID_HTML_TAGS = {
        'html', 'head', 'body', 'div', 'span', 'p', 'a', 'img', 'ul', 'ol', 'li',
        'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot', 'caption', 'col', 'colgroup',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'footer', 'nav', 'main', 'section',
        'article', 'aside', 'figure', 'figcaption', 'blockquote', 'pre', 'code', 'em',
        'strong', 'b', 'i', 'u', 's', 'small', 'sub', 'sup', 'mark', 'del', 'ins',
        'form', 'input', 'textarea', 'select', 'option', 'optgroup', 'label', 'fieldset',
        'legend', 'button', 'datalist', 'output', 'progress', 'meter',
        'br', 'hr', 'wbr', 'details', 'summary', 'dialog', 'menu', 'menuitem',
        'iframe', 'embed', 'object', 'param', 'video', 'audio', 'source', 'track',
        'canvas', 'svg', 'math', 'picture', 'map', 'area',
        'meta', 'link', 'title', 'base', 'style', 'script', 'noscript', 'template',
        'address', 'abbr', 'cite', 'q', 'dfn', 'kbd', 'samp', 'var', 'time', 'ruby',
        'rt', 'rp', 'bdi', 'bdo', 'data', 'slot',
    }
    
    stack = []
    
    for m in tag_re.finditer(clean_content):
        is_closing = m.group(1) == '/'
        tag_name = m.group(2).lower()
        is_self_closing = m.group(4) == '/'
        line = get_line_number(content, m.start())
        
        # Skip non-HTML tags (likely text content like <USD)
        if tag_name not in VALID_HTML_TAGS:
            continue
        
        if tag_name in VOID_ELEMENTS:
            continue
        
        if is_self_closing and not is_closing:
            continue
        
        if is_closing:
            found_idx = None
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag_name:
                    found_idx = i
                    break
            
            if found_idx is not None:
                for j in range(len(stack) - 1, found_idx, -1):
                    unclosed_tag, unclosed_line = stack[j]
                    if unclosed_tag not in ('p', 'span', 'li', 'td', 'th', 'tr', 'option'):
                        add_issue(filepath, "HTML结构", f"行{unclosed_line}",
                            f"未闭合标签: <{unclosed_tag}> (在</{tag_name}>之前未闭合)", "高",
                            f"添加</{unclosed_tag}>闭合标签")
                stack = stack[:found_idx]
        else:
            stack.append((tag_name, line))
    
    if stack:
        tag_name, line = stack[0]
        if tag_name != 'html':  # html unclosed is usually a parser edge case
            add_issue(filepath, "HTML结构", f"行{line}",
                f"未闭合标签: <{tag_name}>", "高",
                f"添加</{tag_name}>闭合标签")

# ===== Check 10: Video source checks =====

def check_video_srcs(filepath, content):
    for m in re.finditer(r'<source[^>]*src\s*=\s*["\']([^"\']*)["\'][^>]*>', content, re.IGNORECASE):
        src = m.group(1)
        line = get_line_number(content, m.start())
        if not src or src.startswith(('http://', 'https://', 'data:')):
            continue
        if not check_file_exists(filepath, src):
            add_issue(filepath, "缺失图片", f"行{line}",
                f"视频文件不存在: src='{src}'", "高",
                f"确认视频路径是否正确")

# ===== Check 11: Duplicate DOCTYPE =====

def check_duplicate_doctype(filepath, content):
    doctype_count = len(re.findall(r'<!DOCTYPE\s+html>', content, re.IGNORECASE))
    if doctype_count > 1:
        add_issue(filepath, "HTML结构", "文件头部",
            f"重复的DOCTYPE声明 ({doctype_count}个)", "中",
            "移除多余的DOCTYPE声明，每个HTML文件只应有一个")

# ===== Check 12: Duplicate html tag =====

def check_duplicate_html_tag(filepath, content):
    html_open_count = len(re.findall(r'<html\b', content, re.IGNORECASE))
    if html_open_count > 1:
        add_issue(filepath, "HTML结构", "文件头部",
            f"重复的<html>标签 ({html_open_count}个)", "中",
            "移除多余的<html>标签，每个HTML文件只应有一个")

# ===== Main audit =====

def audit_file(filepath):
    content = read_file(filepath)
    if not content:
        add_issue(filepath, "内容不完整", "全文", "文件为空或无法读取", "高", "检查文件内容")
        return
    
    check_placeholders(filepath, content)
    check_alt_attributes(filepath, content)
    check_image_srcs(filepath, content)
    check_css_background_images(filepath, content)
    check_empty_elements(filepath, content)
    check_links(filepath, content)
    check_content_completeness(filepath, content)
    check_tables(filepath, content)
    check_html_structure(filepath, content)
    check_video_srcs(filepath, content)
    check_duplicate_doctype(filepath, content)
    check_duplicate_html_tag(filepath, content)

# Run
print(f"开始审计 {len(all_html_files)} 个HTML文件...")

for i, f in enumerate(all_html_files):
    print(f"  [{i+1}/{len(all_html_files)}] {f.relative_to(PROJECT_ROOT)}")
    audit_file(f)

print("\n检查中英文对称性...")
check_cn_en_symmetry()

# ===== Generate report =====

type_counts = defaultdict(int)
severity_counts = defaultdict(int)
file_counts = defaultdict(int)

for issue in issues:
    type_counts[issue["type"]] += 1
    severity_counts[issue["severity"]] += 1
    file_counts[issue["file"]] += 1

report_lines = []
report_lines.append("# HSST 恒生石材网站 全站深度审计报告")
report_lines.append(f"\n**审计时间:** 2026-08-19 18:47 HKT")
report_lines.append(f"**审计范围:** {len(all_html_files)} 个HTML文件（全站）")
report_lines.append(f"**发现问题总数:** {len(issues)} 个\n")

report_lines.append("## 📊 统计概览\n")
report_lines.append("### 按问题类型统计\n")
report_lines.append("| 问题类型 | 数量 |")
report_lines.append("|---------|------|")
for t in ["缺失文字", "缺失图片", "内容不完整", "中英不对称", "HTML结构"]:
    report_lines.append(f"| {t} | {type_counts[t]} |")
report_lines.append("")

report_lines.append("### 按严重程度统计\n")
report_lines.append("| 严重程度 | 数量 |")
report_lines.append("|---------|------|")
for s in ["高", "中", "低"]:
    report_lines.append(f"| {s} | {severity_counts[s]} |")
report_lines.append("")

report_lines.append("### 按文件统计 (Top 25)\n")
report_lines.append("| 文件 | 问题数 |")
report_lines.append("|------|--------|")
sorted_files = sorted(file_counts.items(), key=lambda x: -x[1])
for f, count in sorted_files[:25]:
    report_lines.append(f"| {f} | {count} |")
report_lines.append("")

# Detailed issues by category
report_lines.append("\n---\n")
report_lines.append("## 📋 详细问题清单\n")

for problem_type in ["缺失文字", "缺失图片", "内容不完整", "中英不对称", "HTML结构"]:
    type_issues = [i for i in issues if i["type"] == problem_type]
    if not type_issues:
        report_lines.append(f"### {problem_type}\n\n✅ 未发现问题\n")
        continue
    
    report_lines.append(f"### {problem_type} ({len(type_issues)}个)\n")
    
    by_file = defaultdict(list)
    for issue in type_issues:
        by_file[issue["file"]].append(issue)
    
    for filepath in sorted(by_file.keys()):
        file_issues = by_file[filepath]
        report_lines.append(f"#### 文件: `{filepath}`\n")
        for issue in file_issues:
            report_lines.append(f"```")
            report_lines.append(f"问题类型: {issue['type']}")
            report_lines.append(f"位置: {issue['location']}")
            report_lines.append(f"详情: {issue['detail']}")
            report_lines.append(f"严重程度: {issue['severity']}")
            report_lines.append(f"建议修复: {issue['fix']}")
            report_lines.append(f"```")
        report_lines.append("")

# Summary
report_lines.append("\n---\n")
report_lines.append("## 🔧 修复优先级建议\n")

high_issues = [i for i in issues if i["severity"] == "高"]
report_lines.append(f"### 🔴 高优先级 ({len(high_issues)}个)\n")
report_lines.append("以下问题需要立即修复：\n")

high_by_type = defaultdict(list)
for issue in high_issues:
    high_by_type[issue["type"]].append(issue)

for t in ["缺失文字", "缺失图片", "内容不完整", "中英不对称", "HTML结构"]:
    if high_by_type[t]:
        report_lines.append(f"\n**{t}** ({len(high_by_type[t])}个):\n")
        shown = 0
        for issue in high_by_type[t]:
            if shown >= 20:
                report_lines.append(f"- ... 还有 {len(high_by_type[t])-20} 个")
                break
            report_lines.append(f"- `{issue['file']}` {issue['location']}: {issue['detail']}")
            shown += 1
report_lines.append("")

medium_issues = [i for i in issues if i["severity"] == "中"]
report_lines.append(f"\n### 🟡 中优先级 ({len(medium_issues)}个)\n")
report_lines.append("以下问题建议尽快修复：\n")
for t in ["缺失文字", "缺失图片", "内容不完整", "中英不对称", "HTML结构"]:
    count = sum(1 for i in medium_issues if i["type"] == t)
    if count:
        report_lines.append(f"- **{t}**: {count}个")

# List medium issues grouped
report_lines.append("\n<details>")
report_lines.append("<summary>展开中优先级问题详情</summary>\n")
for t in ["缺失文字", "缺失图片", "内容不完整", "中英不对称", "HTML结构"]:
    t_issues = [i for i in medium_issues if i["type"] == t]
    if t_issues:
        report_lines.append(f"\n**{t}:**")
        for issue in t_issues:
            report_lines.append(f"- `{issue['file']}` {issue['location']}: {issue['detail']}")
report_lines.append("\n</details>\n")

low_issues = [i for i in issues if i["severity"] == "低"]
report_lines.append(f"### 🟢 低优先级 ({len(low_issues)}个)\n")
if low_issues:
    for t in ["缺失文字", "缺失图片", "内容不完整", "中英不对称", "HTML结构"]:
        count = sum(1 for i in low_issues if i["type"] == t)
        if count:
            report_lines.append(f"- **{t}**: {count}个")
else:
    report_lines.append("无低优先级问题。")
report_lines.append("")

# Clean files
clean_files = []
for f in all_html_files:
    rel = str(f.relative_to(PROJECT_ROOT))
    if rel not in file_counts:
        clean_files.append(rel)

if clean_files:
    report_lines.append("\n### ✅ 无问题文件\n")
    report_lines.append(f"以下 {len(clean_files)} 个文件未发现明显问题：\n")
    for f in clean_files:
        report_lines.append(f"- `{f}`")
    report_lines.append("")

# Pattern analysis
report_lines.append("\n---\n")
report_lines.append("## 📈 共性问题模式分析\n")

# Group by detail pattern
pattern_groups = defaultdict(list)
for issue in issues:
    # Normalize the detail to find patterns
    detail = issue["detail"]
    # Extract the core pattern
    if "多角度" in detail or "Multi-Angle" in detail:
        pattern_groups["多角度产品图库section无正文段落"].append(issue)
    elif "探索更多" in detail or "Explore More" in detail:
        pattern_groups["探索更多案例section无正文段落"].append(issue)
    elif "項目實景" in detail or "Project Gallery" in detail:
        pattern_groups["项目实景展示section无正文段落"].append(issue)
    elif "DOCTYPE" in detail or "html" in detail.lower():
        pattern_groups["重复DOCTYPE/html标签"].append(issue)
    elif "死链" in detail:
        pattern_groups["死链"].append(issue)
    elif "残留中文" in detail:
        pattern_groups["英文页残留中文"].append(issue)
    elif "alt" in detail.lower():
        pattern_groups["alt属性问题"].append(issue)

report_lines.append("以下是需要批量处理的共性问题：\n")
for pattern, pattern_issues in sorted(pattern_groups.items(), key=lambda x: -len(x[1])):
    report_lines.append(f"### {pattern} ({len(pattern_issues)}个)\n")
    affected_files = sorted(set(i["file"] for i in pattern_issues))
    report_lines.append(f"影响文件数: {len(affected_files)}\n")
    if len(affected_files) <= 10:
        for f in affected_files:
            report_lines.append(f"- `{f}`")
    else:
        for f in affected_files[:5]:
            report_lines.append(f"- `{f}`")
        report_lines.append(f"- ... 及其他 {len(affected_files)-5} 个文件")
    report_lines.append("")
    
    # Suggest batch fix
    if "多角度" in pattern or "Multi-Angle" in pattern:
        report_lines.append("**批量修复建议:** 为所有产品详情页的「多角度产品图库」section添加简短描述段落。\n")
    elif "探索更多" in pattern or "Explore More" in pattern:
        report_lines.append("**批量修复建议:** 为所有项目详情页的「探索更多案例」section添加引导文字段落。\n")
    elif "項目實景" in pattern or "Project Gallery" in pattern:
        report_lines.append("**批量修复建议:** 为相关项目详情页的「项目实景展示」section添加描述段落。\n")
    elif "DOCTYPE" in pattern:
        report_lines.append("**批量修复建议:** 移除所有文件中重复的DOCTYPE和<html>标签。\n")

report_lines.append("\n---\n")
report_lines.append("## 📝 审计方法说明\n")
report_lines.append("本审计使用Python脚本自动化检查，覆盖以下5大维度：\n")
report_lines.append("1. **缺失文字内容** - 检查空标签、占位符文字、空alt属性、空链接文字、空按钮文字")
report_lines.append("2. **缺失图片** - 检查img src文件是否存在、CSS背景图、视频源文件")
report_lines.append("3. **内容不完整** - 检查空section、空表格单元格、只有标题无正文的section")
report_lines.append("4. **中英文对称性** - 对比中英页面内容长度、英文页残留中文文字")
report_lines.append("5. **HTML结构问题** - 检查未闭合标签、死链、空href、重复DOCTYPE")
report_lines.append(f"\n共检查 {len(all_html_files)} 个HTML文件，发现 {len(issues)} 个问题。")
report_lines.append(f"\n**审计脚本:** `hsst_deep_audit.py`")

# Write
report_content = "\n".join(report_lines)
output_path = Path("/Users/stone/.qclaw/workspace/hsst-deep-audit-report.md")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\n✅ 审计完成！")
print(f"共检查 {len(all_html_files)} 个HTML文件")
print(f"共发现 {len(issues)} 个问题")
print(f"  - 高严重度: {severity_counts['高']}")
print(f"  - 中严重度: {severity_counts['中']}")
print(f"  - 低严重度: {severity_counts['低']}")
print(f"\n报告已写入: {output_path}")
