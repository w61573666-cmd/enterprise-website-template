#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全站接入「返回上一級」浮動按鈕  js/back-button.js
================================================
在每個 HTML 的 </body> 前插入一行 <script src="…/js/back-button.js?v=…">。
相對前綴 = '../' * depth（資源以真實檔案位置為基準，en/ 也算一層）。
頁面零配置——按鈕的語言/文案/上級目標全部由 js 依 pathname 推導。

用法：
  python3 scripts/add_back_button.py            # 寫入（冪等，已插入的跳過）
  python3 scripts/add_back_button.py --check    # 只檢查
  python3 scripts/add_back_button.py --token 20260917c   # 指定令牌
"""
import os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = "--check" in sys.argv
TOKEN = "20260917b"
if "--token" in sys.argv:
    TOKEN = sys.argv[sys.argv.index("--token") + 1]

SKIP = {  # 無導航/無正文的樁頁
    "404.html", "en/404.html",
    "baidu_verify_codeva-CniNzYMxpl.html", "yandex_0292681bfbd0e860.html",
}


def main():
    htmls = []
    for root, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in (".git", ".workbuddy", "node_modules")]
        for f in files:
            if f.endswith(".html"):
                htmls.append(os.path.relpath(os.path.join(root, f), SITE))
    htmls.sort()

    done = skip_existing = skip_stub = 0
    problems = []
    for rel in htmls:
        norm = rel.replace(os.sep, "/")
        if norm in SKIP or os.path.basename(norm).startswith("__"):
            skip_stub += 1                # 樁頁 + 本地預覽頁（__*.html）一律不接入
            continue
        path = os.path.join(SITE, rel)
        html = open(path, encoding="utf-8").read()
        if "back-button.js" in html:
            skip_existing += 1
            continue
        depth = rel.count(os.sep)
        src = "../" * depth + f"js/back-button.js?v={TOKEN}"
        # 引用的檔案必須真實存在
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(rel), src.split("?")[0]))):
            problems.append(f"{rel}: 前綴算錯，{src} 不存在")
            continue
        n_body = len(re.findall(r"</body\s*>", html, re.I))
        if n_body != 1:
            problems.append(f"{rel}: </body> 出現 {n_body} 次，跳過")
            continue
        tag = f'<script src="{src}" defer></script>'
        new = re.sub(r"</body\s*>", tag + "\n</body>", html, count=1, flags=re.I)
        if new == html:
            problems.append(f"{rel}: 插入失敗")
            continue
        if not CHECK:
            open(path, "w", encoding="utf-8").write(new)
        done += 1

    print(f"插入 {done} 頁；已有 {skip_existing} 頁；跳過樁頁 {skip_stub}；共 {len(htmls)} 個 HTML；令牌 {TOKEN}")
    if problems:
        print(f"❌ {len(problems)} 個問題：")
        for p in problems[:30]:
            print("   -", p)
        sys.exit(1)
    print("✅ 完成" + ("（--check 未寫入）" if CHECK else ""))


if __name__ == "__main__":
    main()
