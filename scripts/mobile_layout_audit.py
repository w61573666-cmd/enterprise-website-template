#!/usr/bin/env python3
"""
手机端排版审计脚本 - 检测 grid/flex 卡片网格的"孤儿卡"问题

使用 headless Chrome (CDP) 以 375px 视口宽度加载页面，
检测末行只有 1 张卡片且未铺满全宽的排版问题。

用法:
    python scripts/mobile_layout_audit.py
"""

import json
import subprocess
import time
import sys
import os
import re

try:
    import websocket
except ImportError:
    print("错误: 需要安装 websocket-client")
    print("  pip install websocket-client")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests")
    print("  pip install requests")
    sys.exit(1)


# ── 配置 ──────────────────────────────────────────────────────────────

CHROME_PATH = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)
BASE_URL = "http://localhost:8931"
REMOTE_DEBUGGING_PORT = 9222
VIEWPORT_WIDTH = 375
VIEWPORT_HEIGHT = 812
DEVICE_SCALE_FACTOR = 2

# 关键页面列表（繁体中文名称用于输出）
PAGES = [
    ("index.html", "首頁"),
    ("products.html", "產品中心"),
    ("projects.html", "工程案例"),
    ("solutions.html", "解決方案"),
    ("about.html", "關於我們"),
    ("news.html", "新聞中心"),
    ("guides/index.html", "攻略 Hub"),
    ("products/granite-collection.html", "麻石系列"),
    ("products/white-marble.html", "白色雲石"),
    ("products/engineering-stone-varieties.html", "工程石材"),
    ("projects/hotel.html", "酒店案例"),
    ("faq.html", "FAQ"),
    ("contact.html", "聯繫我們"),
]

# 排除列表：这些 class/id 的容器不是卡片网格，跳过检测
EXCLUDE_SELECTORS = [
    "hsst-form",
    "inquiry-form",
    "surface-treatment-tags",
    "hsst-spec-chips",
    "cs2-chips",
    "contact-eco-tags",
    "news-card-meta",
    "contact-region-item",
    "cta-buttons",
    "hsst-filter-group",
    "ft-badges",
    "client-logos-grid",
    "hsst-wm",
]

# 孤儿卡判定阈值：末行单元素宽度 < 容器宽度 * 此比例
ORPHAN_WIDTH_RATIO = 0.80

# 行判定的 y 坐标容差（像素）
ROW_Y_TOLERANCE = 4


# ── Chrome CDP 工具 ──────────────────────────────────────────────────

class ChromeCDP:
    """通过 CDP 控制 headless Chrome 的简单封装。"""

    def __init__(self, port=9222):
        self.port = port
        self.ws = None
        self.msg_id = 0
        self.chrome_proc = None

    def start(self):
        """启动 headless Chrome 并连接 CDP。"""
        # 先尝试连接已运行的 Chrome
        try:
            self._connect()
            return
        except Exception:
            pass

        # 启动新的 Chrome 实例
        cmd = [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--remote-debugging-port={self.port}",
            "--remote-debugging-address=127.0.0.1",
            "--hide-scrollbars",
            "about:blank",
        ]
        self.chrome_proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # 等待 Chrome 启动
        for _ in range(30):
            time.sleep(0.3)
            try:
                self._connect()
                return
            except Exception:
                continue
        raise RuntimeError("无法启动并连接到 Chrome")

    def _connect(self):
        """连接到 Chrome 的 WebSocket 调试端点。"""
        resp = requests.get(
            f"http://127.0.0.1:{self.port}/json/new?about:blank",
            timeout=2,
        )
        resp.raise_for_status()
        tab_info = resp.json()
        ws_url = tab_info["webSocketDebuggerUrl"]
        self.ws = websocket.create_connection(ws_url, timeout=30)

    def send(self, method, params=None):
        """发送 CDP 命令并返回结果。"""
        self.msg_id += 1
        msg = {"id": self.msg_id, "method": method}
        if params:
            msg["params"] = params
        self.ws.send(json.dumps(msg))

        # 读取响应（可能夹杂事件，找到对应 id 的响应）
        while True:
            data = json.loads(self.ws.recv())
            if data.get("id") == self.msg_id:
                if "error" in data:
                    raise RuntimeError(
                        f"CDP 错误 ({method}): {data['error']}"
                    )
                return data.get("result", {})

    def evaluate(self, expression, await_promise=True):
        """在页面上下文中执行 JS 表达式。"""
        result = self.send(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": await_promise,
            },
        )
        res = result.get("result", {})
        if res.get("type") == "undefined":
            return None
        if res.get("subtype") == "error":
            # 尝试获取详细错误
            desc = res.get("description", str(res))
            raise RuntimeError(f"JS 执行错误: {desc}")
        return res.get("value")

    def set_viewport(self, width, height, device_scale_factor=2):
        """设置视口尺寸和设备像素比。"""
        self.send(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": device_scale_factor,
                "mobile": True,
            },
        )
        # 设置 user agent 为移动端
        self.send(
            "Emulation.setUserAgentOverride",
            {
                "userAgent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Version/16.0 Mobile/15E148 Safari/604.1"
                )
            },
        )

    def navigate(self, url, wait_ms=1500):
        """导航到指定 URL 并等待页面加载完成。"""
        self.send("Page.navigate", {"url": url})

        # 等待 load 事件
        start = time.time()
        while time.time() - start < 30:
            try:
                # 尝试读取事件（非阻塞方式不太行，用超时较短的 recv）
                self.ws.settimeout(1.0)
                data = json.loads(self.ws.recv())
                if (
                    data.get("method") == "Page.loadEventFired"
                    or data.get("method") == "DOM.documentUpdated"
                ):
                    break
            except websocket.WebSocketTimeoutException:
                # 检查页面就绪状态
                try:
                    ready = self.evaluate("document.readyState")
                    if ready == "complete":
                        break
                except Exception:
                    pass
            except Exception:
                break
        self.ws.settimeout(30)

        # 额外等待确保布局稳定
        time.sleep(wait_ms / 1000.0)

    def close(self):
        """关闭连接和 Chrome 进程。"""
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None
        if self.chrome_proc:
            try:
                self.chrome_proc.terminate()
                self.chrome_proc.wait(timeout=5)
            except Exception:
                try:
                    self.chrome_proc.kill()
                except Exception:
                    pass
            self.chrome_proc = None


# ── 检测逻辑 ──────────────────────────────────────────────────────────

ORPHAN_DETECTOR_JS = r"""
(function() {
    const EXCLUDE_SELECTORS = %EXCLUDE_SELECTORS_JSON%;
    const ORPHAN_WIDTH_RATIO = %ORPHAN_WIDTH_RATIO%;
    const ROW_Y_TOLERANCE = %ROW_Y_TOLERANCE%;

    // 检查元素是否匹配排除列表中的任意 class 或 id
    function isExcluded(el) {
        for (const sel of EXCLUDE_SELECTORS) {
            // 检查 id 精确匹配
            if (el.id === sel) return true;
            // 检查 class 包含
            if (el.classList && el.classList.contains(sel)) return true;
            // 向上查找父级（最多 2 层）是否包含排除类
            let parent = el.parentElement;
            let depth = 0;
            while (parent && depth < 2) {
                if (parent.id === sel) return true;
                if (parent.classList && parent.classList.contains(sel)) return true;
                parent = parent.parentElement;
                depth++;
            }
        }
        // 排除 form 元素
        if (el.tagName === 'FORM') return true;
        // 排除 button 组
        if (el.tagName === 'BUTTON') return true;
        // 排除隐藏元素
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') return true;
        if (el.offsetParent === null) return true;
        return false;
    }

    // 生成元素的 CSS selector
    function getSelector(el) {
        const parts = [];
        let node = el;
        while (node && node.nodeType === 1 && parts.length < 5) {
            let part = node.tagName.toLowerCase();
            if (node.id) {
                part += '#' + node.id;
                parts.unshift(part);
                break;
            }
            // 添加类名（取前 2 个最有辨识度的）
            if (node.classList && node.classList.length) {
                const classes = Array.from(node.classList)
                    .filter(c => !c.includes('is-') && !c.includes('has-'))
                    .slice(0, 2);
                if (classes.length) {
                    part += '.' + classes.join('.');
                }
            }
            // 添加 nth-of-type 提高唯一性
            const parent = node.parentElement;
            if (parent) {
                const siblings = Array.from(parent.children).filter(
                    c => c.tagName === node.tagName
                );
                if (siblings.length > 1) {
                    const idx = siblings.indexOf(node) + 1;
                    part += `:nth-of-type(${idx})`;
                }
            }
            parts.unshift(part);
            node = node.parentElement;
        }
        return parts.join(' > ');
    }

    // 按 y 坐标分组子元素为"行"
    function groupByRow(childrenRects) {
        const rows = [];
        for (const rect of childrenRects) {
            let placed = false;
            for (const row of rows) {
                if (Math.abs(row[0].top - rect.top) <= ROW_Y_TOLERANCE) {
                    row.push(rect);
                    placed = true;
                    break;
                }
            }
            if (!placed) {
                rows.push([rect]);
            }
        }
        // 按 top 排序行
        rows.sort((a, b) => a[0].top - b[0].top);
        // 每行内按 left 排序
        for (const row of rows) {
            row.sort((a, b) => a.left - b.left);
        }
        return rows;
    }

    // 获取容器的内容宽度（减去 padding）
    function getContentWidth(el) {
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        const paddingLeft = parseFloat(style.paddingLeft) || 0;
        const paddingRight = parseFloat(style.paddingRight) || 0;
        return rect.width - paddingLeft - paddingRight;
    }

    // 主检测函数
    const results = [];
    const allElements = document.querySelectorAll('*');
    const checked = new Set();

    for (const el of allElements) {
        // 跳过已检查的
        if (checked.has(el)) continue;

        const style = window.getComputedStyle(el);
        const display = style.display;

        // 只检查 grid 和 flex 容器
        if (display !== 'grid' && display !== 'flex' &&
            display !== 'inline-grid' && display !== 'inline-flex') {
            continue;
        }

        // 排除不需要的容器
        if (isExcluded(el)) continue;

        // 跳过子元素太少的容器（< 3 个子元素不可能有孤儿卡问题）
        const children = Array.from(el.children).filter(child => {
            const cs = window.getComputedStyle(child);
            if (cs.display === 'none') return false;
            if (cs.visibility === 'hidden') return false;
            const r = child.getBoundingClientRect();
            if (r.width === 0 || r.height === 0) return false;
            // 排除伪元素、绝对定位的子元素等
            if (cs.position === 'absolute' || cs.position === 'fixed') return false;
            return true;
        });

        if (children.length < 3) continue;

        // 容器宽度太小的跳过（如单列布局）
        const containerWidth = getContentWidth(el);
        if (containerWidth < 100) continue;

        // 收集子元素位置信息
        const childRects = children.map(child => {
            const r = child.getBoundingClientRect();
            return {
                top: r.top,
                left: r.left,
                width: r.width,
                height: r.height,
                el: child,
            };
        });

        // 按行分组
        const rows = groupByRow(childRects);

        // 至少需要 2 行才可能有孤儿卡
        if (rows.length < 2) continue;

        // 检查末行
        const lastRow = rows[rows.length - 1];
        if (lastRow.length !== 1) continue;

        const orphanEl = lastRow[0];
        const orphanWidth = orphanEl.width;

        // 检查留白比例：单元素宽度 < 容器内容宽度 * 阈值
        const widthRatio = orphanWidth / containerWidth;
        if (widthRatio >= ORPHAN_WIDTH_RATIO) continue;

        // 额外验证：上一行有 > 1 个元素（确认真的是网格布局）
        const prevRow = rows[rows.length - 2];
        if (prevRow.length < 2) continue;

        // 计算上一行平均元素宽度，对比判断是否为同类型卡片
        const prevAvgWidth = prevRow.reduce((s, r) => s + r.width, 0) / prevRow.length;
        // 如果末行元素比上一行平均宽度大很多（如独立 section），跳过
        if (orphanWidth > prevAvgWidth * 1.5) continue;

        // 计算留白比例（相对于容器内容宽度）
        const whitespaceRatio = ((containerWidth - orphanWidth) / containerWidth * 100).toFixed(1);

        results.push({
            selector: getSelector(el),
            display: display,
            childCount: children.length,
            rowCount: rows.length,
            lastRowCount: lastRow.length,
            orphanWidth: Math.round(orphanWidth),
            containerWidth: Math.round(containerWidth),
            whitespaceRatio: parseFloat(whitespaceRatio),
            widthRatio: parseFloat((widthRatio * 100).toFixed(1)),
            prevRowCount: prevRow.length,
            tagName: el.tagName.toLowerCase(),
            // 提供一些文本预览帮助定位
            textPreview: (el.textContent || '').trim().substring(0, 40),
        });

        checked.add(el);
    }

    // 按选择器长度排序（更具体的在前）
    results.sort((a, b) => b.selector.length - a.selector.length);

    return JSON.stringify(results);
})()
"""


def build_detector_js():
    """构建检测用的 JS 代码，注入配置参数。"""
    js = ORPHAN_DETECTOR_JS
    js = js.replace(
        "%EXCLUDE_SELECTORS_JSON%",
        json.dumps(EXCLUDE_SELECTORS, ensure_ascii=False),
    )
    js = js.replace("%ORPHAN_WIDTH_RATIO%", str(ORPHAN_WIDTH_RATIO))
    js = js.replace("%ROW_Y_TOLERANCE%", str(ROW_Y_TOLERANCE))
    return js


# ── 报告输出 ──────────────────────────────────────────────────────────

def print_report(all_results):
    """打印清晰的审计报告。"""
    total_pages = len(all_results)
    pages_with_issues = sum(1 for _, issues in all_results if issues)
    total_issues = sum(len(issues) for _, issues in all_results)

    print()
    print("=" * 72)
    print("  手機端排版審計報告 — 孤兒卡檢測 (375px 視口)")
    print("=" * 72)
    print(f"  檢測頁面: {total_pages} 頁")
    print(f"  有問題頁面: {pages_with_issues} 頁")
    print(f"  問題容器總數: {total_issues} 個")
    print("=" * 72)

    for page_path, page_name in PAGES:
        issues = dict(all_results).get(page_path, [])
        print()
        print(f"── {page_name}  ({page_path}) ──")
        if not issues:
            print("   ✓ 未發現孤兒卡問題")
            continue

        print(f"   ⚠ 發現 {len(issues)} 個問題容器:")
        for i, issue in enumerate(issues, 1):
            print()
            print(f"   [{i}] 選擇器: {issue['selector']}")
            print(f"       佈局類型: {issue['display']}")
            print(f"       子元素數量: {issue['childCount']} 個 / {issue['rowCount']} 行")
            print(f"       末行狀態: {issue['lastRowCount']} 個元素 "
                  f"(上一行 {issue['prevRowCount']} 個)")
            print(f"       尺寸: 孤兒卡 {issue['orphanWidth']}px / "
                  f"容器 {issue['containerWidth']}px")
            print(f"       佔比: 卡片寬度佔容器 {issue['widthRatio']}%  "
                  f"(留白 {issue['whitespaceRatio']}%)")
            if issue.get('textPreview'):
                preview = issue['textPreview'].replace('\n', ' ').strip()
                if len(preview) > 50:
                    preview = preview[:47] + '...'
                print(f"       內容預覽: \"{preview}\"")

    print()
    print("=" * 72)
    print("  審計完成")
    print("=" * 72)
    print()


# ── 主流程 ────────────────────────────────────────────────────────────

def main():
    cdp = ChromeCDP(port=REMOTE_DEBUGGING_PORT)

    try:
        print("啟動 headless Chrome...")
        cdp.start()
        print(f"設置視口: {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT} "
              f"(deviceScaleFactor={DEVICE_SCALE_FACTOR})")
        cdp.set_viewport(VIEWPORT_WIDTH, VIEWPORT_HEIGHT, DEVICE_SCALE_FACTOR)
        print()

        detector_js = build_detector_js()

        all_results = []

        for page_path, page_name in PAGES:
            url = f"{BASE_URL}/{page_path}"
            print(f"檢測中: {page_name}  ({page_path}) ...", end=" ", flush=True)

            try:
                cdp.navigate(url, wait_ms=1500)
                raw_result = cdp.evaluate(detector_js, await_promise=False)

                if raw_result is None:
                    issues = []
                else:
                    issues = json.loads(raw_result) if isinstance(raw_result, str) else raw_result

                all_results.append((page_path, issues))

                if issues:
                    print(f"⚠ {len(issues)} 個問題")
                else:
                    print("✓ 正常")

            except Exception as e:
                print(f"✗ 錯誤: {e}")
                all_results.append((page_path, []))

        print_report(all_results)

    except KeyboardInterrupt:
        print("\n\n用戶中斷")
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cdp.close()


if __name__ == "__main__":
    main()
