#!/usr/bin/env python3
"""Bandingkan dua run per kasus berdasarkan SARIF (ruleId, step source, step sink).

Pakai: python3 compare.py <label-a> <label-b> [--same]
  --same : mode uji regresi; keluar dengan kode 1 bila ada kasus yang berbeda.
Contoh: python3 compare.py asli ext-off --same
"""
import json, re, sys
from pathlib import Path

B = Path(__file__).resolve().parent
a, b = sys.argv[1], sys.argv[2]
cases = json.loads((B / "benchmark.json").read_text())

def sig(label, cid):
    f = B / "results" / label / f"test-cases#{cid}#wf.sarif"
    if not f.exists():
        return None
    step = lambda loc: (lambda m: int(m.group(1)) if m else None)(re.search(r"\((\d+)th step\)", loc["physicalLocation"]["artifactLocation"]["uri"]))
    out = []
    for run in json.loads(f.read_text())["runs"]:
        for r in run["results"]:
            out.append((r["ruleId"], step(r["locations"][0]), tuple(step(x) for x in r.get("relatedLocations", []))))
    return sorted(out)

fmt = lambda s: "ERROR/tidak dijalankan" if s is None else (", ".join(f"{r} src {x} → sink {','.join(map(str, y))}" for r, x, y in s) or "–")
diff = 0
print(f"{'Kasus':30} {a:38} {b:38} Sama?")
for c in cases:
    sa, sb = sig(a, c["id"]), sig(b, c["id"])
    if sa is None and sb is None:
        continue
    same = sa == sb
    diff += not same
    print(f"{c['id']:30} {fmt(sa)[:38]:38} {fmt(sb)[:38]:38} {'ya' if same else 'BEDA'}")
print(f"\n=> {diff} kasus berbeda")
if "--same" in sys.argv and diff:
    sys.exit(1)
