# Argus-FS: taint tracking through files in GitHub Actions

An extension of [ARGUS](https://github.com/purs3lab/Argus) (Muralee et al., USENIX Security 2023), a static taint analyser for GitHub Actions workflows. ARGUS follows untrusted input from a workflow trigger to a code-execution sink, but its authors note in Section 5.6 of the paper that it *"does not track taint flows through files"*.

Argus-FS closes that gap for files written and read inside one job. It adds a per-job **file state** that follows tainted data from the step that writes a file to the step that executes it.

```yaml
on: pull_request_target            # runs with write permissions on a PR from anyone
jobs:
  j:
    runs-on: ubuntu-latest
    steps:
      - name: write
        env:
          TITLE: '${{ github.event.pull_request.title }}'   # attacker-controlled
        run: printf '%s' "$TITLE" > /tmp/t.txt
      - name: sink
        run: eval "$(cat /tmp/t.txt)"                      # code injection
```

None of ARGUS, CodeQL for Actions, zizmor or poutine reports an injection in this workflow. Argus-FS reports a code injection in step `sink`, with step `write` as the source.

## Results

All numbers are per test case, with strict scoring: a vulnerable case counts as detected only when the alert points at the labelled sink step. Raw SARIF and per-case tables are in [`benchmark/results/`](benchmark/results).

**Locked benchmark (31 cases, 18 vulnerable / 13 safe).** The cases were written and hashed (`LOCK.sha256`) before any extension code existed.

| Subset | Metric | ARGUS | **Argus-FS** | zizmor | poutine | CodeQL (Actions + JS) |
|---|---|---|---|---|---|---|
| File flows (shell, JS Action → shell) | recall | 0% | **100%** | 0% | 0% | 0% |
| File flows | false positive rate | 12% | **0%** | 0% | 0% | 0% |
| File flow inside one JS Action | recall | 50% | **100%** | 0% | 0% | 0% |
| All 31 cases | recall | 28% | **89%** | 22% | 6% | 17% |
| All 31 cases | precision | 71% | **100%** | 80% | 100% | 100% |

**Held-out set Y (18 cases, 13 vulnerable / 5 safe).** The cases and the expected results were locked before the extension ran on them. The extension ran once, at tag `v0.2-fs`, and no fixes were made before reporting.

| Tool | Recall | Precision | FPR |
|---|---|---|---|
| ARGUS | 0% | – | 0% |
| **Argus-FS v0.2** | **62%** | **80%** | **40%** |
| zizmor, poutine, CodeQL for Actions | 0% | – | 0% |

The gap between the two tables is the honest part of the result. The locked benchmark shows that the prototype meets the patterns it was designed for. The held-out set shows how it generalises to idioms it was not designed for. The misses on set Y (`$RUNNER_TEMP` paths, `xargs sh -c`, `python -c exec`, `while read; eval`) and the false positives (`rm f`, hashing) are the [v0.3 roadmap](docs/EXTENSION.md#6-roadmap-v03).

**Other checks**

- Regression: with `ARGUS_FS` empty, the extended code gives output identical to original ARGUS on 31/31 cases (`benchmark/compare.py asli ext-off --same`).
- Ablation: each of the three components (`shell`, `eventpath`, `js`) is needed. Turning off any one of them loses cases.
- Real workflows: 2,332 public workflows were screened, and ARGUS and Argus-FS were compared on 40 of them that analysed successfully. Alerts were identical (0 new, 0 lost) at +7% analysis time. The vulnerable pattern did not appear in this sample, so this is a stability check, not a precision measurement. Per-repository details are kept private.
- Replication: the original ARGUS image reproduces the authors' saved results on 8/8 bundled examples.

## How it works

ARGUS builds a dependency graph of a workflow and propagates taint between steps only through channels it models (`GITHUB_ENV`, `GITHUB_OUTPUT`, step outputs). A plain file has no model, so taint stops at the write.

Argus-FS keeps `FS: path → taint` for each job:

- **write** (`>`, `tee`, `fs.writeFile[Sync]`): `FS[path] = taint(data)`. A clean write overwrites and clears it.
- **append** (`>>`, `tee -a`, `fs.appendFile[Sync]`): union of the old and new taint.
- **copy/move** (`cp`, `mv`): the taint follows the file.
- **read** (`cat f`, `$(< f)`, `jq … f`, file as an argument): the reading stage inherits `FS[path]`.
- **sink** (`eval`, `bash -c`, `source f`, `./f`, `… | bash`, heredoc to a shell): alert in the reading step.

Paths are normalised against `working-directory`, `$GITHUB_WORKSPACE` and literal shell variables. `$GITHUB_EVENT_PATH` is a tainted file. For JS Actions, two new CodeQL queries turn `fs` writes to a constant path into propagation instead of a sink.

Every behaviour is behind the `ARGUS_FS` flag (`shell`, `eventpath`, `js`, `all`). Design, code changes and limitations: [`docs/EXTENSION.md`](docs/EXTENSION.md).

## Quick start

Requirements: Docker with Compose. The image is about 6.5 GB (CodeQL included).

```bash
git clone <this repo> && cd <this repo>
# the compose file mounts the benchmark case repos, so generate them once (needs git and PyYAML)
(cd benchmark && for g in make_benchmark make_explore make_heldout make_probe; do python3 $g.py; done)
docker compose build

# analyse a repository with the extension on
ARGUS_FS=all docker compose run --rm argus --mode repo --url https://github.com/<owner>/<repo> --branch main
# SARIF lands in results/
```

Leave `ARGUS_FS` unset to get original ARGUS behaviour. All upstream options (`--mode action`, `--commit`, `--workflow-path`, …) still work; see [`docs/UPSTREAM_README.md`](docs/UPSTREAM_README.md).

## Reproducing the benchmark

```bash
cd benchmark
python3 make_benchmark.py --verify    # must print OK (cases generated in Quick start)
sha256sum -c LOCK-y.sha256 LOCK-p.sha256

./run_all.sh asli                     # original behaviour (ARGUS_FS empty)
ARGUS_FS=all ./run_all.sh ext-all     # extension
python3 compare.py asli ext-off --same
./run_ext.sh                          # every configuration and ablation, about 2 hours
```

Run labels follow the original notes: `asli` = original ARGUS, `ext-*` = extension, `abl-*` = ablation. Every test case is a git repository generated by a script, so the labels, the workflows and the locks all come from one source. `run_all.sh` refuses to start if a case no longer matches `LOCK.sha256`.

| Set | Generator | Cases | Role |
|---|---|---|---|
| v3 benchmark | `make_benchmark.py` | 31 (K1 control, K2 cross-module JS, K3 file inside a JS Action, K4 file between shell steps, K5 JS Action → file → shell) | locked before implementation, main metrics |
| X | `make_explore.py` | 12 | exploration; used for development, so no generalisation claim |
| Y | `make_heldout.py` | 18 | held-out, run once |
| P | `make_probe.py` | 6 | compares the CodeQL for Actions file model with Argus-FS |

Tool comparison (zizmor 1.30.1, poutine 1.1.6, CodeQL 2.27.1): `benchmark/tools-compare/run_tools.sh` with the binaries in `tools/` or set `TOOLS_DIR` and `ZIZMOR`.

## Limitations

- The shell parser is a scanner, not a full bash parser.
- Dynamic paths, globs, symlinks, artifacts across jobs, composite Actions and reusable workflows are out of scope.
- File taint does not yet flow into `GITHUB_ENV`/`GITHUB_OUTPUT`.
- A checked-out PR is not treated as a tainted file. CodeQL for Actions covers that case, path-insensitively, so the two tools complement each other (probe set P).
- The benchmark and the extension have the same author. The locks and the held-out set reduce this bias, but they do not remove it.

## Author

Ferrel Destatiananda Edwardo ([@DestaBanget](https://github.com/DestaBanget)): file-state extension, benchmark and evaluation.

## Credits and license

Built on [purs3lab/Argus](https://github.com/purs3lab/Argus) at commit `5ba376d`. All upstream history is kept, and the extension starts at tag `v0.1-fs`. If you use ARGUS in research, cite the original paper:

```bibtex
@inproceedings{muralee2023Argus,
  title={ARGUS: A Framework for Staged Static Taint Analysis of GitHub Workflows and Actions},
  author={S. Muralee, I. Koishybayev, A. Nahapetyan, G. Tystahl, B. Reaves, A. Bianchi, W. Enck,
    A. Kapravelos, A. Machiry},
  booktitle={32nd USENIX Security Symposium (USENIX Security 23)},
  year={2023},
}
```

GPL-3.0, same as upstream. See [`LICENSE`](LICENSE).
