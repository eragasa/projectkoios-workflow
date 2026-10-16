# Second owner SDK pilot

## Objective

Integrate one structurally different pure owner action to test whether the SDK
boundary is genuinely generic rather than shaped around simulation artifacts.
This is the next value-validation task after canonicalizing the demonstrated
durable write path; it should precede additional speculative runtime
infrastructure.

## Candidate owners

Prefer one bounded effect-free action from `projectkoios-ingestion` or
`projectkoios-references`. The owning repository selects the action and retains
its domain request, result, codec, identity, and validation semantics.

## Entry gates

- [x] Confirm the standalone Workflow SDK alpha is installable and consumed by
  Workflow and Simulations.
- [x] Confirm the bounded Simulations durable pure-action slice passes. Complete
  production plan/profile closure and OS-process isolation are not prerequisites
  for the owner-side generality test.
- [ ] Obtain pinned immutable fixtures from the second owner.
- [ ] Confirm no proposed mapping requires the owner to import Workflow service
  internals.

## Required evidence

- [ ] Implement an owner-owned integration ABC encapsulating the Workflow
  `Firer` boundary.
- [ ] Implement an explicit transition binding and exact descriptor.
- [ ] First demonstrate isolated owner-side request/result invocation. Add full
  CPN result admission only if the owner boundary differs materially or exposes
  a missing runtime guarantee.
- [ ] Retain negative correlation and bound test results.
- [ ] Record every SDK change required by the second owner.

A required owner-specific field in the generic SDK must trigger architecture
review rather than automatic expansion of the SDK contract. Failure to find a
natural second owner is evidence against broader adoption and in favor of
keeping Workflow as a narrow Simulations integration tool.
