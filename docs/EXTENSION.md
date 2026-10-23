# File-state extension: design notes

This document describes the file-state layer added on top of ARGUS (`purs3lab/Argus`, commit `5ba376d`).
Goal: track the taint flow `tainted input → write file → read file → execution sink` inside one GitHub Actions job.

Status: research prototype (`v0.2-fs`). Every design decision that is still open is a flag, so it can be changed without a rewrite.

## 1. Running

```bash
docker compose build                                            # once; produces image argus-argus
ARGUS_FS=all docker compose run --rm argus --mode repo --url <repo> --branch <branch>

cd benchmark
python3 make_benchmark.py && python3 make_explore.py && python3 make_heldout.py && python3 make_probe.py
ARGUS_FS=all ./run_all.sh ext-all        # locked v3 benchmark
./run_ext.sh                             # all configurations and ablations (about 2 hours)
./run_x.sh x-ext .. all                  # exploration set X

cd .. && python3 -m unittest tests/test_fsstate.py -v   # shell parser unit tests
```

The code (`argus_components/`) and queries (`qlqueries/`) are mounted into the container, so changes do not need a rebuild.

## 2. Flags (`ARGUS_FS`, comma separated)

| Flag | Behaviour |
|---|---|
| *(empty)* | Original ARGUS behaviour. Used as the regression test (`ext-off` must equal `asli`). |
| `shell` | File state for shell steps: writes, reads, and execution sinks in the reader step. A tainted `$VAR` value flows into the file. |
| `eventpath` | `$GITHUB_EVENT_PATH` is treated as a file whose content is tainted (the event payload). |
| `js` | JS Action: `fs.write*` to a constant path becomes propagation into file state, not a sink. Write → read flows inside one Action are tracked (`FileFlowSinks.ql`). |
| `envexec` | (ablation, outside the file scope) report a tainted `$VAR` inside an execution sink (`eval "$VAR"`). Unlike the `+env` variant, it does not flag every use of `$VAR`. |
| `all` | `shell,eventpath,js` |

## 3. Model

State: `FS : path-key → [TaintObj]`, one per job. It is cleared at the start of every job, because every job runs on a fresh runner.

| Operation | Rule |
|---|---|
| `cmd > f`, `tee f`, `writeFile(Sync)` | `FS[f] = taint(data)`; clean data removes `f` from FS (overwrite) |
| `cmd >> f`, `tee -a f`, `appendFile(Sync)` | `FS[f] = FS[f] ∪ taint(data)` |
| `cp a b` / `mv a b` | `FS[b] = FS[a]` (`mv` also removes `a`) |
| read: path given as an argument, `$(cat f)`, `$(< f)`, `jq … f` | stage taint += `FS[f]` |
| sink: `eval`, `sh/bash -c`, `bash f`, `source f`, `. f`, `./f`, `… \| bash`, `bash <<EOF` | alert in this step when the taint comes from a file or the event payload |

- **Stage data** = pipe input from the previous stage + tainted `${{ }}` + tainted `$VAR` + content of referenced files + heredoc body (when the delimiter is unquoted).
- **Alerts** reuse the ARGUS mechanism (`raise_alert`), so the SARIF format does not change: `locations` = the step where the taint originates, `relatedLocations` = the reader step (sink). Log lines: `ALERT RAISED @ … (file-state)` and `FILE-STATE write …`.
- **Path normalisation**: `/abs` stays as is; relative paths join the step `working-directory`; `$GITHUB_WORKSPACE/…` and `${{ github.workspace }}/…` become workspace-relative; shell variables that hold a literal (step `env` or `F=/tmp/x`) are substituted. Paths that stay dynamic (`$(…)`, globs, unknown variables) are out of scope and ignored.
- **No double counting**: `${{ }}` directly in `run:` is still handled by original ARGUS. File-state alerts only fire for taint that comes from a file or the event payload (and env with `envexec`). `GITHUB_ENV`/`GITHUB_OUTPUT` keep the original model (paths containing `$GITHUB_ENV` never enter FS).

## 4. Code changes

| File | Change |
|---|---|
| `argus_components/fsstate.py` (new) | flags, path normalisation, light shell parser (statements, pipelines, redirects, `tee`, heredoc, `cp`/`mv`, `if/then/do` keywords), sink detection |
| `taintengine/taintengine.py` | per-job `file_state`, `handle_shell_file_flow`, `_fs_write`, `arg_to_file` propagation from JS Actions |
| `report/action_report.py` | with `js`: `fs.write*/read*` sinks from `LessDangerousSinks` are dropped; `FileFlowSinks` results are merged into `arg_to_sink` |
| `utils/codeql.py` | parse `FileWrite.bqrs` and `FileFlowSinks.bqrs` when present |
| `ir/ghworkflowir.py` | `GHRunTask.working_directory` |
| `qlqueries/FileFlowCommon.qll`, `FileWrite.ql`, `FileFlowSinks.ql` (new) | `fs` write/read model (including `*Sync` and `fs.promises`), taint step from write to read of a constant path |
| `docker-compose.yml` | image `argus-argus`, mounts for code, queries and benchmark, passes `ARGUS_FS` |

The original ARGUS queries are not changed. The new queries run in every mode, but their results are only used when the `js` flag is on.

## 5. Known limitations

- The shell parser is a regex/scan parser, not a full bash parser. Every word is a path candidate and is matched against FS. This over-approximates (`echo t.txt` counts as "reading" `t.txt`), but it only matters when `t.txt` is tainted and the stage is a sink.
- Not modelled yet: shell functions, `xargs`, `sed -i`, `dd`, `install`, `bash < f`, complex subshells, `set -o`.
- Dynamic paths, globs, symlinks: out of scope.
- Composite Actions and reusable workflows: file state is not shared with their inner steps (separate engine).
- JS: only `core.getInput` is a source, and the path must be a string literal. Context and env sources in JS are not connected to file state yet.
- Conditional steps (`if:`) are not evaluated (same as original ARGUS).
- Artifacts across jobs: out of scope.
- File taint is not forwarded into `GITHUB_ENV`/`GITHUB_OUTPUT` (`echo "X=$(cat f)" >> $GITHUB_ENV`, then `${{ env.X }}`). Found with probe set P (P03, P05).
- A checked-out PR and downloaded artifacts are not sources. CodeQL for Actions already models these, path-insensitively.
- Found on held-out set Y: `$RUNNER_TEMP`/`$HOME` paths are treated as dynamic; `python -c exec`, `xargs … sh -c` and `while read; eval` are not sinks; `rm f` does not clear state; hashing is not a sanitiser; `cp $GITHUB_EVENT_PATH x` does not copy event taint.

## 6. Roadmap (v0.3)

Ordered from cheapest to most expensive:

1. `$RUNNER_TEMP`, `$HOME` and similar runner variables as symbolic path bases, like `GITHUB_WORKSPACE`.
2. `cp`/`mv` from `$GITHUB_EVENT_PATH`; `rm` clears state.
3. File taint into `GITHUB_ENV`/`GITHUB_OUTPUT`.
4. `xargs`, `find -exec`, `python -c`, `node -e` as sinks.
5. Fix path keys built from `${{ matrix.* }}` and redirects to workspace variables (seen on real workflows, no effect on alerts).

After v0.3, sets X, P and Y are all development sets. A new held-out set is required before reporting generalisation numbers again.
