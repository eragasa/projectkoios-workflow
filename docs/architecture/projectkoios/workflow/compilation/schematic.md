# `projectkoios.workflow.compilation` schematic

## Responsibility

```mermaid
flowchart TD
    WD[WorkflowDefinition<br/>composite Task]
    TD[Exact Task-definition closure]
    CP[Plan compiler]
    PP[Parent WorkflowExecutionPlan<br/>flat CPN]
    CD[Child Workflow definitions]
    CC[Separately compiled child plans]
    PD[Provider and environment descriptors]
    LK[Binding linker]
    EB[WorkflowExecutionBindings]
    RT[Runtime]

    WD --> CP
    TD --> CP
    CD --> CP
    CP --> PP
    CP --> CC
    PP --> LK
    CC --> LK
    PD --> LK
    LK --> EB
    EB --> RT
```

Discovery occurs before compilation and linking. Runtime receives exact artifacts
and performs no identity-only inference or provider discovery.
