# `projectkoios.workflow.sdk.actions` schematic

## Responsibility

```text
owner request/result + action descriptor
                 │ explicit source-definition connection
                 ▼
          compiler action mapping
        ┌────────┴─────────┐
        ▼                  ▼
 pure classification   effectful classification
 pure transition       lifecycle fragment
        │                  │
        └────────┬─────────┘
                 ▼
OccurrenceContext + SelectedBinding
                 │
                 ▼
       TransitionActionBinding
                 │ request mapping
                 ▼
 DataObjectActionRequest → Actionizer → Result
                 │ result mapping
                 ▼
       ExternalOutputBinding
                 │ engine validation
                 ▼
          admitted CPN firing
```

Failure, rejection, cancellation, and ambiguity are attempt outcomes; they do not masquerade as a successful firing. Descriptor metadata constrains lowering but never supplies topology or wiring implicitly.
