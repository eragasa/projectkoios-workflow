# Broader SDK adoption gate

## Objective

Define the evidence required before Workflow recommends the SDK to additional
owner repositories.

## Gate

Broader adoption remains blocked until all of the following hold:

- [ ] Confirm two structurally independent consumer fixtures pass.
- [ ] Accept SDK compatibility, versioning, deprecation, and schema-evolution
  rules.
- [ ] Validate immutable manifests and isolated worker loading.
- [ ] Prove no consumer imports Workflow service, persistence, compiler, or CPN
  runtime internals.
- [ ] Prove retained plans contain immutable descriptors and identities rather
  than live integration objects.
- [ ] Add automated tests for supported upgrades and explicitly incompatible
  versions.
- [ ] Verify installation dependency direction.
- [ ] Document rollback and exact-version pinning behavior.

## Outcome

Passing this gate permits separately authorized owner adoption work. It does not
migrate a consumer, accept effectful lifecycle semantics, or authorize a release
or deployment by itself.
