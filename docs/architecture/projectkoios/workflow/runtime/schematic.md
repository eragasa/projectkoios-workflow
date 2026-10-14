# `projectkoios.workflow.runtime` schematic

> **Status: provisional architecture candidate.**

## Responsibility

```text
compiled+linked plan + net instance marking
                 │
                 ▼
        enable/select/begin occurrence
                 │ reserve exact binding
                 ▼
       one or more correlated attempts
                 │
      ┌──────────┼───────────┐
      ▼          ▼           ▼
  success     failure     ambiguous
      │          │           │
      ▼          ▼           ▼
commit domain   operational  reconcile only
transition      evidence
      │
      ▼
successor marking and provenance
```

Long-running effects never hold a database transaction. Exact reservations and CAS protect firing. Failure evidence may enable a separately declared guarded domain transition, but the failed reserved transition itself does not fire.
