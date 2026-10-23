# Skor benchmark: `abl-shell`

| Kasus | Grup | Aliran | Label | Sink | Sink alert ARGUS | Longgar | Ketat |
|---|---|---|---|---|---|---|---|
| K4-V1-envfile | K4 | env → printf > f → eval "$(cat f)" | V | 1 | step 1 | TP | TP |
| K4-S1-envfile-nosink | K4 | env → printf > f → wc -c f | S | – | – | TN | TN |
| K4-V2-eventfile | K4 | jq $GITHUB_EVENT_PATH > f → eval "$(cat f)" | V | 1 | – | FN | FN |
| K4-S2-eventfile-nosink | K4 | jq $GITHUB_EVENT_PATH > f → wc -c f | S | – | – | TN | TN |
| K4-V3-append | K4 | env → printf >> f (append) → eval | V | 1 | step 1 | TP | TP |
| K4-S3-overwrite | K4 | env → f, lalu f ditimpa konstanta → eval | S | – | – | TN | TN |
| K4-S4-read-before-write | K4 | eval "$(cat f)" dijalankan sebelum f ditulis | S | – | – | TN | TN |
| K4-S5-otherfile | K4 | tainted ke a.txt, eval membaca b.txt (konstan) | S | – | – | TN | TN |
| K4-V4-tee | K4 | env → printf \| tee f → eval | V | 1 | step 1 | TP | TP |
| K4-V5-redirect-read | K4 | env → printf > f → eval "$(< f)" | V | 1 | step 1 | TP | TP |
| K4-V6-relpath | K4 | tulis t.txt, baca ./t.txt (path relatif) | V | 1 | step 1 | TP | TP |
| K4-V7-workspace | K4 | tulis $GITHUB_WORKSPACE/t.txt, baca ./t.txt | V | 1 | step 1 | TP | TP |
| K4-V8-workdir | K4 | working-directory: sub tulis t.txt, baca sub/t.txt | V | 2 | step 2 | TP | TP |
| K4-S6-workdir-other | K4 | working-directory: sub tulis t.txt, baca ./t.txt (file lain, konstan) | S | – | – | TN | TN |
| K5-V1-jsfile | K5 | JS Action fs.writeFile → eval "$(cat f)" | V | 1 | step 0 | TP | FN (lokasi salah) |
| K5-S1-jsfile-nosink | K5 | JS Action fs.writeFile → wc -c f | S | – | step 0 | FP | FP |
| K5-V2-jsfile-sync | K5 | JS Action fs.writeFileSync → eval "$(cat f)" | V | 1 | – | FN | FN |
| K5-S2-jsfile-sync-nosink | K5 | JS Action fs.writeFileSync → wc -c f | S | – | – | TN | TN |

| Subset | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|
| Semua kasus | longgar | 8 | 2 | 1 | 7 | 80% | 89% | 12% |
| Semua kasus | ketat | 7 | 3 | 1 | 7 | 70% | 88% | 12% |
| Scope utama (K4+K5) | longgar | 8 | 2 | 1 | 7 | 80% | 89% | 12% |
| Scope utama (K4+K5) | ketat | 7 | 3 | 1 | 7 | 70% | 88% | 12% |
| K1 kontrol tanpa file | longgar | 0 | 0 | 0 | 0 | – | – | – |
| K1 kontrol tanpa file | ketat | 0 | 0 | 0 | 0 | – | – | – |
| K2 lintas modul JS | longgar | 0 | 0 | 0 | 0 | – | – | – |
| K2 lintas modul JS | ketat | 0 | 0 | 0 | 0 | – | – | – |
| K3 file dalam satu JS Action | longgar | 0 | 0 | 0 | 0 | – | – | – |
| K3 file dalam satu JS Action | ketat | 0 | 0 | 0 | 0 | – | – | – |
| K4 file antar-step shell | longgar | 7 | 1 | 0 | 6 | 88% | 100% | 0% |
| K4 file antar-step shell | ketat | 7 | 1 | 0 | 6 | 88% | 100% | 0% |
| K5 JS Action → file → shell | longgar | 1 | 1 | 1 | 1 | 50% | 50% | 50% |
| K5 JS Action → file → shell | ketat | 0 | 2 | 1 | 1 | 0% | 0% | 50% |
