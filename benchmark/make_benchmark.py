#!/usr/bin/env python3
"""Generator benchmark berlabel (versi 3, 29 Sep 2026).

Satu sumber kebenaran untuk kasus uji: membuat repo git per kasus di test-cases/,
repo JS Action uji di actions/, label di benchmark.json, dan manifest kunci LOCK.sha256.

Pakai:  python3 make_benchmark.py          (buat ulang semua kasus dan action)
        python3 make_benchmark.py --lock   (buat ulang lalu tulis LOCK.sha256)
        python3 make_benchmark.py --verify (cek isi kasus masih sama dengan LOCK.sha256)

Konvensi label:
  V = rentan (vulnerable), S = aman (safe)
  sink = indeks step (0-based, sama dengan "task_N" di SARIF ARGUS) tempat nilai tainted dieksekusi.
  Step penulis file TIDAK memuat ${{ }} tainted langsung, supaya alert yang muncul benar-benar
  mencerminkan aliran lewat file (pelajaran benchmark v1, lihat LAPORAN.md).
"""
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

B = Path(__file__).resolve().parent
TC, AC = B / "test-cases", B / "actions"
T = "${{ github.event.pull_request.title }}"
ENV_T = {"TITLE": T}
GIT = ["git", "-c", "user.name=benchmark", "-c", "user.email=benchmark@localhost",
       "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false"]
DATE = "2026-09-29T00:00:00+07:00"

# ---------------------------------------------------------------- JS Action uji
HEAD = "const core = require('@actions/core');\n"
ACTIONS = {
    # K5: tulis file dari JS Action, dibaca step shell berikutnya
    "file-writer": HEAD + "const fs = require('fs');\nconst title = core.getInput('title');\n"
                   "fs.writeFile('/tmp/t.txt', title, () => {});\n",
    "file-writer-sync": HEAD + "const fs = require('fs');\nconst title = core.getInput('title');\n"
                        "fs.writeFileSync('/tmp/t.txt', title);\n",
    # K1: kanal yang dimodelkan eksplisit oleh ARGUS (GITHUB_OUTPUT dan GITHUB_ENV)
    "output-setter": HEAD + "core.setOutput('t', core.getInput('title'));\n",
    "env-exporter": HEAD + "core.exportVariable('T', core.getInput('title'));\n",
    # K2: lintas modul JS (require), sink di modul lain
    "crossmod-exec": {
        "index.js": HEAD + "const helper = require('./helper');\nhelper.run(core.getInput('title'));\n",
        "helper.js": "const cp = require('child_process');\nexports.run = (cmd) => cp.execSync(cmd);\n"},
    "crossmod-log": {
        "index.js": HEAD + "const helper = require('./helper');\nhelper.run(core.getInput('title'));\n",
        "helper.js": "exports.run = (s) => console.log(s.length);\n"},
    # K3: tulis lalu baca file di dalam satu JS Action
    "selffile-sync-exec": HEAD + "const fs = require('fs');\nconst cp = require('child_process');\n"
        "fs.writeFileSync('/tmp/t.txt', core.getInput('title'));\n"
        "const cmd = fs.readFileSync('/tmp/t.txt', 'utf8');\ncp.execSync(cmd);\n",
    "selffile-sync-log": HEAD + "const fs = require('fs');\n"
        "fs.writeFileSync('/tmp/t.txt', core.getInput('title'));\n"
        "const s = fs.readFileSync('/tmp/t.txt', 'utf8');\nconsole.log(s.length);\n",
    "selffile-async-exec": HEAD + "const fs = require('fs');\nconst cp = require('child_process');\n"
        "fs.writeFile('/tmp/t.txt', core.getInput('title'), () => {\n"
        "  fs.readFile('/tmp/t.txt', 'utf8', (err, cmd) => cp.exec(cmd));\n});\n",
    "selffile-async-log": HEAD + "const fs = require('fs');\n"
        "fs.writeFile('/tmp/t.txt', core.getInput('title'), () => {\n"
        "  fs.readFile('/tmp/t.txt', 'utf8', (err, s) => console.log(s.length));\n});\n",
}
ACTION_YML = "name: {name}\ninputs:\n  title:\n    required: true\nruns:\n  using: node20\n  main: index.js\n"

# ---------------------------------------------------------------- helper step
def run(cmd, env=None, name=None, wd=None, id=None):
    s = {"name": name or "step", "run": cmd}
    if env: s["env"] = env
    if wd: s["working-directory"] = wd
    if id: s["id"] = id
    return s

def use(action, name="write", id=None):
    s = {"name": name, "uses": f"benchowner/{action}@v1", "with": {"title": T}}
    if id: s["id"] = id
    return s

W = "printf '%s' \"$TITLE\" > /tmp/t.txt"          # penulis standar (env -> file)
R = 'eval "$(cat /tmp/t.txt)"'                      # pembaca standar -> sink eksekusi
NOSINK = "wc -c /tmp/t.txt"                         # pembaca tanpa sink

# ------------------------------------------------------------------ kasus uji
# (id, grup, label, sink_step, id_lama, deskripsi aliran, steps)
CASES = [
    # K1: kontrol tanpa file
    ("K1-V1-direct", "K1", "V", 0, "A", "${{ pr.title }} langsung di run → eval",
     [run(f'eval "{T}"', name="sink")]),
    ("K1-S1-const", "K1", "S", None, "", "env konstan → ${{ env.CMD }} → eval",
     [run('eval "${{ env.CMD }}"', env={"CMD": "echo ok"}, name="sink")]),
    ("K1-V2-envdirect", "K1", "V", 0, "E", "env TITLE → eval \"$TITLE\" (tanpa file)",
     [run('eval "$TITLE"', env=ENV_T, name="sink")]),
    ("K1-S2-envnosink", "K1", "S", None, "", "env TITLE → printf | wc -c (mitigasi resmi GitHub)",
     [run("printf '%s' \"$TITLE\" | wc -c", env=ENV_T, name="nosink")]),
    ("K1-V3-jsoutput", "K1", "V", 1, "", "JS Action setOutput → ${{ steps.w.outputs.t }} → eval",
     [use("output-setter", id="w"), run('eval "${{ steps.w.outputs.t }}"', name="sink")]),
    ("K1-V4-jsenv", "K1", "V", 1, "", "JS Action exportVariable → ${{ env.T }} → eval",
     [use("env-exporter"), run('eval "${{ env.T }}"', name="sink")]),
    ("K1-V5-shellenv", "K1", "V", 1, "", "env TITLE → echo \"T=$TITLE\" >> $GITHUB_ENV → ${{ env.T }} → eval",
     [run('echo "T=$TITLE" >> $GITHUB_ENV', env=ENV_T, name="write"), run('eval "${{ env.T }}"', name="sink")]),
    # K2: lintas modul JS (kontrol, bukan scope utama)
    ("K2-V1-crossmod", "K2", "V", 0, "Control", "getInput → require('./helper') → execSync",
     [use("crossmod-exec", name="sink")]),
    ("K2-S1-crossmod-nosink", "K2", "S", None, "", "getInput → require('./helper') → console.log",
     [use("crossmod-log", name="nosink")]),
    # K3: tulis → baca di dalam satu JS Action
    ("K3-V1-selffile-sync", "K3", "V", 0, "", "writeFileSync → readFileSync → execSync (satu Action)",
     [use("selffile-sync-exec", name="sink")]),
    ("K3-S1-selffile-sync-nosink", "K3", "S", None, "", "writeFileSync → readFileSync → console.log",
     [use("selffile-sync-log", name="nosink")]),
    ("K3-V2-selffile-async", "K3", "V", 0, "", "writeFile → readFile → exec (satu Action)",
     [use("selffile-async-exec", name="sink")]),
    ("K3-S2-selffile-async-nosink", "K3", "S", None, "", "writeFile → readFile → console.log",
     [use("selffile-async-log", name="nosink")]),
    # K4: file sebagai media antar-step shell (scope utama)
    ("K4-V1-envfile", "K4", "V", 1, "C", "env → printf > f → eval \"$(cat f)\"",
     [run(W, env=ENV_T, name="write"), run(R, name="sink")]),
    ("K4-S1-envfile-nosink", "K4", "S", None, "D", "env → printf > f → wc -c f",
     [run(W, env=ENV_T, name="write"), run(NOSINK, name="nosink")]),
    ("K4-V2-eventfile", "K4", "V", 1, "B", "jq $GITHUB_EVENT_PATH > f → eval \"$(cat f)\"",
     [run('jq -r .pull_request.title "$GITHUB_EVENT_PATH" > /tmp/t.txt', name="write"), run(R, name="sink")]),
    ("K4-S2-eventfile-nosink", "K4", "S", None, "", "jq $GITHUB_EVENT_PATH > f → wc -c f",
     [run('jq -r .pull_request.title "$GITHUB_EVENT_PATH" > /tmp/t.txt', name="write"), run(NOSINK, name="nosink")]),
    ("K4-V3-append", "K4", "V", 1, "", "env → printf >> f (append) → eval",
     [run("printf '%s' \"$TITLE\" >> /tmp/t.txt", env=ENV_T, name="write"), run(R, name="sink")]),
    ("K4-S3-overwrite", "K4", "S", None, "", "env → f, lalu f ditimpa konstanta → eval",
     [run(W, env=ENV_T, name="write"), run("printf 'echo ok' > /tmp/t.txt", name="overwrite"), run(R, name="sink")]),
    ("K4-S4-read-before-write", "K4", "S", None, "", "eval \"$(cat f)\" dijalankan sebelum f ditulis",
     [run('eval "$(cat /tmp/t.txt 2>/dev/null)"', name="sink"), run(W, env=ENV_T, name="write")]),
    ("K4-S5-otherfile", "K4", "S", None, "", "tainted ke a.txt, eval membaca b.txt (konstan)",
     [run("printf '%s' \"$TITLE\" > /tmp/a.txt; printf 'echo ok' > /tmp/b.txt", env=ENV_T, name="write"),
      run('eval "$(cat /tmp/b.txt)"', name="sink")]),
    ("K4-V4-tee", "K4", "V", 1, "", "env → printf | tee f → eval",
     [run("printf '%s' \"$TITLE\" | tee /tmp/t.txt", env=ENV_T, name="write"), run(R, name="sink")]),
    ("K4-V5-redirect-read", "K4", "V", 1, "", "env → printf > f → eval \"$(< f)\"",
     [run(W, env=ENV_T, name="write"), run('eval "$(< /tmp/t.txt)"', name="sink")]),
    ("K4-V6-relpath", "K4", "V", 1, "", "tulis t.txt, baca ./t.txt (path relatif)",
     [run("printf '%s' \"$TITLE\" > t.txt", env=ENV_T, name="write"), run('eval "$(cat ./t.txt)"', name="sink")]),
    ("K4-V7-workspace", "K4", "V", 1, "", "tulis $GITHUB_WORKSPACE/t.txt, baca ./t.txt",
     [run("printf '%s' \"$TITLE\" > \"$GITHUB_WORKSPACE/t.txt\"", env=ENV_T, name="write"),
      run('eval "$(cat ./t.txt)"', name="sink")]),
    ("K4-V8-workdir", "K4", "V", 2, "", "working-directory: sub tulis t.txt, baca sub/t.txt",
     [run("mkdir -p sub", name="setup"), run("printf '%s' \"$TITLE\" > t.txt", env=ENV_T, name="write", wd="sub"),
      run('eval "$(cat sub/t.txt)"', name="sink")]),
    ("K4-S6-workdir-other", "K4", "S", None, "", "working-directory: sub tulis t.txt, baca ./t.txt (file lain, konstan)",
     [run("mkdir -p sub && printf 'echo ok' > t.txt", name="setup"),
      run("printf '%s' \"$TITLE\" > t.txt", env=ENV_T, name="write", wd="sub"),
      run('eval "$(cat ./t.txt)"', name="sink")]),
    # K5: JS Action menulis file → step shell membaca
    ("K5-V1-jsfile", "K5", "V", 1, "F", "JS Action fs.writeFile → eval \"$(cat f)\"",
     [use("file-writer"), run(R, name="sink")]),
    ("K5-S1-jsfile-nosink", "K5", "S", None, "G", "JS Action fs.writeFile → wc -c f",
     [use("file-writer"), run(NOSINK, name="nosink")]),
    ("K5-V2-jsfile-sync", "K5", "V", 1, "", "JS Action fs.writeFileSync → eval \"$(cat f)\"",
     [use("file-writer-sync"), run(R, name="sink")]),
    ("K5-S2-jsfile-sync-nosink", "K5", "S", None, "", "JS Action fs.writeFileSync → wc -c f",
     [use("file-writer-sync"), run(NOSINK, name="nosink")]),
]

# ------------------------------------------------------------------ YAML writer
def q(v):
    """Kutip nilai YAML bila perlu (tanpa dependensi PyYAML)."""
    s = str(v)
    if s[:1] in "\"'{[&*!|>%@`#" or ": " in s or s.startswith("${{") or s.strip() != s:
        return "'" + s.replace("'", "''") + "'"
    return s

def workflow_yaml(name, steps):
    out = [f"name: {name}", "on: pull_request_target", "permissions:", "  contents: write",
           "jobs:", "  j:", "    runs-on: ubuntu-latest", "    steps:"]
    for st in steps:
        first = True
        for k in ("name", "id", "uses", "with", "env", "working-directory", "run"):
            if k not in st: continue
            pre = "      - " if first else "        "; first = False
            v = st[k]
            if isinstance(v, dict):
                out.append(f"{pre}{k}:")
                out += [f"          {kk}: {q(vv)}" for kk, vv in v.items()]
            else:
                out.append(f"{pre}{k}: {q(v)}")
    return "\n".join(out) + "\n"

def git_repo(path, files, tag=None):
    if path.exists(): shutil.rmtree(path)
    for rel, content in files.items():
        p = path / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content)
    env = {**os.environ, "GIT_AUTHOR_DATE": DATE, "GIT_COMMITTER_DATE": DATE}
    sh = lambda *a: subprocess.run(GIT + list(a), cwd=path, env=env, check=True, capture_output=True)
    sh("init", "-q", "-b", "master"); sh("add", "-A"); sh("commit", "-q", "-m", path.name)
    if tag: sh("tag", tag)

def case_files():
    return {c[0]: workflow_yaml(c[0], c[6]) for c in CASES}

def lock_lines():
    lines = []
    for cid, y in sorted(case_files().items()):
        lines.append(f"{hashlib.sha256(y.encode()).hexdigest()}  test-cases/{cid}/.github/workflows/wf.yml")
    for name in sorted(ACTIONS):
        files = ACTIONS[name] if isinstance(ACTIONS[name], dict) else {"index.js": ACTIONS[name]}
        for rel, content in sorted({**files, "action.yml": ACTION_YML.format(name=name)}.items()):
            lines.append(f"{hashlib.sha256(content.encode()).hexdigest()}  actions/{name}/{rel}")
    return lines

def main():
    if "--verify" in sys.argv:
        bad = 0
        for line in (B / "LOCK.sha256").read_text().splitlines():
            if not line or line.startswith("#"): continue
            h, rel = line.split("  ", 1); p = B / rel
            ok = p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == h
            bad += not ok
            if not ok: print("BERUBAH:", rel)
        print("OK: benchmark sama dengan LOCK.sha256" if not bad else f"{bad} file berubah"); sys.exit(bool(bad))

    for name, src in ACTIONS.items():
        files = src if isinstance(src, dict) else {"index.js": src}
        git_repo(AC / name, {**files, "action.yml": ACTION_YML.format(name=name)}, tag="v1")
    for cid, y in case_files().items():
        git_repo(TC / cid, {".github/workflows/wf.yml": y})

    labels = [{"id": c[0], "group": c[1], "label": c[2], "sink_step": c[3], "old_id": c[4], "flow": c[5],
               "actions": sorted({s["uses"].split("/")[1].split("@")[0] for s in c[6] if "uses" in s})}
              for c in CASES]
    (B / "benchmark.json").write_text(json.dumps(labels, indent=1, ensure_ascii=False) + "\n")
    if "--lock" in sys.argv:
        (B / "LOCK.sha256").write_text("# Benchmark v3 dikunci 29 Sep 2026, sebelum implementasi ekstensi.\n"
                                        "# Cek: python3 make_benchmark.py --verify\n" + "\n".join(lock_lines()) + "\n")
    nv = sum(c[2] == "V" for c in CASES)
    print(f"{len(CASES)} kasus ({nv} V, {len(CASES) - nv} S), {len(ACTIONS)} JS Action")

if __name__ == "__main__":
    main()
