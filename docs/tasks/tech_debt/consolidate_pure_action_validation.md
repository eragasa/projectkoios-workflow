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

## Completed organization slice

The [retained evidence](pure_action_internal_organization_evidence.md) records
validation results and artifact digests for this slice.

The current pure-firing vertical slice completed the bounded organization work
that had become actionable:

- execution-side reconstruction and successful-reservation correlation are
  centralized in `projectkoios.workflow.execution._validation`;
- invocation and firing outcomes are reconstructed by their defining phase
  modules and reused by later phases;
- the former monolithic reservation verification module is split into shared
  fixtures plus input, reservation, invocation, CPN firing, and commit modules;
- canonical CPN definition representation identity and encoding are separated
  from the plan/profile models in `pure_action_cpn_representation`.

Validation ownership for this slice is retained as follows:

| Boundary record | Reconstruction owner |
| --- | --- |
| authorized inputs | `execution._validation` |
| successful reservation plus canonical request copy | `execution._validation` |
| CPN plan | `execution._validation` |
| invocation outcome and mapped result | `execution.pure_action_invocation` |
| firing outcome | `execution.pure_action_firing` |
| CPN definition representation bytes | `compilation.pure_action_cpn_representation` |

The broader admitted transition/firer-contract and serialization-count actions
above remain open. This completed slice did not claim those later hot-loop
optimizations or canonical CPN decoding; subsequent bounded representation and
refiring evidence covers decoding without changing this task's remaining scope.
