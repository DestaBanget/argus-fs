#!/bin/bash
# Set held-out Y (test-cases-y/; jalankan ekstensi SEKALI). Pakai: ./run_y.sh <label> [ARGUS_DIR] [ARGUS_FS]
set -u; L=${1:?label}; B=$(cd "$(dirname "$0")" && pwd); A=$(cd "${2:-$B/..}" && pwd); FS=${3:-}
mkdir -p $B/results/$L $B/logs/$L
{
echo "== run $L (set Y)  mulai $(date '+%F %T %Z')  ARGUS dir $A ($(git -C $A rev-parse --abbrev-ref HEAD) $(git -C $A rev-parse --short HEAD))  ARGUS_FS='$FS'"
for d in $B/test-cases-y/*/; do c=$(basename $d)
  rm -f $A/results/test-cases-y#$c#*.sarif
  (cd $A && docker compose run --rm -T -e ARGUS_FS="$FS" argus --mode repo --url /test-cases-y/$c --branch master </dev/null) > $B/logs/$L/$c.log 2>&1
  printf '%-22s exit=%s  ALERT RAISED x%s\n' $c $? $(grep -c "ALERT RAISED" $B/logs/$L/$c.log)
  mv $A/results/test-cases-y#$c#*.sarif $B/results/$L/ 2>/dev/null || echo "    (tidak ada SARIF)"
done
echo; SET=y python3 $B/score.py $L
} 2>&1 | tee $B/logs/$L/_terminal.log
