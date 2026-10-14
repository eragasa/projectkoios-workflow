# `projectkoios.workflow.petrinet.colored.enablement.results.identity` schematics

## Composition map

```mermaid
flowchart TD
    owner["projectkoios.workflow.petrinet.colored.enablement.results.identity"]
    owner --> contracts["Directly owned class contracts"]
```

Arrows denote ownership and composition, not scheduling or transferred
authority. Each child retains its local invariants.

## Coordination and authority boundary

```mermaid
flowchart LR
    evidence["Domain-authored canonical evidence"] --> owner["projectkoios.workflow.petrinet.colored.enablement.results.identity"]
    owner --> typed["Typed values, findings, and pure operation results"]
    effects["Providers, stores, filesystems, and networks"] -. "excluded" .-> owner
    acceptance["Scientific acceptance and protected authorization"] -. "not granted" .-> owner
```

## Strategy

The package validates bounded inputs, derives content identity, invokes an
explicit semantic operation, and retains correlated output. It does not reduce
CPN execution to a DAG or recursively embed child topology.
