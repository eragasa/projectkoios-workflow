# `AbstractWorkflow` schematic

## Responsibility

```mermaid
flowchart TD
    P[Parent Workflow composition]
    T[Task instance]
    OW[Concrete owner Workflow]
    AW[AbstractWorkflow<br/>composite AbstractTask]
    WD[Immutable WorkflowDefinition]
    CP[Separately compiled child plan]
    CR[Distinct child Workflow run]
    D[Correlated terminal delivery]

    P --> T
    T --> OW
    OW --> AW
    AW --> WD
    WD --> CP
    CP --> CR
    CR --> D
    D --> P
```

The parent sees one Task instance. Definition construction and child execution
remain separate; no arrow returns from retained state to a mutable owner object.
