# Skor benchmark: `p-ext`

| Kasus | Grup | Aliran | Label | Sink | Sink alert ARGUS | Longgar | Ketat |
|---|---|---|---|---|---|---|---|
| P01-checkout-file-env | P | checkout kode PR → CMD=$(cat config.txt) ke GITHUB_ENV → ${{ env.CMD }} | V | 2 | – | FN | FN |
| P02-checkout-const-file | P | checkout kode PR, tetapi file yang dibaca ditulis konstan oleh workflow | S | – | – | TN | TN |
| P03-written-file-env | P | env TITLE → printf > f → CMD=$(cat f) ke GITHUB_ENV → ${{ env.CMD }} | V | 2 | – | FN | FN |
| P04-eventpath-same-step | P | CMD=$(jq .pull_request.title $GITHUB_EVENT_PATH) ke GITHUB_ENV (satu step) → ${{ env.CMD }} | V | 1 | – | FN | FN |
| P05-eventpath-file | P | jq $GITHUB_EVENT_PATH > f → CMD=$(cat f) ke GITHUB_ENV → ${{ env.CMD }} | V | 2 | – | FN | FN |
| P06-written-file-eval | P | sama dengan K4-V1 (eval "$(cat f)"), sebagai jangkar | V | 1 | step 1 | TP | TP |

| Subset | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|
| Semua kasus | longgar | 1 | 4 | 0 | 1 | 20% | 100% | 0% |
| Semua kasus | ketat | 1 | 4 | 0 | 1 | 20% | 100% | 0% |
| Scope utama (K4+K5) | longgar | 0 | 0 | 0 | 0 | – | – | – |
| Scope utama (K4+K5) | ketat | 0 | 0 | 0 | 0 | – | – | – |
| P probe model file CodeQL | longgar | 1 | 4 | 0 | 1 | 20% | 100% | 0% |
| P probe model file CodeQL | ketat | 1 | 4 | 0 | 1 | 20% | 100% | 0% |
