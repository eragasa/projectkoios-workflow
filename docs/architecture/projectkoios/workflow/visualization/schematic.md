# `projectkoios.workflow.visualization` schematic

## Responsibility

```text
immutable definition + marking
+ enablement/selection/firing evidence
+ composition map + optional annotations
                  │
                  ▼
       ColoredPetriNetView projection
                  │
          ┌───────┴────────┐
          ▼                ▼
    static SVG       interactive HTML/Web
```

Scientific annotations remain separate from generic identities and cannot affect behavior.
