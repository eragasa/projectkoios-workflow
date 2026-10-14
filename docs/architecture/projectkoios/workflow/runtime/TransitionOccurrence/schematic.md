# `TransitionOccurrence` schematic

## Responsibility

```text
enabling marking + selected binding
               │
               ▼
      TransitionOccurrence
        ├── reservation
        ├── attempt 1
        ├── attempt 2 after admitted retry policy
        └── terminal occurrence disposition
               │ success only
               ▼
           firing record
```

A later cyclic re-enablement is a distinct occurrence even when it uses the same transition and equivalent token values.
