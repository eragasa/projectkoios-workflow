# `projectkoios.workflow.runtime` implementation

> **Status: provisional architecture iteration 2.**

## Responsibility

Retain append-only history, exact identity chains, atomic predecessor
coordination, and closed uncertainty outcomes while separating three Task
execution routes:

1. pure atomic Task execution through an SDK `Firer` and atomic CPN commit;
2. effectful atomic Task execution through durable dispatch, observation,
   reconciliation, and cancellation records; and
3. workflow-backed Task execution through a distinct correlated child Workflow
   run and explicit terminal delivery.

Every state change is immutable evidence. Markings and query tables are derived
projections. Authoritative replay rehydrates exact definitions, plans, bindings,
Task instances, invocations, occurrences, attempts, results, child correlations,
evidence, and markings without invoking an owner or repeating an effect.
Missing or corrupt required evidence fails closed; replay never repairs history
from current defaults.

The implemented experimental pure-action chain is the candidate executor for
route 1. Its existing names and bytes remain compatible. Pure owner
re-execution is a separate verification operation and never mutates the
original run.

Route 2 remains behind the effectful-integration gate. Retry creates a new
attempt; ambiguity prevents automatic redispatch; cancellation is nonterminal
until observed and reconciled.

For route 3, the parent durably retains child-creation intent before creation,
uses an idempotency identity, correlates one distinct child run, and accepts only
an explicitly supported terminal delivery. Child ambiguity, cancellation, or
nonquiescence cannot be relabeled as success. Parent and child commits are
separate and replayable.

Simulations' QE/VASP Task split is owner evidence for route-compatible provider
specialization, not authorization to move backend resources into runtime.
`ksdft2effmass/experiments/` is owner evidence for pure Task composition and
workflow-backed Tasks, not authorization to persist numerical payload bodies.
