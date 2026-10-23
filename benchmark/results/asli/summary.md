# Skor benchmark: `asli`

| Kasus | Grup | Aliran | Label | Sink | Sink alert ARGUS | Longgar | Ketat |
|---|---|---|---|---|---|---|---|
| K1-V1-direct | K1 | ${{ pr.title }} langsung di run → eval | V | 0 | step 0 | TP | TP |
| K1-S1-const | K1 | env konstan → ${{ env.CMD }} → eval | S | – | – | TN | TN |
| K1-V2-envdirect | K1 | env TITLE → eval "$TITLE" (tanpa file) | V | 0 | – | FN | FN |
| K1-S2-envnosink | K1 | env TITLE → printf \| wc -c (mitigasi resmi GitHub) | S | – | – | TN | TN |
| K1-V3-jsoutput | K1 | JS Action setOutput → ${{ steps.w.outputs.t }} → eval | V | 1 | step 1 | TP | TP |
| K1-V4-jsenv | K1 | JS Action exportVariable → ${{ env.T }} → eval | V | 1 | step 1 | TP | TP |
| K1-V5-shellenv | K1 | env TITLE → echo "T=$TITLE" >> $GITHUB_ENV → ${{ env.T }} → eval | V | 1 | – | FN | FN |
| K2-V1-crossmod | K2 | getInput → require('./helper') → execSync | V | 0 | step 0 | TP | TP |
| K2-S1-crossmod-nosink | K2 | getInput → require('./helper') → console.log | S | – | – | TN | TN |
| K3-V1-selffile-sync | K3 | writeFileSync → readFileSync → execSync (satu Action) | V | 0 | – | FN | FN |
| K3-S1-selffile-sync-nosink | K3 | writeFileSync → readFileSync → console.log | S | – | – | TN | TN |
| K3-V2-selffile-async | K3 | writeFile → readFile → exec (satu Action) | V | 0 | step 0 | TP | TP |
| K3-S2-selffile-async-nosink | K3 | writeFile → readFile → console.log | S | – | step 0 | FP | FP |
| K4-V1-envfile | K4 | env → printf > f → eval "$(cat f)" | V | 1 | – | FN | FN |
| K4-S1-envfile-nosink | K4 | env → printf > f → wc -c f | S | – | – | TN | TN |
| K4-V2-eventfile | K4 | jq $GITHUB_EVENT_PATH > f → eval "$(cat f)" | V | 1 | – | FN | FN |
| K4-S2-eventfile-nosink | K4 | jq $GITHUB_EVENT_PATH > f → wc -c f | S | – | – | TN | TN |
| K4-V3-append | K4 | env → printf >> f (append) → eval | V | 1 | – | FN | FN |
| K4-S3-overwrite | K4 | env → f, lalu f ditimpa konstanta → eval | S | – | – | TN | TN |
| K4-S4-read-before-write | K4 | eval "$(cat f)" dijalankan sebelum f ditulis | S | – | – | TN | TN |
| K4-S5-otherfile | K4 | tainted ke a.txt, eval membaca b.txt (konstan) | S | – | – | TN | TN |
| K4-V4-tee | K4 | env → printf \| tee f → eval | V | 1 | – | FN | FN |
| K4-V5-redirect-read | K4 | env → printf > f → eval "$(< f)" | V | 1 | – | FN | FN |
| K4-V6-relpath | K4 | tulis t.txt, baca ./t.txt (path relatif) | V | 1 | – | FN | FN |
| K4-V7-workspace | K4 | tulis $GITHUB_WORKSPACE/t.txt, baca ./t.txt | V | 1 | – | FN | FN |
| K4-V8-workdir | K4 | working-directory: sub tulis t.txt, baca sub/t.txt | V | 2 | – | FN | FN |
| K4-S6-workdir-other | K4 | working-directory: sub tulis t.txt, baca ./t.txt (file lain, konstan) | S | – | – | TN | TN |
| K5-V1-jsfile | K5 | JS Action fs.writeFile → eval "$(cat f)" | V | 1 | step 0 | TP | FN (lokasi salah) |
| K5-S1-jsfile-nosink | K5 | JS Action fs.writeFile → wc -c f | S | – | step 0 | FP | FP |
| K5-V2-jsfile-sync | K5 | JS Action fs.writeFileSync → eval "$(cat f)" | V | 1 | – | FN | FN |
| K5-S2-jsfile-sync-nosink | K5 | JS Action fs.writeFileSync → wc -c f | S | – | – | TN | TN |

| Subset | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|
| Semua kasus | longgar | 6 | 12 | 2 | 11 | 33% | 75% | 15% |
| Semua kasus | ketat | 5 | 13 | 2 | 11 | 28% | 71% | 15% |
| Scope utama (K4+K5) | longgar | 1 | 9 | 1 | 7 | 10% | 50% | 12% |
| Scope utama (K4+K5) | ketat | 0 | 10 | 1 | 7 | 0% | 0% | 12% |
| K1 kontrol tanpa file | longgar | 3 | 2 | 0 | 2 | 60% | 100% | 0% |
| K1 kontrol tanpa file | ketat | 3 | 2 | 0 | 2 | 60% | 100% | 0% |
| K2 lintas modul JS | longgar | 1 | 0 | 0 | 1 | 100% | 100% | 0% |
| K2 lintas modul JS | ketat | 1 | 0 | 0 | 1 | 100% | 100% | 0% |
| K3 file dalam satu JS Action | longgar | 1 | 1 | 1 | 1 | 50% | 50% | 50% |
| K3 file dalam satu JS Action | ketat | 1 | 1 | 1 | 1 | 50% | 50% | 50% |
| K4 file antar-step shell | longgar | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 file antar-step shell | ketat | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K5 JS Action → file → shell | longgar | 1 | 1 | 1 | 1 | 50% | 50% | 50% |
| K5 JS Action → file → shell | ketat | 0 | 2 | 1 | 1 | 0% | 0% | 50% |
