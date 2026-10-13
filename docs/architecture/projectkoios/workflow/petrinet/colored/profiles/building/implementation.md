# `projectkoios.workflow.petrinet.colored.profiles.building` implementation

## Source mapping

Production ownership maps to `src/python/projectkoios/workflow/petrinet/colored/profiles/building.py`. This documentation mirrors ownership
but is not an alternate API, topology definition, or canonical representation.

## Dependency rule

Direct internal dependencies from the shared repository graph are `petrinet.colored.canonical.bindings`, `petrinet.colored.canonical.definitions`, `petrinet.colored.canonical.directives`, `petrinet.colored.canonical.enablement`, `petrinet.colored.canonical.expressions.guards.canonicalization`, `petrinet.colored.canonical.expressions.guards.decoding`, `petrinet.colored.canonical.expressions.values.canonicalization`, `petrinet.colored.canonical.expressions.values.decoding`, `petrinet.colored.canonical.firing.results.identity`, `petrinet.colored.canonical.json`, `petrinet.colored.canonical.markings`, `petrinet.colored.canonical.selections`, `petrinet.colored.children.exports.canonical.exporting`, `petrinet.colored.control.records.canonical`, `petrinet.colored.control.records.ordering`, `petrinet.colored.control.records.schema`, `petrinet.colored.control.records.types.graph`, `petrinet.colored.control.records.values.canonicalization`, `petrinet.colored.control.records.values.decoding`, `petrinet.colored.enablement.failures.building`, `petrinet.colored.enablement.ordering`, `petrinet.colored.enablement.transitions`, `petrinet.colored.expressions.collection.expressions`, `petrinet.colored.expressions.collection.guards`, `petrinet.colored.expressions.collection.variables`, `petrinet.colored.expressions.construction`, `petrinet.colored.expressions.evaluation.expressions`, `petrinet.colored.expressions.evaluation.guards`, `petrinet.colored.expressions.grammar`, `petrinet.colored.expressions.projection`, `petrinet.colored.expressions.validation.bounds`, `petrinet.colored.expressions.validation.structure`, `petrinet.colored.firing.failures.building`, `petrinet.colored.firing.markings.successor`, `petrinet.colored.firing.occurrences.reconstruction`, `petrinet.colored.firing.results.identity`, `petrinet.colored.firing.transitions`, `petrinet.colored.markings`, `petrinet.colored.outputs.external`, `petrinet.colored.plans.compilation`, `petrinet.colored.profiles.definition`, `petrinet.colored.selection`, `petrinet.colored.shadow.contracts`, `petrinet.colored.shadow.replay.contracts`, `petrinet.colored.validation.definitions.complete`, `petrinet.colored.validation.definitions.input`, `petrinet.colored.validation.definitions.output`, `petrinet.colored.validation.markings`, `petrinet.colored.values`.
Dependencies point toward narrower
typed contracts. Parent packages may re-export public contracts but must not
supply compatibility aliases for removed flat modules. The package graph remains
acyclic; this is a source-composition rule, not a workflow DAG restriction.

## Coordination and composition

The node composes children through typed inputs and immutable results. Content
identities are derived by the operation or record that owns their canonical
preimage. Deployment linking stays outside immutable execution-plan semantics.
Static child-plan reference validation does not constrain cyclic CPN topology,
repeated firing, concurrency, retries, or reconciliation.

## Verification

Repository checks require complete architecture trios, Mermaid schematics,
mirrored source ownership, no legacy shim, no package import cycle, strict
mypy, Ruff, pytest, exact provenance, and built-artifact import checks. These
software checks do not authorize provider execution or scientific acceptance.
