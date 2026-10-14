# `WorkflowExecutionPlanConstructor` schematic

## Responsibility

```text
resolved immutable inputs
          │
          ├── validate identity/order/membership
          ├── close nested targets
          ├── compose fragments deterministically
          ├── flatten and validate CPN
          └── close transition/action mappings
          │
          ▼
complete plan | closed findings
```

No intermediate partial plan crosses the constructor boundary.
