"""Unit test parser shell dan normalisasi path ekstensi file-state.
Jalankan dari root Argus-ext:  python3 -m unittest tests/test_fsstate.py -v
(Tidak butuh Docker/CodeQL; fsstate.py tidak bergantung pada modul ARGUS lain.)"""
import importlib.util
import pathlib
import unittest

_p = pathlib.Path(__file__).resolve().parents[1] / "argus_components" / "fsstate.py"
_spec = importlib.util.spec_from_file_location("fsstate", _p)
fs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fs)

WS = ("ws", "")


def stages(cmd, ctx=None):
    ctx = ctx or fs.Ctx(WS)
    out = []
    for st in fs.statements(cmd):
        a = fs.literal_assignments(fs.words(st))
        if a is not None:
            ctx.vars.update(a)
            continue
        for sg in fs.pipeline(st):
            text, writes, words, here = fs.parse_stage(sg)
            out.append({"text": text, "writes": writes, "sink": fs.exec_sink(words, ctx),
                        "reads": fs.mentioned_paths(text, ctx), "ops": fs.file_ops(words, ctx), "here": here})
    return out


class TestNormalize(unittest.TestCase):
    def test_bentuk_path(self):
        self.assertEqual(fs.normalize("/tmp/t.txt"), "abs:/tmp/t.txt")
        self.assertEqual(fs.normalize("./t.txt"), "ws:t.txt")
        self.assertEqual(fs.normalize("t.txt"), "ws:t.txt")
        self.assertEqual(fs.normalize('"$GITHUB_WORKSPACE/t.txt"'), "ws:t.txt")
        self.assertEqual(fs.normalize("${{ github.workspace }}/a/../t.txt"), "ws:t.txt")
        self.assertEqual(fs.normalize("t.txt", ("ws", "sub")), "ws:sub/t.txt")
        self.assertEqual(fs.normalize('"$GITHUB_EVENT_PATH"'), fs.EVENT_KEY)

    def test_di_luar_scope(self):
        for p in ["$F", "/tmp/*.txt", "/dev/null", "-c", "~/x", "$(date).txt"]:
            self.assertIsNone(fs.normalize(p), p)

    def test_variabel_literal(self):
        ctx = fs.Ctx(WS, {"F": "/tmp/t.txt"})
        self.assertEqual(ctx.norm('"$F"'), "abs:/tmp/t.txt")
        self.assertEqual(ctx.norm("${F}"), "abs:/tmp/t.txt")


class TestShell(unittest.TestCase):
    def test_tulis_dan_append(self):
        s = stages("printf '%s' \"$T\" > /tmp/a; echo x >> /tmp/b 2>/dev/null")
        self.assertEqual(s[0]["writes"], [("/tmp/a", False)])
        self.assertEqual(s[1]["writes"], [("/tmp/b", True)])

    def test_stderr_bukan_data(self):
        self.assertEqual(stages("cmd 2> /tmp/err.log")[0]["writes"], [])

    def test_tee(self):
        s = stages('echo "$T" | tee -a /tmp/t.txt')
        self.assertEqual(s[1]["writes"], [("/tmp/t.txt", True)])
        self.assertNotIn("abs:/tmp/t.txt", s[1]["reads"])

    def test_sink(self):
        self.assertEqual(stages('eval "$(cat /tmp/t.txt)"')[0]["sink"], ("code", None))
        self.assertEqual(stages('bash -c "$(< f)"')[0]["sink"], ("code", None))
        self.assertEqual(stages("source ./x.sh")[0]["sink"], ("file", "ws:x.sh"))
        self.assertEqual(stages("cat f | bash")[1]["sink"], ("stdin", None))
        self.assertIsNone(stages("wc -c /tmp/t.txt")[0]["sink"])
        self.assertIsNone(stages("cat /tmp/t.txt")[0]["sink"])

    def test_bacaan(self):
        self.assertIn("abs:/tmp/t.txt", stages('eval "$(< /tmp/t.txt)"')[0]["reads"])
        self.assertIn(fs.EVENT_KEY, stages('jq -r .x "$GITHUB_EVENT_PATH" > f')[0]["reads"])

    def test_kata_kunci(self):
        s = stages('if [ -f f ]; then eval "$(cat f)"; fi')
        self.assertEqual(s[1]["sink"], ("code", None))

    def test_heredoc(self):
        s = stages("cat > /tmp/t.sh <<EOF\n$T; a | b\nEOF\nbash /tmp/t.sh")
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0]["here"], (False, "$T; a | b"))
        self.assertEqual(s[0]["writes"], [("/tmp/t.sh", False)])
        self.assertEqual(stages("cat <<'EOF' > f\n$T\nEOF")[0]["here"], (True, "$T"))

    def test_cp_mv(self):
        self.assertEqual(stages("cp /tmp/a /tmp/b")[0]["ops"], [("cp", "abs:/tmp/a", "abs:/tmp/b")])
        self.assertEqual(stages("mv -f a b/")[0]["ops"], [("mv", "ws:a", "ws:b")])

    def test_assignment(self):
        ctx = fs.Ctx(WS)
        s = stages('F=/tmp/t.txt; eval "$(cat "$F")"', ctx)
        self.assertIn("abs:/tmp/t.txt", s[0]["reads"])

    def test_komentar_dan_kutip(self):
        s = stages("echo 'a > b; c' # x > y")
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0]["writes"], [])


if __name__ == "__main__":
    unittest.main()
