# `WorkflowDefinition` schematic

## Responsibility

```mermaid
flowchart TD
    ID[Workflow and Task identity]
    TI[Ordered Task instances]
    CO[Immutable composition]
    IO[Input and export contracts]
    WD[WorkflowDefinition<br/>composite TaskDefinition]
    PP[Parent plan Task reference]
    CP[Separately compiled child plan]

    ID --> WD
    TI --> WD
    CO --> WD
    IO --> WD
    WD --> PP
    WD --> CP
```

The same immutable Workflow definition can be compiled as a root or referenced
as a Task target. No retained arrow returns to a mutable source owner.
