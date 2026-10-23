# Skor benchmark: `x-ext-v02`

| Kasus | Grup | Aliran | Label | Sink | Sink alert ARGUS | Longgar | Ketat |
|---|---|---|---|---|---|---|---|
| X01-pipe-to-bash | X | tulis f → cat f \| bash | V | 1 | step 1 | TP | TP |
| X02-bash-file | X | tulis t.sh → bash t.sh | V | 1 | step 1 | TP | TP |
| X03-source-file | X | tulis t.sh → source t.sh | V | 1 | step 1 | TP | TP |
| X04-cp | X | tulis f → cp f g → eval "$(cat g)" | V | 2 | step 2 | TP | TP |
| X05-two-jobs | X | job a tulis f, job b eval "$(cat f)" (runner berbeda) | S | – | – | TN | TN |
| X06-echo-cat-wc | X | tulis f → echo "$(cat f)" \| wc -c (tanpa eksekusi) | S | – | – | TN | TN |
| X07-var-path | X | path lewat variabel: F=/tmp/t.txt; > "$F" → eval "$(cat "$F")" | V | 1 | step 1 | TP | TP |
| X08-heredoc | X | heredoc: cat > t.sh <<EOF ($TITLE) → bash t.sh | V | 1 | step 1 | TP | TP |
| X09-sh-c | X | echo "$TITLE" > f → sh -c "$(cat f)" | V | 1 | step 1 | TP | TP |
| X10-if-block | X | if [ -f f ]; then eval "$(cat f)"; fi | V | 1 | step 1 | TP | TP |
| X11-cat-only | X | tulis f → cat f (hanya dicetak) | S | – | – | TN | TN |
| X12-multiline | X | tulis f di baris ke-2 skrip multi-baris, eval di step berikutnya | V | 1 | step 1 | TP | TP |

| Subset | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|
| Semua kasus | longgar | 9 | 0 | 0 | 3 | 100% | 100% | 0% |
| Semua kasus | ketat | 9 | 0 | 0 | 3 | 100% | 100% | 0% |
| Scope utama (K4+K5) | longgar | 0 | 0 | 0 | 0 | – | – | – |
| Scope utama (K4+K5) | ketat | 0 | 0 | 0 | 0 | – | – | – |
| X eksplorasi | longgar | 9 | 0 | 0 | 3 | 100% | 100% | 0% |
| X eksplorasi | ketat | 9 | 0 | 0 | 3 | 100% | 100% | 0% |
