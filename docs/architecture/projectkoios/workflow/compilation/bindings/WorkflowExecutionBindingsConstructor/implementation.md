# `WorkflowExecutionBindingsConstructor` implementation

## Responsibility

Expose linking as a typed service action. Resolve catalog compatibility before calling the constructor; pass exact selected descriptor snapshots rather than lookup queries.

DEFECT00003 tests must cover missing, extra, reordered, mutable, identity-colliding, route-incompatible, and nested-definition-incompatible bindings. Already compiled plans must remain byte-identical before and after linking.
