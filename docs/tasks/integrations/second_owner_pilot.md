# Second owner SDK pilot

## Objective

After the Simulations pure slice passes, integrate one structurally different
pure owner action to test whether the SDK boundary is genuinely generic rather
than shaped around simulation artifacts.

## Candidate owners

Prefer one bounded effect-free action from `projectkoios-ingestion` or
`projectkoios-references`. The owning repository selects the action and retains
its domain request, result, codec, identity, and validation semantics.

## Entry gates

- [ ] Confirm Workflow SDK alpha readiness is complete.
- [ ] Confirm the Simulations pilot and pure firing vertical slice pass.
- [ ] Obtain pinned immutable fixtures from the second owner.
- [ ] Confirm no proposed mapping requires the owner to import Workflow service
  internals.

## Required evidence

- [ ] Implement an owner-owned integration ABC encapsulating the Workflow
  `Firer` boundary.
- [ ] Implement an explicit transition binding and exact descriptor.
- [ ] Demonstrate successful isolated-worker invocation and CPN result admission.
- [ ] Retain negative correlation and bound test results.
- [ ] Record every SDK change required by the second owner.

A required owner-specific field in the generic SDK must trigger architecture
review rather than automatic expansion of the SDK contract.
