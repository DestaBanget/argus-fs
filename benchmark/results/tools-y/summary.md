# Skor tool pembanding (set Y)

Versi: zizmor 1.30.1 · Version: 1.1.6 · CodeQL command-line toolchain release 2.27.1.

Sel = skor ketat (step sink alert). Hanya aturan kelas injeksi yang dihitung.

| Kasus | Label | Sink | zizmor | poutine | codeql-actions |
|---|---|---|---|---|---|
| Y01-runner-temp | V | 1 | FN | FN | FN |
| Y02-built-script | V | 1 | FN | FN | FN |
| Y03-python-exec | V | 1 | FN | FN | FN |
| Y04-bash-c | V | 1 | FN | FN | FN |
| Y05-xargs-sh | V | 1 | FN | FN | FN |
| Y06-source-event-vars | V | 1 | FN | FN | FN |
| Y07-cat-copy | V | 2 | FN | FN | FN |
| Y08-headref-sh-c | V | 1 | FN | FN | FN |
| Y09-pipe-sh | V | 1 | FN | FN | FN |
| Y10-dot-source | V | 1 | FN | FN | FN |
| Y11-while-read-eval | V | 1 | FN | FN | FN |
| Y12-js-promises | V | 1 | FN | FN | FN |
| Y13-js-runner-temp | V | 1 | FN | FN | FN |
| Y14-rm-then-guard | S | – | TN | TN | TN |
| Y15-hash-eval | S | – | TN | TN | TN |
| Y16-repo-script | S | – | TN | TN | TN |
| Y17-backup-file | S | – | TN | TN | TN |
| Y18-event-number | S | – | TN | TN | TN |

| Subset | Tool | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|---|
| Semua kasus | zizmor | longgar | 0 | 13 | 0 | 5 | 0% | – | 0% |
| Semua kasus | zizmor | ketat | 0 | 13 | 0 | 5 | 0% | – | 0% |
| Semua kasus | poutine | longgar | 0 | 13 | 0 | 5 | 0% | – | 0% |
| Semua kasus | poutine | ketat | 0 | 13 | 0 | 5 | 0% | – | 0% |
| Semua kasus | codeql-actions | longgar | 0 | 13 | 0 | 5 | 0% | – | 0% |
| Semua kasus | codeql-actions | ketat | 0 | 13 | 0 | 5 | 0% | – | 0% |

## Semua temuan mentah (aturan, step)

- **Y01-runner-temp**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y02-built-script**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y03-python-exec**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y04-bash-c**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y05-xargs-sh**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y06-source-event-vars**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: actions/output-clobbering/high@0
- **Y07-cat-copy**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y08-headref-sh-c**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y09-pipe-sh**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y10-dot-source**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y11-while-read-eval**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y12-js-promises**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0
- **Y13-js-runner-temp**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0
- **Y14-rm-then-guard**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y15-hash-eval**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y16-repo-script**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y17-backup-file**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **Y18-event-number**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
