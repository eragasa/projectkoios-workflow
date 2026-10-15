# `WorkflowEngine` schematic

## Responsibility

```mermaid
flowchart TD
    P[WorkflowExecutionPlan]
    B[WorkflowExecutionBindings]
    S[Selected CPN binding]
    M[Enabling marking revision]
    I[Opaque input-source references]
    SR[Owner source repository]
    U[Repository-authorized SDK inputs]
    R[Durable reservation]
    Q[Pre-owner source and predecessor revalidation]
    V[Post-owner source and predecessor revalidation]
    E[WorkflowEngine]
    W[Isolated worker invocation]
    O[Correlated SDK result]
    A[Pure result mapping]
    X[Candidate external-output binding]
    F[ColoredPetriNetTransitionFirer]
    K[In-memory compact atomic commit]
    C[Durable compact commit and marking coordinate]
    CS[Read-only compact structural replay]
    T[Canonical in-memory CPN replay transcript]
    RF[Pure CPN refiring and successor comparison]
    D[Future durable transcript linkage]

    P --> E
    B --> E
    S --> E
    M --> E
    I --> SR
    SR --> U
    U --> E
    R --> E
    E --> Q
    U --> Q
    R --> Q
    Q --> W
    W --> O
    O --> E
    E --> V
    R --> V
    V --> A
    A --> X
    X --> E
    E --> F
    F --> K
    K --> C
    C --> CS
    F --> T
    P --> T
    T --> RF
    C -. future atomic reference .-> D
    T -. future durable retention .-> D
```

The engine admits the candidate external binding only after rechecking result
correlation, descriptor and mapping identities, the exact predecessor revision,
the selected binding, and its reservation. Failure at any check prevents CPN
firing. Authoritative input resolution does not import owner storage or private
locators. The durable compact commit consumes the reservation and advances the
marking coordinate atomically while retaining identity-only event bytes.

Compact structural replay does not invoke the CPN. The separate bounded
transcript reconstructs canonical CPN state and proves pure refiring under the
exact supported retained profile without invoking the owner. It is currently
in-memory only; durable transcript retention and atomic linkage to the compact
commit remain future work.

For the artifact-set direction, the external binding carries only the opaque
owner logical-identity string. Owner payload bodies, canonical artifact-set
evidence documents, private locators, and native files do not enter the CPN
transcript or compact commit event.
