# `projectkoios.workflow.petrinet.colored.canonical.firing.results.documents` implementation

## Source mapping

Production ownership maps to `src/python/projectkoios/workflow/petrinet/colored/canonical/firing/results/documents.py`. This documentation mirrors ownership
but is not an alternate API, topology definition, or canonical representation.

## Dependency rule

Direct relative dependencies are `....firing.results.definition`, `....profiles.definition`. Dependencies point toward narrower
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
