# `projectkoios.workflow.compilation.planning` schematic

## Responsibility

```text
WorkflowDefinition
+ ordered TaskDefinitions
+ fragments and connections
+ exact NestedWorkflowTargets
              │
              ▼
WorkflowExecutionPlanConstructor
              │ compose, flatten, validate, close
              ▼
     WorkflowExecutionPlan
```

The plan retains source and composition evidence alongside the canonical executable CPN definition.
