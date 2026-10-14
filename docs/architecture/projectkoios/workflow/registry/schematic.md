# `projectkoios.workflow.registry` schematic

## Responsibility

```text
definition exporter ──canonical candidate──┐
worker manifest ──────capability descriptor─┼─▶ registry validation/storage
BOM/environment ──────compatibility pins────┘
                                              │
                                              ▼
                         compiler/linker exact inputs
```

Provider unavailability changes a status projection; it does not remove the descriptor needed to interpret retained runs.
