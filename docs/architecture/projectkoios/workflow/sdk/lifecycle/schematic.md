# `projectkoios.workflow.sdk.lifecycle` schematic

> **Status: provisional architecture candidate.**

## Responsibility

```text
begin occurrence and reserve exact binding
   → prepare (effect-free)
   → stage (first write)
   → grant or deny/expire
   → persist dispatch intent and outbox
   → start (sole launch boundary)
   ├── running → observe → collect terminal evidence
   ├── cancel requested → cancelling → confirmed terminal
   └── ambiguous → reconcile same start key only

admitted success → commit occurrence → domain output tokens
other outcomes  → operational evidence; no domain firing
```

The current alternatives either retain inputs in the predecessor marking under an exact engine reservation or consume them through `begin_occurrence` into a lossless occurrence token. Both prevent duplicate launch and preserve the same invariant: only admitted success may commit the reserved logical/domain transition. A workflow needing a domain failure token uses a separate explicit guarded transition over operational failure evidence.
