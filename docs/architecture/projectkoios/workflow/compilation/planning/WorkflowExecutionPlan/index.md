# `WorkflowExecutionPlan`

## Responsibility

`WorkflowExecutionPlan` is the immutable durable declaration of one compiled
Workflow. It closes the exact Workflow and Task-definition inputs, canonical
flat CPN IR, Task-instance mappings, atomic route descriptors,
workflow-backed-Task child-plan references, input/export contracts, and compiler
evidence.

It contains no live owner Task, handler, firer, provider, effect, authority,
repository, run, marking, or process-local handle. A child Workflow plan remains
a separate artifact and run target; deployment binding is also separate.

## Current bounded candidate

`ExperimentalWorkflowPureActionExecutionPlan` and its input/CPN extensions close
only one pure atomic Task route under the existing `pure-action` terminology.
They retain selected-binding, source-mapping, output-mapping, definition, and
candidate execution-profile evidence. Their schemas and identities remain
unchanged compatibility evidence.

These records do not implement Task-definition closure, Workflow composition,
workflow-backed Tasks, child delivery, complete CPN profile closure, or the full
CPN-bindings contract.
