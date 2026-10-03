# Ekstensi file-state untuk ARGUS (prototipe skripsi)

Branch `file-state` di atas ARGUS resmi (`purs3lab/Argus`, commit `5ba376d`).
Tujuan: melacak aliran taint `input tainted → tulis file → baca file → sink eksekusi` di dalam satu job GitHub Actions.
Status: **prototipe**, dibuat sebelum bimbingan (29 Sep 2026). Semua keputusan desain yang masih terbuka dibuat sebagai flag supaya mudah diubah.

## 1. Menjalankan

```bash
# dari argus-benchmark/
ARGUS_DIR=../Argus-ext ARGUS_FS=all ./run_all.sh ext-all     # benchmark v3 terkunci
./run_ext.sh                                                  # semua konfigurasi + ablasi
./run_x.sh x-ext ../Argus-ext all                             # set uji eksplorasi X
python3 -m unittest tests/test_fsstate.py -v                  # dari Argus-ext/, unit test parser
```

Container memakai image yang sama dengan ARGUS asli (`argus-argus`). Kode (`argus_components/`) dan query (`qlqueries/`) di-mount, jadi tidak perlu build ulang.

## 2. Flag (`ARGUS_FS`, dipisah koma)

| Flag | Perilaku |
|---|---|
| *(kosong)* | Perilaku ARGUS asli. Dipakai sebagai uji regresi (`ext-off` harus = `asli`). |
| `shell` | File-state untuk step shell: tulis, baca, sink eksekusi di step pembaca. Nilai env `$VAR` yang tainted ikut terbawa ke file. |
| `eventpath` | `$GITHUB_EVENT_PATH` diperlakukan sebagai file yang isinya tainted (payload event). |
| `js` | JS Action: `fs.write*` ke path konstan menjadi propagasi ke file-state, bukan sink. Aliran tulis → baca file di dalam satu Action dilacak (`FileFlowSinks.ql`). |
| `envexec` | (ablasi, di luar scope file) `$VAR` tainted di dalam sink eksekusi (`eval "$VAR"`) dilaporkan. Berbeda dari varian +env yang menandai setiap pemakaian `$VAR`. |
| `all` | `shell,eventpath,js` |

## 3. Model

State: `FS : kunci-path → [TaintObj]`, satu per job (dikosongkan di awal setiap job, karena setiap job memakai runner baru).

| Operasi | Aturan |
|---|---|
| `cmd > f`, `tee f`, `writeFile(Sync)` | `FS[f] = taint(data)`; data bersih → `f` dihapus dari FS (overwrite) |
| `cmd >> f`, `tee -a f`, `appendFile(Sync)` | `FS[f] = FS[f] ∪ taint(data)` |
| `cp a b` / `mv a b` | `FS[b] = FS[a]` (mv juga menghapus `a`) |
| baca: path disebut sebagai argumen, `$(cat f)`, `$(< f)`, `jq … f` | taint stage += `FS[f]` |
| sink: `eval`, `sh/bash -c`, `bash f`, `source f`, `. f`, `./f`, `… \| bash`, `bash <<EOF` | alert di step ini bila taint berasal dari file/event |

- **Data sebuah stage** = input pipe dari stage sebelumnya + `${{ }}` tainted + `$VAR` tainted + isi file yang disebut + isi heredoc (bila delimiter tidak dikutip).
- **Alert** memakai mekanisme ARGUS (`raise_alert`), jadi SARIF-nya sama: `locations` = step asal taint, `relatedLocations` = step pembaca (sink). Log: `ALERT RAISED @ … (file-state)` dan `FILE-STATE write …`.
- **Normalisasi path**: `/abs` tetap; relatif digabung dengan `working-directory` step; `$GITHUB_WORKSPACE/…`, `${{ github.workspace }}/…` → relatif workspace; variabel shell berisi literal (env step atau `F=/tmp/x`) disubstitusi. Path yang masih dinamis (`$(…)`, glob, variabel tak dikenal) → di luar scope, diabaikan.
- **Tidak dihitung ganda**: `${{ }}` langsung di `run:` tetap ditangani ARGUS asli. Alert file-state hanya untuk taint yang berasal dari file/event (dan env bila `envexec`). `GITHUB_ENV`/`GITHUB_OUTPUT` tetap memakai model lama (path berisi `$GITHUB_ENV` tidak dimasukkan ke FS).

## 4. Perubahan kode

| File | Perubahan |
|---|---|
| `argus_components/fsstate.py` (baru) | flag, normalisasi path, parser shell ringan (statement, pipeline, redirect, tee, heredoc, cp/mv, kata kunci `if/then/do`), deteksi sink |
| `taintengine/taintengine.py` | `file_state` per job, `handle_shell_file_flow`, `_fs_write`, propagasi `arg_to_file` dari JS Action |
| `report/action_report.py` | dengan `js`: sink `fs.write*/read*` dari LessDangerousSinks dibuang; hasil `FileFlowSinks` digabung ke `arg_to_sink` |
| `utils/codeql.py` | parsing `FileWrite.bqrs`, `FileFlowSinks.bqrs` (bila ada) |
| `ir/ghworkflowir.py` | `GHRunTask.working_directory` |
| `qlqueries/FileFlowCommon.qll`, `FileWrite.ql`, `FileFlowSinks.ql` (baru) | model tulis/baca `fs` (termasuk `*Sync` dan `fs.promises`), langkah taint tulis → baca path konstan |
| `docker-compose.yml` | image `argus-argus`, mount kode/query/benchmark, teruskan `ARGUS_FS` |

Query asli ARGUS tidak diubah. Query baru ikut dijalankan pada semua mode, tetapi hasilnya hanya dipakai bila flag `js` aktif.

## 5. Keterbatasan prototipe (sengaja, atau belum)

- Parser shell berbasis regex/scan, bukan parser bash penuh. Setiap kata dianggap kandidat path dan dicocokkan dengan FS (over-approximation: `echo t.txt` dianggap "membaca" `t.txt`, tetapi hanya berpengaruh bila `t.txt` tainted dan stage-nya sink).
- Belum dimodelkan: fungsi shell, `xargs`, `sed -i`, `dd`, `install`, redirect `<` ke shell (`bash < f`), subshell kompleks, `set -o` dsb.
- Path dinamis, glob, symlink: di luar scope (sesuai Tabel 3.1 proposal).
- Composite Action dan reusable workflow: file-state tidak dibagi dengan step di dalamnya (engine terpisah).
- JS: hanya sumber `core.getInput`; path harus literal string. Sumber context/env di JS belum dihubungkan ke file-state.
- Step bersyarat (`if:`) tidak dievaluasi (sama dengan ARGUS asli).
- Artifact antar-job: di luar scope.
- Taint file tidak diteruskan ke `GITHUB_ENV`/`GITHUB_OUTPUT` (`echo "X=$(cat f)" >> $GITHUB_ENV` lalu `${{ env.X }}`): ditemukan lewat set probe P (P03, P05), kandidat v0.3.
- Checkout kode PR dan artifact yang diunduh bukan source (CodeQL Actions sudah memodelkannya secara path-insensitive; lihat `argus-benchmark/LAPORAN.md` §9).
