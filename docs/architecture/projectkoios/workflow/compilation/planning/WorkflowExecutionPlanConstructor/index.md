# `WorkflowExecutionPlanConstructor`

## Responsibility

`WorkflowExecutionPlanConstructor` closes and compiles all declarative workflow inputs into one `WorkflowExecutionPlan`. It is authoritative for exact membership/order, nested-target closure, fragment composition, CPN lowering, and mapping completeness.

It does not discover definitions or providers. Callers must supply already resolved immutable inputs.
