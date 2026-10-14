# `projectkoios.workflow.compilation.definitions` schematic

## Responsibility

```text
AbstractWorkflow ──final property──▶ WorkflowDefinition
AbstractTask ──────final property──▶ TaskDefinition
                                      │
                                      ▼
                         WorkflowExecutionPlanConstructor
```

Definition equality is structural and content-bound. A later change to a source owner creates another definition identity rather than mutating the retained definition.
