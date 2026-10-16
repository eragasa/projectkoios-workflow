# `TransitionOccurrence` schematic

## Responsibility

```mermaid
flowchart TD
    T[Run-scoped Task instance]
    S[Enabling marking and selected binding]
    O[TransitionOccurrence]
    A[One or more attempts]
    C[Optional distinct child Workflow run]
    D[Admitted Task outcome or child delivery]
    F[Pure CPN firing record]

    T --> O
    S --> O
    O --> A
    O --> C
    A --> D
    C --> D
    D --> F
```

A later cyclic re-enablement is a distinct occurrence even for the same Task and
transition. Task, occurrence, attempt, child run, and firing identities remain
separate.
