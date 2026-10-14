# `projectkoios.workflow.sdk.runtime` schematic

> **Status: provisional architecture candidate.**

## Responsibility

```text
compiled definition + enabling marking + selected binding
                           │
                           ▼
                   OccurrenceContext
                    ├── occurrence identity
                    ├── attempt identity/ordinal
                    ├── exact token/binding evidence
                    └── optional parent correlation
                           │
                           ▼
                 worker/provider request
```

Workers may return observations correlated to this context but cannot use it to modify the net directly.
