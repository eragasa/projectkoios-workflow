# `WorkflowExecutionBindingsConstructor`

## Responsibility

`WorkflowExecutionBindingsConstructor` proves that one proposed deployment
completely and exactly implements a compiled Workflow plan. It binds atomic
Tasks to exact firer or lifecycle descriptors and workflow-backed Tasks to exact
child-plan deployments.

It does not discover plugins, call handlers, start parent or child runs, or
compensate for an incomplete plan.
