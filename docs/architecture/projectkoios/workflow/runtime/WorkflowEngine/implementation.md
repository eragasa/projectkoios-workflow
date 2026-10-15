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

## Experimental predecessor-reservation candidate

`ExperimentalWorkflowPureActionReservationService` is a bounded candidate for
the pre-invocation and post-invocation current-state checks. It constructs the
SDK request from the exact linked plan, selected-binding evidence, coordinates,
and inline inputs, then content-identifies a reservation over the plan,
deployment binding, selection evidence, request, predecessor marking/revision,
occurrence, and attempt. A nominal repository ABC owns atomic reserve and
revalidate operations.

The included in-memory repository is thread-safe, non-durable software evidence.
It admits at most one distinct reservation per net-instance predecessor, treats
an exact replay as idempotent, and rejects stale, conflicting, absent, or known
consumed reservations. Its whole-predecessor lock granularity is deliberately
conservative. Durable storage, input-source provenance, owner invocation, CPN
firing, atomic reservation consumption, successor persistence, and replay remain
outside this candidate. In particular, the candidate exposes no standalone
consume operation: reservation consumption must later share the accepted atomic
boundary with CPN firing and persistence.
