# Skor benchmark: `y-asli`

| Kasus | Grup | Aliran | Label | Sink | Sink alert ARGUS | Longgar | Ketat |
|---|---|---|---|---|---|---|---|
| Y01-runner-temp | Y | tulis ke $RUNNER_TEMP/t.txt → eval "$(cat $RUNNER_TEMP/t.txt)" | V | 1 | – | FN | FN |
| Y02-built-script | Y | skrip dirakit dengan echo > / >> lalu chmod +x dan ./run.sh | V | 1 | – | FN | FN |
| Y03-python-exec | Y | tulis f → python3 -c "exec(open(f).read())" | V | 1 | – | FN | FN |
| Y04-bash-c | Y | tulis f → bash -c "$(cat f)" | V | 1 | – | FN | FN |
| Y05-xargs-sh | Y | tulis f → xargs -I{} sh -c '{}' < f | V | 1 | – | FN | FN |
| Y06-source-event-vars | Y | echo "export T=\"$(jq .issue.title $GITHUB_EVENT_PATH)\"" > vars.sh → source vars.sh | V | 1 | – | FN | FN |
| Y07-cat-copy | Y | tulis f → cat f > g → eval "$(cat g)" | V | 2 | – | FN | FN |
| Y08-headref-sh-c | Y | env BRANCH=${{ github.head_ref }} → echo > f → sh -c "$(< f)" | V | 1 | – | FN | FN |
| Y09-pipe-sh | Y | tulis f → cat f \| sh | V | 1 | – | FN | FN |
| Y10-dot-source | Y | tulis ./env.sh → . ./env.sh | V | 1 | – | FN | FN |
| Y11-while-read-eval | Y | tulis f → while read l; do eval "$l"; done < f | V | 1 | – | FN | FN |
| Y12-js-promises | Y | JS Action fs.promises.writeFile → eval "$(cat f)" | V | 1 | – | FN | FN |
| Y13-js-runner-temp | Y | JS Action tulis path.join(RUNNER_TEMP) → eval "$(cat $RUNNER_TEMP/t.txt)" | V | 1 | – | FN | FN |
| Y14-rm-then-guard | Y | tulis f → rm f → [ -f f ] && eval "$(cat f)" (file sudah tidak ada) | S | – | – | TN | TN |
| Y15-hash-eval | Y | tulis f → eval "H=$(sha256sum < f)" (hanya hash yang dieksekusi) | S | – | – | TN | TN |
| Y16-repo-script | Y | tulis f (tainted), lalu grep -c f dan bash ./build.sh (skrip repo, bukan f) | S | – | – | TN | TN |
| Y17-backup-file | Y | tainted ke f, konstan ke f.bak, eval membaca f.bak | S | – | – | TN | TN |
| Y18-event-number | Y | cp $GITHUB_EVENT_PATH ev.json → eval "N=$(jq .pull_request.number ev.json)" (angka) | S | – | – | TN | TN |

| Subset | Skoring | TP | FN | FP | TN | Recall | Precision | FPR |
|---|---|---|---|---|---|---|---|---|
| Semua kasus | longgar | 0 | 13 | 0 | 5 | 0% | – | 0% |
| Semua kasus | ketat | 0 | 13 | 0 | 5 | 0% | – | 0% |
| Scope utama (K4+K5) | longgar | 0 | 0 | 0 | 0 | – | – | – |
| Scope utama (K4+K5) | ketat | 0 | 0 | 0 | 0 | – | – | – |
| Y held-out | longgar | 0 | 13 | 0 | 5 | 0% | – | 0% |
| Y held-out | ketat | 0 | 13 | 0 | 5 | 0% | – | 0% |
