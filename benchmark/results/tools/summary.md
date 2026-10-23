# Skor tool pembanding (benchmark v3)

Versi: zizmor 1.30.1 · Version: 1.1.6 · CodeQL command-line toolchain release 2.27.1.

Sel = skor ketat (step sink alert). Hanya aturan kelas injeksi yang dihitung.

| Kasus | Label | Sink | zizmor | poutine | codeql-actions | codeql-js | codeql |
|---|---|---|---|---|---|---|---|
| K1-V1-direct | V | 0 | TP (step 0) | TP (step 0) | TP (step 0) | FN | TP (step 0) |
| K1-S1-const | S | – | FP (step 0) | TN | TN | TN | TN |
| K1-V2-envdirect | V | 0 | FN | FN | FN | FN | FN |
| K1-S2-envnosink | S | – | TN | TN | TN | TN | TN |
| K1-V3-jsoutput | V | 1 | TP (step 1) | FN | FN | FN | FN |
| K1-V4-jsenv | V | 1 | TP (step 1) | FN | FN | FN | FN |
| K1-V5-shellenv | V | 1 | TP (step 0,1) | FN | TP (step 0,1) | FN | TP (step 0,1) |
| K2-V1-crossmod | V | 0 | FN | FN | FN | TP (step 0) | TP (step 0) |
| K2-S1-crossmod-nosink | S | – | TN | TN | TN | TN | TN |
| K3-V1-selffile-sync | V | 0 | FN | FN | FN | FN | FN |
| K3-S1-selffile-sync-nosink | S | – | TN | TN | TN | TN | TN |
| K3-V2-selffile-async | V | 0 | FN | FN | FN | FN | FN |
| K3-S2-selffile-async-nosink | S | – | TN | TN | TN | TN | TN |
| K4-V1-envfile | V | 1 | FN | FN | FN | FN | FN |
| K4-S1-envfile-nosink | S | – | TN | TN | TN | TN | TN |
| K4-V2-eventfile | V | 1 | FN | FN | FN | FN | FN |
| K4-S2-eventfile-nosink | S | – | TN | TN | TN | TN | TN |
| K4-V3-append | V | 1 | FN | FN | FN | FN | FN |
| K4-S3-overwrite | S | – | TN | TN | TN | TN | TN |
| K4-S4-read-before-write | S | – | TN | TN | TN | TN | TN |
| K4-S5-otherfile | S | – | TN | TN | TN | TN | TN |
| K4-V4-tee | V | 1 | FN | FN | FN | FN | FN |
| K4-V5-redirect-read | V | 1 | FN | FN | FN | FN | FN |
| K4-V6-relpath | V | 1 | FN | FN | FN | FN | FN |
| K4-V7-workspace | V | 1 | FN | FN | FN | FN | FN |
| K4-V8-workdir | V | 2 | FN | FN | FN | FN | FN |
| K4-S6-workdir-other | S | – | TN | TN | TN | TN | TN |
| K5-V1-jsfile | V | 1 | FN | FN | FN | FN | FN |
| K5-S1-jsfile-nosink | S | – | TN | TN | TN | TN | TN |
| K5-V2-jsfile-sync | V | 1 | FN | FN | FN | FN | FN |
| K5-S2-jsfile-sync-nosink | S | – | TN | TN | TN | TN | TN |

| Subset | Tool | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|---|
| Semua kasus | zizmor | longgar | 4 | 14 | 1 | 12 | 22% | 80% | 8% |
| Semua kasus | zizmor | ketat | 4 | 14 | 1 | 12 | 22% | 80% | 8% |
| Semua kasus | poutine | longgar | 1 | 17 | 0 | 13 | 6% | 100% | 0% |
| Semua kasus | poutine | ketat | 1 | 17 | 0 | 13 | 6% | 100% | 0% |
| Semua kasus | codeql-actions | longgar | 2 | 16 | 0 | 13 | 11% | 100% | 0% |
| Semua kasus | codeql-actions | ketat | 2 | 16 | 0 | 13 | 11% | 100% | 0% |
| Semua kasus | codeql-js | longgar | 1 | 17 | 0 | 13 | 6% | 100% | 0% |
| Semua kasus | codeql-js | ketat | 1 | 17 | 0 | 13 | 6% | 100% | 0% |
| Semua kasus | codeql | longgar | 3 | 15 | 0 | 13 | 17% | 100% | 0% |
| Semua kasus | codeql | ketat | 3 | 15 | 0 | 13 | 17% | 100% | 0% |
| Scope utama (K4+K5) | zizmor | longgar | 0 | 10 | 0 | 8 | 0% | – | 0% |
| Scope utama (K4+K5) | zizmor | ketat | 0 | 10 | 0 | 8 | 0% | – | 0% |
| Scope utama (K4+K5) | poutine | longgar | 0 | 10 | 0 | 8 | 0% | – | 0% |
| Scope utama (K4+K5) | poutine | ketat | 0 | 10 | 0 | 8 | 0% | – | 0% |
| Scope utama (K4+K5) | codeql-actions | longgar | 0 | 10 | 0 | 8 | 0% | – | 0% |
| Scope utama (K4+K5) | codeql-actions | ketat | 0 | 10 | 0 | 8 | 0% | – | 0% |
| Scope utama (K4+K5) | codeql-js | longgar | 0 | 10 | 0 | 8 | 0% | – | 0% |
| Scope utama (K4+K5) | codeql-js | ketat | 0 | 10 | 0 | 8 | 0% | – | 0% |
| Scope utama (K4+K5) | codeql | longgar | 0 | 10 | 0 | 8 | 0% | – | 0% |
| Scope utama (K4+K5) | codeql | ketat | 0 | 10 | 0 | 8 | 0% | – | 0% |
| K1 | zizmor | longgar | 4 | 1 | 1 | 1 | 80% | 80% | 50% |
| K1 | zizmor | ketat | 4 | 1 | 1 | 1 | 80% | 80% | 50% |
| K1 | poutine | longgar | 1 | 4 | 0 | 2 | 20% | 100% | 0% |
| K1 | poutine | ketat | 1 | 4 | 0 | 2 | 20% | 100% | 0% |
| K1 | codeql-actions | longgar | 2 | 3 | 0 | 2 | 40% | 100% | 0% |
| K1 | codeql-actions | ketat | 2 | 3 | 0 | 2 | 40% | 100% | 0% |
| K1 | codeql-js | longgar | 0 | 5 | 0 | 2 | 0% | – | 0% |
| K1 | codeql-js | ketat | 0 | 5 | 0 | 2 | 0% | – | 0% |
| K1 | codeql | longgar | 2 | 3 | 0 | 2 | 40% | 100% | 0% |
| K1 | codeql | ketat | 2 | 3 | 0 | 2 | 40% | 100% | 0% |
| K2 | zizmor | longgar | 0 | 1 | 0 | 1 | 0% | – | 0% |
| K2 | zizmor | ketat | 0 | 1 | 0 | 1 | 0% | – | 0% |
| K2 | poutine | longgar | 0 | 1 | 0 | 1 | 0% | – | 0% |
| K2 | poutine | ketat | 0 | 1 | 0 | 1 | 0% | – | 0% |
| K2 | codeql-actions | longgar | 0 | 1 | 0 | 1 | 0% | – | 0% |
| K2 | codeql-actions | ketat | 0 | 1 | 0 | 1 | 0% | – | 0% |
| K2 | codeql-js | longgar | 1 | 0 | 0 | 1 | 100% | 100% | 0% |
| K2 | codeql-js | ketat | 1 | 0 | 0 | 1 | 100% | 100% | 0% |
| K2 | codeql | longgar | 1 | 0 | 0 | 1 | 100% | 100% | 0% |
| K2 | codeql | ketat | 1 | 0 | 0 | 1 | 100% | 100% | 0% |
| K3 | zizmor | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K3 | zizmor | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K3 | poutine | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K3 | poutine | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K3 | codeql-actions | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K3 | codeql-actions | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K3 | codeql-js | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K3 | codeql-js | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K3 | codeql | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K3 | codeql | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K4 | zizmor | longgar | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 | zizmor | ketat | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 | poutine | longgar | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 | poutine | ketat | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 | codeql-actions | longgar | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 | codeql-actions | ketat | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 | codeql-js | longgar | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 | codeql-js | ketat | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 | codeql | longgar | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K4 | codeql | ketat | 0 | 8 | 0 | 6 | 0% | – | 0% |
| K5 | zizmor | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 | zizmor | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 | poutine | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 | poutine | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 | codeql-actions | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 | codeql-actions | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 | codeql-js | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 | codeql-js | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 | codeql | longgar | 0 | 2 | 0 | 2 | 0% | – | 0% |
| K5 | codeql | ketat | 0 | 2 | 0 | 2 | 0% | – | 0% |

## Semua temuan mentah (aturan, step)

- **K1-V1-direct**: zizmor: excessive-permissions@None, dangerous-triggers@None, template-injection@0, template-injection@0, template-injection@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: injection@0; codeql-actions: actions/code-injection/critical@0; codeql-js: –
- **K1-S1-const**: zizmor: excessive-permissions@None, dangerous-triggers@None, template-injection@0, template-injection@0, template-injection@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K1-V2-envdirect**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K1-S2-envnosink**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K1-V3-jsoutput**: zizmor: excessive-permissions@None, dangerous-triggers@None, template-injection@1, template-injection@1, template-injection@1, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: –
- **K1-V4-jsenv**: zizmor: excessive-permissions@None, dangerous-triggers@None, template-injection@1, template-injection@1, template-injection@1, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: –
- **K1-V5-shellenv**: zizmor: excessive-permissions@None, dangerous-triggers@None, template-injection@1, template-injection@1, template-injection@1, undocumented-permissions@None, github-env@0, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: actions/envvar-injection/critical@0, actions/code-injection/critical@1; codeql-js: –
- **K2-V1-crossmod**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: js/indirect-command-line-injection@0
- **K2-S1-crossmod-nosink**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: –
- **K3-V1-selffile-sync**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: js/insecure-temporary-file@0
- **K3-S1-selffile-sync-nosink**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: js/insecure-temporary-file@0
- **K3-V2-selffile-async**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: js/insecure-temporary-file@0
- **K3-S2-selffile-async-nosink**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: js/insecure-temporary-file@0
- **K4-V1-envfile**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-S1-envfile-nosink**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-V2-eventfile**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-S2-eventfile-nosink**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-V3-append**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-S3-overwrite**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-S4-read-before-write**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-S5-otherfile**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-V4-tee**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-V5-redirect-read**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-V6-relpath**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-V7-workspace**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-V8-workdir**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K4-S6-workdir-other**: zizmor: excessive-permissions@None, dangerous-triggers@None, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: –; codeql-actions: –; codeql-js: –
- **K5-V1-jsfile**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: js/insecure-temporary-file@0
- **K5-S1-jsfile-nosink**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: js/insecure-temporary-file@0
- **K5-V2-jsfile-sync**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: js/insecure-temporary-file@0
- **K5-S2-jsfile-sync-nosink**: zizmor: excessive-permissions@None, dangerous-triggers@None, unpinned-uses@0, unpinned-uses@0, undocumented-permissions@None, anonymous-definition@None, concurrency-limits@None, concurrency-limits@None; poutine: github_action_from_unverified_creator_used@0; codeql-actions: actions/unpinned-tag@0; codeql-js: js/insecure-temporary-file@0
