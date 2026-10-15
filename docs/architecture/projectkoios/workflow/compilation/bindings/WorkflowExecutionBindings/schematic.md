# `WorkflowExecutionBindings` schematic

## Responsibility

```mermaid
flowchart TD
    P[Workflow execution plan]
    T[Compiled transition mapping]
    A[Pure action descriptor]
    M[Result-mapping descriptor]
    W[Worker and environment handle]
    E[External lifecycle provider]
    N[Exact nested definition]
    B[Immutable execution bindings]
    X[Experimental pure-action plan candidate]
    I[Canonical SDK integration manifest]
    Y[Experimental pure-action execution bindings]
    S[Input-extended plan]
    Z[Experimental input bindings]

    P --> T
    T --> A
    A --> M
    A --> W
    T --> E
    T --> N
    M --> B
    W --> B
    E --> B
    N --> B
    X --> Y
    I --> Y
    Y --> Z
    S --> Z
```

The pure result-mapping descriptor fixes the correspondence among owner logical
output roles, evidence roles, and declared CPN external variables. For the QE
SCF artifact-set direction it distinguishes `artifact_set_identity` output from
canonical `artifact_set` evidence.

The experimental base path verifies only that the manifest contains the exact
firer descriptor already selected by the bounded plan candidate. The
input-binding wrapper additionally requires the input-extended plan to retain
that exact base plan. Deployment can substitute neither the selected-binding
profile, output mapping, nor input-source mappings.

Complete mappings are ordered and content-bound. Changing the provider, identity
codec, mapping revision, or environment produces another binding artifact; it
never mutates the compiled plan or reinterprets retained evidence.
