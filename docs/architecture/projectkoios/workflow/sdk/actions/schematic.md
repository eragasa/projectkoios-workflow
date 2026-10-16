# `projectkoios.workflow.sdk.actions` schematic

## Responsibility

```mermaid
flowchart TD
    TD[Pure atomic Task definition]
    FD[Exact Firer descriptor]
    CM[Explicit compiler mapping]
    OC[Occurrence and attempt context]
    SB[Selected CPN binding]
    RQ[Canonical SDK request]
    FR[Validated owner Firer]
    RS[Closed correlated result]
    OM[Pure output mapping]
    EB[Candidate external binding]
    EN[WorkflowEngine admission]
    CF[Pure CPN firing]

    TD --> FD
    FD --> CM
    OC --> RQ
    SB --> RQ
    CM --> RQ
    RQ --> FR
    FR --> RS
    RS --> OM
    OM --> EB
    EB --> EN
    EN --> CF
```

The action/firer performs one pure atomic Task operation. It is not the durable
Task definition, an effect lifecycle, a workflow-backed Task, or the CPN firer.
Rejection and failure never masquerade as successful CPN firing.
