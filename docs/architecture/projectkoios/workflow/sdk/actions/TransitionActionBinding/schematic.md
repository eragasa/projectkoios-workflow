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
    D --> Q
    C --> Q
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
request construction, but it does not reserve the predecessor or establish the
provenance of independently supplied owner inputs. Those remain explicit
pure-firing foundation gates.

For the QE SCF artifact-set direction, the identity branch carries the opaque
`artifact_set_identity` string and the evidence branch carries the canonical
`artifact_set` document. The two identities are deliberately different: one is
owner semantic state and the other binds exact evidence bytes.

The result mapping is versioned with the action descriptor so a changed adapter
cannot reinterpret a retained result during replay. This pure mapping produces
a candidate external-output binding; only `WorkflowEngine` may admit it against
the reserved predecessor and request CPN firing.
