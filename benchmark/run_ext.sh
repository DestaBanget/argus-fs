#!/bin/bash
# Run the file-state extension (this repo) on the locked v3 benchmark.
# Pakai: ./run_ext.sh            (semua konfigurasi di bawah, ±2 jam)
#        ./run_ext.sh ext-all    (satu konfigurasi)
B=$(cd "$(dirname "$0")" && pwd)
run(){ ARGUS_DIR=$B/.. ARGUS_FS="$2" $B/run_all.sh "$1" "${3:-}" > /dev/null 2>&1; echo "$1 selesai: $(tail -n +2 $B/logs/$1/_terminal.log | grep -c 'exit=') kasus"; }
declare -A CFG=(
  [ext-all]="all|"                                       # ekstensi penuh: shell, eventpath, js
  [ext-off]="|"                                          # kode ekstensi, semua flag mati: harus = ARGUS asli (uji regresi)
  [abl-shell]="shell|^(K4|K5)"                           # ablasi: hanya file-state shell
  [abl-js]="js|^(K3|K5)"                                 # ablasi: hanya perubahan JS
  [abl-envexec]="all,envexec|^(K1-(V1|S1|V2|S2|V5)|K4)"  # ablasi: + $VAR tainted di dalam eval
)
ORDER=(ext-all ext-off abl-shell abl-js abl-envexec)
[ -n "${1:-}" ] && ORDER=("$1")
for l in "${ORDER[@]}"; do IFS='|' read -r fs pat <<<"${CFG[$l]}"; run "$l" "$fs" "$pat"; done
