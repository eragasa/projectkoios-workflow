# `WorkflowExecutionBindings`

## Responsibility

`WorkflowExecutionBindings` is the immutable deployment linkage for one exact
Workflow plan. It records the complete ordered correspondence between compiled
Task-instance mappings and pure firers, effect lifecycle handlers, worker
environments, or child Workflow deployments.

For a pure atomic Task it retains the exact SDK descriptor, manifest, and
plan-selected result mapping. For an effectful atomic Task it retains the exact
accepted lifecycle descriptor. For a workflow-backed Task it retains the exact
child-plan deployment and child-run route contract. It contains no live
implementation object.

Changing a provider, environment, or child deployment creates another binding
artifact. Changing Task semantics, output mapping, or child target requires a
new execution plan before it can be linked.

## Current bounded candidate

`ExperimentalWorkflowPureActionExecutionBindings` and its input extension link
one exact existing pure-action plan to one canonical SDK manifest. They remain
bounded evidence for a pure atomic Task route and do not implement effectful or
workflow-backed Task binding.
