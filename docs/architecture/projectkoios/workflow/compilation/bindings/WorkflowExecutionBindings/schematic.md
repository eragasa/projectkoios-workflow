# `WorkflowExecutionBindings` schematic

## Responsibility

```mermaid
flowchart TD
    P[Workflow execution plan]
    AT[Atomic Task mapping]
    WT[Workflow-backed Task mapping]
    PF[Pure Firer descriptor]
    EF[Effect lifecycle descriptor]
    CD[Child-plan deployment]
    B[Immutable execution bindings]
    X[Existing experimental pure-action bindings]

    P --> AT
    P --> WT
    AT --> PF
    AT --> EF
    WT --> CD
    PF --> B
    EF --> B
    CD --> B
    X -. bounded pure atomic route .-> B
```

Complete mappings are ordered and content-bound. Deployment can substitute
neither plan-selected Task semantics nor child targets. Live implementations
remain outside the artifact.
