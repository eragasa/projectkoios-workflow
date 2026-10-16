# `projectkoios.workflow.sdk` schematic

## Responsibility

```mermaid
flowchart TD
    subgraph A[Implemented SDK 0.1.0a1]
        F[Firer nominal ABC<br/>pure atomic Task boundary]
        M[Immutable manifest and descriptors]
        Q[Canonical request/result/evidence records]
    end

    subgraph O[Owner repository]
        TA[Typed owner Task API]
        QE[Provider-specific implementation<br/>for example QE or VASP]
        OA[Owner integration ABC]
    end

    subgraph S[Workflow service]
        WK[Validated worker]
        EN[Durable pure Task execution]
        CPN[ColoredPetriNetTransitionFirer]
    end

    subgraph V[Iteration-2 future source model]
        T[Task nominal source contract]
        W[Workflow composite Task]
    end

    TA --> OA
    QE --> OA
    OA --> F
    M --> WK
    F --> WK
    Q --> WK
    WK --> EN
    EN --> CPN
    T -. proposed .-> W
    W -. proposed immutable definitions .-> S
```

The implemented SDK points outward only through immutable records and nominal
ABCs. The proposed Task/Workflow source model is not part of `0.1.0a1` and does
not authorize effects or owner migration.
