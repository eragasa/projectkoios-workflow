# `projectkoios.workflow.runtime` schematic

> **Status: provisional architecture iteration 2.**

## Responsibility

```mermaid
flowchart TD
    R[Parent Workflow run]
    S[Selected Task instance and CPN binding]
    O[Occurrence and attempt]
    K{Task execution kind}
    P[Pure Firer route]
    E[Effect lifecycle route]
    W[Workflow-backed route]
    C[Distinct child Workflow run]
    D[Admitted child terminal delivery]
    A[Admitted Task result]
    F[Pure parent CPN firing]
    M[Atomic successor marking and history]

    R --> S
    S --> O
    O --> K
    K --> P
    K --> E
    K --> W
    W --> C
    C --> D
    P --> A
    E --> A
    D --> A
    A --> F
    F --> M
    M --> R
```

Long-running effects and child execution never hold a database transaction.
Exact reservations and compare-and-swap protect parent firing. Rejected,
failed, ambiguous, cancelled, or unadmitted child outcomes cannot fabricate a
successful Task result or domain transition.
