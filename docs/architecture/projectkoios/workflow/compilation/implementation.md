# `projectkoios.workflow.compilation` implementation

## Responsibility

Preserve the mandatory plan/runtime-binding separation while adapting historical
compiler evidence to the iteration-2 Task model. Compiler and linker APIs use
immutable requests/results, return closed findings, and never return partially
trusted artifacts.

The compiler consumes one Workflow definition plus the exact closure of its Task
definitions. It validates atomic routes, workflow-backed Task targets, child
input/export contracts, acyclic definition references, fragment composition,
and canonical flat parent CPN IR. Each child Workflow is compiled independently.

The linker binds atomic Tasks to exact firer or lifecycle descriptors and binds
workflow-backed Tasks to exact child-plan deployments. It does not select new
semantic mappings or retain live implementations.

Current strict canonical definition and marking codecs remain bounded pure-action
reconstruction primitives. Their schemas and bytes are unchanged; they do not by
themselves implement the complete Task/Workflow plan or authorize runtime state.
