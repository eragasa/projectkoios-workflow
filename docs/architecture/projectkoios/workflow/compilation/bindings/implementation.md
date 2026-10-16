# `projectkoios.workflow.compilation.bindings` implementation

## Responsibility

Represent deployment state as frozen descriptors and opaque handles. Keep live
owner handlers, firers, providers, and child-run implementations in isolated
process-local tables keyed by retained binding identity.

Enforce complete ordered closure, exact definition equality, Task specialization,
route/effect shape, protocol compatibility, environment digest, output mapping,
and child plan identity. A Workflow-backed Task binding cannot replace its
plan-selected child target, inline the child graph, or reuse a parent run as the
child run.

Never accept identity-only agreement when complete descriptor content differs.
Provider-specific resources such as QE executables or VASP execution requests
remain owner-controlled and absent from generic binding artifacts.
