# Broader SDK adoption gate

## Objective

Define the evidence required before Workflow recommends the SDK to additional
owner repositories.

## Gate

Broader adoption remains blocked until all of the following hold:

- [ ] Complete the [pure-firing foundations](pure_firing_foundations.md) and
  [vertical-slice](pure_firing_vertical_slice.md) tasks.
- [ ] Confirm two structurally independent consumer fixtures pass; the second
  owner must demonstrate genuine reuse rather than another Simulations-shaped
  adapter.
- [ ] Accept SDK compatibility, versioning, deprecation, and schema-evolution
  rules.
- [ ] Validate immutable manifests and isolated worker loading.
- [ ] Prove no consumer imports Workflow service, persistence, compiler, or CPN
  runtime internals.
- [ ] Prove retained plans contain immutable descriptors and identities rather
  than live integration objects.
- [ ] Ensure supported owner paths expose no experimental Workflow service-side
  API.
- [ ] Prove retained evidence identifies every behavior profile required for
  deterministic replay.
- [ ] Demonstrate replay across every supported SDK and retained-schema version.
- [ ] Demonstrate that direct construction or nominal type membership cannot
  bypass runtime admission.
- [ ] Add automated tests for supported upgrades and explicitly incompatible
  versions.
- [ ] Verify installation dependency direction, including that protected owner
  code and reusable owner workflow contracts do not import Workflow runtime
  implementations.
- [ ] Prove adoption is additive behind owner-controlled boundaries and does not
  require replacing an owner's simpler domain workflow facade.
- [ ] Document rollback and exact-version pinning behavior.

## Outcome

Passing this gate permits separately authorized owner adoption work. It does not
migrate or replace an owner workflow facade, accept effectful lifecycle
semantics, or authorize a release or deployment by itself.
