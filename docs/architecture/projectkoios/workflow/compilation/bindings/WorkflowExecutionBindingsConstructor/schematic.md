# `WorkflowExecutionBindingsConstructor` schematic

## Responsibility

```text
exact plan + proposed binding descriptors
                  │
                  ├── membership/order equality
                  ├── definition/version equality
                  ├── route/effect compatibility
                  ├── capability/protocol compatibility
                  └── nested-target equality
                  │
                  ▼
 complete bindings | closed findings
```

The engine accepts only the completed aggregate and therefore needs no registry access.
