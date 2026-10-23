# Skor benchmark: `abl-js`

| Kasus | Grup | Aliran | Label | Sink | Sink alert ARGUS | Longgar | Ketat |
|---|---|---|---|---|---|---|---|
| K3-V1-selffile-sync | K3 | writeFileSync → readFileSync → execSync (satu Action) | V | 0 | step 0 | TP | TP |
| K3-S1-selffile-sync-nosink | K3 | writeFileSync → readFileSync → console.log | S | – | – | TN | TN |
| K3-V2-selffile-async | K3 | writeFile → readFile → exec (satu Action) | V | 0 | step 0 | TP | TP |
| K3-S2-selffile-async-nosink | K3 | writeFile → readFile → console.log | S | – | – | TN | TN |
| K5-V1-jsfile | K5 | JS Action fs.writeFile → eval "$(cat f)" | V | 1 | – | FN | FN |
| K5-S1-jsfile-nosink | K5 | JS Action fs.writeFile → wc -c f | S | – | – | TN | TN |
| K5-V2-jsfile-sync | K5 | JS Action fs.writeFileSync → eval "$(cat f)" | V | 1 | – | FN | FN |
| K5-S2-jsfile-sync-nosink | K5 | JS Action fs.writeFileSync → wc -c f | S | – | – | TN | TN |

| Subset | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|
| Semua kasus | longgar | 2 | 2 | 0 | 4 | 50% | 100% | 0% |
| Semua kasus | ketat | 2 | 2 | 0 | 4 | 50% | 100% | 0% |
| Scope utama (K4+K5) | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| Scope utama (K4+K5) | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K1 kontrol tanpa file | longgar | 0 | 0 | 0 | 0 | – | – | – |
| K1 kontrol tanpa file | ketat | 0 | 0 | 0 | 0 | – | – | – |
| K2 lintas modul JS | longgar | 0 | 0 | 0 | 0 | – | – | – |
| K2 lintas modul JS | ketat | 0 | 0 | 0 | 0 | – | – | – |
| K3 file dalam satu JS Action | longgar | 2 | 0 | 0 | 2 | 100% | 100% | 0% |
| K3 file dalam satu JS Action | ketat | 2 | 0 | 0 | 2 | 100% | 100% | 0% |
| K4 file antar-step shell | longgar | 0 | 0 | 0 | 0 | – | – | – |
| K4 file antar-step shell | ketat | 0 | 0 | 0 | 0 | – | – | – |
| K5 JS Action → file → shell | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 JS Action → file → shell | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
