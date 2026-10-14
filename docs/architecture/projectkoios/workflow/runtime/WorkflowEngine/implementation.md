# `WorkflowEngine` implementation

## Responsibility

Adapt the invocation invariants of historical `workflows/engine.py`, blob
`cd39ac8e9684ff08ba012d8dda50bc089293969f`, while generalizing beyond
synchronous in-process execution.

The engine accepts the exact binding aggregate produced by the linker. For one
pure external action it must:

1. load the exact predecessor marking, selected binding, reservation,
   transition-firer binding, and result-mapping descriptor;
2. validate SDK descriptor, occurrence, attempt, request, result variant, role,
   codec, representation, bounds, and complete request/result correlation;
3. invoke the mapping as a pure operation and validate its candidate external
   variable against the compiled transition;
4. revalidate the predecessor revision, marking identity, selected CPN binding,
   and reservation immediately before firing;
5. call `ColoredPetriNetTransitionFirer` only for admitted success; and
6. atomically retain SDK request/result/evidence, mapping identity, external
   binding, firing audit, successor marking, and occurrence history.

For a canonical ASCII logical-identity output, admission rejects whitespace,
controls, non-ASCII data, machine paths, trailing bytes, an incompatible CPN
value kind, and any attempt to use an evidence payload digest as the owner
identity. Workflow treats the accepted string as opaque and imports no owner
class or codec implementation.

Replay rehydrates the retained records and never reinvokes the owner firer or
recomputes an identity to repair missing evidence. Pure actions, external
effects, and nested routes retain distinct lifecycles. Uncaught provider
exceptions are contained by the worker boundary; rejected, failed, ambiguous,
or stale outcomes never reach pure CPN firing.
