#!/usr/bin/env python3
"""Set uji eksplorasi (X), 29 Sep 2026. BUKAN bagian benchmark terkunci.

Dibuat setelah prototipe ekstensi selesai ditulis, tetapi label ditetapkan sebelum ekstensi
dijalankan pada set ini. Tujuannya menguji generalisasi dan memetakan keterbatasan prototipe,
bukan untuk metrik utama. Hasilnya dilaporkan terpisah.

Pakai: python3 make_explore.py   -> test-cases-x/ dan benchmark-x.json
"""
import json
from pathlib import Path
import yaml
from make_benchmark import run, git_repo, ENV_T, W, R

class _Lit(str): pass
yaml.SafeDumper.add_representer(_Lit, lambda d, v: d.represent_scalar("tag:yaml.org,2002:str", v, style="|"))

B = Path(__file__).resolve().parent
TC = B / "test-cases-x"
WS = "printf '%s' \"$TITLE\" > /tmp/t.sh"

# (id, label, sink_step, deskripsi, steps | {job: (needs, steps)}, dugaan hasil prototipe)
CASES = [
    ("X01-pipe-to-bash", "V", 1, "tulis f → cat f | bash", [run(W, env=ENV_T, name="write"), run("cat /tmp/t.txt | bash", name="sink")],
     "FN: eksekusi lewat stdin shell belum dimodelkan"),
    ("X02-bash-file", "V", 1, "tulis t.sh → bash t.sh", [run(WS, env=ENV_T, name="write"), run("bash /tmp/t.sh", name="sink")], "TP"),
    ("X03-source-file", "V", 1, "tulis t.sh → source t.sh", [run(WS, env=ENV_T, name="write"), run("source /tmp/t.sh", name="sink")], "TP"),
    ("X04-cp", "V", 2, "tulis f → cp f g → eval \"$(cat g)\"",
     [run(W, env=ENV_T, name="write"), run("cp /tmp/t.txt /tmp/u.txt", name="copy"), run('eval "$(cat /tmp/u.txt)"', name="sink")],
     "FN: cp/mv belum dimodelkan"),
    ("X05-two-jobs", "S", None, "job a tulis f, job b eval \"$(cat f)\" (runner berbeda)",
     {"a": (None, [run(W, env=ENV_T, name="write")]), "b": ("a", [run(R, name="sink")])}, "TN: file-state dikosongkan per job"),
    ("X06-echo-cat-wc", "S", None, "tulis f → echo \"$(cat f)\" | wc -c (tanpa eksekusi)",
     [run(W, env=ENV_T, name="write"), run('echo "$(cat /tmp/t.txt)" | wc -c', name="nosink")], "TN"),
    ("X07-var-path", "V", 1, "path lewat variabel: F=/tmp/t.txt; > \"$F\" → eval \"$(cat \"$F\")\"",
     [run("F=/tmp/t.txt; printf '%s' \"$TITLE\" > \"$F\"", env=ENV_T, name="write"), run('F=/tmp/t.txt; eval "$(cat "$F")"', name="sink")],
     "FN: path dinamis di luar scope"),
    ("X08-heredoc", "V", 1, "heredoc: cat > t.sh <<EOF ($TITLE) → bash t.sh",
     [run('cat > /tmp/t.sh <<EOF\n$TITLE\nEOF', env=ENV_T, name="write"), run("bash /tmp/t.sh", name="sink")],
     "FN: isi heredoc belum dimodelkan"),
    ("X09-sh-c", "V", 1, "echo \"$TITLE\" > f → sh -c \"$(cat f)\"",
     [run('echo "$TITLE" > /tmp/t.txt', env=ENV_T, name="write"), run('sh -c "$(cat /tmp/t.txt)"', name="sink")], "TP"),
    ("X10-if-block", "V", 1, "if [ -f f ]; then eval \"$(cat f)\"; fi",
     [run(W, env=ENV_T, name="write"), run('if [ -f /tmp/t.txt ]; then eval "$(cat /tmp/t.txt)"; fi', name="sink")],
     "FN: kata kunci then/do sebelum perintah belum ditangani"),
    ("X11-cat-only", "S", None, "tulis f → cat f (hanya dicetak)", [run(W, env=ENV_T, name="write"), run("cat /tmp/t.txt", name="nosink")], "TN"),
    ("X12-multiline", "V", 1, "tulis f di baris ke-2 skrip multi-baris, eval di step berikutnya",
     [run('echo "mulai"\n' + W + '\necho "selesai"', env=ENV_T, name="write"), run('echo "baca"\n' + R, name="sink")], "TP"),
]

def to_yaml(name, steps):
    jobs = steps if isinstance(steps, dict) else {"j": (None, steps)}
    wf = {"name": name, "on": "pull_request_target", "permissions": {"contents": "write"}, "jobs": {}}
    for j, (needs, st) in jobs.items():
        job = {"runs-on": "ubuntu-latest"}
        if needs: job["needs"] = needs
        job["steps"] = [{k: (_Lit(v) if isinstance(v, str) and "\n" in v else v) for k, v in x.items()} for x in st]
        wf["jobs"][j] = job
    return yaml.safe_dump(wf, sort_keys=False, allow_unicode=True, width=200)

def main():
    TC.mkdir(exist_ok=True)
    for cid, lab, sink, flow, steps, guess in CASES:
        git_repo(TC / cid, {".github/workflows/wf.yml": to_yaml(cid, steps)})
    labels = [{"id": c[0], "group": "X", "label": c[1], "sink_step": c[2], "old_id": "", "flow": c[3], "actions": [], "expected_ext": c[5]}
              for c in CASES]
    (B / "benchmark-x.json").write_text(json.dumps(labels, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(CASES)} kasus eksplorasi")

if __name__ == "__main__":
    main()
