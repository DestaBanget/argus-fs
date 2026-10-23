#!/usr/bin/env python3
"""Set uji held-out Y (3 Okt 2026). BUKAN bagian benchmark terkunci, dan BUKAN dev set.

Tujuan: angka generalisasi yang jujur untuk ekstensi v0.2-fs, setelah set X terpakai untuk pengembangan.
Aturan:
  1. Kasus, label, dan dugaan hasil v0.2 (expected_ext) ditulis lalu dikunci (LOCK-y.sha256) sebelum
     ekstensi dijalankan pada set ini.
  2. Ekstensi dijalankan SEKALI (tag v0.2-fs). Tidak ada perbaikan kode berdasarkan hasil set ini
     sebelum angkanya dilaporkan apa adanya.
Kasus meniru idiom yang umum di workflow nyata (RUNNER_TEMP, skrip yang dirakit lalu dijalankan,
python/xargs/while-read, salinan payload event), bukan hanya pola yang sudah dimodelkan.

Pakai: python3 make_heldout.py   -> test-cases-y/, actions-y/, benchmark-y.json
"""
import json
from pathlib import Path
from make_benchmark import run, use, git_repo, ENV_T, W, HEAD, ACTION_YML
from make_explore import to_yaml

B = Path(__file__).resolve().parent
TC, AC = B / "test-cases-y", B / "actions-y"

ACTIONS = {
    # fs.promises (dimodelkan di FileFlowCommon.qll, tetapi belum pernah diuji)
    "promise-writer": HEAD + "const fs = require('fs');\n"
        "fs.promises.writeFile('/tmp/t.txt', core.getInput('title'));\n",
    # path tidak literal (RUNNER_TEMP), idiom umum di Action nyata
    "tempdir-writer": HEAD + "const fs = require('fs');\nconst path = require('path');\n"
        "fs.writeFileSync(path.join(process.env.RUNNER_TEMP, 't.txt'), core.getInput('title'));\n",
}

EV = '"$GITHUB_EVENT_PATH"'
# (id, label, sink_step, deskripsi, steps, dugaan hasil v0.2)
CASES = [
    ("Y01-runner-temp", "V", 1, "tulis ke $RUNNER_TEMP/t.txt → eval \"$(cat $RUNNER_TEMP/t.txt)\"",
     [run("printf '%s' \"$TITLE\" > \"$RUNNER_TEMP/t.txt\"", env=ENV_T, name="write"), run('eval "$(cat "$RUNNER_TEMP/t.txt")"', name="sink")],
     "FN: $RUNNER_TEMP bukan variabel literal, path dianggap dinamis"),
    ("Y02-built-script", "V", 1, "skrip dirakit dengan echo > / >> lalu chmod +x dan ./run.sh",
     [run('echo "#!/bin/bash" > run.sh\necho "echo $TITLE" >> run.sh\nchmod +x run.sh', env=ENV_T, name="write"), run("./run.sh", name="sink")],
     "TP"),
    ("Y03-python-exec", "V", 1, "tulis f → python3 -c \"exec(open(f).read())\"",
     [run(W, env=ENV_T, name="write"), run("python3 -c \"exec(open('/tmp/t.txt').read())\"", name="sink")],
     "FN: interpreter python bukan sink"),
    ("Y04-bash-c", "V", 1, "tulis f → bash -c \"$(cat f)\"",
     [run(W, env=ENV_T, name="write"), run('bash -c "$(cat /tmp/t.txt)"', name="sink")], "TP"),
    ("Y05-xargs-sh", "V", 1, "tulis f → xargs -I{} sh -c '{}' < f",
     [run(W, env=ENV_T, name="write"), run("xargs -I{} sh -c '{}' < /tmp/t.txt", name="sink")],
     "TP (kebetulan: sh -c + file disebut; xargs tidak dimodelkan)"),
    ("Y06-source-event-vars", "V", 1, "echo \"export T=\\\"$(jq .issue.title $GITHUB_EVENT_PATH)\\\"\" > vars.sh → source vars.sh",
     [run(f'echo "export T=\\"$(jq -r .pull_request.title {EV})\\"" > vars.sh', name="write"), run('source vars.sh\necho "$T"', name="sink")],
     "TP"),
    ("Y07-cat-copy", "V", 2, "tulis f → cat f > g → eval \"$(cat g)\"",
     [run(W, env=ENV_T, name="write"), run("cat /tmp/t.txt > /tmp/g.txt", name="copy"), run('eval "$(cat /tmp/g.txt)"', name="sink")],
     "TP"),
    ("Y08-headref-sh-c", "V", 1, "env BRANCH=${{ github.head_ref }} → echo > f → sh -c \"$(< f)\"",
     [run('echo "$BRANCH" > branch.txt', env={"BRANCH": "${{ github.head_ref }}"}, name="write"), run('sh -c "$(< branch.txt)"', name="sink")],
     "TP"),
    ("Y09-pipe-sh", "V", 1, "tulis f → cat f | sh", [run(W, env=ENV_T, name="write"), run("cat /tmp/t.txt | sh", name="sink")], "TP"),
    ("Y10-dot-source", "V", 1, "tulis ./env.sh → . ./env.sh",
     [run('echo "T=$TITLE" > env.sh', env=ENV_T, name="write"), run(". ./env.sh", name="sink")], "TP"),
    ("Y11-while-read-eval", "V", 1, "tulis f → while read l; do eval \"$l\"; done < f",
     [run(W, env=ENV_T, name="write"), run('while read -r l; do eval "$l"; done < /tmp/t.txt', name="sink")],
     "FN: taint lewat read ke variabel l tidak dimodelkan"),
    ("Y12-js-promises", "V", 1, "JS Action fs.promises.writeFile → eval \"$(cat f)\"",
     [use("promise-writer"), run('eval "$(cat /tmp/t.txt)"', name="sink")], "TP"),
    ("Y13-js-runner-temp", "V", 1, "JS Action tulis path.join(RUNNER_TEMP) → eval \"$(cat $RUNNER_TEMP/t.txt)\"",
     [use("tempdir-writer"), run('eval "$(cat "$RUNNER_TEMP/t.txt")"', name="sink")],
     "FN: path tidak literal di JS dan di shell"),
    ("Y14-rm-then-guard", "S", None, "tulis f → rm f → [ -f f ] && eval \"$(cat f)\" (file sudah tidak ada)",
     [run(W, env=ENV_T, name="write"), run("rm -f /tmp/t.txt", name="remove"), run('[ -f /tmp/t.txt ] && eval "$(cat /tmp/t.txt)" || true', name="guard")],
     "FP: rm tidak dimodelkan"),
    ("Y15-hash-eval", "S", None, "tulis f → eval \"H=$(sha256sum < f)\" (hanya hash yang dieksekusi)",
     [run(W, env=ENV_T, name="write"), run('eval "H=$(sha256sum < /tmp/t.txt | cut -c1-64)"', name="sink")],
     "FP: sanitasi oleh sha256sum tidak dimodelkan"),
    ("Y16-repo-script", "S", None, "tulis f (tainted), lalu grep -c f dan bash ./build.sh (skrip repo, bukan f)",
     [run(W, env=ENV_T, name="write"), run("grep -c x /tmp/t.txt || true\nbash ./build.sh", name="build")], "TN"),
    ("Y17-backup-file", "S", None, "tainted ke f, konstan ke f.bak, eval membaca f.bak",
     [run(W + "\nprintf 'echo ok' > /tmp/t.txt.bak", env=ENV_T, name="write"), run('eval "$(cat /tmp/t.txt.bak)"', name="sink")], "TN"),
    ("Y18-event-number", "S", None, "cp $GITHUB_EVENT_PATH ev.json → eval \"N=$(jq .pull_request.number ev.json)\" (angka)",
     [run(f"cp {EV} ev.json", name="copy"), run('eval "N=$(jq -r .pull_request.number ev.json)"', name="sink")],
     "FP: tidak sensitif terhadap field (seluruh payload dianggap tainted)"),
]

def main():
    TC.mkdir(exist_ok=True); AC.mkdir(exist_ok=True)
    for name, src in ACTIONS.items():
        git_repo(AC / name, {"index.js": src, "action.yml": ACTION_YML.format(name=name)}, tag="v1")
    for cid, lab, sink, flow, steps, guess in CASES:
        files = {".github/workflows/wf.yml": to_yaml(cid, steps)}
        if cid == "Y16-repo-script": files["build.sh"] = "echo build\n"
        git_repo(TC / cid, files)
    labels = [{"id": c[0], "group": "Y", "label": c[1], "sink_step": c[2], "old_id": "", "flow": c[3],
               "actions": sorted({s["uses"].split("/")[1].split("@")[0] for s in c[4] if "uses" in s}), "expected_ext": c[5]}
              for c in CASES]
    (B / "benchmark-y.json").write_text(json.dumps(labels, indent=1, ensure_ascii=False) + "\n")
    nv = sum(c[1] == "V" for c in CASES)
    print(f"{len(CASES)} kasus held-out ({nv} V, {len(CASES) - nv} S), {len(ACTIONS)} JS Action")

if __name__ == "__main__":
    main()
