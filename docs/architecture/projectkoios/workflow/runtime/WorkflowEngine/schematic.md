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
    V[Post-owner revalidation]
    E[WorkflowEngine]
    W[Isolated worker invocation]
    O[Correlated SDK result]
    A[Pure result mapping]
    X[Candidate external-output binding]
    F[ColoredPetriNetTransitionFirer]
    C[Atomic evidence and marking commit]

    P --> E
    B --> E
    S --> E
    M --> E
    I --> SR
    SR --> U
    U --> E
    R --> E
    E --> W
    W --> O
    O --> E
    E --> V
    R --> V
    V --> A
    A --> X
    X --> E
    E --> F
    F --> C
```

The engine admits the candidate external binding only after rechecking result
correlation, descriptor and mapping identities, the exact predecessor revision,
the selected binding, and its reservation. Failure at any check prevents CPN
firing. The current experimental authority candidate resolves opaque input
references without importing owner storage or locators, and reservation reloads
the exact source observation. The reservation candidate covers request closure,
atomic in-memory reservation, and revalidation only; the durable reservation
and atomic firing commit shown here remain future work.

For the artifact-set direction, the external binding carries the owner logical
identity string. The SDK request, result, canonical artifact-set evidence,
payload digests, candidate binding, firing result, successor marking, and
occurrence history enter the same accepted persistence boundary.
