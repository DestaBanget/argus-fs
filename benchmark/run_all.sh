#!/bin/bash
# Pakai: ./run_all.sh <label> [pola]
#   Jalankan ARGUS pada semua kasus di test-cases/ (atau yang namanya cocok dengan regex pola, mis. "^K(1|4)"),
#   simpan SARIF ke results/<label>/, log mentah per kasus ke logs/<label>/<kasus>.log,
#   dan output terminal lengkap ke logs/<label>/_terminal.log. Lalu cetak skor (score.py).
# Variabel opsional:
#   ARGUS_DIR=<path>         use another ARGUS checkout (default: this repo, the parent of benchmark/)
#   ARGUS_FS=all             file-state extension flags (empty = original ARGUS behaviour)
set -u; L=${1:?label}; P=${2:-}; B=$(cd "$(dirname "$0")" && pwd); A=$(cd "${ARGUS_DIR:-$B/..}" && pwd); FS=${ARGUS_FS:-}
mkdir -p $B/results/$L $B/logs/$L
python3 $B/make_benchmark.py --verify || { echo "Benchmark berubah dari LOCK.sha256, batal"; exit 1; }
{
echo "== run $L  mulai $(date '+%F %T %Z')"
echo "ARGUS dir    : $A  (branch $(git -C $A rev-parse --abbrev-ref HEAD))"
echo "ARGUS commit : $(git -C $A rev-parse HEAD)"
echo "ARGUS_FS     : '${FS}'"
echo "Perubahan lokal ARGUS:"; git -C $A diff --stat | sed 's/^/  /'
echo "LOCK.sha256  : $(sha256sum $B/LOCK.sha256 | cut -c1-16)"
for d in $B/test-cases/*/; do c=$(basename $d); [[ -z "$P" || $c =~ $P ]] || continue
  rm -f $A/results/test-cases#$c#*.sarif
  t0=$(date +%s)
  (cd $A && docker compose run --rm -T -e ARGUS_FS="$FS" argus --mode repo --url /test-cases/$c --branch master </dev/null) > $B/logs/$L/$c.log 2>&1
  rc=$?
  n=$(grep -c "ALERT RAISED" $B/logs/$L/$c.log)
  printf '%-30s exit=%s  %4ss  ALERT RAISED x%s\n' $c $rc $(( $(date +%s) - t0 )) $n
  grep "ALERT RAISED" $B/logs/$L/$c.log | sed 's/\x1b\[[0-9;]*m//g; s/^/    /'
  mv $A/results/test-cases#$c#*.sarif $B/results/$L/ 2>/dev/null || echo "    (tidak ada SARIF)"
done
echo "== selesai $(date '+%F %T %Z')"
echo
python3 $B/score.py $L
} 2>&1 | tee $B/logs/$L/_terminal.log
