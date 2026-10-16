# Selective Workflow runtime adoption for Simulations

## Objective

Preserve Simulations' domain-focused SCF architecture while using Workflow only
where the QE pilot demonstrates a concrete need for durable pure-action safety.

## Accepted comparison result

The existing Simulations architecture is better for its current public role:

- `PwDftScfWorkflowFacade` exposes typed domain actions, events, status, and
  outcomes;
- `LocalPwDftScfWorkflow` and `LocalSnakesRun` provide a small engine-hiding local
  lifecycle; and
- registration, submission, completion, failure, and analysis remain explicit
  owner-domain concepts.

The experimental Workflow path is better for a narrower operational role:

- authoritative immutable-source admission;
- exact occurrence reservation and revalidation;
- validated cross-repository owner invocation;
- atomic durable CPN state advancement; and
- compact, CPN, lifecycle, and safety replay without owner reinvocation.

Accordingly, the QE artifact-set integration is additive. It is not evidence for
replacing the existing SCF facade or local SNAKES lifecycle.

## Current constraints

- [x] Keep the protected Simulations core independent of Workflow runtime
  implementations.
- [x] Keep the reusable `projectkoios.simulations.workflows` layer independent of
  Workflow service, persistence, compiler, and CPN runtime implementations.
- [x] Place the full-runtime source adapter in the outward
  `projectkoios.adapters` namespace behind an explicit optional dependency.
- [x] Keep owner requests, results, codecs, identities, and artifact semantics in
  Simulations.
- [x] Prove the bounded QE pure action can commit and replay without replacing
  the owner lifecycle architecture.
- [ ] Retain dependency tests that fail if the protected core or reusable owner
  workflow layer begins importing the full Workflow runtime.

## Future replacement gate

Do not implement a Workflow-backed `PwDftScfWorkflowFacade` unless all of the
following become true:

- [ ] the effectful integration gate accepts dispatch, ambiguous-outcome,
  reconciliation, cancellation, and restart semantics;
- [ ] the Workflow implementation passes behavioral-equivalence tests for every
  existing typed action, accepted event, status, terminal outcome, and failure
  path;
- [ ] persistence and replay provide a required operational property that the
  existing local architecture cannot provide acceptably;
- [ ] the owner explicitly accepts the migration and compatibility policy; and
- [ ] the local SNAKES implementation has a recorded retention, deprecation, or
  removal decision.

## Exclusions

This task does not authorize calculator execution, a backend migration, removal
of SNAKES, provider objects in reusable workflow contracts, or use of the pure
`Firer` boundary for registration or submission effects.
