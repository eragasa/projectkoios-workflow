# `WorkflowDefinition` schematic

## Responsibility

```text
workflow identity
+ immutable composition declaration
+ contract/compiler version
               │
               ▼
       WorkflowDefinition
               │ exact member of plan input
               ▼
WorkflowExecutionPlanConstructor
```

No arrow returns to a mutable `AbstractWorkflow` instance after construction.
