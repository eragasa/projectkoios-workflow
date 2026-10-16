# `projectkoios.workflow.compilation.bindings` schematic

## Responsibility

```mermaid
flowchart TD
    P[WorkflowExecutionPlan]
    A[Atomic Task descriptors]
    C[Workflow-backed Task child targets]
    F[Exact firer/lifecycle descriptors]
    D[Exact child-plan deployments]
    L[WorkflowExecutionBindingsConstructor]
    B[WorkflowExecutionBindings]
    R[WorkflowEngine]

    P --> L
    A --> L
    C --> L
    F --> L
    D --> L
    L --> B
    B --> R
```

Durable bindings contain descriptor identities and opaque handles only. Live
implementations and provider-specific resources remain outside retained plans
and compact runtime state.
