# `ColoredPetriNetTransitionEnabler` schematic

## Responsibility

```text
definition + marking
        │ enumerate typed variable assignments
        │ evaluate input arcs and guards
        │ reject capacity-invalid successors
        │ deduplicate canonically
        ▼
complete ordered EnabledBinding tuple
```

Enablement identity binds both the exact definition and exact predecessor marking.
