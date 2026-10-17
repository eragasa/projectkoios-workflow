# Workflow SDK alpha consumption readiness

## Objective

Establish the minimum accepted and installable Workflow SDK surface before any
external owner repository imports it as a runtime dependency.

## Authorized baseline

- [x] Select `projectkoios-workflow` as the source repository.
- [x] Select `sdk/` as a separate build root.
- [x] Select `projectkoios-workflow-sdk` as the distribution.
- [x] Select `projectkoios.workflow_sdk` as the public import root.
- [x] Select `0.1.0a1` as the initial target version.
- [x] Limit alpha runtime dependencies to the Python standard library.
- [x] Require nominal ABCs for runtime extension enforcement.
- [x] Limit the first alpha to pure firing.
- [x] Record the decision in the
  [SDK architecture](../../architecture/projectkoios/workflow/sdk/).

## Remaining work

- [x] Accept and record the exact public symbol, record-field, and result-variant
  inventory for `0.1.0a1` in the
  [authorized public API](../../architecture/projectkoios/workflow/sdk/public_api.md).
- [x] Accept and record the
  [canonical encoding](../../architecture/projectkoios/workflow/sdk/serialization.md)
  of SDK-owned records used across the isolated worker boundary.
- [x] Implement the separate `sdk/` build root and public package.
- [x] Build `projectkoios-workflow-sdk` as an independently installable wheel.
- [x] Implement the Workflow-owned nominal `Firer` ABC and the minimum immutable
  request, result, descriptor, identity, binding, and correlation records.
- [x] Enforce request/result correlation, closed result types, and resource bounds
  at runtime rather than relying only on static typing.
- [x] Make `projectkoios-workflow` consume the SDK wheel instead of maintaining
  private duplicate public-contract types.
- [x] Validate installation and imports in an isolated environment containing only
  declared runtime dependencies.
- [ ] Complete the remaining
  [pure-firing foundations](pure_firing_foundations.md) before declaring a
  supported full-runtime pure path; this is no longer an owner-side SDK alpha
  prerequisite.
- [x] Retain a bounded real-owner
  [pure-firing vertical slice](pure_firing_vertical_slice.md).
- [x] Publish an alpha contract statement identifying unstable surfaces,
  unsupported operations, compatibility limits, and prohibited production uses.

## Completion evidence

- [x] Record the wheel name, version, digest, and contents in the
  [standalone implementation evidence](sdk_alpha_implementation_evidence.md).
- [x] Retain public-import and abstract-class enforcement test results.
- [x] Retain malformed, oversized, stale-correlation, and unknown-result rejection
  test results.
- [x] Retain isolated-install test output.
- [x] Prove that Workflow imports the installed SDK surface in the
  [self-consumption evidence](sdk_alpha_self_consumption_evidence.md).
- [x] Retain pure vertical-slice evidence.
- [x] Retain the versioned alpha compatibility statement.
- [x] Retain a two-build
  [reproducible non-release artifact candidate](sdk_alpha_reproducible_artifact_candidate.md)
  with exact `RECORD`, source-byte, clean-install, and Simulations compatibility
  evidence. The historical candidate exposed missing license text; exact
  committed-source correction evidence now includes the license, two identical
  builds, complete `RECORD` and source checks, isolated installation, and
  repeated Simulations compatibility. Two public-clone rebuilds and Workflow CI
  also passed. The operator selected retaining `0.1.0a1`; any release remains
  separately gated.

## Exclusions

This task does not authorize broader owner adoption, effectful execution,
calculator launch, replacement of an owner workflow architecture, production
deployment, or compatibility beyond the recorded alpha contract.
