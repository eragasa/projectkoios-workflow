# `WorkflowExecutionBindingsConstructor` implementation

## Responsibility

Expose linking as a typed pure service operation. Resolve catalogs before
construction and pass exact descriptor snapshots rather than lookup queries.

Tests cover missing, extra, reordered, mutable, identity-colliding, wrong
Task-kind, route-incompatible, provider-incompatible, and child-plan-incompatible
bindings. A workflow-backed binding must preserve its plan-selected child target
and terminal-delivery contract. Already compiled plans remain byte-identical
before and after linking.
