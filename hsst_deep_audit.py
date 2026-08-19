#!/usr/bin/env python3
"""
HSST 全站深度审计脚本 v2
审计所有81个HTML文件的5大维度问题
- 修正了CSS花括号误报问题
- 修正了HTML标签闭合检查的误报
- 更精准的占位符检测
"""

import os
import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path("/Users/stone/.qclaw/workspace/hengsheng-stone")

all_html_files = sorted(PROJECT_ROOT.rglob("*.html"))
all_html_files = [f for f in all_html_files if ".git" not in str(f)]

# Build set of all existing files (relative to project root)
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

# ===== Extract content outside of <style> and <script> for text checks =====

def strip_style_script(content):
    """Remove <style> and <script> blocks for text-based checks."""
    result = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    result = re.sub(r'<script[^>]*>.*?</script>', '', result, flags=re.DOTALL | re.IGNORECASE)
    return result

def strip_html_tags(text):
    return re.sub(r'<[^>]+>', ' ', text)

# ===== Check 1: Placeholder text =====

REAL_PLACEHOLDERS = [
    (r'Lorem ipsum', 'Lorem ipsum占位文字'),
    (r'TODO\b', 'TODO标记'),
    (r'TBD\b', 'TBD标记'),
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
    # Only check visible text (outside style/script)
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

# ===== Check 5: Empty elements with class but no content =====

def check_empty_elements(filepath, content):
    text_content = strip_style_script(content)
    
    # Empty <p> with class
    for m in re.finditer(r'<p([^>]*)>\s*</p>', text_content, re.IGNORECASE):
        attrs = m.group(1).strip()
        line = get_line_number(content, m.start())
        if 'class' in attrs.lower():
            add_issue(filepath, "缺失文字", f"行{line}",
                f"<p>标签有class但无文字内容", "中",
                "填充段落文字内容或移除空标签")
    
    # Empty headings
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        pattern = rf'<{tag}([^>]*)>\s*</{tag}>'
        for m in re.finditer(pattern, text_content, re.IGNORECASE):
            line = get_line_number(content, m.start())
            add_issue(filepath, "缺失文字", f"行{line}",
                f"<{tag}>标签无文字内容", "高",
                f"填充<{tag}>标题文字")
    
    # Empty <a> with href
    for m in re.finditer(r'<a([^>]*)>\s*</a>', text_content, re.IGNORECASE):
        attrs = m.group(1).strip()
        line = get_line_number(content, m.start())
        if 'href' in attrs.lower():
            add_issue(filepath, "缺失文字", f"行{line}",
                f"<a>标签有href但无文字内容", "高",
                "添加链接文字")
    
    # Empty <button>
    for m in re.finditer(r'<button([^>]*)>\s*</button>', text_content, re.IGNORECASE):
        line = get_line_number(content, m.start())
        add_issue(filepath, "缺失文字", f"行{line}",
            f"<button>标签无文字内容", "高",
            "添加按钮文字")
    
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
        link_text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        line = get_line_number(content, m.start())
        
        if href == '' :
            add_issue(filepath, "HTML结构", f"行{line}",
                f"链接href为空: 文字='{link_text[:30]}'", "高",
                "提供有效的href")
            continue
        
        if href == '#':
            if link_text:
                # href="#" is common for JS buttons - low severity
                pass  # skip to reduce noise
            continue
        
        if href.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:')):
            continue
        
        # Check internal links
        clean_href = href.split('#')[0].split('?')[0]
        if clean_href and not check_file_exists(filepath, href):
            add_issue(filepath, "HTML结构", f"行{line}",
                f"死链(目标文件不存在): href='{href}' 文字='{link_text[:30]}'", "高",
                f"修复链接路径或创建目标文件")

# ===== Check 7: Content completeness =====

def check_content_completeness(filepath, content):
    text_content = strip_style_script(content)
    
    # Sections with heading but no paragraph
    for m in re.finditer(r'<section[^>]*>(.*?)</section>', text_content, re.IGNORECASE | re.DOTALL):
        section_content = m.group(1)
        line = get_line_number(content, m.start())
        
        headings = re.findall(r'<h[1-6][^>]*>.*?</h[1-6]>', section_content, re.IGNORECASE | re.DOTALL)
        paragraphs = re.findall(r'<p[^>]*>.*?</p>', section_content, re.IGNORECASE | re.DOTALL)
        divs_with_text = re.findall(r'<div[^>]*class="[^"]*(?:content|text|desc|body|info|detail)[^"]*"[^>]*>.*?</div>', section_content, re.IGNORECASE | re.DOTALL)
        
        if headings and not paragraphs and not divs_with_text:
            other_text_tags = re.findall(r'<(?:li|td|blockquote)[^>]*>', section_content, re.IGNORECASE)
            if not other_text_tags:
                heading_text = re.sub(r'<[^>]+>', '', headings[0]).strip()
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

def extract_text_content(content):
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def check_cn_en_symmetry():
    pairs = get_paired_files()
    
    for cn_file, en_file in pairs:
        cn_content = read_file(cn_file)
        en_content = read_file(en_file)
        
        cn_text = extract_text_content(cn_content)
        en_text = extract_text_content(en_content)
        
        # Chinese text in English pages
        cn_chars_in_en = re.findall(r'[\u4e00-\u9fff]+', en_text)
        if cn_chars_in_en:
            # Filter known exceptions
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

# ===== Check 9: HTML structure (improved) =====

def check_html_structure(filepath, content):
    VOID_ELEMENTS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                      'link', 'meta', 'param', 'source', 'track', 'wbr'}
    
    # Use a simple tag matcher
    tag_pattern = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*?)(/?)>', re.DOTALL)
    
    stack = []
    in_style = False
    in_script = False
    
    for m in tag_pattern.finditer(content):
        is_closing = m.group(1) == '/'
        tag_name = m.group(2).lower()
        attrs = m.group(3)
        is_self_closing = m.group(4) == '/'
        line = get_line_number(content, m.start())
        
        # Skip tags inside style/script
        if tag_name == 'style':
            if is_closing:
                in_style = False
            else:
                in_style = True
            continue
        if tag_name == 'script':
            if is_closing:
                in_script = False
            else:
                in_script = True
            continue
        if in_style or in_script:
            continue
        
        if tag_name in VOID_ELEMENTS or is_self_closing:
            continue
        
        if is_closing:
            # Find matching open tag in stack
            found = False
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag_name:
                    # Pop all unclosed tags between
                    for j in range(len(stack) - 1, i, -1):
                        unclosed_tag, unclosed_line = stack[j]
                        add_issue(filepath, "HTML结构", f"行{unclosed_line}",
                            f"未闭合标签: <{unclosed_tag}> (在</{tag_name}>之前未闭合)", "高",
                            f"添加</{unclosed_tag}>闭合标签")
                    stack = stack[:i]
                    found = True
                    break
            if not found:
                # Closing tag without opening
                pass  # Lower priority, skip for now
        else:
            stack.append((tag_name, line))
    
    # Report remaining unclosed tags
    for tag_name, line in stack:
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
report_lines.append(f"**审计文件数:** {len(all_html_files)} 个HTML")
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

report_lines.append("### 按文件统计 (Top 20)\n")
report_lines.append("| 文件 | 问题数 |")
report_lines.append("|------|--------|")
sorted_files = sorted(file_counts.items(), key=lambda x: -x[1])
for f, count in sorted_files[:20]:
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

high_by_type = defaultdict(list)
for issue in high_issues:
    high_by_type[issue["type"]].append(issue)

for t in ["缺失文字", "缺失图片", "内容不完整", "中英不对称", "HTML结构"]:
    if high_by_type[t]:
        report_lines.append(f"- **{t}**: {len(high_by_type[t])}个")
        shown = 0
        for issue in high_by_type[t]:
            if shown >= 15:
                report_lines.append(f"  - ... 还有 {len(high_by_type[t])-15} 个")
                break
            report_lines.append(f"  - `{issue['file']}` {issue['location']}: {issue['detail']}")
            shown += 1
report_lines.append("")

medium_issues = [i for i in issues if i["severity"] == "中"]
report_lines.append(f"### 🟡 中优先级 ({len(medium_issues)}个)\n")
for t in ["缺失文字", "缺失图片", "内容不完整", "中英不对称", "HTML结构"]:
    count = sum(1 for i in medium_issues if i["type"] == t)
    if count:
        report_lines.append(f"- **{t}**: {count}个")
report_lines.append("")

low_issues = [i for i in issues if i["severity"] == "低"]
report_lines.append(f"### 🟢 低优先级 ({len(low_issues)}个)\n")
for t in ["缺失文字", "缺失图片", "内容不完整", "中英不对称", "HTML结构"]:
    count = sum(1 for i in low_issues if i["type"] == t)
    if count:
        report_lines.append(f"- **{t}**: {count}个")
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

report_lines.append("\n---\n")
report_lines.append("## 📝 审计方法说明\n")
report_lines.append("本审计使用Python脚本自动化检查，覆盖以下5大维度：\n")
report_lines.append("1. **缺失文字内容** - 检查空标签、占位符、空alt、空链接文字、空按钮文字")
report_lines.append("2. **缺失图片** - 检查img src、CSS背景图、视频源文件是否存在")
report_lines.append("3. **内容不完整** - 检查空section、空表格单元格、只有标题无正文的section")
report_lines.append("4. **中英文对称性** - 对比中英页面内容长度、英文页残留中文文字")
report_lines.append("5. **HTML结构问题** - 检查未闭合标签、死链、空href")
report_lines.append(f"\n共检查 {len(all_html_files)} 个HTML文件，发现 {len(issues)} 个问题。")

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
