# `projectkoios.workflow.compilation` implementation

## Responsibility

Adapt the architecture of historical `ksdft2effmass/workflows/{definitions,planning,bindings}.py` at commit `5210b760...`, while replacing the earlier task/gate executable graph with canonical CPN IR.

The DEFECT00003 plan/runtime-binding separation is mandatory. Compiler and linker APIs use action requests/results, return closed validation findings, and produce no partially trusted plan. Identity structure should remain compact: content-address the complete artifacts rather than introducing nominal wrappers for every field.
