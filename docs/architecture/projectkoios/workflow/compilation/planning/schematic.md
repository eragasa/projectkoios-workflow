# `projectkoios.workflow.compilation.planning` schematic

## Responsibility

```mermaid
flowchart TD
    W[WorkflowDefinition]
    T[Ordered Task definitions and instances]
    F[Fragments and connections]
    C[Exact child Workflow targets and contracts]
    PC[WorkflowExecutionPlanConstructor]
    P[Flat parent WorkflowExecutionPlan]
    CP[Separate child WorkflowExecutionPlans]

    W --> PC
    T --> PC
    F --> PC
    C --> PC
    PC --> P
    C --> CP
    CP --> P
```

The parent plan retains source and composition evidence plus exact references to
separately compiled child plans. It does not contain child markings or history.
