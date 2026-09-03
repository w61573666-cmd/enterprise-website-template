#!/bin/bash
# IndexNow 自动推送脚本 - 每次部署后执行
# 读取 sitemap 全部 URL，调用 IndexNow 协议推送
# 支持 sitemapindex 格式（自动递归读取子 sitemap）

KEY="763f4d076a057089b538afed0aa7fdab"
KEY_LOCATION="https://www.hsst.hk/hsst2026indexnowkey.txt"
SITEMAP_URL="https://www.hsst.hk/sitemap.xml"
ENDPOINTS=(
  "https://api.indexnow.org/IndexNow"
  "https://www.bing.com/indexnow"
  "https://yandex.com/indexnow"
  "https://searchadvisor.naver.com/indexnow"
  "https://search.seznam.cz/indexnow"
)

# 从 sitemap 提取所有页面 URL（支持 sitemapindex 递归）
# macOS 兼容：不使用 grep -P，用 python3 提取
URLS=$(python3 -c "
import sys, re, urllib.request

def fetch_urls(sitemap_url):
    try:
        req = urllib.request.Request(sitemap_url, headers={'User-Agent': 'IndexNow-Push/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode('utf-8')
    except Exception as e:
        print(f'Error fetching {sitemap_url}: {e}', file=sys.stderr)
        return []

    locs = re.findall(r'<loc>(.*?)</loc>', content)

    # 如果是 sitemapindex，递归读取子 sitemap
    if '<sitemapindex' in content:
        urls = []
        for sub_url in locs:
            urls.extend(fetch_urls(sub_url))
        return urls
    else:
        # urlset，直接返回所有 loc
        return [u.strip() for u in locs if u.strip()]

all_urls = fetch_urls('$SITEMAP_URL')
for u in sorted(set(all_urls)):
    print(u)
")

URL_COUNT=$(echo "$URLS" | wc -l | tr -d ' ')
echo "📋 Found $URL_COUNT URLs in sitemap"

if [ "$URL_COUNT" -eq 0 ]; then
  echo "❌ No URLs found, aborting."
  exit 1
fi

# 构建 JSON payload
PAYLOAD=$(echo "$URLS" | python3 -c "
import json, sys
urls = [l.strip() for l in sys.stdin if l.strip()]
print(json.dumps({
    'host': 'www.hsst.hk',
    'key': '$KEY',
    'keyLocation': '$KEY_LOCATION',
    'urlList': urls
}))
")

# 推送到每个端点
for endpoint in "${ENDPOINTS[@]}"; do
  echo -n "→ $endpoint: "
  HTTP_CODE=$(curl -s -o /tmp/indexnow_resp.txt -w '%{http_code}' \
    -X POST "$endpoint" \
    -H 'Content-Type: application/json' \
    -d "$PAYLOAD")
  echo "HTTP $HTTP_CODE"
  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "202" ]; then
    echo "  ✅ Success"
  else
    echo "  ❌ Failed: $(cat /tmp/indexnow_resp.txt | head -1)"
  fi
done

echo "Done!"
