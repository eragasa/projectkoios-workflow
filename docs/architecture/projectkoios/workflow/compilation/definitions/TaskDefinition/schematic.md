# `TaskDefinition` schematic

## Responsibility

```mermaid
flowchart TD
    T[TaskDefinition]
    A[Atomic Task variant]
    W[Workflow composite variant]
    P[Pure Firer descriptor]
    E[Effect lifecycle descriptor]
    C[Ordered Task instances]
    X[Exact child Workflow references]
    PC[Parent Workflow plan compilation]

    T --> A
    T --> W
    A --> P
    A --> E
    W --> C
    W --> X
    A --> PC
    W --> PC
```

The compiler maps each Task definition completely. Runtime activity never uses a
Task definition identity as a substitute for occurrence or attempt identity.
