# `AbstractTask` schematic

## Responsibility

```mermaid
flowchart TD
    T[AbstractTask nominal source owner]
    A[Atomic Task]
    W[Workflow composite Task]
    P[Pure Firer descriptor]
    E[Effect lifecycle descriptor]
    C[Ordered child Task instances]
    TD[Immutable TaskDefinition]
    WD[Immutable WorkflowDefinition]

    T --> A
    T --> W
    A --> P
    A --> E
    W --> C
    A --> TD
    W --> WD
    WD --> TD
```

Exactly one specialization shape is admitted. Route and composition declarations
control compilation and linking but never replace CPN enablement, selection, or
firing semantics.
