# Skor tool pembanding (set X)

Versi: zizmor 1.30.1 · Version: 1.1.6 · CodeQL command-line toolchain release 2.27.1.

Sel = skor ketat (step sink alert). Hanya aturan kelas injeksi yang dihitung.

| Kasus | Label | Sink | zizmor | poutine | codeql-actions |
|---|---|---|---|---|---|
| X01-pipe-to-bash | V | 1 | FN | FN | FN |
| X02-bash-file | V | 1 | FN | FN | FN |
| X03-source-file | V | 1 | FN | FN | FN |
| X04-cp | V | 2 | FN | FN | FN |
| X05-two-jobs | S | – | TN | TN | TN |
| X06-echo-cat-wc | S | – | TN | TN | TN |
| X07-var-path | V | 1 | FN | FN | FN |
| X08-heredoc | V | 1 | FN | FN | FN |
| X09-sh-c | V | 1 | FN | FN | FN |
| X10-if-block | V | 1 | FN | FN | FN |
| X11-cat-only | S | – | TN | TN | TN |
| X12-multiline | V | 1 | FN | FN | FN |

| Subset | Tool | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|---|
| Semua kasus | zizmor | longgar | 0 | 9 | 0 | 3 | 0% | – | 0% |
| Semua kasus | zizmor | ketat | 0 | 9 | 0 | 3 | 0% | – | 0% |
| Semua kasus | poutine | longgar | 0 | 9 | 0 | 3 | 0% | – | 0% |
| Semua kasus | poutine | ketat | 0 | 9 | 0 | 3 | 0% | – | 0% |
| Semua kasus | codeql-actions | longgar | 0 | 9 | 0 | 3 | 0% | – | 0% |
| Semua kasus | codeql-actions | ketat | 0 | 9 | 0 | 3 | 0% | – | 0% |

## Semua temuan mentah (aturan, step)

- **X01-pipe-to-bash**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X02-bash-file**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X03-source-file**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X04-cp**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X05-two-jobs**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X06-echo-cat-wc**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X07-var-path**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X08-heredoc**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X09-sh-c**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X10-if-block**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X11-cat-only**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **X12-multiline**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
