# `projectkoios.workflow.compilation.bindings` schematic

## Responsibility

```text
WorkflowExecutionPlan
+ exact provider descriptors
+ exact worker/environment descriptors
+ exact nested definition references
                 │
                 ▼
WorkflowExecutionBindingsConstructor
                 │
                 ▼
WorkflowExecutionBindings
                 │ already complete
                 ▼
            WorkflowEngine
```

Durable bindings contain descriptor identities and handles. Live plugin objects remain process-local in isolated workers.
