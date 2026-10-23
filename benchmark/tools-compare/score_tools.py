#!/usr/bin/env python3
"""Skoring tool pembanding (zizmor, poutine, CodeQL Actions, CodeQL JS) dengan aturan yang sama seperti score.py.

Pakai: python3 tools-compare/score_tools.py [set]     (set: kosong = benchmark v3, x, p)
Baca : results/tools[-set]/<tool>/*.json|sarif       Tulis: results/tools[-set]/summary.md, summary.json

Hanya aturan kelas injeksi yang dihitung sebagai alert (aturan lain, mis. dangerous-triggers atau unpinned-uses,
muncul di hampir semua kasus dan tidak membedakan rentan/aman). Semua temuan mentah tetap dicantumkan di summary.md.
Step sebuah temuan = step workflow yang memuat baris temuan. Temuan CodeQL JS di dalam source Action
dipetakan ke step yang memanggil Action itu (sama seperti ARGUS melaporkan sink di dalam Action).
"""
import json, re, sys
from pathlib import Path

B = Path(__file__).resolve().parent.parent
SET = sys.argv[1] if len(sys.argv) > 1 else ""
TC = B / (f"test-cases-{SET}" if SET else "test-cases")
O = B / "results" / (f"tools-{SET}" if SET else "tools")
cases = json.loads((B / (f"benchmark-{SET}.json" if SET else "benchmark.json")).read_text())

INJ = {
    "zizmor": lambda r: r in ("template-injection", "github-env"),
    "poutine": lambda r: r in ("injection", "untrusted_checkout_exec"),
    "codeql-actions": lambda r: "injection" in r,
    "codeql-js": lambda r: "injection" in r,
}

def step_of_line(cid):
    """baris (1-based) -> indeks step di dalam job-nya"""
    lines = (TC / cid / ".github/workflows/wf.yml").read_text().splitlines()
    m, ind, idx = {}, None, -1
    for i, l in enumerate(lines, 1):
        if l.strip() == "steps:":
            ind, idx = None, -1; continue
        if re.match(r"^\s*- ", l) and (ind is None or len(l) - len(l.lstrip()) == ind) and idx >= -1:
            ind = len(l) - len(l.lstrip()); idx += 1
        elif ind is not None and l.strip() and len(l) - len(l.lstrip()) < ind:
            ind, idx = None, -2  # keluar dari daftar steps
        if idx >= 0: m[i] = idx
    return m

def raw(tool, cid):
    """[(rule, baris)] atau None bila tidak ada output"""
    if tool == "zizmor":
        f = O / "zizmor" / f"{cid}.json"
        if not f.exists(): return None
        return [(x["ident"], l["concrete"]["location"]["start_point"]["row"] + 1) for x in json.loads(f.read_text()) for l in x["locations"]]
    if tool == "poutine":
        f = O / "poutine" / f"{cid}.json"
        if not f.exists(): return None
        return [(x["rule_id"], x["meta"].get("line")) for x in json.loads(f.read_text()).get("findings") or []]
    f = O / "codeql-actions" / f"{cid}.sarif"
    if not f.exists() or not f.stat().st_size: return None
    return [(r["ruleId"], r["locations"][0]["physicalLocation"]["region"]["startLine"]) for r in json.loads(f.read_text())["runs"][0]["results"]]

def js_alerts(c):
    """temuan CodeQL JS pada Action yang dipakai kasus -> step pemanggil Action"""
    out = []
    wf = (TC / c["id"] / ".github/workflows/wf.yml").read_text().splitlines()
    sl = step_of_line(c["id"])
    for a in c.get("actions", []):
        f = O / "codeql-js" / f"{a}.sarif"
        if not f.exists(): continue
        line = next(i for i, l in enumerate(wf, 1) if f"benchowner/{a}@" in l)
        out += [(r["ruleId"], sl[line]) for r in json.loads(f.read_text())["runs"][0]["results"]]
    return out

TOOLS = ["zizmor", "poutine", "codeql-actions"] + ([] if SET else ["codeql-js", "codeql"])
rows = []
for c in cases:
    sl = step_of_line(c["id"])
    row = {"id": c["id"], "group": c["group"], "label": c["label"], "sink_step": c["sink_step"], "flow": c["flow"], "tools": {}}
    for t in TOOLS:
        if t == "codeql-js": all_ = js_alerts(c)
        elif t == "codeql": all_ = None  # gabungan, diisi di bawah
        else:
            r = raw(t, c["id"]); all_ = None if r is None else [(rule, sl.get(ln)) for rule, ln in r]
        if t == "codeql":
            a, b = row["tools"]["codeql-actions"], row["tools"]["codeql-js"]
            inj = None if a["inj"] is None else a["inj"] + b["inj"]; all_ = (a["all"] or []) + b["all"]
        else:
            inj = None if all_ is None else [x for x in all_ if INJ[t](x[0])]
        steps = sorted({s for _, s in inj if s is not None}) if inj else []
        if inj is None: loose = strict = "ERR"
        elif c["label"] == "V":
            loose = "TP" if inj else "FN"; strict = "TP" if c["sink_step"] in steps else "FN"
        else: loose = strict = "FP" if inj else "TN"
        row["tools"][t] = {"inj": inj, "all": all_, "steps": steps, "loose": loose, "strict": strict}
    rows.append(row)

def metrics(rs, t, key):
    n = {k: sum(r["tools"][t][key] == k for r in rs) for k in ("TP", "FN", "FP", "TN", "ERR")}
    pct = lambda a, b: f"{100 * a / b:.0f}%" if b else "–"
    return {**n, "recall": pct(n["TP"], n["TP"] + n["FN"]), "precision": pct(n["TP"], n["TP"] + n["FP"]), "fpr": pct(n["FP"], n["FP"] + n["TN"])}

groups = sorted({c["group"] for c in cases})
subsets = [("Semua kasus", rows)] + ([("Scope utama (K4+K5)", [r for r in rows if r["group"] in ("K4", "K5")])] if not SET else [])
subsets += [(g, [r for r in rows if r["group"] == g]) for g in groups] if len(groups) > 1 else []
table = [(n, t, k, metrics(rs, t, k)) for n, rs in subsets for t in TOOLS for k in ("loose", "strict")]

md = [f"# Skor tool pembanding ({'benchmark v3' if not SET else 'set ' + SET.upper()})", "",
      "Versi: " + " · ".join(l.strip() for l in (O / "VERSIONS.txt").read_text().splitlines() if l.strip()), "",
      "Sel = skor ketat (step sink alert). Hanya aturan kelas injeksi yang dihitung.", "",
      "| Kasus | Label | Sink | " + " | ".join(TOOLS) + " |", "|---|---|---|" + "---|" * len(TOOLS)]
for r in rows:
    cell = lambda t: f"{r['tools'][t]['strict']}" + (f" (step {','.join(map(str, r['tools'][t]['steps']))})" if r["tools"][t]["steps"] else "")
    md.append(f"| {r['id']} | {r['label']} | {'–' if r['sink_step'] is None else r['sink_step']} | " + " | ".join(cell(t) for t in TOOLS) + " |")
md += ["", "| Subset | Tool | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |", "|---|---|---|---|---|---|---|---|---|---|"]
md += [f"| {n} | {t} | {'longgar' if k == 'loose' else 'ketat'} | {m['TP']} | {m['FN']} | {m['FP']} | {m['TN']} | {m['recall']} | {m['precision']} | {m['fpr']} |"
       for n, t, k, m in table]
md += ["", "## Semua temuan mentah (aturan, step)", ""]
for r in rows:
    md.append(f"- **{r['id']}**: " + "; ".join(f"{t}: " + (", ".join(f"{a}@{s}" for a, s in r["tools"][t]["all"] or []) or "–") for t in TOOLS if t != "codeql"))
(O / "summary.md").write_text("\n".join(md) + "\n")
(O / "summary.json").write_text(json.dumps({"cases": rows, "metrics": [{"subset": n, "tool": t, "scoring": k, **m} for n, t, k, m in table]},
                                           indent=1, ensure_ascii=False) + "\n")
print("\n".join(md[:md.index("## Semua temuan mentah (aturan, step)")]))
