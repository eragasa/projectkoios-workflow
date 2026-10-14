# `projectkoios.workflow.petrinet.colored.firing.failures` schematics

## Composition map

```mermaid
flowchart TD
    owner["projectkoios.workflow.petrinet.colored.firing.failures"]
    owner --> child0["building"]
```

Arrows denote ownership and composition, not scheduling or transferred
authority. Each child retains its local invariants.

## Coordination and authority boundary

```mermaid
flowchart LR
    evidence["Domain-authored canonical evidence"] --> owner["projectkoios.workflow.petrinet.colored.firing.failures"]
    owner --> typed["Typed values, findings, and pure operation results"]
    effects["Providers, stores, filesystems, and networks"] -. "excluded" .-> owner
    acceptance["Scientific acceptance and protected authorization"] -. "not granted" .-> owner
```

## Strategy

The package validates bounded inputs, derives content identity, invokes an
explicit semantic operation, and retains correlated output. It does not reduce
CPN execution to a DAG or recursively embed child topology.
