#!/bin/bash
# IndexNow 自动推送脚本 - 每次部署后执行
# 读取 sitemap 全部 URL，调用 IndexNow 协议推送

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

# 从 sitemap 提取所有 URL
URLS=$(curl -s "$SITEMAP_URL" | grep -oP '(?<=<loc>)[^<]+' | grep -v 'sitemap' | sort -u)
URL_COUNT=$(echo "$URLS" | wc -l)
echo "📋 Found $URL_COUNT URLs in sitemap"

# 构建 JSON payload
URL_JSON=$(echo "$URLS" | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")
PAYLOAD=$(python3 -c "
import json
print(json.dumps({
    'host': 'www.hsst.hk',
    'key': '$KEY',
    'keyLocation': '$KEY_LOCATION',
    'urlList': $URL_JSON
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
