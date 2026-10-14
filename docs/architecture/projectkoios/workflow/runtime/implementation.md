# `projectkoios.workflow.runtime` implementation

> **Status: provisional architecture candidate.**

## Responsibility

Replace the current narrow local runtime rather than stretching its closed event vocabulary. Retain its append-only, request-idempotency, identity-chain, and indeterminate-persistence lessons.

Every state change is an immutable event. Marking and query tables are derived projections. Authoritative orchestration replay is effect-free and action-free: it rehydrates exact retained definitions, plans, events, markings, reservations, occurrences, attempts, results, evidence, and projections without invoking a provider or rerunning even a pure owner action. Missing or corrupt required evidence makes replay fail closed or incomplete; replay never recomputes to repair history. Retry, cancellation, ambiguity, and child correlation must be explicit records and CPN/runtime policy—not inferred from missing files or worker disappearance.

Pure-action re-execution is a separate verification or rebuild operation. With exact pinned implementation, inputs, configuration, and bounds, it may recompute and compare identities, bytes, or values, producing new verification evidence without mutating the original run.

The lifecycle-subnet candidate treats retry as a guarded transition that creates a new attempt token under the same occurrence, cancellation as nonterminal until confirmed, and child cancellation/join as explicit token correlation. The alternative reservation-table candidate must demonstrate equivalent replay and concurrency semantics without creating hidden process state. Architecture review has not selected between them.
