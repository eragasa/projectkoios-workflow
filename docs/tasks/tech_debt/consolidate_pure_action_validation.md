# Consolidate pure-action validation

## Problem

The experimental request factory, output mapping descriptor, output mapper, and
mapped-result record repeat canonical SDK round trips, transition/firer
compatibility checks, payload-contract checks, and resource-bound calculations.
The duplication is currently bounded and fail-closed, but it can produce drift,
inconsistent diagnostics, and repeated serialization in a runtime loop.

## Activation condition

Make this work actionable after the pure-firing reservation, admitted-input, and
admission-stage records stabilize, or before the path enters a runtime hot loop,
whichever occurs first.

## Action

- [ ] Inventory repeated transition/firer, payload, bound, and correlation checks.
- [ ] Define one immutable admitted transition/firer contract produced by one
  validator.
- [ ] Keep wire decoding and canonical round trips at explicit trust boundaries.
- [ ] Reuse admitted in-process records without treating their nominal type alone
  as authorization.
- [ ] Preserve fail-closed validation, exact built-in type checks, and specific
  rejection diagnostics.
- [ ] Remove duplicate helpers only after equivalent adversarial coverage passes.

## Completion evidence

- [ ] Retain a validation-ownership table.
- [ ] Prove every former rejection case remains rejected.
- [ ] Retain strict type-checking, lint, formatting, and full test results.
- [ ] Record serialization-count or equivalent evidence showing that admitted
  records are not repeatedly round-tripped without a trust-boundary reason.

This task does not weaken canonical decoding or combine runtime admission with
owner-domain semantics.
