/**
 * @name FileWrite
 * @description Ekstensi file-state: input Action yang ditulis ke file dengan path konstan
 * @kind path-problem
 * @tags security
 * @id javascipt/filewrite
 * @precision medium
 */

import javascript
import DataFlow::PathGraph
import FileFlowCommon

class FileWriteConfiguration extends TaintTracking::Configuration {
    FileWriteConfiguration() { this = "FileWrite" }

    override predicate isSource(DataFlow::Node source) { source = coreSources() }

    override predicate isSink(DataFlow::Node sink) { sink = fsWriteCall().getArgument(1) }
}

from FileWriteConfiguration cfg, DataFlow::PathNode source, DataFlow::PathNode sink, CallExpr e, Expr arg, DataFlow::CallNode w
where cfg.hasFlowPath(source, sink) and
    e = source.getNode().asExpr() and
    arg = e.getArgument(0) and
    w = fsWriteCall() and
    sink.getNode() = w.getArgument(1)
select arg, source, sink, w.getCalleeName(), constPath(w)
