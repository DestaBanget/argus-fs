# Skor tool pembanding (set P)

Versi: zizmor 1.30.1 · Version: 1.1.6 · CodeQL command-line toolchain release 2.27.1.

Sel = skor ketat (step sink alert). Hanya aturan kelas injeksi yang dihitung.

| Kasus | Label | Sink | zizmor | poutine | codeql-actions |
|---|---|---|---|---|---|
| P01-checkout-file-env | V | 2 | TP (step 1,2) | FN | TP (step 1,2) |
| P02-checkout-const-file | S | – | FP (step 2,3) | TN | FP (step 2,3) |
| P03-written-file-env | V | 2 | TP (step 1,2) | FN | FN |
| P04-eventpath-same-step | V | 1 | TP (step 0,1) | FN | TP (step 0,1) |
| P05-eventpath-file | V | 2 | TP (step 1,2) | FN | FN |
| P06-written-file-eval | V | 1 | FN | FN | FN |

| Subset | Tool | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|---|
| Semua kasus | zizmor | longgar | 4 | 1 | 1 | 0 | 80% | 80% | 100% |
| Semua kasus | zizmor | ketat | 4 | 1 | 1 | 0 | 80% | 80% | 100% |
| Semua kasus | poutine | longgar | 0 | 5 | 0 | 1 | 0% | – | 0% |
| Semua kasus | poutine | ketat | 0 | 5 | 0 | 1 | 0% | – | 0% |
| Semua kasus | codeql-actions | longgar | 2 | 3 | 1 | 0 | 40% | 67% | 100% |
| Semua kasus | codeql-actions | ketat | 2 | 3 | 1 | 0 | 40% | 67% | 100% |

## Semua temuan mentah (aturan, step)

- **P01-checkout-file-env**: zizmor: artipacked@0, excessive-permissions@None, dangerous-triggers@None, template-injection@2, template-injection@2, template-injection@2, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, github-env@1, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: actions/envvar-injection/critical@1, actions/code-injection/critical@2, actions/untrusted-checkout/high@0, actions/output-clobbering/high@1
- **P02-checkout-const-file**: zizmor: artipacked@0, excessive-permissions@None, dangerous-triggers@None, template-injection@3, template-injection@3, template-injection@3, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, github-env@2, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: actions/envvar-injection/critical@2, actions/code-injection/critical@3, actions/untrusted-checkout/high@0, actions/output-clobbering/high@2
- **P03-written-file-env**: zizmor: excessive-permissions@None, dangerous-triggers@None, template-injection@2, template-injection@2, template-injection@2, undocumented-permissions@None, github-env@1, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **P04-eventpath-same-step**: zizmor: excessive-permissions@None, dangerous-triggers@None, template-injection@1, template-injection@1, template-injection@1, undocumented-permissions@None, github-env@0, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: actions/envvar-injection/critical@0, actions/code-injection/critical@1, actions/output-clobbering/high@0
- **P05-eventpath-file**: zizmor: excessive-permissions@None, dangerous-triggers@None, template-injection@2, template-injection@2, template-injection@2, undocumented-permissions@None, github-env@1, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
- **P06-written-file-eval**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –
