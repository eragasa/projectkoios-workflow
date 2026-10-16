# Selective Workflow runtime adoption for Simulations

## Objective

Preserve Simulations' domain-focused, calculator-neutral SCF architecture while
using Workflow where durable Task execution supplies a concrete safety property.
The existing SCF Workflow already coordinates backend-specialized Tasks; future
integration must preserve that structure rather than flattening the lifecycle
into one opaque provider call.

## Accepted owner model

The owner-facing SCF Workflow consists of:

- `PwDftScfWorkflowFacade`, which exposes typed actions, events, status, and
  outcomes;
- `LocalPwDftScfWorkflow` and `LocalSnakesRun`, which provide the current local
  lifecycle;
- `PwDftScfHandlerTask`, which retains shared task correlation;
- `QePwDftScfTask` and `VaspPwDftScfTask`, which retain different backend
  resources behind the same calculator-neutral lifecycle; and
- `QePwDftScfActionHandler` and `VaspPwDftScfActionHandler`, which execute the
  common actions and return common events.

The Tasks are configured on the handlers rather than stored as live objects in
`LocalPwDftScfWorkflow`. The Workflow nevertheless orchestrates their identities
through registration, submission, completion or failure, and output analysis.
Registration and submission are lifecycle actions concerning a correlated Task;
they are not automatically separate Tasks.

The experimental Workflow path is better for a narrower operational role:

- authoritative immutable-source admission;
- exact occurrence reservation and revalidation;
- validated cross-repository owner invocation;
- atomic durable CPN state advancement; and
- compact, CPN, lifecycle, and safety replay without owner reinvocation.

Accordingly, the QE artifact-set integration is additive pure Task evidence. It
is not evidence for replacing the SCF facade, flattening QE and VASP, or routing
calculator effects through `Firer`.

## Target composition

When an enclosing Workflow invokes SCF, the parent should see one Workflow-backed
Task. That invocation creates a distinct SCF child Workflow run. Inside the child
run, the calculator Task remains backend-specialized and its common action/event
lifecycle remains visible to durable orchestration.

```text
parent Workflow
└── SCF Workflow Task
    └── distinct SCF child Workflow run
        └── calculator Task
            ├── QE Task + QE handler
            └── VASP Task + VASP handler
```

A separately reusable output-analysis or saved-state projection operation may be
a pure Task. Pure CPN transitions and lifecycle commands are not Tasks merely
because they occur inside the Workflow.

## Current constraints

- [x] Keep the protected Simulations core independent of Workflow runtime
  implementations.
- [x] Keep the reusable `projectkoios.simulations.workflows` layer independent of
  Workflow service, persistence, compiler, and CPN runtime implementations.
- [x] Place the full-runtime source adapter in the outward
  `projectkoios.adapters` namespace behind an explicit optional dependency.
- [x] Keep owner requests, results, codecs, identities, artifact semantics, and
  QE/VASP backend resources in Simulations.
- [x] Prove the bounded QE pure operation can commit and replay without
  replacing the owner lifecycle architecture.
- [ ] Retain dependency tests that fail if protected core or reusable owner
  workflow code imports the full Workflow runtime.
- [x] Inventory the exact common and backend-specific fields of
  `PwDftScfHandlerTask`, `QePwDftScfTask`, and `VaspPwDftScfTask` in the
  [two-owner inventory](../task_workflow_owner_inventory.md).
- [ ] Prove a future generic Task descriptor can retain opaque owner identities
  without copying executables, paths, working directories, pseudopotentials,
  native execution requests, or provider objects into Workflow state.
- [x] Map common actions and events to candidate Task lifecycle evidence without
  reclassifying them as independent Tasks by name alone, while preserving raised
  boundary errors separately from retained failure events.

## Future composition and migration gate

Do not implement a Workflow-backed `PwDftScfWorkflowFacade` or replace the local
SNAKES runtime unless all of the following become true:

- [ ] the common Task/Workflow composition model is accepted;
- [ ] the parent Task invocation and child SCF Workflow-run identities are exact,
  distinct, durable, and replayable;
- [ ] the effectful integration gate accepts dispatch, ambiguous-outcome,
  reconciliation, cancellation, and restart semantics;
- [ ] the Workflow implementation passes behavioral-equivalence tests for every
  existing typed action, accepted event, status, terminal outcome, and failure
  path;
- [ ] equivalence covers both QE and VASP Task specializations and rejects
  backend substitution;
- [ ] persistence and replay provide a required operational property that the
  existing local architecture cannot provide acceptably;
- [ ] the owner explicitly accepts the migration and compatibility policy; and
- [ ] the local SNAKES implementation has a recorded retention, deprecation, or
  removal decision.

An outward adapter remains the preferred first composition mechanism. Direct
inheritance from accepted SDK Task/Workflow ABCs may be considered only after
adapter parity demonstrates that it preserves owner APIs and dependency
boundaries.

## Exclusions

This task does not authorize calculator execution, backend migration, removal of
SNAKES, provider objects in reusable workflow contracts, use of the pure `Firer`
boundary for registration or submission effects, or an assumption that a VASP
saved-state result has QE artifact-set semantics.
