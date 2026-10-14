# `ExternalLifecycleProvider` schematic

## Responsibility

```text
Workflow occurrence/attempt
          │ typed lifecycle requests
          ▼
ExternalLifecycleProvider
          │
          ├── immutable workspace evidence
          ├── generation-safe job handle
          ├── dispatch receipt
          ├── observations/reconciliation
          └── closed terminal evidence
```

A lost response after possible launch returns `Ambiguous`; it never returns an ordinary failure that would permit automatic redispatch.
