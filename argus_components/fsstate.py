# Ekstensi file-state (skripsi): pelacakan aliran taint melalui file dalam satu job.
#
# Semua perilaku baru dikendalikan oleh variabel lingkungan ARGUS_FS (daftar flag dipisah koma).
# ARGUS_FS kosong = perilaku ARGUS asli, tanpa perubahan.
#
#   shell     : file-state untuk step shell (tulis > >> tee, baca cat/$(< f)/dsb., sink eval/sh -c/bash f)
#   eventpath : $GITHUB_EVENT_PATH diperlakukan sebagai file yang isinya dikontrol penyerang
#   js        : JS Action: fs.write* ke path konstan menjadi propagasi ke file-state (bukan sink),
#               dan aliran tulis -> baca file di dalam satu Action dilacak (FileFlowSinks.ql)
#   (v0.2: heredoc, pipe ke shell, cp/mv, kata kunci if/then/do, variabel path literal)
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


class Ctx:
    """Konteks satu step shell: direktori kerja dan variabel shell berisi literal (untuk path)."""
    def __init__(self, cwd=("ws", ""), vars=None):
        self.cwd = cwd
        self.vars = dict(vars or {})

    def expand(self, p):
        def sub(m):
            n = m.group(1)
            return self.vars[n] if n in self.vars else m.group(0)
        return _VAR.sub(sub, p)

    def norm(self, p):
        return normalize(self.expand(_strip_quotes(p)), self.cwd)


_LITERAL = re.compile(r"^[A-Za-z0-9_./~+-]+$")


def literal_assignments(ws):
    """Kata-kata berbentuk NAME=nilai-literal (tanpa $, kutip dilepas) -> dict; None bila bukan statement assignment murni."""
    out = {}
    for x in ws:
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", x)
        if not m:
            return None
        if _LITERAL.match(m.group(2) or "x"):
            out[m.group(1)] = m.group(2)
    return out


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


HD_OPEN = "\x01"
_HEREDOC = re.compile(r"""<<(-?)[ \t]*(['"]?)([A-Za-z_][A-Za-z0-9_]*)\2""")


def _attach_heredocs(cmd):
    """Isi heredoc digabung ke baris pembukanya: <baris> \x01<Q|U><isi dalam hex>\x01 (Q = delimiter dikutip, tanpa ekspansi)."""
    lines, out, i = cmd.split("\n"), [], 0
    while i < len(lines):
        line = lines[i]; i += 1
        m = _HEREDOC.search(line)
        if not m or _outside_quotes_mask(line)[m.start()] is False:
            out.append(line); continue
        body = []
        while i < len(lines) and (lines[i].strip() if m.group(1) else lines[i]) != m.group(3):
            body.append(lines[i]); i += 1
        i += 1
        # isi di-hex supaya ; | & di dalam heredoc tidak memecah statement
        out.append(line + " " + HD_OPEN + ("Q" if m.group(2) else "U") + "\n".join(body).encode().hex() + HD_OPEN)
    return "\n".join(out)


def statements(cmd):
    cmd = _attach_heredocs(cmd.replace("\\\n", " "))
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


KEYWORDS = {"then", "do", "else", "elif", "if", "while", "until", "{", "!", "time", "fi", "done", "}"}


def strip_keywords(w):
    i = 0
    while i < len(w) and w[i] in KEYWORDS:
        i += 1
    return w[i:]


def parse_stage(stage):
    """-> (teks tanpa target tulis, [(target, append)], kata-kata perintah, heredoc)
    heredoc = None atau (dikutip: bool, isi)"""
    heredoc = None
    m = re.search(HD_OPEN + "([QU])(.*?)" + HD_OPEN, stage, re.S)
    if m:
        heredoc = (m.group(1) == "Q", bytes.fromhex(m.group(2)).decode())
        stage = stage[:m.start()] + stage[m.end():]
        stage = _HEREDOC.sub(" ", stage)
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
    w = strip_keywords(words(text))
    if w and posixpath.basename(w[0]) == "tee":
        append = any(x in ("-a", "--append") for x in w[1:])
        for x in w[1:]:
            if not x.startswith("-"):
                writes.append((x, append))
        text = w[0]  # isi tee = input pipe; argumennya adalah target, bukan bacaan
        w = [w[0]]
    return text, writes, w, heredoc


_TOKEN = re.compile(r"""\$\{?[A-Za-z_][A-Za-z0-9_]*\}?(?:/[^\s"'`;|&<>()]*)?|[^\s"'`;|&<>()=]+""")
_VAR = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?")


def mentioned_paths(text, ctx):
    """Kunci file-state yang disebut di teks (argumen, $(cat f), $(< f), dsb.)."""
    keys = []
    for tok in _TOKEN.findall(text):
        k = ctx.norm(tok)
        if k and k not in keys:
            keys.append(k)
    return keys


def env_names(text):
    return list(dict.fromkeys(_VAR.findall(text)))


SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}


def exec_sink(w, ctx):
    """Jenis sink eksekusi pada stage.
    -> ("code", None)   : isi stage dieksekusi sebagai kode (eval, sh -c)
       ("file", key)    : file dieksekusi (bash f, source f, . f, ./f)
       ("stdin", None)  : shell membaca kode dari stdin (... | bash, bash <<EOF)
       None
    """
    w = strip_keywords(w)
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
        return exec_sink(w[1:], ctx)
    if cmd == "eval":
        return ("code", None)
    if cmd in SHELLS:
        args = w[1:]
        if any(a == "-c" or (a.startswith("-") and "c" in a[1:] and not a.startswith("--")) for a in args):
            return ("code", None)
        rest = [a for a in args if not a.startswith("-")]
        if rest:
            k = ctx.norm(rest[0])
            return ("file", k) if k else None
        return ("stdin", None)
    if cmd in ("source", ".") and len(w) > 1:
        k = ctx.norm(w[1])
        return ("file", k) if k else None
    if w[0].startswith("./") or w[0].startswith("/"):
        k = ctx.norm(w[0])
        return ("file", k) if k else None
    return None


def file_ops(w, ctx):
    """cp/mv: -> [(op, src_key, dst_key)]"""
    w = strip_keywords(w)
    if not w or posixpath.basename(w[0]) not in ("cp", "mv"):
        return []
    args = [a for a in w[1:] if not a.startswith("-")]
    if len(args) < 2:
        return []
    srcs, dst = args[:-1], args[-1]
    out = []
    for src in srcs:
        d = dst if len(srcs) == 1 else dst.rstrip("/") + "/" + posixpath.basename(_strip_quotes(src))
        sk, dk = ctx.norm(src), ctx.norm(d)
        if sk and dk:
            out.append((posixpath.basename(w[0]), sk, dk))
    return out
