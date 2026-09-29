/**
 * Ekstensi file-state (skripsi): model pemanggilan tulis/baca file pada modul `fs`.
 * Hanya dipakai oleh FileWrite.ql dan FileFlowSinks.ql; query asli ARGUS tidak berubah.
 */
import javascript

/** Pemanggilan yang menulis data (argumen ke-1) ke path (argumen ke-0). */
DataFlow::CallNode fsWriteCall() {
    result = DataFlow::moduleImport("fs").getAMemberCall(["writeFile", "writeFileSync", "appendFile", "appendFileSync"]) or
    result = DataFlow::moduleImport("fs").getAPropertyRead("promises").getAMemberCall(["writeFile", "appendFile"]) or
    result = DataFlow::moduleImport("fs/promises").getAMemberCall(["writeFile", "appendFile"])
}

/** Pemanggilan yang membaca isi file pada path (argumen ke-0). */
DataFlow::CallNode fsReadCall() {
    result = DataFlow::moduleImport("fs").getAMemberCall(["readFile", "readFileSync"]) or
    result = DataFlow::moduleImport("fs").getAPropertyRead("promises").getAMemberCall("readFile") or
    result = DataFlow::moduleImport("fs/promises").getAMemberCall("readFile")
}

/** Path konstan (literal string) dari argumen ke-0. Path dinamis di luar scope. */
string constPath(DataFlow::CallNode c) {
    result = c.getArgument(0).asExpr().getStringValue()
}

/**
 * Langkah taint tambahan: data yang ditulis ke path P mengalir ke hasil pembacaan path P yang sama.
 * - readFileSync / fs.promises.readFile: nilai kembalian.
 * - readFile(p, [opsi], callback): parameter ke-1 callback.
 */
predicate fileTaintStep(DataFlow::Node pred, DataFlow::Node succ) {
    exists(DataFlow::CallNode w, DataFlow::CallNode r |
        w = fsWriteCall() and r = fsReadCall() and
        constPath(w) = constPath(r) and
        pred = w.getArgument(1) and
        (
            (r.getCalleeName() != "readFile" or not exists(r.getABoundCallbackParameter(r.getNumArgument() - 1, 1))) and succ = r
            or
            succ = r.getABoundCallbackParameter(r.getNumArgument() - 1, 1)
        )
    )
}

DataFlow::Node coreSources() {
    result = DataFlow::moduleImport("@actions/core").getAMemberCall("getInput") or
    result = DataFlow::moduleImport("@actions/core").getAMemberCall("getMultilineInput")
}
