# `TransitionActionBinding` schematic

## Responsibility

```mermaid
flowchart TD
    M[Content-identified mapping descriptor]
    C[Retained occurrence context]
    Q[Exact SDK firing request]
    R[Correlated SDK success]
    A[Exact descriptor and metadata admission]
    I[Path-free canonical ASCII identity]
    V[Declared external STRING variable]
    E[Ordered canonical evidence]
    H[Exact-byte SHA-256]
    X[Identity-bound candidate external binding]

    M --> A
    C --> A
    Q --> A
    R --> A
    A --> I
    I --> V
    V --> X
    A --> E
    E --> H
    E --> X
```

For the QE SCF artifact-set direction, the identity branch carries the opaque
`artifact_set_identity` string and the evidence branch carries the canonical
`artifact_set` document. The two identities are deliberately different: one is
owner semantic state and the other binds exact evidence bytes.

The result mapping is versioned with the action descriptor so a changed adapter
cannot reinterpret a retained result during replay. This pure mapping produces
a candidate external-output binding; only `WorkflowEngine` may admit it against
the reserved predecessor and request CPN firing.
