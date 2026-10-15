# Experimental pure-action input-admission evidence

## Scope

This record covers a bounded Workflow-owned candidate for plan-selected,
source-correlated SDK inputs. It does not claim durable source authority,
complete execution-plan conformance, owner invocation, CPN firing, persistence,
or replay.

## Implemented boundary

- `ExperimentalWorkflowPureActionInputMappingDescriptor` assigns each SDK input
  role an opaque source kind, a nominal source-representation profile, and a
  mapping version.
- `ExperimentalWorkflowPureActionInputPlan` content-identifies the exact ordered
  descriptor tuple while preserving the identity and reconstruction rules of
  older pure-action plan records.
- `ExperimentalWorkflowPureActionInputBindings` links that input plan to the
  exact previously linked plan and SDK integration manifest.
- `ExperimentalWorkflowPureActionInputSourceEvidence` binds a bounded path-free
  source identity to exact SDK payload metadata, byte length, and payload
  SHA-256. Workflow treats both the source identity and payload bytes as opaque.
- `ExperimentalWorkflowPureActionAdmittedInputs` closes input bindings,
  selected-binding evidence, runtime coordinates, ordered source evidence, and
  the exact SDK request under one content identity.
- `ExperimentalWorkflowPureActionReservationService` now accepts only that
  reconstructed aggregate. The admission-bound v0 reservation shape includes
  the input-admission identity; the earlier v0 base shape remains reconstructable.

The source-evidence record is structural correlation, not proof that a durable
repository owns the claimed source identity. Direct dataclass construction does
not grant runtime authority.

## Adversarial evidence

Focused tests cover:

- behavior-affecting input mapping and source-profile changes;
- source kind, profile, role, codec, payload, and source-identity substitution;
- missing, duplicated, and reordered source inputs;
- changed occurrence/attempt coordinates;
- path-shaped source identities;
- directly forged admitted-input and reservation identities;
- reservation identity changes when source evidence changes even if the SDK
  request bytes remain exact;
- selected-binding profile substitution;
- concurrent reservation conflicts, stale state, consumed state, and revision
  rewind; and
- reconstruction of the earlier v0 base reservation identity.

Validation retained for local Workflow commit `6351a93` (based on `d3c58a3`):

- focused input-admission/reservation tests: `16 passed`;
- full Workflow suite: `336 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `44` source files;
- Ruff, formatting, architecture, shadow provenance, documentation-link, and
  diff checks: passed;
- input mapping source SHA-256:
  `6271de3bd24fcca14807c958e845e921f2dda2a80204396ab8a9c441bc4fdc85`;
- input plan/linking source SHA-256:
  `c75953f10fa6f044e88aeb6b31eb64246ece35eb1d6e272e37eb69061862b969`;
- input admission source SHA-256:
  `50717d5469c459424569377b10da16e9d11eae242b136473b75852cb68edb0e3`;
- evolved reservation source SHA-256:
  `8dc5d9f9cc7300590897fd09bb4c501b5370166141f26244070bfa0e385905dd`;
- focused test source SHA-256:
  `c63efc2811620b0d9f6657432a2214f7e0cc49bb8462e978aa38fcf84aba960e`;
- two wheels built with `SOURCE_DATE_EPOCH=315532800` were byte-identical;
- wheel SHA-256:
  `c067c288f85a430ee88b52ccff73832b02e750e61591f8184c741cdcd4866c84`;
- the wheel installed into the isolated Workflow/SDK/Simulations pilot
  environment, passed dependency checking, exposed the new nominal records,
  and preserved the existing plan, deployment-binding, and mapped-result
  identities.

Deterministic fixture identities:

- input plan: `803ccb8ceba8014fdd4e89fd68a22689c1a03f45176951ca37c889ed3aa64bc7`;
- input bindings:
  `7b8762927f516ce0c9c1aa5b1cfe61c762c18908cc3508dd944be592c0b35398`;
- input admission:
  `e2668a460f385525a630ee57107f95011e8fe5908a9f5e67d55351f0d60e20ab`;
- SDK request: `e88386da127cc2e2e1b9fd3e60f947aa11700a09c3aab6e031f3d885a9de28d8`;
- v0 admission-bound reservation shape:
  `b25d1dbecb22b1f593c04d3713568ba3dc716b241a1b98121900323fd0d541e2`;
- reconstructed v0 base reservation shape:
  `2189a0d705aa0523585e434eaa6efc922bcdda1c7535e217c671776a23e9baf7`.

## Subsequent evolution

The later
[pure-action input-authority candidate](pure_action_input_authority_evidence.md)
resolves references through a nominal owner/source repository and revalidates
the exact source before reservation. The counts and hashes above remain evidence
for `6351a93`, not the evolved source files.

## Remaining authority gaps

This structural candidate alone does not validate a source identity against an
owner repository. It does not implement owner invocation, result admission, CPN
firing, atomic reservation consumption, successor persistence, rollback, or
replay. Nominal record membership alone grants no source authority.
