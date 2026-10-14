# `AbstractWorkflow` schematic

## Responsibility

```text
ConcreteScientificWorkflow
          │ implements declarations
          ▼
    AbstractWorkflow
          │ final definition construction
          ▼
    WorkflowDefinition
          │ compiler input
          ▼
 WorkflowExecutionPlan
```

The arrow from the concrete owner ends at immutable definition construction. The plan retains no reference back to the owner object.
