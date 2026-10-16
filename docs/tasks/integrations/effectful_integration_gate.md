# Effectful integration gate

## Objective

Prevent calculator execution, schedulers, OCR processes, remote services, and
other external effects from adopting an incomplete Workflow lifecycle boundary.
This gate is deferred until an owner requests durable effect orchestration; the
existing Simulations typed SCF lifecycle remains the current architecture in the
meantime.

## Task-model prerequisite

An effectful operation is an atomic Task route, not a special kind of Workflow
or a call hidden behind the pure SDK `Firer`. Before this gate can activate, the
common Task model must distinguish immutable Task definition, provider-specific
owner configuration, handler, invocation, occurrence, attempt, and outcome.
A workflow-backed Task uses the separate child-run route rather than this effect
route.

## Gate

Effectful integration remains blocked until Workflow has accepted and tested:

- [ ] Accept and test occurrence- and attempt-scoped identity derivation.
- [ ] Accept and test provider start-key derivation and collision behavior.
- [ ] Accept and test authority admission and revalidation at the effect boundary.
- [ ] Persist durable dispatch intent before external invocation.
- [ ] Accept and test the exact distinction between rejected-before-effect,
  known-not-applied, known-applied-with-failure, and ambiguous outcomes.
- [ ] Accept and test observation and query-only reconciliation.
- [ ] Accept and test separately authorized cancellation.
- [ ] Test worker crash, response loss, restart, and lease-expiry recovery.
- [ ] Prove automatic redispatch is prevented while an outcome is ambiguous.
- [ ] Retain evidence sufficient for deterministic replay and provenance.

## Required proof

At least one isolated provider fixture must complete this checklist. Before a
Simulations SCF migration, equivalent common lifecycle behavior and
backend-substitution rejection must also be demonstrated for both QE and VASP
Task specializations:

- [ ] Exercise a crash before possible effect entry.
- [ ] Exercise a crash after possible effect entry.
- [ ] Exercise duplicate start requests.
- [ ] Exercise a changed request digest under a reused start key.
- [ ] Exercise ambiguous response loss.
- [ ] Exercise reconciliation without repeating the effect.
- [ ] Exercise cancellation races.
- [ ] Exercise worker restart and recovery.

## Exclusions

Passing a pure SDK pilot does not satisfy this gate. An effectful owner action
must not be hidden behind the pure firing path. Registration, submission,
cancellation, and other existing owner lifecycle operations must not be migrated
to Workflow merely because a pure projection pilot succeeded.
