#!/usr/bin/env python3
"""Skoring hasil ARGUS terhadap label benchmark.json.

Pakai: python3 score.py <label>     (membaca results/<label>/*.sarif)
Tulis: results/<label>/summary.md dan results/<label>/summary.json

Dua skoring (unit = kasus):
  longgar : kasus V dianggap terdeteksi bila ada alert apa pun.
  ketat   : kasus V dianggap terdeteksi hanya bila ada alert yang lokasi sink-nya = step sink (label sink_step).
Lokasi sink diambil dari relatedLocations SARIF (locations berisi lokasi source).
Kasus S dengan alert apa pun = FP pada kedua skoring.
"""
import json, os, re, sys
from pathlib import Path

B = Path(__file__).resolve().parent
L = sys.argv[1]
R = B / "results" / L
# SET=x: set uji eksplorasi (test-cases-x/, benchmark-x.json); SET=p: set probe; default: benchmark v3 terkunci
SET = os.environ.get("SET", "")
TCN = f"test-cases-{SET}" if SET else "test-cases"
cases = json.loads((B / (f"benchmark-{SET}.json" if SET else "benchmark.json")).read_text())
GROUPS = {"X": "eksplorasi"} if SET == "x" else {"P": "probe model file CodeQL"} if SET == "p" else {"Y": "held-out"} if SET == "y" else {"K1": "kontrol tanpa file", "K2": "lintas modul JS", "K3": "file dalam satu JS Action",
          "K4": "file antar-step shell", "K5": "JS Action → file → shell"}

def alerts(cid):
    f = R / f"{TCN}#{cid}#wf.sarif"
    if not f.exists(): return None
    out = []
    for run in json.loads(f.read_text())["runs"]:
        for r in run["results"]:
            # SARIF ARGUS: "locations" = lokasi source, "relatedLocations" = lokasi sink (workflow_report.py).
            # Step dinilai dari lokasi sink; log "ALERT RAISED @ ..." juga mencetak lokasi sink.
            step = lambda loc: (lambda m: int(m.group(1)) if m else None)(
                re.search(r"\((\d+)th step\)", loc["physicalLocation"]["artifactLocation"]["uri"]))
            sinks = [step(x) for x in r.get("relatedLocations", [])] or [step(r["locations"][0])]
            out += [{"rule": r["ruleId"], "step": st, "source_step": step(r["locations"][0]), "msg": r["message"]["text"]} for st in sinks]
    return out

# kasus tanpa log run di logs/<label>/ tidak dijalankan pada run ini (mis. subset ablasi) -> dilewati.
# Hasil tersimpan di repo tidak menyertakan logs/, jadi SARIF yang ada juga menandai kasus yang dijalankan.
cases = [c for c in cases if (B / "logs" / L / f"{c['id']}.log").exists() or (R / f"{TCN}#{c['id']}#wf.sarif").exists()]
rows = []
for c in cases:
    a = alerts(c["id"])
    steps = sorted({x["step"] for x in a}) if a else []
    if a is None:
        loose = strict = "ERR"
    elif c["label"] == "V":
        loose = "TP" if a else "FN"
        strict = "TP" if c["sink_step"] in steps else "FN"
    else:
        loose = strict = "FP" if a else "TN"
    note = ""
    if c["label"] == "V" and a and c["sink_step"] not in steps: note = "lokasi salah"
    rows.append({**c, "alerts": a, "steps": steps, "loose": loose, "strict": strict, "note": note})

def metrics(rs, key):
    n = {k: sum(r[key] == k for r in rs) for k in ("TP", "FN", "FP", "TN", "ERR")}
    pct = lambda a, b: f"{100 * a / b:.0f}%" if b else "–"
    return {**n, "recall": pct(n["TP"], n["TP"] + n["FN"]), "precision": pct(n["TP"], n["TP"] + n["FP"]),
            "fpr": pct(n["FP"], n["FP"] + n["TN"])}

subsets = [("Semua kasus", rows), ("Scope utama (K4+K5)", [r for r in rows if r["group"] in ("K4", "K5")])]
subsets += [(f"{g} {d}", [r for r in rows if r["group"] == g]) for g, d in GROUPS.items()]
table = [(name, key, metrics(rs, key)) for name, rs in subsets for key in ("loose", "strict")]

# ---- terminal
fmt = "{:30} {:5} {:4} {:14} {:6} {:6} {}"
print(f"Skor '{L}'  ({len(rows)} kasus, V={sum(r['label']=='V' for r in rows)}, S={sum(r['label']=='S' for r in rows)})")
print(fmt.format("Kasus", "Label", "Sink", "Sink alert", "Longgr", "Ketat", "Catatan"))
for r in rows:
    al = "ERROR" if r["alerts"] is None else (", ".join(f"step {s}" for s in r["steps"]) or "-")
    print(fmt.format(r["id"], r["label"], "-" if r["sink_step"] is None else r["sink_step"], al, r["loose"], r["strict"], r["note"]))
print()
mf = "{:32} {:8} {:>3} {:>3} {:>3} {:>3} {:>3}  {:>7} {:>9} {:>5}"
print(mf.format("Subset", "Skoring", "TP", "FN", "FP", "TN", "ERR", "Recall", "Precision", "FPR"))
for name, key, m in table:
    print(mf.format(name, "longgar" if key == "loose" else "ketat", m["TP"], m["FN"], m["FP"], m["TN"], m["ERR"],
                    m["recall"], m["precision"], m["fpr"]))

# ---- file
md = [f"# Skor benchmark: `{L}`", "", "| Kasus | Grup | Aliran | Label | Sink | Sink alert ARGUS | Longgar | Ketat |",
      "|---|---|---|---|---|---|---|---|"]
for r in rows:
    al = "ERROR" if r["alerts"] is None else (", ".join(f"step {s}" for s in r["steps"]) or "–")
    md.append(f"| {r['id']} | {r['group']} | {r['flow'].replace('|', '\\|')} | {r['label']} | "
              f"{'–' if r['sink_step'] is None else r['sink_step']} | {al} | {r['loose']} | {r['strict']}{' (' + r['note'] + ')' if r['note'] else ''} |")
md += ["", "| Subset | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |", "|---|---|---|---|---|---|---|---|---|"]
md += [f"| {n} | {'longgar' if k == 'loose' else 'ketat'} | {m['TP']} | {m['FN']} | {m['FP']} | {m['TN']} | {m['recall']} | {m['precision']} | {m['fpr']} |"
       for n, k, m in table]
(R / "summary.md").write_text("\n".join(md) + "\n")
(R / "summary.json").write_text(json.dumps({"cases": rows, "metrics": [{"subset": n, "scoring": k, **m} for n, k, m in table]},
                                           indent=1, ensure_ascii=False) + "\n")
