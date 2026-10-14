# `TransitionActionBinding` schematic

## Responsibility

```mermaid
flowchart TD
    M[Compiled transition mapping]
    B[Selected token binding]
    C[Occurrence context]
    Q[Exact owner action request]
    R[Correlated owner action result]
    I[Logical-identity output role]
    V[Identified external CPN variable]
    E[Canonical document evidence]
    H[Exact-byte SHA-256]
    X[Candidate external-output binding]

    M --> Q
    B --> Q
    C --> Q
    Q --> R
    R --> I
    I --> V
    V --> X
    R --> E
    E --> H
```

For the QE SCF artifact-set direction, the identity branch carries the opaque
`artifact_set_identity` string and the evidence branch carries the canonical
`artifact_set` document. The two identities are deliberately different: one is
owner semantic state and the other binds exact evidence bytes.

The result mapping is versioned with the action descriptor so a changed adapter
cannot reinterpret a retained result during replay. This pure mapping produces
a candidate external-output binding; only `WorkflowEngine` may admit it against
the reserved predecessor and request CPN firing.
