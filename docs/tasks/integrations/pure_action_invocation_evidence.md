# Experimental pure-action invocation evidence

## Scope

This record covers the bounded v0 Workflow-owned path from one current,
repository-authorized reservation through an exact SDK owner invocation to a
candidate mapped external-output binding. It does not grant CPN firing authority
or claim complete runtime, persistence, or replay conformance.

## Implemented boundary

- `projectkoios.workflow.execution.ExperimentalWorkflowPureActionInvocationService`
  reconstructs and correlates
  the authorized inputs, successful reservation, and exact SDK request.
- It re-resolves every input source and revalidates the predecessor immediately
  before owner invocation. It repeats both checks after live worker resolution
  so owner-controlled integration lookup cannot open a stale-state window.
- `WorkflowWorkerIntegrationValidator` requires the live nominal worker
  integration to match the exact retained SDK manifest before selecting one
  firer.
- The concrete non-overridable SDK `Firer.fire()` performs descriptor, input, and
  closed-result correlation around the consumer-owned `_fire()` method.
- Workflow canonically round-trips the closed SDK result, contains worker and
  owner exceptions, and revalidates sources and predecessor state after every
  owner call, including calls that raise.
- Rejected and failed SDK results remain distinct retained outcomes. A stale
  post-invocation result is preserved but cannot be mapped.
- Only a current `WorkflowFiringSucceeded` enters the exact plan-selected output
  mapper. Mapping failures preserve the SDK success without producing an
  external-output binding.
- The content-identified invocation outcome retains no live firer, worker,
  repository, exception object, or private owner locator.

All records remain experimental v0 prerelease records.

## Adversarial evidence

Focused tests cover exact successful mapping, owner rejection, owner failure,
stale pre-invocation state, state change during owner execution, owner
exceptions with post-call revalidation, worker-manifest mismatch, state change
during live worker resolution, attempted owner mutation of its isolated request
copy, mapping incompatibility, source-authority revalidation, result correlation,
and frozen content identities.

Validation from the uncommitted candidate on base Workflow revision `d4a8f11`:

- focused authority/admission/reservation/invocation tests: `36 passed`;
- full Workflow suite: `356 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `48` source files;
- Ruff, formatting of changed sources, architecture, runtime dependency,
  shadow-provenance, documentation-link, and diff checks: passed;
- invocation source SHA-256:
  `ff15139b995a9d00dd1a7e60658e5c05004ee5561c910e7d5c6c52232a105d77`;
- evolved input-authorization source SHA-256:
  `1f2431f08edb355ed9043134c0dd88ee36054418865ea2d3b6ebdca8615ec161`;
- evolved reservation source SHA-256:
  `f914f78609e035a95308f468395a6a8b7e7c4f29506ca9de476231c5f5dfca33`;
- focused test source SHA-256:
  `910ecdfeb0bb88b080fc7b04d5c3cdc7f785703b988ca6c97c97959e2f6d581d`;
- two Workflow wheels built with `SOURCE_DATE_EPOCH=315532800` were
  byte-identical, SHA-256
  `f7641a1ab76df4dc7f39531ce461f500b2a84e054a4b1a4db92703cfee7ee186`;
- two unchanged standalone SDK wheels built with the same epoch were
  byte-identical, SHA-256
  `925f6974c49c8935ebf2f002b18c86d29375e1b11c3ffc17a29d305fb8095ff4`.

Deterministic successful fixture identities:

- input authorization:
  `567b0c136108d2920a6af69c9b70b7a36f7dd18bb60501513197a1dd978bc65c`;
- reservation:
  `c16c80412e269b5b2b717ce779cc210184ed5fd60873eb6c5cfb9d7293d0c313`;
- SDK request:
  `e88386da127cc2e2e1b9fd3e60f947aa11700a09c3aab6e031f3d885a9de28d8`;
- SDK result:
  `3bb17f3f11af90049b929de922822f0da1b30266cfe61061f2b945c2157ca7cb`;
- mapped action result:
  `e10245431002fe7aa61a9233b5cc305bbc80a2fff51cae639945e07940b14eb3`;
- invocation outcome:
  `61e0065affc56078cf07d9470a0abbda9da8e550696b8b5e85f2ca611b608246`.

## Remaining gaps

The invocation candidate does not claim or persist an invocation, consume a
reservation, atomically retain an SDK result or mapped binding, persist a
successor marking, roll back a partial write, or replay a committed occurrence.
The later [pure-action CPN firing candidate](pure_action_firing_evidence.md)
computes a pure successor but deliberately does not close those commit gaps.
A complete plan must also close the authoritative compiled transition rather
than receiving the shadow transition definition as a runtime argument. Source
and predecessor checks are sequential observations across nominal repositories,
not one durable transactional snapshot; the eventual accepted persistence
boundary must close the remaining race before firing and commit.
