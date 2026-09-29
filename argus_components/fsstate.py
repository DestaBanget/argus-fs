# Ekstensi file-state (skripsi): pelacakan aliran taint melalui file dalam satu job.
#
# Semua perilaku baru dikendalikan oleh variabel lingkungan ARGUS_FS (daftar flag dipisah koma).
# ARGUS_FS kosong = perilaku ARGUS asli, tanpa perubahan.
#
#   shell     : file-state untuk step shell (tulis > >> tee, baca cat/$(< f)/dsb., sink eval/sh -c/bash f)
#   eventpath : $GITHUB_EVENT_PATH diperlakukan sebagai file yang isinya dikontrol penyerang
#   js        : JS Action: fs.write* ke path konstan menjadi propagasi ke file-state (bukan sink),
#               dan aliran tulis -> baca file di dalam satu Action dilacak (FileFlowSinks.ql)
#   envexec   : (ablasi) env $VAR tainted di dalam sink eksekusi shell (eval "$VAR") dilaporkan
#   all       : shell,eventpath,js

import os
import posixpath
import re
import shlex

_ALIASES = {"all": {"shell", "eventpath", "js"}}


def flags():
    out = set()
    for f in os.environ.get("ARGUS_FS", "").replace(" ", "").split(","):
        if f:
            out |= _ALIASES.get(f, {f})
    return out


def enabled(flag):
    return flag in flags()


# ------------------------------------------------------------------ path

EVENT_KEY = "event:"
_WS_PREFIXES = ("$GITHUB_WORKSPACE", "${GITHUB_WORKSPACE}", "${{ github.workspace }}", "${{github.workspace}}")
_EVENT_NAMES = ("$GITHUB_EVENT_PATH", "${GITHUB_EVENT_PATH}")


def _strip_quotes(p):
    p = p.strip()
    while len(p) >= 2 and p[0] == p[-1] and p[0] in "\"'":
        p = p[1:-1].strip()
    return p


def cwd_key(working_directory):
    """Direktori kerja step sebagai (basis, path). Basis 'ws' = relatif terhadap workspace."""
    wd = _strip_quotes(working_directory or "")
    if not wd:
        return ("ws", "")
    for pre in _WS_PREFIXES:
        if wd == pre or wd.startswith(pre + "/"):
            return ("ws", posixpath.normpath(wd[len(pre):].lstrip("/") or "."))
    if wd.startswith("/"):
        return ("abs", posixpath.normpath(wd))
    if "$" in wd:
        return None
    return ("ws", posixpath.normpath(wd))


def normalize(path, cwd=("ws", "")):
    """Kunci file-state untuk sebuah path, atau None bila path dinamis (di luar scope)."""
    p = _strip_quotes(path)
    if not p:
        return None
    if p in _EVENT_NAMES:
        return EVENT_KEY
    for pre in _WS_PREFIXES:
        if p == pre or p.startswith(pre + "/"):
            return "ws:" + posixpath.normpath(p[len(pre):].lstrip("/") or ".")
    if any(ch in p for ch in "$*?`[]{}<>|&;()") or p.startswith("~") or p.startswith("-"):
        return None
    if p.startswith("/"):
        if p.startswith("/dev/"):
            return None
        return "abs:" + posixpath.normpath(p)
    if cwd is None:
        return None
    base, d = cwd
    joined = posixpath.normpath(posixpath.join(d, p)) if d else posixpath.normpath(p)
    return ("abs:" if base == "abs" else "ws:") + joined


def normalize_js(path):
    """Path pada JS Action: relatif terhadap cwd proses = workspace."""
    return normalize(path, ("ws", ""))


# ------------------------------------------------------------------ shell

def _scan(cmd, seps):
    """Pisah cmd pada separator top-level (di luar kutip, $( ), backtick). seps: list string, cek terpanjang dulu."""
    parts, cur, i, n = [], [], 0, len(cmd)
    sq = dq = False
    depth = 0
    bt = False
    seps = sorted(seps, key=len, reverse=True)
    while i < n:
        c = cmd[i]
        if c == "\\" and not sq and i + 1 < n:
            cur.append(cmd[i:i + 2]); i += 2; continue
        if sq:
            if c == "'": sq = False
            cur.append(c); i += 1; continue
        if c == "'" and not dq and depth == 0 and not bt:
            sq = True; cur.append(c); i += 1; continue
        if c == "'" and (depth > 0 or bt) and not dq:
            # kutip tunggal di dalam $( ): lompati sampai penutup
            j = cmd.find("'", i + 1)
            j = n - 1 if j < 0 else j
            cur.append(cmd[i:j + 1]); i = j + 1; continue
        if c == '"':
            dq = not dq; cur.append(c); i += 1; continue
        if c == "`":
            bt = not bt; cur.append(c); i += 1; continue
        if c == "$" and i + 1 < n and cmd[i + 1] == "(":
            depth += 1; cur.append("$("); i += 2; continue
        if c == "(" and depth > 0:
            depth += 1; cur.append(c); i += 1; continue
        if c == ")" and depth > 0:
            depth -= 1; cur.append(c); i += 1; continue
        if not dq and depth == 0 and not bt:
            if c == "#" and (not cur or cur[-1] in " \t\n"):
                j = cmd.find("\n", i)
                i = n if j < 0 else j
                continue
            hit = next((s for s in seps if cmd.startswith(s, i)), None)
            if hit and not (hit == "|" and cmd.startswith("||", i)) and not (hit == "&" and (cmd.startswith("&&", i) or (i > 0 and cmd[i - 1] in "<>") or cmd.startswith("&>", i))):
                parts.append("".join(cur)); cur = []; i += len(hit); continue
        cur.append(c); i += 1
    parts.append("".join(cur))
    return [p for p in (x.strip() for x in parts) if p]


def statements(cmd):
    cmd = cmd.replace("\\\n", " ")
    return _scan(cmd, ["\n", ";", "&&", "||", "&"])


def pipeline(stmt):
    return _scan(stmt, ["|"])


_REDIR = re.compile(r"""(?<![<>&\d])(?P<fd>\d?)(?P<op>&>>|&>|>>|>\|?)(?!&)\s*(?P<tgt>"[^"]*"|'[^']*'|[^\s;|&<>()]+)""")


def _outside_quotes_mask(s):
    """True untuk karakter di level atas (bukan di dalam kutip / $( ))."""
    mask, sq, dq, depth = [], False, False, 0
    i = 0
    while i < len(s):
        c = s[i]
        top = not sq and not dq and depth == 0
        mask.append(top)
        if c == "\\" and not sq:
            mask.append(top); i += 2; continue
        if sq:
            if c == "'": sq = False
        elif c == "'" and not dq:
            sq = True
        elif c == '"':
            dq = not dq
        elif c == "$" and i + 1 < len(s) and s[i + 1] == "(":
            depth += 1
        elif c == ")" and depth > 0:
            depth -= 1
        i += 1
    return mask[:len(s)]


def words(stage):
    try:
        return shlex.split(stage, posix=True)
    except ValueError:
        return stage.split()


def parse_stage(stage):
    """-> (teks tanpa target tulis, [(target, append)], kata-kata perintah)"""
    mask = _outside_quotes_mask(stage)
    writes, spans = [], []
    for m in _REDIR.finditer(stage):
        if not mask[m.start()]:
            continue
        if m.group("fd") and m.group("fd") != "1":
            spans.append(m.span()); continue       # stderr dsb.: bukan data
        writes.append((m.group("tgt"), ">>" in m.group("op")))
        spans.append(m.span())
    text = stage
    for a, b in reversed(spans):
        text = text[:a] + " " + text[b:]
    w = words(text)
    if w and posixpath.basename(w[0]) == "tee":
        append = any(x in ("-a", "--append") for x in w[1:])
        for x in w[1:]:
            if not x.startswith("-"):
                writes.append((x, append))
        text = w[0]  # isi tee = input pipe; argumennya adalah target, bukan bacaan
        w = [w[0]]
    return text, writes, w


_TOKEN = re.compile(r"""\$\{?[A-Za-z_][A-Za-z0-9_]*\}?(?:/[^\s"'`;|&<>()]*)?|[^\s"'`;|&<>()=]+""")
_VAR = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?")


def mentioned_paths(text, cwd):
    """Kunci file-state yang disebut di teks (argumen, $(cat f), $(< f), dsb.)."""
    keys = []
    for tok in _TOKEN.findall(text):
        k = normalize(tok, cwd)
        if k and k not in keys:
            keys.append(k)
    return keys


def env_names(text):
    return list(dict.fromkeys(_VAR.findall(text)))


SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}


def exec_sink(w, cwd):
    """Jenis sink eksekusi pada stage.
    -> ("code", None)   : isi stage dieksekusi sebagai kode (eval, sh -c)
       ("file", key)    : file dieksekusi (bash f, source f, . f, ./f)
       None
    """
    if not w:
        return None
    i = 0
    while i < len(w) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w[i]):   # VAR=x cmd
        i += 1
    w = w[i:]
    if not w:
        return None
    cmd = posixpath.basename(w[0])
    if cmd in ("sudo", "exec", "command", "env", "nohup", "time") and len(w) > 1:
        return exec_sink(w[1:], cwd)
    if cmd == "eval":
        return ("code", None)
    if cmd in SHELLS:
        args = w[1:]
        if any(a == "-c" or (a.startswith("-") and "c" in a[1:] and not a.startswith("--")) for a in args):
            return ("code", None)
        rest = [a for a in args if not a.startswith("-")]
        if rest:
            k = normalize(rest[0], cwd)
            return ("file", k) if k else None
        return None
    if cmd in ("source", ".") and len(w) > 1:
        k = normalize(w[1], cwd)
        return ("file", k) if k else None
    if w[0].startswith("./") or w[0].startswith("/"):
        k = normalize(w[0], cwd)
        return ("file", k) if k else None
    return None
