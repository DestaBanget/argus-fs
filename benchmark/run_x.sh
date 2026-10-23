#!/bin/bash
# Set uji eksplorasi (test-cases-x/, bukan benchmark terkunci). Pakai: ./run_x.sh <label> [ARGUS_DIR] [ARGUS_FS]
set -u; L=${1:?label}; B=$(cd "$(dirname "$0")" && pwd); A=$(cd "${2:-$B/..}" && pwd); FS=${3:-}
mkdir -p $B/results/$L $B/logs/$L
{
echo "== run $L (set X)  mulai $(date '+%F %T %Z')  ARGUS dir $A ($(git -C $A rev-parse --abbrev-ref HEAD) $(git -C $A rev-parse --short HEAD))  ARGUS_FS='$FS'"
for d in $B/test-cases-x/*/; do c=$(basename $d)
  rm -f $A/results/test-cases-x#$c#*.sarif
  (cd $A && docker compose run --rm -T -e ARGUS_FS="$FS" argus --mode repo --url /test-cases-x/$c --branch master </dev/null) > $B/logs/$L/$c.log 2>&1
  printf '%-22s exit=%s  ALERT RAISED x%s\n' $c $? $(grep -c "ALERT RAISED" $B/logs/$L/$c.log)
  mv $A/results/test-cases-x#$c#*.sarif $B/results/$L/ 2>/dev/null || echo "    (tidak ada SARIF)"
done
echo; SET=x python3 $B/score.py $L
} 2>&1 | tee $B/logs/$L/_terminal.log
