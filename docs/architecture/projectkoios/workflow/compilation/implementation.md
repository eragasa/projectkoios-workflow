# `projectkoios.workflow.compilation` implementation

## Responsibility

Adapt the architecture of historical `ksdft2effmass/workflows/{definitions,planning,bindings}.py` at commit `5210b760...`, while replacing the earlier task/gate executable graph with canonical CPN IR.

The DEFECT00003 plan/runtime-binding separation is mandatory. Compiler and linker APIs use action requests/results, return closed validation findings, and produce no partially trusted plan. Identity structure should remain compact: content-address the complete artifacts rather than introducing nominal wrappers for every field.

The bounded pure-action candidate owns strict canonical reconstruction codecs for
its exact flat shadow-CPN definition and semantic marking representations.
Decoders accept only their selected profile, closed field shapes, exact built-in
JSON types, and bounded values; a successful reconstruction must re-encode to
the original bytes exactly. The CPN-plan candidate validates retained definition
bytes through this full decoder before accepting their nominal identity and
digest.

The marking codec is a reconstruction primitive for a later retained replay
bundle. Marking bodies do not enter compact commit events, and the current codec
does not by itself authorize runtime state, select an execution profile, or
claim complete `WorkflowExecutionPlan` or CPN-bindings conformance.
