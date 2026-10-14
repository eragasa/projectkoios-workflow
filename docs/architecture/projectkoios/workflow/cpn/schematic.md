# `projectkoios.workflow.cpn` schematic

## Responsibility

```text
fragment composition ──▶ flat ColoredPetriNetDefinition
                                 +
                         predecessor marking
                                 │
                                 ▼
validate → enumerate enablement → select → pure fire
                                               │
                                               ▼
                                      successor marking
```

For effect-bound transitions, the runtime reserves a selected binding and obtains an external-output binding before calling the pure firer.
