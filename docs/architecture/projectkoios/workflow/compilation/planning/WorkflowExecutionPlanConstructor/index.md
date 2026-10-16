# `WorkflowExecutionPlanConstructor`

## Responsibility

`WorkflowExecutionPlanConstructor` closes one Workflow definition and its exact
Task-definition closure into one `WorkflowExecutionPlan`. It is authoritative
for membership/order, Task specialization, workflow-backed child-plan closure,
fragment composition, flat parent CPN lowering, and mapping completeness.

It does not discover definitions or providers, execute Tasks, create child runs,
or inline child graphs. Callers supply already resolved immutable inputs.
