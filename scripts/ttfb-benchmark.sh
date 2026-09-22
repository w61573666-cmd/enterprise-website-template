#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# 恆生石材官網 TTFB（首字節響應時間）測速
#
# 用法：
#   bash scripts/ttfb-benchmark.sh [標籤] [每頁取樣次數]
#     bash scripts/ttfb-benchmark.sh "Hong Kong office" 10
#     bash scripts/ttfb-benchmark.sh "GitHub Actions US runner"
#
# 輸出：JSON（含 DNS / TCP / TLS / TTFB / 總耗時 的 min / p50 / p95 / max，單位 ms）
# 依賴：curl、python3
# ---------------------------------------------------------------------------
set -u

LABEL="${1:-$(hostname 2>/dev/null || echo unknown)}"
N="${2:-7}"
SITE="https://www.hsst.hk"
URLS=(
  "/"
  "/en/"
  "/products/white-marble/arabescato-white.html"
  "/projects/hotel.html"
  "/products.html"
)

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

for u in "${URLS[@]}"; do
  for i in $(seq 1 "$N"); do
    line=$(curl -sS -o /dev/null \
      -w '%{time_namelookup} %{time_connect} %{time_appconnect} %{time_starttransfer} %{time_total} %{http_code}' \
      --max-time 20 "${SITE}${u}" 2>/dev/null)
    code=$(echo "$line" | awk '{print $NF}')
    if [ "$code" = "200" ]; then
      echo "$u $line" >> "$TMP"
    fi
  done
done

LABEL="$LABEL" SITE="$SITE" N="$N" python3 - "$TMP" <<'PYEOF'
import os, sys, json, datetime

path = sys.argv[1]
label = os.environ['LABEL']
site = os.environ['SITE']
per = int(os.environ['N'])

buckets = {}
with open(path) as fh:
    for line in fh:
        parts = line.split()
        if len(parts) < 7:
            continue
        url = parts[0]
        vals = [float(x) for x in parts[1:6]]
        buckets.setdefault(url, []).append(vals)


def stats(v):
    v = sorted(v)
    if not v:
        return {'n': 0}
    def pct(p):
        if len(v) == 1:
            return v[0]
        i = min(len(v) - 1, int(round((len(v) - 1) * p)))
        return v[i]
    return {
        'n': len(v),
        'min': round(min(v) * 1000, 1),
        'p50': round(pct(0.50) * 1000, 1),
        'p95': round(pct(0.95) * 1000, 1),
        'max': round(max(v) * 1000, 1),
    }


names = ['dns', 'tcp', 'tls', 'ttfb', 'total']
results = []
for url in ['/', '/en/', '/products/white-marble/arabescato-white.html',
            '/projects/hotel.html', '/products.html']:
    rows = buckets.get(url, [])
    timing = {}
    for idx, nm in enumerate(names):
        timing[nm] = stats([r[idx] for r in rows])
    results.append({'url': url, 'timing_ms': timing})

out = {
    'label': label,
    'site': site,
    'samples_per_url': per,
    'measured_at': datetime.datetime.now(datetime.timezone.utc)
                   .strftime('%Y-%m-%dT%H:%M:%SZ'),
    'results': results,
}
print(json.dumps(out, indent=2))
PYEOF
