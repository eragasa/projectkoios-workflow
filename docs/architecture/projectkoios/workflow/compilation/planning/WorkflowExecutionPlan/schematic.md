# `WorkflowExecutionPlan` schematic

## Responsibility

```mermaid
flowchart TD
    D[Source definition closure]
    C[Canonical flat CPN IR]
    I[Initial-marking contract]
    P[Selected-binding representation profile]
    A[Transition and action mappings]
    N[Exact nested targets]
    E[Compiler and composition evidence]
    W[Complete WorkflowExecutionPlan]

    D --> W
    C --> W
    I --> W
    P --> W
    A --> W
    N --> W
    E --> W

    P --> X[Experimental pure-action plan candidate]
    A --> X
    X --> Y[Experimental input-extended plan]
    S[Ordered input-source mappings] --> Y
    Y --> Z[Experimental CPN-closed plan]
    C --> Z
    R[Candidate CPN execution profile] --> Z
```

The base experimental candidate closes the selected-binding profile and one
exact output-mapping descriptor. The input-extended wrapper additionally closes
one source kind, source profile, and mapping version per ordered SDK input role.
The CPN-closed candidate additionally binds exact canonical definition bytes and
a candidate execution profile. None is sufficient to start or replay a workflow
under the complete contract. The complete plan contains no live runtime objects
and remains separate from deployment linking.
