# `projectkoios.workflow.runtime` architecture

> **Status: provisional architecture iteration 2.** Pure atomic Task execution is
> implemented as a bounded experimental path; effect and child-run lifecycles
> remain incomplete.

## Responsibility

Runtime owns durable Workflow runs around the pure CPN kernel: marking
revisions, selected bindings, reservations, Task invocations, transition
occurrences, attempts, pure firer coordination, effect lifecycle correlation,
child Workflow runs, terminal delivery, cancellation, reconciliation,
checkpoints, and replay.

A parent run contains Task invocations. Atomic Tasks use pure or effectful
execution routes. A workflow-backed Task creates a separate child run with its
own plan, marking, history, and replay. Parent and child state are never merged;
only an admitted correlated child terminal delivery may supply the parent Task
result.

Runtime does not own source compilation, provider discovery, domain result
semantics, scientific acceptance, or pure kernel rules. Actions, events, UI work
items, lifecycle commands, and CPN transitions are projections or evidence, not
substitutes for Task, occurrence, attempt, or run identity.
