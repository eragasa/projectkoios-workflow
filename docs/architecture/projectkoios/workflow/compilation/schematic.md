# `projectkoios.workflow.compilation` schematic

## Responsibility

```text
registry-resolved source owners
          │ final frozen definitions
          ▼
 definitions → planning/compiler → WorkflowExecutionPlan
                                      │
provider/environment descriptors ─────┤
                                      ▼
                             binding linker
                                      ▼
                      WorkflowExecutionBindings
                                      │
                                      ▼
                           runtime CPN engine
```

Discovery occurs before compilation and linking. Runtime receives exact artifacts and performs no identity-only inference.
