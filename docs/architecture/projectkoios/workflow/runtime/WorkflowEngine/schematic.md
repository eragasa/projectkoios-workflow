# `WorkflowEngine` schematic

## Responsibility

```mermaid
flowchart TD
    P[WorkflowExecutionPlan]
    B[WorkflowExecutionBindings]
    S[Selected Task instance and CPN binding]
    E[WorkflowEngine]
    K{Execution route}

    I[Pure atomic Task]
    SR[Owner source repository]
    R[Durable reservation]
    W[Validated SDK Firer]
    O[Admitted owner result]
    M[Pure output mapping]

    FX[Effectful atomic Task]
    EL[Durable effect lifecycle<br/>future gated]

    WT[Workflow-backed Task]
    CI[Durable child-creation intent<br/>future]
    CR[Distinct child Workflow run<br/>future]
    CD[Admitted terminal delivery<br/>future]

    F[ColoredPetriNetTransitionFirer]
    C[Atomic compact commit + CPN evidence<br/>lifecycle + reservation + marking]
    RP[Owner-independent compact/lifecycle/safety replay]
    RF[Bounded pure CPN refiring]

    P --> E
    B --> E
    S --> E
    E --> K
    K --> I
    K --> FX
    K --> WT

    I --> SR
    SR --> R
    R --> W
    W --> O
    O --> M
    M --> F

    FX --> EL
    EL -. admitted terminal result .-> F

    WT --> CI
    CI --> CR
    CR --> CD
    CD -. admitted child result .-> F

    F --> C
    C --> RP
    C --> RF
```

Only the pure atomic Task route is implemented by the current bounded
experimental chain. It repeatedly validates source and predecessor authority,
admits only a correlated SDK success, invokes the pure CPN firer, and commits
compact state plus canonical CPN replay evidence atomically.

Effect lifecycle and child-run orchestration remain future gated routes. Neither
may be hidden behind `Firer`. A child Workflow remains separately compiled and
persisted; only its admitted terminal delivery reaches the parent firing.

Owner payload bodies, native files, numerical arrays, private locators, and
provider resources do not enter the compact commit or CPN transcript.
