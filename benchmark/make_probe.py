#!/usr/bin/env python3
"""Set probe P (3 Okt 2026). BUKAN bagian benchmark terkunci.

Tujuan: membandingkan model file milik CodeQL for GitHub Actions dengan model file-state ekstensi.
CodeQL Actions (2.27.1, actions-all 0.6.2) sudah punya model file yang kasar:
  - FileSource = artifact yang diunduh / checkout kode PR (FlowSources.qll);
  - step run sesudahnya yang memuat perintah cat/</jq/yq/head/tail dianggap membaca file tainted,
    tanpa melihat path (TaintSteps.qll fileDownloadToRunStep, FlowSteps.qll commandToEnvStoreStep);
  - jq ... $GITHUB_EVENT_PATH di dalam satu step = source (GitHubEventPathSource).
Sink code injection CodeQL adalah ekspresi ${{ }}, jadi probe memakai rute file -> GITHUB_ENV -> ${{ env.CMD }}
agar kedua tool punya sink yang mereka kenal.

Label dan dugaan hasil ditulis sebelum tool dijalankan pada set ini.
Pakai: python3 make_probe.py   -> test-cases-p/ dan benchmark-p.json
"""
import json
from pathlib import Path
from make_benchmark import run, git_repo, ENV_T, W
from make_explore import to_yaml

B = Path(__file__).resolve().parent
TC = B / "test-cases-p"

CHECKOUT = {"name": "checkout", "uses": "actions/checkout@v4", "with": {"ref": "${{ github.event.pull_request.head.sha }}"}}
TO_ENV = 'echo "CMD=$(cat {f})" >> "$GITHUB_ENV"'
USE_ENV = run("${{ env.CMD }}", name="sink")

# (id, label, sink_step, deskripsi, steps, dugaan CodeQL Actions, dugaan ekstensi)
CASES = [
    ("P01-checkout-file-env", "V", 2, "checkout kode PR → CMD=$(cat config.txt) ke GITHUB_ENV → ${{ env.CMD }}",
     [CHECKOUT, run(TO_ENV.format(f="config.txt"), name="to-env"), USE_ENV],
     "TP: FileSource checkout + cat", "FN: checkout kode PR bukan source (di luar scope)"),
    ("P02-checkout-const-file", "S", None, "checkout kode PR, tetapi file yang dibaca ditulis konstan oleh workflow",
     [CHECKOUT, run("printf 'echo ok' > /tmp/c.txt", name="write"), run(TO_ENV.format(f="/tmp/c.txt"), name="to-env"), USE_ENV],
     "FP: model CodeQL tidak melihat path", "TN"),
    ("P03-written-file-env", "V", 2, "env TITLE → printf > f → CMD=$(cat f) ke GITHUB_ENV → ${{ env.CMD }}",
     [run(W, env=ENV_T, name="write"), run(TO_ENV.format(f="/tmp/t.txt"), name="to-env"), USE_ENV],
     "FN: file yang ditulis workflow bukan FileSource", "tidak pasti: file → GITHUB_ENV belum diuji"),
    ("P04-eventpath-same-step", "V", 1, "CMD=$(jq .pull_request.title $GITHUB_EVENT_PATH) ke GITHUB_ENV (satu step) → ${{ env.CMD }}",
     [run('echo "CMD=$(jq -r .pull_request.title "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"', name="to-env"), USE_ENV],
     "TP: GitHubEventPathSource", "tidak pasti: eventpath → GITHUB_ENV belum diuji"),
    ("P05-eventpath-file", "V", 2, "jq $GITHUB_EVENT_PATH > f → CMD=$(cat f) ke GITHUB_ENV → ${{ env.CMD }}",
     [run('jq -r .pull_request.title "$GITHUB_EVENT_PATH" > /tmp/t.txt', name="write"), run(TO_ENV.format(f="/tmp/t.txt"), name="to-env"), USE_ENV],
     "FN: source jq harus satu step dengan penulisan GITHUB_ENV", "tidak pasti: file → GITHUB_ENV belum diuji"),
    ("P06-written-file-eval", "V", 1, "sama dengan K4-V1 (eval \"$(cat f)\"), sebagai jangkar",
     [run(W, env=ENV_T, name="write"), run('eval "$(cat /tmp/t.txt)"', name="sink")],
     "FN: eval di shell bukan sink CodeQL", "TP"),
]

def main():
    TC.mkdir(exist_ok=True)
    for cid, lab, sink, flow, steps, gq, ge in CASES:
        git_repo(TC / cid, {".github/workflows/wf.yml": to_yaml(cid, steps)})
    labels = [{"id": c[0], "group": "P", "label": c[1], "sink_step": c[2], "old_id": "", "flow": c[3], "actions": [],
               "expected_codeql": c[5], "expected_ext": c[6]} for c in CASES]
    (B / "benchmark-p.json").write_text(json.dumps(labels, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(CASES)} kasus probe")

if __name__ == "__main__":
    main()
