# `TransitionActionBinding` schematic

## Responsibility

```mermaid
flowchart TD
    EN[Exact successful CPN enablement]
    SR[Exact selected CPN result]
    SE[Content-identified selected-binding evidence]
    P[Workflow adapter-profile identity]
    K[Bounded canonical binding encoder]
    D[Derived selected-binding SHA-256]
    C[Retained runtime coordinates]
    IM[Plan-selected input-source mappings]
    IR[Opaque input-source references]
    OR[Owner source repository]
    IS[Resolved source evidence]
    AU[Repository-authorized inputs]
    IA[Content-identified admitted inputs]
    Q[Exact SDK firing request]
    M[Content-identified mapping descriptor]
    R[Correlated SDK success]
    A[Exact descriptor and metadata admission]
    I[Path-free canonical ASCII identity]
    V[Declared external STRING variable]
    E[Ordered canonical evidence]
    H[Exact-byte SHA-256]
    X[Identity-bound candidate external binding]

    EN --> SE
    SR --> SE
    P --> SE
    SE --> K
    K --> D
    D --> IA
    C --> IA
    IM --> IA
    IR --> OR
    OR --> IS
    IS --> IA
    IA --> AU
    OR --> AU
    AU --> Q
    Q --> A
    M --> A
    C --> A
    R --> A
    A --> I
    I --> V
    V --> X
    A --> E
    E --> H
    E --> X
```

The selected-binding evidence prevents a bare arbitrary binding from entering
request construction. The admitted-input aggregate additionally prevents the
reservation service from independently combining raw owner payloads with that
selection. The authorization service resolves opaque references through a
nominal owner/source repository, and reservation revalidates those exact source
observations. Private storage and locators remain owner-controlled; predecessor
authority remains the separate reservation boundary.

For the QE SCF artifact-set direction, the identity branch carries the opaque
`artifact_set_identity` string and the evidence branch carries the canonical
`artifact_set` document. The two identities are deliberately different: one is
owner semantic state and the other binds exact evidence bytes.

The result mapping is versioned with the action descriptor so a changed adapter
cannot reinterpret a retained result during replay. This pure mapping produces
a candidate external-output binding; only `WorkflowEngine` may admit it against
the reserved predecessor and request CPN firing.
