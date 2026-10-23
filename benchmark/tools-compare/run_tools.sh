#!/usr/bin/env bash
# Jalankan tool pembanding (zizmor, poutine, CodeQL Actions, CodeQL JavaScript) pada benchmark v3 terkunci.
# Output mentah: results/tools/<tool>/<kasus>.(json|sarif); versi tool: results/tools/VERSIONS.txt
# Pakai: tools-compare/run_tools.sh [set]   (run from benchmark/; set: kosong = benchmark v3, x, p)
set -u
B=$(cd "$(dirname "$0")/.." && pwd); T=${TOOLS_DIR:-$B/../tools}; SET=${1:-}
TC=test-cases${SET:+-$SET}; O=$B/results/tools${SET:+-$SET}
cd "$B" && sha256sum -c --quiet LOCK.sha256 || { echo "benchmark berubah, berhenti"; exit 1; }
ZZ=${ZIZMOR:-$(command -v zizmor)}; PT=$T/poutine/poutine; CQA=$T/cq-actions/codeql/codeql; CQJ=$T/cq-js/codeql/codeql
mkdir -p $O/zizmor $O/poutine $O/codeql-actions $O/codeql-js; W=$(mktemp -d)
{ $ZZ --version; $PT version | head -1; $CQA version | head -1; } > $O/VERSIONS.txt 2>/dev/null
for d in $TC/*/; do c=$(basename $d); echo "== $c"
  $ZZ --persona=auditor --offline --format=json $d > $O/zizmor/$c.json 2>/dev/null
  $PT analyze_local $d --format json > $O/poutine/$c.json 2>/dev/null
  rm -rf $W/db; $CQA database create $W/db --language=actions --source-root=$d -q >/dev/null 2>&1
  $CQA database analyze $W/db codeql/actions-queries:codeql-suites/actions-all.qls --format=sarif-latest --output=$O/codeql-actions/$c.sarif -q >/dev/null 2>&1
done
# CodeQL JS hanya relevan untuk source JS Action (K1-V3/V4, K2, K3, K5): dianalisis per Action
[ -z "$SET" ] && for d in actions/*/; do a=$(basename $d); echo "== action $a"
  rm -rf $W/db; $CQJ database create $W/db --language=javascript --source-root=$d -q >/dev/null 2>&1
  $CQJ database analyze $W/db codeql/javascript-queries:codeql-suites/javascript-security-extended.qls --format=sarif-latest --output=$O/codeql-js/$a.sarif -q >/dev/null 2>&1
done
rm -rf $W; echo selesai
