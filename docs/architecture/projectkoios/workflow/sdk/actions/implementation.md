# `projectkoios.workflow.sdk.actions` implementation

## Responsibility

Provide the nominal `Firer` ABC and immutable records that enforce exact
request/result types, descriptor identity, occurrence correlation, bounds, and
closed outcomes for one pure atomic Task.

`Firer.fire()` remains a non-overridable validating template method. Consumer
integrations implement `_fire()` and may delegate to typed owner Actions. The
Firer is execution behavior, not the durable Task definition and not the CPN
transition firer.

The compiler consumes explicit descriptors and explicit source connections. It
may validate port/color compatibility but must not inspect annotations or method
bodies to invent places, arcs, guards, joins, retries, concurrency, acceptance,
or child topology. Reflection may locate an explicitly declared manifest in an
isolated worker; it is never workflow authoring.

Large or private owner data remains in owner storage and crosses the SDK boundary
only under the accepted bounded transport. Workflow compact state retains
identities and evidence references, not numerical arrays, native artifacts,
provider resources, or private locators.
