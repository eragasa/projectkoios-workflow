# Experimental pure-action reservation evidence

## Scope

This record covers the bounded Workflow-owned predecessor-reservation candidate
for one pure external action. It does not claim complete `WorkflowEngine`,
`WorkflowExecutionPlan`, `WorkflowExecutionBindings`, persistence, or canonical
CPN-bindings conformance.

## Implemented boundary

- `ExperimentalWorkflowPureActionReservation` content-identifies the exact:
  - experimental plan and deployment-binding identities;
  - structural selected-binding evidence identity;
  - SDK request identity;
  - net instance, predecessor marking, and predecessor revision; and
  - occurrence, attempt, and attempt ordinal.
- `ExperimentalWorkflowPureActionReservationService` constructs the SDK request
  from the plan-selected mapping and selected-binding evidence before attempting
  reservation. Failed stale or conflicting attempts do not expose an invocable
  request through the result.
- `ExperimentalWorkflowPureActionReservationRepository` is a nominal ABC for
  atomic reserve and revalidate operations.
- `ExperimentalInMemoryPureActionReservationRepository` is a thread-safe,
  non-durable reference implementation. It admits one distinct reservation per
  current net-instance predecessor, returns idempotence only for the exact same
  reservation, and rejects conflicting concurrent attempts.
- Post-owner revalidation distinguishes current, absent, stale, and already
  consumed reservations. Consumed identities are loaded as repository state;
  this candidate intentionally exposes no independent consumption operation.

## Negative and concurrency evidence

Tests prove that the candidate:

- rejects stale predecessor coordinates before exposing the request;
- detects a changed marking/revision after reservation and prevents revision
  rewind from resurrecting it;
- detects an already consumed reservation;
- rejects substitution of the plan-selected representation profile;
- derives a different reservation identity when exact request bytes change;
- rejects a directly forged reservation identity during reconstruction; and
- allows only one of two concurrent distinct attempts to reserve the same
  predecessor.

Validation from the uncommitted candidate on base Workflow revision `d8f81c5`:

- focused reservation tests: `8 passed`;
- full Workflow suite: `328 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `41` source files;
- Ruff checks and formatting, architecture documentation, documentation links,
  diff checks, and shadow provenance tests: passed;
- reservation source SHA-256:
  `2228db60a5535126d88b73add10454b0555b591d99c723806bec0148e523847f`;
- focused test source SHA-256:
  `3bd52b3709e20a163a27782df773312e0f06609b85fe3a1a55f86126d646c9ce`;
- two wheels built with `SOURCE_DATE_EPOCH=315532800` were byte-identical;
- wheel SHA-256:
  `0c41b7744f720789e0419b65078004117ac3ab15ebb6d67ac62a9383731ffb6b`;
- the wheel installed into the isolated Workflow/SDK/Simulations pilot
  environment, passed dependency checking, exposed the nominal reservation
  types, and preserved the existing cross-wheel mapping identities.

## Remaining authority gaps

This candidate does not establish input-source provenance, durable reservation
storage, owner invocation, result admission, CPN firing, atomic reservation
consumption, successor-marking persistence, rollback, or replay. Direct record
construction is structural data only; runtime authority comes from a repository
reporting the exact reservation as current. Reservation consumption must later
be coupled to firing and persistence in one accepted atomic boundary.
