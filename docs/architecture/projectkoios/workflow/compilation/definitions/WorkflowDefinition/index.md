# `WorkflowDefinition`

## Responsibility

`WorkflowDefinition` is the immutable generic snapshot of one external workflow source owner. It identifies the workflow and its declared composition without retaining the owner object.

It is not yet the complete executable plan. Closure over tasks, fragments, nested targets, canonical CPN IR, and action mappings belongs to `WorkflowExecutionPlanConstructor`.
