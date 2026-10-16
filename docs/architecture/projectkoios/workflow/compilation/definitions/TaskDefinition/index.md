# `TaskDefinition`

## Responsibility

`TaskDefinition` is the immutable source-level description of one parent-visible
Task role. It binds exact identity, definition kind, contracts, and either atomic
route state or composite Workflow state.

Atomic Task definitions name one pure firer or effect lifecycle route.
`WorkflowDefinition` is the composite specialization and is therefore valid in
a parent Task position. Task definition identity is distinct from run-scoped
Task instance, invocation, occurrence, attempt, and result identities.
