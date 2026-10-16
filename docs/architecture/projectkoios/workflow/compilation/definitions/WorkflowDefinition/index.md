# `WorkflowDefinition`

## Responsibility

`WorkflowDefinition` is the immutable composite specialization of
`TaskDefinition`. It identifies one Workflow and its ordered run-independent
Task-instance composition without retaining owner objects.

When referenced from a parent, the Workflow definition occupies one Task role.
Its invocation creates a separate child Workflow run. The definition does not
embed that run, its marking, or its separately compiled CPN plan.

Complete executable closure over Tasks, fragments, child targets, canonical CPN
IR, action mappings, and exports belongs to `WorkflowExecutionPlanConstructor`.
