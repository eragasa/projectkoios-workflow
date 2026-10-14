# `projectkoios.workflow.petrinet.colored.expressions` schematics

## Composition map

```mermaid
flowchart TD
    owner["projectkoios.workflow.petrinet.colored.expressions"]
    owner --> child0["collection"]
    owner --> child1["construction"]
    owner --> child2["errors"]
    owner --> child3["evaluation"]
    owner --> child4["grammar"]
    owner --> child5["projection"]
    owner --> child6["validation"]
```

Arrows denote ownership and composition, not scheduling or transferred
authority. Each child retains its local invariants.

## Coordination and authority boundary

```mermaid
flowchart LR
    evidence["Domain-authored canonical evidence"] --> owner["projectkoios.workflow.petrinet.colored.expressions"]
    owner --> typed["Typed values, findings, and pure operation results"]
    effects["Providers, stores, filesystems, and networks"] -. "excluded" .-> owner
    acceptance["Scientific acceptance and protected authorization"] -. "not granted" .-> owner
```

## Strategy

The package validates bounded inputs, derives content identity, invokes an
explicit semantic operation, and retains correlated output. It does not reduce
CPN execution to a DAG or recursively embed child topology.
