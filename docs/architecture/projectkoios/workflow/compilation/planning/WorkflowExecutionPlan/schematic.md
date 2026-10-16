# `WorkflowExecutionPlan` schematic

## Responsibility

```mermaid
flowchart TD
    W[Workflow definition]
    T[Task-definition and instance closure]
    C[Canonical flat parent CPN IR]
    A[Atomic Task mappings]
    N[Workflow-backed Task child-plan references]
    X[Input/export and terminal-delivery contracts]
    E[Compiler evidence]
    P[Complete WorkflowExecutionPlan]
    PA[Existing experimental pure-action plan chain]

    W --> P
    T --> P
    C --> P
    A --> P
    N --> P
    X --> P
    E --> P
    PA -. compatible bounded atomic-route evidence .-> P
```

The complete plan has no live runtime objects. Child plans and deployment
bindings remain separate artifacts; the current experimental pure-action plans
do not claim complete iteration-2 conformance.
