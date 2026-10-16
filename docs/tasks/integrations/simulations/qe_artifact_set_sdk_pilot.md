# QE artifact-set Workflow SDK pilot

## Objective

Use the corrected QE SCF saved-state artifact-set projection as the first pure
consumer fixture for the Workflow SDK without changing its domain API or
performing calculator execution.

## Entry gates

- [x] Confirm [Workflow SDK alpha readiness](../sdk_alpha_readiness.md) has an
  installable, versioned candidate surface.
- [x] Confirm the reviewed QE artifact-set record, codec, identity derivation, and
  candidate projection remain green in `projectkoios-simulations`.
- [x] Perform the work on a dedicated feature branch with exact dependency pins.

## Simulations-owned work

- [x] Add an exact pre-release `projectkoios-workflow-sdk` dependency.
- [x] Define a Simulations-owned integration ABC that encapsulates the Workflow
  `Firer` boundary.
- [x] Wrap the existing pure QE artifact-set action without changing its domain
  request, result, identity, codec, or candidate schema.
- [x] Publish an immutable descriptor and explicit Workflow transition binding.
- [x] Return only bounded correlated SDK output/evidence.
- [x] Retain owner-local authority, scientific acceptance, codec, and artifact
  semantics.

## Selected long-term output shape

The operator selected the
[owner-identity output direction](../../../architecture/projectkoios/workflow/sdk/actions/TransitionActionBinding/):

- `artifact_set_identity` becomes the strict bounded Simulations-owned canonical
  ASCII output mapped opaquely to a CPN string variable;
- the existing canonical `artifact_set` document becomes SDK evidence;
- the artifact-set payload SHA-256 remains exact-byte integrity and replay
  evidence and must not substitute for the owner logical identity; and
- Workflow must not import Simulations types or parse its domain document.

The original owner-side pilot emits `artifact_set_identity` as its sole
external-state output and retains `artifact_set` as evidence without granting
CPN admission. The separately composed
[durable vertical slice](qe_artifact_set_durable_vertical_slice_evidence.md) now
exercises Workflow-owned admission, pure CPN firing, atomic persistence, and
bounded replay while preserving that authority boundary.

### Follow-up work

- [x] Define exact Simulations-owned identity payload type, schema, codec,
  representation, media type, and bounds.
- [x] Emit `artifact_set_identity` as the external-state output.
- [x] Move the canonical `artifact_set` document to the SDK evidence contract.
- [x] Rebuild and re-review the owner descriptor, transition binding, wheel, and
  isolated cross-wheel evidence.

## Workflow-owned work

- [x] Construct the SDK firing request from an exact selected CPN binding.
- [ ] Invoke the integration in an isolated OS-process worker environment. The
  current candidate validates the nominal worker composition and canonical copy
  boundary in-process only.
- [x] Reject descriptor, occurrence, attempt, binding, and request/result mismatch.
- [x] Admit the returned output through an explicit external-output binding.
- [x] Complete and retain the pure CPN firing and replay evidence, with
  [real-owner durable evidence](qe_artifact_set_durable_vertical_slice_evidence.md).

## Completion evidence

- [x] Record exact wheel and repository revisions in the
  [pilot evidence](qe_artifact_set_sdk_pilot_evidence.md).
- [x] Retain isolated-installation evidence for Workflow SDK plus the Simulations
  integration.
- [x] Retain positive end-to-end firing and replay evidence.
- [x] Retain adversarial mismatch and bound test results.
- [x] Prove the existing QE candidate source/schema remains unchanged unless
  separately authorized by its owner.

## Exclusions

No calculator launch, staging, artifact retention operation, scheduler access,
production migration, scientific acceptance, or effectful lifecycle claim is in
scope.
