# `WorkflowExecutionBindingsConstructor`

## Responsibility

`WorkflowExecutionBindingsConstructor` proves that a proposed deployment completely and exactly implements one compiled execution plan. It is the final validation boundary before a plan can be started in an environment.

It does not discover plugins, call provider code, start a run, or compensate for an incomplete plan.
