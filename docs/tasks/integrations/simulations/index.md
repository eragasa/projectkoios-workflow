# Simulations integration tasks

This directory indexes bounded integration work between
`projectkoios-workflow` and `projectkoios-simulations`.

Until an accepted Workflow release exists, base owner integrations remain
limited to the standalone pinned SDK. Experimental full-runtime adapters must
stay in outward namespaces, use an explicit optional dependency, and must not be
treated as compatibility promises by the protected simulation core or reusable
workflow contracts.

## Priority

Preserve Simulations' existing typed SCF facade and local SNAKES lifecycle.
Adopt Workflow selectively for pure actions requiring durable authorization,
atomic state advancement, and owner-independent replay. See
[selective runtime adoption](selective_runtime_adoption.md).

## Tasks

- [Selective Workflow runtime adoption](selective_runtime_adoption.md) — boundary
  and future replacement gate for the existing SCF architecture.
- [QE artifact-set Workflow SDK pilot](qe_artifact_set_sdk_pilot.md) — first
  pure consumer fixture and isolated owner-side SDK firing evidence.
- [QE artifact-set durable vertical-slice evidence](qe_artifact_set_durable_vertical_slice_evidence.md)
  — real owner source authorization, invocation, pure CPN firing, atomic commit,
  and owner-independent replay through the experimental Workflow runtime.

The remaining full-plan and production-readiness gates stay tracked by the
[pure-firing vertical slice](../pure_firing_vertical_slice.md) and
[pure-firing foundations](../pure_firing_foundations.md).
