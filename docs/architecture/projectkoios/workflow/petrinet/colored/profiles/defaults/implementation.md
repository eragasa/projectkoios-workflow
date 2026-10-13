# `projectkoios.workflow.petrinet.colored.profiles.defaults` implementation

## Source mapping

Production ownership maps to `src/python/projectkoios/workflow/petrinet/colored/profiles/defaults.py`. This documentation mirrors ownership
but is not an alternate API, topology definition, or canonical representation.

## Dependency rule

Direct relative dependencies are `..canonical.bindings`, `..canonical.definitions`, `..canonical.directives`, `..canonical.enablement`, `..canonical.firing_results.identity`, `..canonical.expressions.guards`, `..canonical.expressions.values`, `..canonical.json`, `..canonical.markings`, `..canonical.selections`, `..children.exports.canonical`, `..control.records.canonical`, `..control.records.ordering`, `..control.records.schema`, `..control.records.type_graph`, `..control.records.value_canonical`, `..enablement.ordering`, `..enablement.failure_building`, `..enablement.transitions`, `..expressions.collection`, `..expressions.construction`, `..expressions.evaluation`, `..expressions.grammar`, `..expressions.projection`, `..expressions.validation`, `..external_outputs`, `..firing.failure_building`, `..firing.identity_derivation`, `..firing.successor_marking`, `..firing.occurrence_reconstruction`, `..firing.transitions`, `..markings`, `..plans.definition`, `..selection`, `..shadow.contracts`, `..shadow.replay_contracts`, `..validation.definitions`, `..validation.markings`, `..values`, `.definition`. Dependencies point toward narrower
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
