#!/usr/bin/env python3
"""
IndexNow 自动推送脚本 - 每次部署后执行
读取 sitemap 全部 URL，调用 IndexNow 协议推送
macOS 兼容版本
"""

import json
import sys
import urllib.request
import urllib.error
import re

KEY = "763f4d076a057089b538afed0aa7fdab"
KEY_LOCATION = "https://www.hsst.hk/hsst2026indexnowkey.txt"
SITEMAP_URL = "https://www.hsst.hk/sitemap.xml"
ENDPOINTS = [
    "https://api.indexnow.org/IndexNow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
    "https://searchadvisor.naver.com/indexnow",
    "https://search.seznam.cz/indexnow",
]


def fetch_sitemap_urls():
    """Fetch all URLs from sitemap (including sub-sitemaps)"""
    try:
        with urllib.request.urlopen(SITEMAP_URL, timeout=30) as resp:
            content = resp.read().decode("utf-8")
    except Exception as e:
        print(f"❌ Failed to fetch sitemap: {e}")
        return []

    # Check if it's a sitemap index
    if "<sitemapindex" in content:
        # Extract sub-sitemap URLs
        sub_sitemaps = re.findall(r"<loc>([^<]+)</loc>", content)
        all_urls = []
        for sub_url in sub_sitemaps:
            print(f"  📄 Fetching sub-sitemap: {sub_url}")
            try:
                with urllib.request.urlopen(sub_url, timeout=30) as resp:
                    sub_content = resp.read().decode("utf-8")
                urls = re.findall(r"<loc>([^<]+)</loc>", sub_content)
                # Filter out sitemap URLs
                urls = [u for u in urls if "sitemap" not in u.lower()]
                all_urls.extend(urls)
            except Exception as e:
                print(f"  ⚠️  Failed to fetch sub-sitemap: {e}")
        return all_urls
    else:
        urls = re.findall(r"<loc>([^<]+)</loc>", content)
        return [u for u in urls if "sitemap" not in u.lower()]


def push_to_endpoint(endpoint, payload):
    """Push URLs to an IndexNow endpoint"""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="replace")
            return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body
    except Exception as e:
        return 0, str(e)


def main():
    print("📋 IndexNow Push Script")
    print(f"   Sitemap: {SITEMAP_URL}")
    print()

    urls = fetch_sitemap_urls()
    if not urls:
        print("❌ No URLs found in sitemap. Exiting.")
        sys.exit(1)

    urls = sorted(set(urls))
    print(f"📋 Found {len(urls)} URLs in sitemap")
    print()

    payload = {
        "host": "www.hsst.hk",
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }

    for endpoint in ENDPOINTS:
        print(f"→ {endpoint}: ", end="", flush=True)
        status, body = push_to_endpoint(endpoint, payload)
        if status in (200, 202):
            print(f"HTTP {status} ✅ Success")
        else:
            print(f"HTTP {status} ❌ Failed: {body[:200]}")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
