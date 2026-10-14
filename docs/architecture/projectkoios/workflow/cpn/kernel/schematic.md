# `projectkoios.workflow.cpn.kernel` schematic

## Responsibility

```text
Definition + Marking
        │
        ▼
TransitionEnabler ──▶ complete EnabledBinding set
                              │
                              ▼
                       BindingSelector
                              │
                              ▼
                      selected binding
                              │ + optional external output
                              ▼
                      TransitionFirer
                              │
                              ▼
                     successor Marking
```

Every arrow carries content identities. Stale or substituted inputs fail closed.
